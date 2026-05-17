╔═══════════════════════════════════════════════════════════════════════════════╗
║                   ALUMNICONNECT DEPLOYMENT GUIDE                               ║
║                     Fix /iceaa/ Path Prefix Issue                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

SERVER INFO:
├─ IP: 172.30.240.39
├─ SSH Port: 36109
├─ SSH User: root
├─ SSH Pass: ice26Dru26&4mD
├─ URL: https://csf.ru.ac.bd/iceaa/
└─ Backend: http://127.0.0.1:5000

════════════════════════════════════════════════════════════════════════════════

ISSUE FIXED:
  ❌ OLD: https://csf.ru.ac.bd/admin-dashboard (loses /iceaa/)
  ✅ NEW: https://csf.ru.ac.bd/iceaa/admin-dashboard (keeps /iceaa/)

ROOT CAUSE:
  1. Nginx config used 'if' rewrite which doesn't work well with 'alias'
  2. React dist wasn't built with /iceaa/ base path

FIXES APPLIED:
  1. ✅ Nginx config: Changed to try_files (proper SPA routing)
  2. ✅ Vite config: Already has /iceaa/ base for production
  3. ✅ React build: npm run build will bake in /iceaa/ paths

════════════════════════════════════════════════════════════════════════════════

AUTOMATED DEPLOYMENT (Recommended):
════════════════════════════════════

From f:\Temp\ac1\AC in PowerShell, run:

  .\deploy.ps1 -SshUser root -SshHost 172.30.240.39 -SshPort 36109

This will:
  1. npm run build in react-app/
  2. SCP dist/ to server
  3. SCP nginx config to server
  4. SSH and reload nginx + restart backend
  5. Verify deployment

════════════════════════════════════════════════════════════════════════════════

MANUAL DEPLOYMENT (Step-by-step):
════════════════════════════════════

STEP 1: Build React app locally
────────────────────────────────
In PowerShell from f:\Temp\ac1\AC:

  cd react-app
  npm install
  npm run build

Expected: Creates react-app\dist\ folder with:
  - index.html
  - assets/ folder with JS/CSS files
  - All paths include /iceaa/ prefix


STEP 2: Deploy React dist to server
────────────────────────────────────
From f:\Temp\ac1\AC:

  scp -P 36109 -r react-app\dist root@172.30.240.39:/var/www/html/iceaa/ICE_AlumniConnect/

Expected: Copies dist folder to server


STEP 3: Deploy nginx config to server
──────────────────────────────────────
From f:\Temp\ac1\AC:

  scp -P 36109 deployment\nginx\alumniconnect_iceaa.conf root@172.30.240.39:/etc/nginx/sites-available/

Expected: Updates nginx config file


STEP 4: Apply changes on server
────────────────────────────────
From PowerShell:

  ssh -p 36109 root@172.30.240.39

Then copy-paste these commands on the server:

  # Backup current config
  sudo cp /etc/nginx/sites-available/alumniconnect_iceaa.conf /etc/nginx/sites-available/alumniconnect_iceaa.conf.backup.$(date +%s)

  # Test nginx config
  sudo nginx -t

  # If test passes, reload nginx
  sudo systemctl reload nginx

  # Restart backend
  systemctl restart alumniconnect

  # Verify both services are running
  echo "Nginx:" && systemctl is-active nginx
  echo "Backend:" && systemctl is-active alumniconnect

Expected: Both should show "active"


STEP 5: Test the deployment
────────────────────────────
Open browser and test:

  Home page:
    https://csf.ru.ac.bd/iceaa/

  Admin Dashboard:
    https://csf.ru.ac.bd/iceaa/admin-dashboard
    (should NOT be: /admin-dashboard)

  Student Login:
    https://csf.ru.ac.bd/iceaa/student-login
    (should NOT be: /student-login)

  Alumni Dashboard:
    https://csf.ru.ac.bd/iceaa/alumni-dashboard
    (should NOT be: /alumni-dashboard)

════════════════════════════════════════════════════════════════════════════════

TROUBLESHOOTING:
════════════════════════════════════════════════════════════════════════════════

