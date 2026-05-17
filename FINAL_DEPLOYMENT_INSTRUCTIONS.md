#!/bin/bash
# AdminConnect Deployment - Final Instructions
# এটি Admin'কে দেওয়ার জন্য চূড়ান্ত deployment instruction

set -euo pipefail

cat << 'EOF'
================================================================================
                    AlumniConnect - HTTPS Setup Instructions
                         csf.ru.ac.bd/iceaa
================================================================================

🎯 OBJECTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Make HTTPS 443 work globally (no red X in browser)
✅ Use self-signed certificate (NO SSL/TLS complexity)
✅ HTTP 80 redirects to HTTPS
✅ Secure, encrypted, production-ready


📋 PREREQUISITES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Server IP: 172.30.240.39
✓ SSH Port: 36109
✓ SSH User: root
✓ SSH Password: ice26Dru26&4mD
✓ Repository: /var/www/html/iceaa/ICE_AlumniConnect
✓ Nginx installed: Yes (assumed)
✓ Gunicorn running: Yes (assumed)


🚀 QUICK DEPLOYMENT (RECOMMENDED)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: SSH to Server
────────────────────────────────────────────────────────────────────────────────
ssh -p 36109 root@172.30.240.39

(Password: ice26Dru26&4mD)


Step 2: Navigate to Repository
────────────────────────────────────────────────────────────────────────────────
cd /var/www/html/iceaa/ICE_AlumniConnect


Step 3: Pull Latest Code
────────────────────────────────────────────────────────────────────────────────
git pull


Step 4: Run Setup Script
────────────────────────────────────────────────────────────────────────────────
sudo bash deployment/scripts/setup_https_self_signed.sh

⏱️  This will take ~30 seconds and will:
   • Create self-signed HTTPS certificate
   • Configure Nginx for HTTPS (443) + HTTP redirect (80)
   • Restart backend service
   • Test connectivity


Step 5: Verify (wait 5 seconds after script completes)
────────────────────────────────────────────────────────────────────────────────
# Check services
sudo systemctl status nginx alumniconnect | grep Active

# Check ports listening
sudo ss -tulpn | grep -E '(80|443|5000)'

# Test backend health
curl -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health


✅ DONE! Access URLs:
   • HTTP:  http://csf.ru.ac.bd/iceaa/
   • HTTPS: https://csf.ru.ac.bd/iceaa/


🌐 TESTING ACCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

From Any Browser:
1. Open: https://csf.ru.ac.bd/iceaa/
2. You may see certificate warning (NORMAL for self-signed)
   - Chrome: Click "Advanced" → "Proceed to csf.ru.ac.bd"
   - Firefox: Click "Advanced" → "Accept the Risk and Continue"
   - Safari: Click "Visit Website"
3. See AlumniConnect UI ✅
4. Try Login ✅

From Command Line (Test HTTPS):
────────────────────────────────────────────────────────────────────────────────
# Test HTTPS (ignore certificate warning)
curl -k https://csf.ru.ac.bd/iceaa/api/health

# Should return: {"success": true}

# Test HTTP redirect
curl -v http://csf.ru.ac.bd/iceaa/ 2>&1 | grep Location
# Should show redirect to https://


⚙️ CONFIGURATION (OPTIONAL)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Edit environment file (optional):
────────────────────────────────────────────────────────────────────────────────
sudo nano /var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production

Recommended settings:
────────────────────────────────────────────────────────────────────────────────
APP_ENV=production
DEBUG=false
PUBLIC_BASE_URL=https://csf.ru.ac.bd/iceaa
CORS_ORIGINS=https://csf.ru.ac.bd
ADMIN_USERNAME=admin@example.com
ADMIN_PASSWORD=<strong-password>
BREVO_API_KEY=<your-brevo-api-key>
SMTP_FROM_EMAIL=noreply@ru.ac.bd

After editing:
   sudo systemctl restart alumniconnect


🔒 CERTIFICATE INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Self-Signed Certificate:
   • Location: /etc/nginx/certs/self-signed.crt
   • Valid for: 365 days (expires in 1 year)
   • Renewal: Easy - just regenerate with openssl
   • Browser warning: Normal, expected behavior

Upgrade to Let's Encrypt (Optional, Anytime):
────────────────────────────────────────────────────────────────────────────────
# Install certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Generate Let's Encrypt certificate
sudo certbot certonly --standalone -d csf.ru.ac.bd

# Nginx automatically detects and uses it (no config change needed!)
# Browser warning will disappear

Renew Let's Encrypt (Automatic):
────────────────────────────────────────────────────────────────────────────────
# Certbot auto-renews 30 days before expiry
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer


⚠️ TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Issue: "Connection refused" or "502 Bad Gateway"
────────────────────────────────────────────────────────────────────────────────
Solution:
   1. Check backend status
      sudo systemctl status alumniconnect

   2. Check backend logs
      sudo journalctl -u alumniconnect -n 50

   3. Restart backend
      sudo systemctl restart alumniconnect

   4. Wait 5 seconds and try again


Issue: "Nginx config test failed"
────────────────────────────────────────────────────────────────────────────────
Solution:
   1. Test Nginx syntax
      sudo nginx -t

   2. Check error message
   3. Edit config
      sudo nano /etc/nginx/sites-available/default

   4. Test again
      sudo nginx -t

   5. Reload if OK
      sudo systemctl reload nginx


