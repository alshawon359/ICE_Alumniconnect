#!/bin/bash
set -e

echo "=== Pulling latest changes from git ==="
cd /var/www/html/iceaa/ICE_AlumniConnect
git pull origin main

echo ""
echo "=== Removing old iceaa.conf from nginx sites-available ==="
rm -f /etc/nginx/sites-available/iceaa.conf

echo ""
echo "=== Removing old iceaa.conf symlink from nginx sites-enabled ==="
rm -f /etc/nginx/sites-enabled/iceaa.conf

echo ""
echo "=== Creating correct symlink to alumniconnect_iceaa.conf ==="
ln -sf /etc/nginx/sites-available/alumniconnect_iceaa.conf /etc/nginx/sites-enabled/alumniconnect_iceaa.conf

echo ""
echo "=== Testing nginx configuration ==="
nginx -t

echo ""
echo "=== Restarting nginx and alumniconnect services ==="
systemctl restart nginx
systemctl restart alumniconnect

echo ""
echo "=== Waiting 2 seconds and checking service status ==="
sleep 2
echo "Service Status:"
systemctl is-active nginx alumniconnect

echo ""
echo "=== Nginx sites-enabled configuration ==="
ls -la /etc/nginx/sites-enabled/

echo ""
echo "✅ All done! Website should now be fully functional with unified config."
