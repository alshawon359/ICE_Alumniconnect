#!/bin/bash
# ============================================================================
# AlumniConnect Production Health Check
# ============================================================================
# Verifies all components are working correctly in production

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

log_pass() {
    echo -e "${GREEN}[✓]${NC} $1"
    ((CHECKS_PASSED++))
}

log_fail() {
    echo -e "${RED}[✗]${NC} $1"
    ((CHECKS_FAILED++))
}

log_warn() {
    echo -e "${YELLOW}[⚠]${NC} $1"
    ((CHECKS_WARNING++))
}

log_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

log_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
}

# ============================================================================
# Health Checks
# ============================================================================

check_services() {
    log_header "1. Service Status"
    
    # Nginx
    if systemctl is-active --quiet nginx; then
        log_pass "Nginx is running"
    else
        log_fail "Nginx is NOT running"
    fi
    
    # Backend service
    if systemctl is-active --quiet alumniconnect; then
        log_pass "Backend service is running"
    else
        log_fail "Backend service is NOT running"
    fi
    
    # MySQL
    if mysqladmin ping -h localhost >/dev/null 2>&1; then
        log_pass "MySQL is running"
    else
        log_fail "MySQL is NOT running"
    fi
}

check_ports() {
    log_header "2. Port Availability"
    
    # Port 80 (Nginx)
    if ss -tulpn 2>/dev/null | grep -q ":80 "; then
        log_pass "Port 80 (Nginx) is listening"
    else
        log_fail "Port 80 (Nginx) is NOT listening"
    fi
    
    # Port 5000 (Gunicorn)
    if ss -tulpn 2>/dev/null | grep -q "127.0.0.1:5000"; then
        log_pass "Port 5000 (Gunicorn) is listening on 127.0.0.1"
    else
        log_fail "Port 5000 (Gunicorn) is NOT listening"
    fi
    
    # Port 3306 (MySQL)
    if ss -tulpn 2>/dev/null | grep -q ":3306 "; then
        log_pass "Port 3306 (MySQL) is listening"
    else
        log_fail "Port 3306 (MySQL) is NOT listening"
    fi
}

check_frontend() {
    log_header "3. Frontend Deployment"
    
    REPO_PATH="/var/www/html/iceaa/ICE_AlumniConnect"
    
    # Check build exists
    if [ -d "${REPO_PATH}/react-app/dist" ]; then
        log_pass "Frontend build directory exists"
    else
        log_fail "Frontend build directory does not exist"
        return
    fi
    
    # Check index.html
    if [ -f "${REPO_PATH}/react-app/dist/index.html" ]; then
        log_pass "Frontend index.html exists"
    else
        log_fail "Frontend index.html not found"
    fi
    
    # Check assets
    if ls "${REPO_PATH}/react-app/dist/assets/" *.js >/dev/null 2>&1; then
        log_pass "Frontend JavaScript assets exist"
    else
        log_fail "Frontend JavaScript assets not found"
    fi
    
    # HTTP test
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/iceaa/)
    if [ "$HTTP_STATUS" = "200" ]; then
        log_pass "Frontend responds (HTTP 200): http://localhost/iceaa/"
    else
        log_fail "Frontend HTTP error: $HTTP_STATUS"
    fi
}

check_backend() {
    log_header "4. Backend API"
    
    # Health check endpoint
    HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost/iceaa/api/health)
    HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
    BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        log_pass "Backend health check passed (HTTP 200)"
        if echo "$BODY" | grep -q "success"; then
            log_pass "Backend returns success status"
        else
            log_warn "Backend response: $BODY"
        fi
    else
        log_fail "Backend health check failed (HTTP $HTTP_CODE)"
    fi
}

check_database() {
    log_header "5. Database Connectivity"
    
    # Check if we can connect
    if ! mysql -h localhost -u root -e "SELECT 1" >/dev/null 2>&1; then
        log_fail "Cannot connect to MySQL"
        return
    fi
    log_pass "MySQL connection successful"
    
    # Check if database exists
    if mysql -h localhost -u root -e "USE alumniconnect;" >/dev/null 2>&1; then
        log_pass "Database 'alumniconnect' exists"
    else
        log_fail "Database 'alumniconnect' not found"
        return
    fi
    
    # Check tables
    TABLE_COUNT=$(mysql -h localhost -u root -D alumniconnect -se "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA='alumniconnect';" 2>/dev/null || echo "0")
    if [ "$TABLE_COUNT" -gt 0 ]; then
        log_pass "Database has $TABLE_COUNT tables"
    else
        log_warn "Database has no tables"
    fi
}

