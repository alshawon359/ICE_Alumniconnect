#!/bin/bash
# ============================================================================
# AlumniConnect Production Deployment Script
# ============================================================================
# Sets up production-ready deployment on csf.ru.ac.bd
# This script handles:
# - Environment configuration
# - Database setup
# - Frontend build
# - Backend setup
# - Nginx configuration
# - Service startup and verification
# ============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_PATH="/var/www/html/iceaa/ICE_AlumniConnect"
BACKEND_PATH="${REPO_PATH}/backend"
FRONTEND_PATH="${REPO_PATH}/react-app"
LOG_DIR="/var/log/alumniconnect"
NGINX_CONFIG="/etc/nginx/sites-enabled/iceaa.conf"
SERVICE_NAME="alumniconnect"

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_step() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command not found: $1"
        exit 1
    fi
}

# ============================================================================
# Step 1: Verify Prerequisites
# ============================================================================

step_verify_prerequisites() {
    log_step "Step 1: Verifying Prerequisites"
    
    check_command "python3"
    check_command "node"
    check_command "npm"
    check_command "nginx"
    check_command "mysql"
    
    if [ ! -d "$REPO_PATH" ]; then
        log_error "Repository not found at $REPO_PATH"
        exit 1
    fi
    
    log_success "All prerequisites found"
}

# ============================================================================
# Step 2: Create directories and set permissions
# ============================================================================

step_setup_directories() {
    log_step "Step 2: Setting up directories and permissions"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    chown -R www-data:www-data "$LOG_DIR"
    chmod 755 "$LOG_DIR"
    log_success "Log directory created: $LOG_DIR"
    
    # Create uploads directory if needed
    mkdir -p "${BACKEND_PATH}/uploads"
    chown -R www-data:www-data "${BACKEND_PATH}/uploads"
    chmod 755 "${BACKEND_PATH}/uploads"
    log_success "Uploads directory created"
    
    # Ensure repo ownership
    chown -R www-data:www-data "$REPO_PATH"
    chmod -R 755 "$REPO_PATH"
    log_success "Repository ownership set"
}

# ============================================================================
# Step 3: Setup Backend Environment
# ============================================================================

step_setup_backend_env() {
    log_step "Step 3: Setting up Backend Environment"
    
    if [ ! -f "${BACKEND_PATH}/.env.production" ]; then
        log_warning "Production env file not found. Using template..."
        cp "${BACKEND_PATH}/.env.production.example" "${BACKEND_PATH}/.env.production" 2>/dev/null || \
        cp "${BACKEND_PATH}/.env.local.production" "${BACKEND_PATH}/.env.production"
    fi
    
    log_info "Please verify settings in: ${BACKEND_PATH}/.env.production"
    log_warning "Critical variables to update:"
    echo "  - SECRET_KEY (must be random 32+ chars)"
    echo "  - MYSQL_PASSWORD"
    echo "  - BREVO_API_KEY (optional, for email)"
    echo ""
    
    # Source the env file for verification
    set -a
    source "${BACKEND_PATH}/.env.production"
    set +a
    
    # Verify critical settings
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE_THIS_TO_RANDOM_32_CHAR_KEY_12345678" ]; then
        log_error "SECRET_KEY not set or using default placeholder"
        log_info "Generate a secure key with: head -c 32 /dev/urandom | base64"
        exit 1
    fi
    
    if [ -z "$MYSQL_PASSWORD" ] || [ "$MYSQL_PASSWORD" = "CHANGE_THIS_PASSWORD" ]; then
        log_error "MYSQL_PASSWORD not set or using default"
        exit 1
    fi
    
    log_success "Backend environment configured"
}

# ============================================================================
# Step 4: Setup Database
# ============================================================================

step_setup_database() {
    log_step "Step 4: Setting up Database"
    
    # Source env again
    set -a
    source "${BACKEND_PATH}/.env.production"
    set +a
    
    # Test MySQL connection
    if ! mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" -e "SELECT 1" &>/dev/null; then
        log_error "Cannot connect to MySQL database"
        log_info "Verify: Host=$MYSQL_HOST User=$MYSQL_USER DB=$MYSQL_DB"
        exit 1
    fi
    log_success "MySQL connection verified"
    
    # Create database if not exists
    mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
        -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DB};"
    log_success "Database exists: $MYSQL_DB"
    
    # Apply schema
    if [ -f "${BACKEND_PATH}/schema.sql" ]; then
        mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
            "${MYSQL_DB}" < "${BACKEND_PATH}/schema.sql"
        log_success "Database schema applied"
    else
        log_warning "schema.sql not found - database tables should exist already"
    fi
}

# ============================================================================
# Step 5: Build Frontend
# ============================================================================

step_build_frontend() {
    log_step "Step 5: Building Frontend (React)"
    
    cd "$FRONTEND_PATH"
    
    log_info "Installing dependencies..."
    npm ci --legacy-peer-deps
    
    log_info "Building for production (base path: /iceaa/)..."
    npm run build
    
    if [ ! -d "${FRONTEND_PATH}/dist" ]; then
        log_error "Frontend build failed - dist folder not created"
        exit 1
    fi
    
    if [ ! -f "${FRONTEND_PATH}/dist/index.html" ]; then
        log_error "Frontend build failed - index.html not found"
        exit 1
    fi
    
    log_success "Frontend built successfully"
    log_info "Build output: ${FRONTEND_PATH}/dist"
}

