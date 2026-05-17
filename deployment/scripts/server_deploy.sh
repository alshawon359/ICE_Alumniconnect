#!/bin/bash
# Server Deployment Script - AlumniConnect HTTPS Fix
# রান করুন server-এ root হিসেবে

set -euo pipefail

echo "╔════════════════════════════════════════════════════════╗"
echo "║   AlumniConnect - Server Deployment & Setup           ║"
echo "║   HTTPS 443 Fix - Self-Signed Certificate             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Configuration
REPO_PATH="/var/www/html/iceaa/ICE_AlumniConnect"
REPO_URL="https://github.com/alshawon359/ICE_Alumniconnect.git"
BRANCH="main"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 1: Verify Permissions${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}✗ This script must be run as root${NC}"
   exit 1
fi
echo -e "${GREEN}✓ Running as root${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 2: Check Repository${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -d "$REPO_PATH" ]; then
    echo -e "${RED}✗ Repository not found at $REPO_PATH${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Repository exists at $REPO_PATH${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 3: Pull Latest Code from GitHub${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$REPO_PATH"

# Check git status
echo "Current git status:"
git status --short | head -5 || echo "  (clean)"
echo ""

# Pull latest
echo "Pulling from GitHub ($BRANCH branch)..."
if git pull origin "$BRANCH"; then
    echo -e "${GREEN}✓ Pull successful${NC}"
else
    echo -e "${YELLOW}⚠ Pull had conflicts or warnings - continuing${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 4: Run HTTPS Setup Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

SETUP_SCRIPT="$REPO_PATH/deployment/scripts/setup_https_self_signed.sh"

if [ ! -f "$SETUP_SCRIPT" ]; then
    echo -e "${RED}✗ Setup script not found at $SETUP_SCRIPT${NC}"
    exit 1
fi

echo "Running setup script..."
bash "$SETUP_SCRIPT"
SETUP_EXIT=$?

if [ $SETUP_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Setup script completed successfully${NC}"
else
    echo -e "${YELLOW}⚠ Setup script exited with code $SETUP_EXIT${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Step 5: Final Verification${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo ""
echo "Service Status:"
echo "────────────────────────────────────────────────────────"
systemctl is-active nginx > /dev/null && echo -e "${GREEN}✓ Nginx${NC}" || echo -e "${RED}✗ Nginx${NC}"
systemctl is-active alumniconnect > /dev/null && echo -e "${GREEN}✓ AlumniConnect Backend${NC}" || echo -e "${RED}✗ AlumniConnect Backend${NC}"

echo ""
echo "Listening Ports:"
echo "────────────────────────────────────────────────────────"
ss -tulpn 2>/dev/null | grep -E '(LISTEN.*(80|443|5000))' | while read line; do
    if echo "$line" | grep -q ":80 "; then
        echo -e "${GREEN}✓ Port 80 (HTTP)${NC}"
    elif echo "$line" | grep -q ":443 "; then
        echo -e "${GREEN}✓ Port 443 (HTTPS)${NC}"
    elif echo "$line" | grep -q ":5000 "; then
        echo -e "${GREEN}✓ Port 5000 (Backend API)${NC}"
    fi
done || echo -e "${YELLOW}⚠ Could not determine port status${NC}"

echo ""
echo "Certificate Status:"
echo "────────────────────────────────────────────────────────"
if [ -f "/etc/nginx/certs/self-signed.crt" ]; then
    echo -e "${GREEN}✓ Self-signed certificate exists${NC}"
    openssl x509 -in /etc/nginx/certs/self-signed.crt -noout -dates 2>/dev/null | sed 's/^/  /'
else
    echo -e "${RED}✗ Certificate not found${NC}"
fi

echo ""
echo "Backend Health:"
echo "────────────────────────────────────────────────────────"
if curl -s -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health 2>/dev/null | grep -q success; then
    echo -e "${GREEN}✓ Backend API responding${NC}"
else
    echo -e "${YELLOW}⚠ Backend might not be ready yet${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Deployment Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════╝${NC}"

echo ""
echo "Access your application:"
echo "  HTTP:  http://csf.ru.ac.bd/iceaa/"
echo "  HTTPS: https://csf.ru.ac.bd/iceaa/"
echo ""
echo "Note: Browser may show certificate warning (self-signed)"
echo "      Click 'Proceed' or 'Accept' to continue"
echo ""
echo "To view logs:"
echo "  Nginx:   sudo tail -50 /var/log/nginx/error.log"
echo "  Backend: sudo journalctl -u alumniconnect -n 50"
echo ""

exit 0
