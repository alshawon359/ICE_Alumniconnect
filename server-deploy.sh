#!/bin/bash
# Server-side deployment script for AlumniConnect
# Run this on the server after dist and nginx config are uploaded

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     AlumniConnect Server-Side Deployment Script              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

DIST_PATH="/var/www/html/iceaa/ICE_AlumniConnect/react-app/dist"
NGINX_CONFIG="/etc/nginx/sites-available/alumniconnect_iceaa.conf"
NGINX_BACKUP="/etc/nginx/sites-available/alumniconnect_iceaa.conf.backup.$(date +%s)"

# ════════════════════════════════════════════════════════════════════

echo "[1/5] Verifying dist folder..."
if [ ! -d "$DIST_PATH" ]; then
    echo "✗ Error: dist folder not found at $DIST_PATH"
    exit 1
fi

if [ ! -f "$DIST_PATH/index.html" ]; then
    echo "✗ Error: index.html not found in dist"
    exit 1
fi

echo "✓ Dist folder verified"
ls -lh "$DIST_PATH" | head -5

# ════════════════════════════════════════════════════════════════════

echo ""
echo "[2/5] Backing up nginx config..."
if [ -f "$NGINX_CONFIG" ]; then
    sudo cp "$NGINX_CONFIG" "$NGINX_BACKUP"
    echo "✓ Backup created: $NGINX_BACKUP"
else
    echo "⚠ Warning: nginx config not found at $NGINX_CONFIG"
fi

# ════════════════════════════════════════════════════════════════════

echo ""
echo "[3/5] Testing nginx config..."
if sudo nginx -t 2>&1; then
    echo "✓ Nginx config syntax is valid"
else
    echo "✗ Error: Nginx config syntax invalid"
    echo "Restoring backup..."
    sudo cp "$NGINX_BACKUP" "$NGINX_CONFIG"
    exit 1
fi

# ════════════════════════════════════════════════════════════════════

echo ""
echo "[4/5] Reloading nginx..."
sudo systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx reloaded successfully"
else
    echo "✗ Error: Nginx failed to reload"
    exit 1
fi

# ════════════════════════════════════════════════════════════════════

echo ""
echo "[5/5] Restarting backend service..."
systemctl restart alumniconnect
sleep 2

if systemctl is-active --quiet alumniconnect; then
    echo "✓ Backend service restarted successfully"
else
    echo "✗ Error: Backend service failed to start"
    journalctl -u alumniconnect -n 20 --no-pager
    exit 1
fi

# ════════════════════════════════════════════════════════════════════

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              ✓ Deployment Complete!                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Service Status:"
echo "  Nginx:   $(systemctl is-active nginx)"
echo "  Backend: $(systemctl is-active alumniconnect)"
echo ""
echo "Test URLs:"
echo "  Home:     https://csf.ru.ac.bd/iceaa/"
echo "  Admin:    https://csf.ru.ac.bd/iceaa/admin-dashboard"
echo "  Student:  https://csf.ru.ac.bd/iceaa/student-login"
echo ""
echo "Recent [EMAIL] logs:"
journalctl -u alumniconnect -n 20 --no-pager | grep -i EMAIL | tail -5
echo ""