# ============================================================================
# Step 6: Setup Backend Python Environment
# ============================================================================

step_setup_backend_python() {
    log_step "Step 6: Setting up Backend Python Environment"
    
    cd "$BACKEND_PATH"
    
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    log_info "Activating virtual environment and installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    
    log_success "Python environment ready"
}

# ============================================================================
# Step 7: Configure Nginx
# ============================================================================

step_configure_nginx() {
    log_step "Step 7: Configuring Nginx"
    
    if [ ! -f "$NGINX_CONFIG" ]; then
        log_info "Creating Nginx configuration..."
        sudo cp "${REPO_PATH}/deployment/nginx/alumniconnect_iceaa.conf" "$NGINX_CONFIG"
    fi
    
    # Test Nginx config
    if ! nginx -t &>/dev/null; then
        log_error "Nginx configuration test failed"
        nginx -t
        exit 1
    fi
    
    log_success "Nginx configuration valid"
}

# ============================================================================
# Step 8: Create/Update Systemd Service
# ============================================================================

step_setup_systemd_service() {
    log_step "Step 8: Setting up Systemd Service"
    
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
    
    if [ ! -f "$SERVICE_FILE" ]; then
        log_info "Creating systemd service file..."
        cat > "$SERVICE_FILE" << 'SERVICEEOF'
[Unit]
Description=AlumniConnect Backend API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/html/iceaa/ICE_AlumniConnect/backend
Environment="APP_ENV=production"
EnvironmentFile=/var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production
ExecStart=/var/www/html/iceaa/ICE_AlumniConnect/backend/venv/bin/gunicorn -c gunicorn.conf.py wsgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF
        
        chmod 644 "$SERVICE_FILE"
        systemctl daemon-reload
        log_success "Systemd service created"
    else
        log_info "Service file already exists"
    fi
}

# ============================================================================
# Step 9: Start Services
# ============================================================================

step_start_services() {
    log_step "Step 9: Starting Services"
    
    log_info "Restarting Nginx..."
    systemctl restart nginx
    if systemctl is-active --quiet nginx; then
        log_success "Nginx running"
    else
        log_error "Nginx failed to start"
        systemctl status nginx
        exit 1
    fi
    
    log_info "Starting backend service..."
    systemctl restart "$SERVICE_NAME"
    sleep 2
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "Backend service running"
    else
        log_error "Backend service failed to start"
        systemctl status "$SERVICE_NAME"
        journalctl -u "$SERVICE_NAME" -n 20
        exit 1
    fi
}

# ============================================================================
# Step 10: Verification Tests
# ============================================================================

step_verify_deployment() {
    log_step "Step 10: Verifying Deployment"
    
    sleep 2
    
    # Test 1: Check ports
    log_info "Checking ports..."
    if ss -tulpn | grep -q ":80 "; then
        log_success "Port 80 listening (Nginx)"
    else
        log_error "Port 80 not listening"
    fi
    
    if ss -tulpn | grep -q "127.0.0.1:5000"; then
        log_success "Port 5000 listening (Gunicorn)"
    else
        log_error "Port 5000 not listening"
    fi
    
    # Test 2: Frontend
    log_info "Testing frontend..."
    FRONTEND_TEST=$(curl -s -I http://localhost/iceaa/ | head -n1)
    if echo "$FRONTEND_TEST" | grep -q "200\|301"; then
        log_success "Frontend responds: $FRONTEND_TEST"
    else
        log_warning "Frontend response unexpected: $FRONTEND_TEST"
    fi
    
    # Test 3: Backend health
    log_info "Testing backend health endpoint..."
    HEALTH_TEST=$(curl -s http://localhost/iceaa/api/health)
    if echo "$HEALTH_TEST" | grep -q "success"; then
        log_success "Backend health check passed"
    else
        log_warning "Backend health check: $HEALTH_TEST"
    fi
    
    # Test 4: Services
    log_info "Checking service status..."
    systemctl status nginx --no-pager | head -n 3
    systemctl status "$SERVICE_NAME" --no-pager | head -n 3
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_step "AlumniConnect Production Deployment"
    log_info "This script will set up a production-ready deployment"
    log_info "Domain: csf.ru.ac.bd/iceaa"
    echo ""
    
    check_root
    
    step_verify_prerequisites
    step_setup_directories
    step_setup_backend_env
    step_setup_database
    step_build_frontend
    step_setup_backend_python
    step_configure_nginx
    step_setup_systemd_service
    step_start_services
    step_verify_deployment
    
    echo ""
    log_step "✓ DEPLOYMENT COMPLETE!"
    echo ""
    log_success "AlumniConnect is now deployed and running"
    echo ""
    echo "Access your application:"
    echo "  URL: http://csf.ru.ac.bd/iceaa/"
    echo ""
    echo "Check logs:"
    echo "  Backend:  journalctl -u $SERVICE_NAME -f"
    echo "  Nginx:    tail -f /var/log/nginx/iceaa_error.log"
    echo ""
    echo "Update config:"
    echo "  Edit: ${BACKEND_PATH}/.env.production"
    echo "  Then: systemctl restart $SERVICE_NAME"
    echo ""
}

main "$@"