check_logs() {
    log_header "6. Log Files"
    
    LOG_DIR="/var/log/alumniconnect"
    
    if [ -d "$LOG_DIR" ]; then
        log_pass "Log directory exists: $LOG_DIR"
        
        # Check for recent errors in app.log
        if [ -f "${LOG_DIR}/app.log" ]; then
            ERROR_COUNT=$(grep -c "ERROR\|CRITICAL" "${LOG_DIR}/app.log" 2>/dev/null || echo "0")
            if [ "$ERROR_COUNT" -eq 0 ]; then
                log_pass "No errors in app.log"
            else
                log_warn "Found $ERROR_COUNT errors in app.log (last 5):"
                grep "ERROR\|CRITICAL" "${LOG_DIR}/app.log" | tail -5 | sed 's/^/    /'
            fi
        fi
        
        # Check Nginx error log
        if [ -f "/var/log/nginx/iceaa_error.log" ]; then
            NGINX_ERRORS=$(wc -l < "/var/log/nginx/iceaa_error.log")
            if [ "$NGINX_ERRORS" -lt 10 ]; then
                log_pass "Nginx error log is clean ($NGINX_ERRORS lines)"
            else
                log_warn "Nginx error log has $NGINX_ERRORS lines"
            fi
        fi
    else
        log_warn "Log directory does not exist: $LOG_DIR"
    fi
}

check_environment() {
    log_header "7. Environment Configuration"
    
    BACKEND_PATH="/var/www/html/iceaa/ICE_AlumniConnect/backend"
    ENV_FILE="${BACKEND_PATH}/.env.production"
    
    if [ -f "$ENV_FILE" ]; then
        log_pass "Production environment file exists"
        
        # Check critical variables
        if grep -q "^SECRET_KEY=" "$ENV_FILE"; then
            SECRET_KEY=$(grep "^SECRET_KEY=" "$ENV_FILE" | cut -d= -f2)
            if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE_THIS_TO_RANDOM_32_CHAR_KEY_12345678" ]; then
                log_fail "SECRET_KEY is not set or using placeholder"
            else
                log_pass "SECRET_KEY is configured"
            fi
        fi
        
        if grep -q "^MYSQL_PASSWORD=" "$ENV_FILE"; then
            MYSQL_PASS=$(grep "^MYSQL_PASSWORD=" "$ENV_FILE" | cut -d= -f2)
            if [ -z "$MYSQL_PASS" ] || [ "$MYSQL_PASS" = "CHANGE_THIS_PASSWORD" ]; then
                log_fail "MYSQL_PASSWORD is not set or using placeholder"
            else
                log_pass "MYSQL_PASSWORD is configured"
            fi
        fi
        
        if grep -q "^CORS_ORIGINS=" "$ENV_FILE"; then
            CORS=$(grep "^CORS_ORIGINS=" "$ENV_FILE" | cut -d= -f2)
            log_info "CORS origins: $CORS"
        fi
    else
        log_fail "Production environment file not found: $ENV_FILE"
    fi
}

check_permissions() {
    log_header "8. File Permissions"
    
    REPO_PATH="/var/www/html/iceaa/ICE_AlumniConnect"
    
    # Check ownership
    OWNER=$(stat -c %U "$REPO_PATH" 2>/dev/null || echo "unknown")
    if [ "$OWNER" = "www-data" ] || [ "$OWNER" = "root" ]; then
        log_pass "Repository ownership OK ($OWNER)"
    else
        log_warn "Repository owner is $OWNER (expected www-data or root)"
    fi
    
    # Check uploads directory
    if [ -d "${REPO_PATH}/backend/uploads" ]; then
        if [ -w "${REPO_PATH}/backend/uploads" ]; then
            log_pass "Uploads directory is writable"
        else
            log_warn "Uploads directory is NOT writable"
        fi
    fi
}

check_nginx_config() {
    log_header "9. Nginx Configuration"
    
    if nginx -t 2>&1 | grep -q "successful"; then
        log_pass "Nginx configuration is valid"
    else
        log_fail "Nginx configuration has errors:"
        nginx -t
    fi
}

# ============================================================================
# Summary
# ============================================================================

print_summary() {
    log_header "Summary"
    
    TOTAL=$((CHECKS_PASSED + CHECKS_FAILED + CHECKS_WARNING))
    
    echo ""
    echo "  ✓ Passed:  $CHECKS_PASSED"
    echo "  ✗ Failed:  $CHECKS_FAILED"
    echo "  ⚠ Warning: $CHECKS_WARNING"
    echo "  ─────────────"
    echo "  Total:   $TOTAL"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✓ All critical checks passed!${NC}"
        echo -e "${GREEN}Your application is production-ready.${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
        return 0
    else
        echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}✗ Some checks failed. Please review above.${NC}"
        echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
        return 1
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    check_services
    check_ports
    check_frontend
    check_backend
    check_database
    check_logs
    check_environment
    check_permissions
    check_nginx_config
    print_summary
}

main "$@"