ISSUE 1: Browser still shows /admin-dashboard without /iceaa/
──────────────────────────────────────────────────────────────
Solution:
  1. Hard refresh browser: Ctrl+Shift+Delete (or Cmd+Shift+Delete on Mac)
  2. Select "Clear browsing data"
  3. Check "Cookies and other site data" + "Cached images and files"
  4. Refresh page

Or:
  1. Open DevTools (F12)
  2. Settings → Network → Check "Disable cache"
  3. Refresh page (Ctrl+R)


ISSUE 2: Getting 404 errors on /iceaa/ paths
──────────────────────────────────────────────
Check 1: Verify nginx config syntax
  ssh -p 36109 root@172.30.240.39
  sudo nginx -t

Check 2: Verify dist folder exists
  ls -la /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/
  # Should show index.html and assets/ folder

Check 3: Verify index.html exists
  test -f /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/index.html && echo "✓ Found" || echo "✗ Missing"

Check 4: View nginx error logs
  sudo tail -50 /var/log/nginx/error.log
  sudo tail -50 /var/log/nginx/access.log


ISSUE 3: Nginx reload fails
────────────────────────────
On server:
  # Check syntax
  sudo nginx -t
  # Shows error message - fix it
  
  # If SSL cert missing
  sudo certbot renew
  
  # Then reload
  sudo systemctl reload nginx


ISSUE 4: Backend not responding
────────────────────────────────
On server:
  # Restart backend
  systemctl restart alumniconnect
  sleep 2
  
  # Check status
  systemctl status alumniconnect
  
  # View logs
  journalctl -u alumniconnect -n 50 --no-pager


ISSUE 5: Assets (CSS/JS) not loading
─────────────────────────────────────
Check that dist/ folder has:
  react-app/dist/
  ├─ index.html
  └─ assets/
      ├─ index-XXXXX.js
      ├─ index-XXXXX.css
      └─ [other asset files]

In browser DevTools (F12):
  - Check Network tab for failed requests
  - Look for 404 errors on asset files
  - Verify paths start with /iceaa/assets/


════════════════════════════════════════════════════════════════════════════════

KEY FILES MODIFIED:
════════════════════════════════════════════════════════════════════════════════

1. deployment/nginx/alumniconnect_iceaa.conf
   BEFORE:
     if (!-e $request_filename) {
         rewrite ^/iceaa/(.*)$ /index.html last;  # ❌ Doesn't work with alias
     }
   
   AFTER:
     try_files $uri $uri/ /index.html;  # ✅ Works correctly with alias


2. react-app/vite.config.js
   ✅ Already correct:
     base: mode === 'production' ? '/iceaa/' : '/'


3. react-app/package.json
   ✅ Scripts:
     "build": "vite build"  # Builds with /iceaa/ base in production


════════════════════════════════════════════════════════════════════════════════

FILES FOR DEPLOYMENT:
════════════════════════════════════════════════════════════════════════════════

Located in f:\Temp\ac1\AC\:

  1. deploy.ps1 (PowerShell script - automates everything)
  2. DEPLOYMENT_STEPS.txt (manual steps)
  3. react-app/dist/ (built React app)
  4. deployment/nginx/alumniconnect_iceaa.conf (nginx config)


════════════════════════════════════════════════════════════════════════════════

FINAL CHECKLIST:
════════════════════════════════════════════════════════════════════════════════

  ☐ Run: .\deploy.ps1 (or follow manual steps)
  ☐ Verify nginx -t shows no errors
  ☐ Test: https://csf.ru.ac.bd/iceaa/ (should work)
  ☐ Test: https://csf.ru.ac.bd/iceaa/admin-dashboard (should work)
  ☐ Test: Hard refresh browser (Ctrl+Shift+Delete)
  ☐ Check browser DevTools (F12) for any 404 errors
  ☐ Verify backend logs: journalctl -u alumniconnect -n 50
  ☐ Verify nginx logs: sudo tail -50 /var/log/nginx/error.log


════════════════════════════════════════════════════════════════════════════════
✅ DEPLOYMENT READY! Run: .\deploy.ps1
════════════════════════════════════════════════════════════════════════════════
