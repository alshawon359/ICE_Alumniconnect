#!/usr/bin/env bash
# Setup and Test Script for AlumniConnect at csf.ru.ac.bd/iceaa
# This script sets up HTTPS without Let's Encrypt SSL/TLS certificates
# Use this when you want self-signed certificates for testing

set -euo pipefail

echo "=========================================="
echo "AlumniConnect Setup - Self-Signed HTTPS"
echo "=========================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# 1. Create self-signed certificate directory
echo -e "${YELLOW}[1/6]${NC} Creating certificate directory..."
mkdir -p /etc/nginx/certs

# 2. Generate self-signed certificate if not exists
if [ ! -f /etc/nginx/certs/self-signed.crt ]; then
    echo -e "${YELLOW}[2/6]${NC} Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -out /etc/nginx/certs/self-signed.crt \
        -keyout /etc/nginx/certs/self-signed.key \
        -days 365 \
        -subj "/CN=csf.ru.ac.bd/O=AlumniConnect/C=BD"
    chmod 644 /etc/nginx/certs/self-signed.crt
    chmod 600 /etc/nginx/certs/self-signed.key
    echo -e "${GREEN}✓ Certificate generated at /etc/nginx/certs/self-signed.crt${NC}"
else
    echo -e "${GREEN}✓ Certificate already exists${NC}"
fi

# 3. Update Nginx configuration
echo -e "${YELLOW}[3/6]${NC} Setting up Nginx configuration..."
REPO_PATH="/var/www/html/iceaa/ICE_AlumniConnect"

if [ ! -f "$REPO_PATH/deployment/nginx/alumniconnect_iceaa.conf" ]; then
    echo -e "${RED}✗ Repository not found at $REPO_PATH${NC}"
    exit 1
fi

# Backup existing config if it exists
if [ -f /etc/nginx/sites-available/default ]; then
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%s)
fi

# Copy updated config to nginx
cp "$REPO_PATH/deployment/nginx/alumniconnect_iceaa.conf" /etc/nginx/sites-available/default
echo -e "${GREEN}✓ Nginx config updated${NC}"

# 4. Test Nginx configuration
echo -e "${YELLOW}[4/6]${NC} Testing Nginx configuration..."
if nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
else
    echo -e "${RED}✗ Nginx configuration test failed${NC}"
    exit 1
fi

# 5. Reload Nginx
echo -e "${YELLOW}[5/6]${NC} Reloading Nginx..."
systemctl reload nginx
echo -e "${GREEN}✓ Nginx reloaded${NC}"

# 6. Start/restart backend service
echo -e "${YELLOW}[6/6]${NC} Starting AlumniConnect service..."
if systemctl is-active --quiet alumniconnect; then
    systemctl restart alumniconnect
    echo -e "${GREEN}✓ AlumniConnect service restarted${NC}"
else
    systemctl start alumniconnect
    echo -e "${GREEN}✓ AlumniConnect service started${NC}"
fi

# Verification
echo ""
echo -e "${GREEN}=========================================="
echo "Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "✓ Self-signed certificate: /etc/nginx/certs/self-signed.crt"
echo "✓ Nginx configured for HTTPS (port 443)"
echo "✓ HTTP (port 80) redirects to HTTPS"
echo ""
echo "Testing connectivity..."
echo ""

# Test backend health
echo "Testing backend health..."
if curl -s -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health | grep -q success; then
    echo -e "${GREEN}✓ Backend is responsive${NC}"
else
    echo -e "${YELLOW}⚠ Backend might not be ready (normal if first start)${NC}"
fi

echo ""
echo "Access URLs:"
echo "  HTTP (auto-redirects):   http://csf.ru.ac.bd/iceaa/"
echo "  HTTPS (self-signed):     https://csf.ru.ac.bd/iceaa/"
echo ""
echo "Note: Browser will show certificate warning for self-signed cert - this is normal"
echo "      Click 'Advanced' and proceed when testing locally"
echo ""

# Set env vars if not already set
APP_ENV_FILE="/var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production"
if [ -f "$APP_ENV_FILE" ]; then
    echo "Verifying environment variables..."
    if ! grep -q "PUBLIC_BASE_URL" "$APP_ENV_FILE"; then
        echo "PUBLIC_BASE_URL=https://csf.ru.ac.bd/iceaa" >> "$APP_ENV_FILE"
        echo "  Added PUBLIC_BASE_URL"
    fi
    if ! grep -q "CORS_ORIGINS" "$APP_ENV_FILE"; then
        echo "CORS_ORIGINS=https://csf.ru.ac.bd" >> "$APP_ENV_FILE"
        echo "  Added CORS_ORIGINS"
    fi
fi

echo -e "${GREEN}Setup successful!${NC}"