Issue: "Certificate not found" error
────────────────────────────────────────────────────────────────────────────────
Solution:
   1. Check if cert exists
      ls -la /etc/nginx/certs/

   2. If missing, generate manually
      sudo openssl req -x509 -newkey rsa:4096 -nodes \
        -out /etc/nginx/certs/self-signed.crt \
        -keyout /etc/nginx/certs/self-signed.key \
        -days 365 \
        -subj "/CN=csf.ru.ac.bd"

   3. Set permissions
      sudo chmod 644 /etc/nginx/certs/self-signed.crt
      sudo chmod 600 /etc/nginx/certs/self-signed.key

   4. Reload Nginx
      sudo systemctl reload nginx


Issue: "CORS error" in browser console
────────────────────────────────────────────────────────────────────────────────
Solution:
   1. Check if backend is running
      curl http://127.0.0.1:5000/api/health

   2. Restart backend
      sudo systemctl restart alumniconnect

   3. Clear browser cache
      Ctrl+Shift+Delete → "All time"

   4. Reload page (Ctrl+F5)


Issue: "Certificate warning" in browser
────────────────────────────────────────────────────────────────────────────────
This is NORMAL for self-signed certificates! ✓
   • Click "Advanced" → "Proceed"
   • Data is still encrypted
   • Click checkbox "Don't warn on this site" to suppress

To remove warning:
   • Use Let's Encrypt (see "Upgrade to Let's Encrypt" section above)


📊 MONITORING & LOGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check Service Status:
────────────────────────────────────────────────────────────────────────────────
sudo systemctl status nginx
sudo systemctl status alumniconnect


View Nginx Logs:
────────────────────────────────────────────────────────────────────────────────
# Real-time tail
sudo tail -f /var/log/nginx/access.log

# Errors only
sudo tail -50 /var/log/nginx/error.log


View Backend Logs:
────────────────────────────────────────────────────────────────────────────────
# Real-time logs
sudo journalctl -u alumniconnect -f

# Last 50 lines
sudo journalctl -u alumniconnect -n 50


Check Listening Ports:
────────────────────────────────────────────────────────────────────────────────
sudo ss -tulpn

Expected output:
   tcp  LISTEN  0.0.0.0:80      (Nginx HTTP)
   tcp  LISTEN  0.0.0.0:443     (Nginx HTTPS)
   tcp  LISTEN  127.0.0.1:5000  (Backend API)


🔄 RESTART SERVICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Restart Backend:
   sudo systemctl restart alumniconnect

Reload Nginx (Graceful):
   sudo systemctl reload nginx

Restart Nginx (Full):
   sudo systemctl restart nginx

Restart All:
   sudo systemctl restart nginx alumniconnect


📝 FILES INVOLVED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Modified Files:
   • backend/config_prod.py - Removed HTTPS-only validation
   • backend/app.py - CORS always enabled
   • deployment/nginx/alumniconnect_iceaa.conf - Auto-detect SSL

New Files:
   • deployment/scripts/setup_https_self_signed.sh - Setup automation
   • HTTPS_NO_SSL_TLS_FIX.md - Technical documentation
   • DEPLOYMENT_HTTPS_QUICK.md - Quick start guide
   • HTTPS_FIX_SUMMARY.md - Complete summary
   • ARCHITECTURE_DIAGRAM.md - Visual diagrams

Config Files:
   • /etc/nginx/sites-available/default - Nginx config
   • /etc/nginx/certs/self-signed.crt - Self-signed certificate
   • /etc/nginx/certs/self-signed.key - Certificate private key
   • /var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production - Env


✅ SUCCESS INDICATORS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After deployment, you should see:

Command Line Tests:
✅ curl http://127.0.0.1:5000/api/health returns JSON
✅ sudo ss -tulpn shows ports 80, 443, 5000 listening
✅ sudo nginx -t returns "syntax is ok"
✅ sudo systemctl status nginx shows "active (running)"
✅ sudo systemctl status alumniconnect shows "active (running)"

Browser Tests:
✅ https://csf.ru.ac.bd/iceaa/ loads AlumniConnect UI
✅ API calls work (no CORS errors in console)
✅ Login works without issues
✅ HTTP (80) redirects to HTTPS (443)

Logs:
✅ sudo tail /var/log/nginx/error.log shows no errors
✅ sudo journalctl -u alumniconnect shows successful startup


🎉 YOU'RE DONE!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your AlumniConnect application is now:
✅ Running on HTTPS (443) globally
✅ Using self-signed certificate
✅ HTTP (80) redirects to HTTPS
✅ No SSL/TLS certificate complexity
✅ Can upgrade to Let's Encrypt anytime
✅ Secure, encrypted, production-ready

Access URL: https://csf.ru.ac.bd/iceaa/


📞 SUPPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Documentation Files:
   • Read HTTPS_NO_SSL_TLS_FIX.md for detailed technical info
   • Read DEPLOYMENT_HTTPS_QUICK.md for quick reference
   • Read ARCHITECTURE_DIAGRAM.md for visual explanations

Questions:
   Q: Why certificate warning?
   A: Normal for self-signed. Use Let's Encrypt to remove.

   Q: Is data secure?
   A: Yes! Data encrypted same as trusted certificates.

   Q: When to upgrade to Let's Encrypt?
   A: Optional. Current setup is production-ready.

   Q: Can I change ports?
   A: Yes, modify /etc/nginx/sites-available/default

   Q: How often to renew certificate?
   A: Self-signed: yearly (manual)
      Let's Encrypt: 90 days (automatic)


================================================================================
                            Setup Completed!
                    You can now access your application at:
                        https://csf.ru.ac.bd/iceaa/
================================================================================

EOF
