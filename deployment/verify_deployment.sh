#!/bin/bash
# AlumniConnect Production Deployment - Server Commands
# Server: 172.30.240.39 | App: /var/www/html/iceaa/ICE_AlumniConnect

echo "═══════════════════════════════════════════════════════════"
echo "  AlumniConnect Production Deployment Commands"
echo "  Domain: https://csf.ru.ac.bd/iceaa"
echo "═══════════════════════════════════════════════════════════"

# 1. NGINX VERIFICATION & RELOAD
echo ""
echo "1️⃣ NGINX Configuration Check:"
echo "   ➜ sudo nginx -t"
sudo nginx -t

echo ""
echo "2️⃣ NGINX Status:"
echo "   ➜ sudo systemctl status nginx"
sudo systemctl status nginx --no-pager || sudo service nginx status

echo ""
echo "3️⃣ NGINX Reload (Apply Changes):"
echo "   ➜ sudo systemctl reload nginx"
sudo systemctl reload nginx

# 2. GUNICORN CHECK
echo ""
echo "4️⃣ Check if Gunicorn is running on port 5000:"
echo "   ➜ sudo ss -tulpn | grep 5000"
sudo ss -tulpn | grep 5000 || echo "   ⚠️  Gunicorn NOT running - see step 6"

# 3. PORT AVAILABILITY
echo ""
echo "5️⃣ Check port 5000 is available:"
echo "   ➜ sudo lsof -i :5000"
sudo lsof -i :5000 2>/dev/null || echo "   ✓ Port 5000 is free"

# 4. START GUNICORN
echo ""
echo "6️⃣ START Gunicorn (if not running):"
echo "   ➜ cd /var/www/html/iceaa/ICE_AlumniConnect"
echo "   ➜ gunicorn -c backend/gunicorn.conf.py backend.app:app"
echo ""
echo "   OR use systemd service:"
echo "   ➜ sudo systemctl start alumniconnect"
echo "   ➜ sudo systemctl status alumniconnect"

# 5. TEST API LOCALLY
echo ""
echo "7️⃣ Test API endpoint (localhost):"
echo "   ➜ curl http://127.0.0.1:5000/api/health"
curl -s http://127.0.0.1:5000/api/health 2>/dev/null || echo "   ⚠️  Could not reach API - is Gunicorn running?"

# 6. NGINX ERROR LOGS
echo ""
echo "8️⃣ Recent NGINX Errors:"
echo "   ➜ sudo tail -10 /var/log/nginx/error.log"
sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "   (No errors in log)"

# 7. NGINX ACCESS LOGS (ICEAA only)
echo ""
echo "9️⃣ Recent ICEAA Requests:"
echo "   ➜ sudo tail -10 /var/log/nginx/access.log | grep iceaa"
sudo tail -20 /var/log/nginx/access.log 2>/dev/null | grep iceaa || echo "   (No requests yet)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ Deployment Check Complete"
echo "═══════════════════════════════════════════════════════════"
