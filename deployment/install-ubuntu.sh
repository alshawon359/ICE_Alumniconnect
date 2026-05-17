#!/bin/bash
###############################################################################
# AlumniConnect Production Deployment Script for Ubuntu/Debian
# 
# Usage: sudo bash deploy.sh
# 
# This script:
# - Installs system dependencies
# - Sets up Python virtual environment
# - Installs Python packages
# - Configures MySQL database
# - Enables systemd service
# - Configures SSL with Let's Encrypt
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
# Please update these values before running:
DOMAIN="your-domain.com"  # CHANGE THIS: Replace with your actual domain
APP_DIR="/var/www/alumniconnect"
APP_USER="www-data"
PYTHON_BIN="python3"

echo -e "${GREEN}====== AlumniConnect Production Deployment (Gunicorn) ======${NC}"

# ============================================
# 1. Check if running as root
# ============================================
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}[1/8] Installing system dependencies...${NC}"

# Update package lists
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    mysql-server \
    mysql-client \
    curl \
    git \
    certbot \
    build-essential \
    libssl-dev \
    libffi-dev

echo -e "${GREEN}[2/8] Creating application directory...${NC}"

# Create app directory
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or copy application (assuming git repo)
if [ ! -d "$APP_DIR/.git" ]; then
    echo -e "${YELLOW}Git repository not found. Please clone your repository into $APP_DIR${NC}"
    echo "Example: git clone <your-repo> $APP_DIR"
    exit 1
fi

# ============================================
# 3. Setup Python virtual environment
# ============================================
echo -e "${GREEN}[3/8] Setting up Python virtual environment...${NC}"

${PYTHON_BIN} -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r backend/requirements.txt

# ============================================
# 4. Setup MySQL database
# ============================================
echo -e "${GREEN}[4/8] Setting up MySQL database...${NC}"

# Start MySQL
systemctl start mysql
systemctl enable mysql

# Create database and user
MYSQL_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")

mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS alumniconnect;
CREATE USER IF NOT EXISTS 'alumni_user'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';
GRANT ALL PRIVILEGES ON alumniconnect.* TO 'alumni_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo -e "${YELLOW}MySQL password saved: $MYSQL_PASSWORD${NC}"

# ============================================
# 5. Create production .env file
# ============================================
echo -e "${GREEN}[5/8] Creating production configuration...${NC}"

# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Create .env.production file
cat > "$APP_DIR/backend/.env.production" <<EOF
APP_ENV=production
DEBUG=false
SECRET_KEY=$SECRET_KEY
PORT=5000
PUBLIC_BASE_URL=https://$DOMAIN

MYSQL_USER=alumni_user
MYSQL_PASSWORD=$MYSQL_PASSWORD
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=alumniconnect

MAIL_PROVIDER=brevo
BREVO_API_KEY=<ADD-YOUR-BREVO-API-KEY>
SMTP_FROM_EMAIL=noreply@$DOMAIN
SMTP_FROM_NAME=AlumniConnect

CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

LOG_LEVEL=INFO
LOG_FILE=/var/log/alumniconnect/app.log
LOG_ERROR_FILE=/var/log/alumniconnect/error.log

CLOUDINARY_CLOUD_NAME=<ADD-YOUR-CLOUDINARY-CLOUD-NAME>
CLOUDINARY_API_KEY=<ADD-YOUR-CLOUDINARY-API-KEY>
CLOUDINARY_API_SECRET=<ADD-YOUR-CLOUDINARY-API-SECRET>

ADMIN_USERNAME=admin
ADMIN_PASSWORD=<CHANGE-ME>

RATELIMIT_ENABLED=true
RATELIMIT_STORAGE_URL=memory://
EOF

chmod 600 "$APP_DIR/backend/.env.production"

echo -e "${YELLOW}Created $APP_DIR/backend/.env.production${NC}"
echo -e "${YELLOW}Please edit and add missing credentials (Brevo API key, Cloudinary, admin password)${NC}"

# ============================================
# 6. Create log directory
# ============================================
echo -e "${GREEN}[6/8] Setting up logging...${NC}"

mkdir -p /var/log/alumniconnect
chown -R $APP_USER:$APP_USER /var/log/alumniconnect
chmod 755 /var/log/alumniconnect

# ============================================
# 7. Setup SSL with Let's Encrypt
# ============================================
echo -e "${GREEN}[7/8] Setting up SSL certificate...${NC}"

certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

# ============================================
# 8. Setup systemd service
# ============================================
echo -e "${GREEN}[8/8] Setting up systemd service and Gunicorn...${NC}"

# Copy systemd service file
cp "$APP_DIR/deployment/systemd/alumniconnect.service" /etc/systemd/system/

# Create service wrapper script
cat > "$APP_DIR/run-gunicorn.sh" <<'GUNICORN_SCRIPT'
#!/bin/bash
set -e

cd /var/www/alumniconnect
source venv/bin/activate

export APP_ENV=production
export PYTHONUNBUFFERED=1

exec gunicorn \
    --workers 4 \
    --worker-class sync \
    --threads 2 \
    --bind 127.0.0.1:5000 \
    --timeout 120 \
    --access-logfile /var/log/alumniconnect/access.log \
    --error-logfile /var/log/alumniconnect/error.log \
    --log-level info \
    wsgi:application
GUNICORN_SCRIPT

chmod +x "$APP_DIR/run-gunicorn.sh"

# Enable and start service
systemctl daemon-reload
systemctl enable alumniconnect
systemctl start alumniconnect



# ============================================
# Final Status
# ============================================
echo ""
echo -e "${GREEN}====== Deployment Complete ======${NC}"
echo ""
echo "✓ System dependencies installed"
echo "✓ Python virtual environment created"
echo "✓ MySQL database configured"
echo "✓ Gunicorn configured"
echo "✓ SSL certificate installed"
echo "✓ Systemd service enabled"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Edit $APP_DIR/backend/.env.production and add:"
echo "   - BREVO_API_KEY"
echo "   - CLOUDINARY_* credentials"
echo "   - ADMIN_PASSWORD"
echo ""
echo "2. Test the application:"
echo "   curl https://$DOMAIN/api/health"
echo ""
echo "3. View application logs:"
echo "   journalctl -u alumniconnect -f"
echo ""
echo "4. View access logs:"
echo "   tail -f /var/log/alumniconnect/access.log"
echo ""
echo "5. Restart application after config changes:"
echo "   systemctl restart alumniconnect"
echo ""
echo -e "${GREEN}Deployment ready!${NC}"
