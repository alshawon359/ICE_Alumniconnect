#!/bin/bash
# Remote Deployment Script for AlumniConnect
# This script can be run remotely to deploy all changes to the production server
# Usage: bash remote_deploy.sh

set -euo pipefail

# Configuration
REMOTE_USER="root"
REMOTE_HOST="172.30.240.39"
REMOTE_PORT="36109"
REPO_PATH="/var/www/html/iceaa/ICE_AlumniConnect"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================="
echo "AlumniConnect Remote Deployment"
echo "=========================================${NC}"

# Step 1: Validate SSH connection
echo -e "${YELLOW}[1/4]${NC} Testing SSH connection..."
if ssh -p "$REMOTE_PORT" -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "echo OK" &>/dev/null; then
    echo -e "${GREEN}✓ SSH connection OK${NC}"
else
    echo -e "${RED}✗ SSH connection failed${NC}"
    echo "  Host: $REMOTE_HOST:$REMOTE_PORT"
    echo "  User: $REMOTE_USER"
    exit 1
fi

# Step 2: Pull latest code
echo -e "${YELLOW}[2/4]${NC} Pulling latest code..."
ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "cd $REPO_PATH && git pull" || {
    echo -e "${YELLOW}⚠ Git pull failed - code might already be latest${NC}"
}

# Step 3: Run setup script
echo -e "${YELLOW}[3/4]${NC} Running setup script..."
ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "bash $REPO_PATH/deployment/scripts/setup_https_self_signed.sh"

# Step 4: Verify deployment
echo -e "${YELLOW}[4/4]${NC} Verifying deployment..."
echo "Checking services..."
ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" <<'VERIFY'
echo "Nginx status:"
systemctl status nginx --no-pager | grep -E '(Active|Listening)'

echo ""
echo "Backend status:"
systemctl status alumniconnect --no-pager | grep -E '(Active|PID)'

echo ""
echo "Listening ports:"
ss -tulpn | grep -E '(80|443|5000)'

echo ""
echo "Certificate files:"
ls -lah /etc/nginx/certs/ 2>/dev/null || echo "  (No certs yet)"

echo ""
echo "Testing backend health..."
curl -s -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health | grep -q success && echo "✓ Backend OK" || echo "⚠ Backend not responding"
VERIFY

echo ""
echo -e "${GREEN}========================================="
echo "Deployment Complete!"
echo "=========================================${NC}"
echo ""
echo "Access URLs:"
echo "  http://csf.ru.ac.bd/iceaa/"
echo "  https://csf.ru.ac.bd/iceaa/"
echo ""
echo "Next steps:"
echo "  1. Visit https://csf.ru.ac.bd/iceaa/ in browser"
echo "  2. Accept self-signed certificate warning (if needed)"
echo "  3. Log in with admin credentials"
echo "  4. Test all features"
echo ""
