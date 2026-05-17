╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║          🚀 ALUMNICONNECT DEPLOYMENT - COMPLETE PACKAGE READY 🚀               ║
║                                                                                ║
║                    Fix /iceaa/ Path Prefix Issue                               ║
║                    Email: Hardcoded Brevo Credentials                          ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝


📋 WHAT'S BEEN DONE:
════════════════════════════════════════════════════════════════════════════════

✅ EMAIL DELIVERY (Already Live):
   • Hardcoded Brevo API credentials in backend/app.py
   • API Key, sender email, sender name all hardcoded
   • Brevo 201 responses confirmed in logs
   • Status: 🟢 DEPLOYED & TESTED

✅ PATH PREFIX FIX (Ready to Deploy):
   • Fixed nginx config: try_files instead of if-rewrite
   • Verified vite.config.js has /iceaa/ base for production
   • Created automated deployment scripts
   • Status: 🟡 READY TO DEPLOY


🎯 NEXT STEPS (2 OPTIONS):
════════════════════════════════════════════════════════════════════════════════

┌─ OPTION 1: FULLY AUTOMATED (Recommended) ────────────────────────────────────┐
│                                                                               │
│ Run this ONE command from PowerShell in f:\Temp\ac1\AC:                      │
│                                                                               │
│    .\deploy.ps1                                                              │
│                                                                               │
│ This will automatically:                                                     │
│   1. Build React app with /iceaa/ base path                                  │
│   2. Deploy dist/ to server                                                  │
│   3. Deploy nginx config to server                                           │
│   4. Reload nginx + restart backend                                          │
│   5. Verify both services are running                                        │
│                                                                               │
│ ⏱️  Takes ~3-5 minutes                                                        │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌─ OPTION 2: MANUAL DEPLOYMENT (If script fails) ──────────────────────────────┐
│                                                                               │
│ Follow the step-by-step guide in:                                            │
│   📄 DEPLOYMENT_GUIDE.md                                                     │
│                                                                               │
│ Or read:                                                                     │
│   📄 DEPLOYMENT_STEPS.txt                                                    │
│                                                                               │
│ ⏱️  Takes ~5-10 minutes                                                       │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘


📦 DEPLOYMENT PACKAGE CONTENTS:
════════════════════════════════════════════════════════════════════════════════

Scripts Created:
  ├─ deploy.ps1                  (PowerShell - fully automated)
  ├─ server-deploy.sh            (Bash - run on server)
  
Documentation:
  ├─ DEPLOYMENT_GUIDE.md         (Complete guide with troubleshooting)
  ├─ DEPLOYMENT_STEPS.txt        (Quick reference steps)
  
Configuration:
  ├─ deployment/nginx/alumniconnect_iceaa.conf    (✅ Fixed)
  ├─ react-app/vite.config.js                     (✅ Correct)
  ├─ backend/app.py                               (✅ Hardcoded email)

Application:
  ├─ react-app/                  (Ready to build)
  └─ backend/                    (Ready to deploy)


🔍 PRE-DEPLOYMENT CHECKLIST:
════════════════════════════════════════════════════════════════════════════════

☐ Verify you're in f:\Temp\ac1\AC directory
☐ Verify internet connection (npm download + ssh)
☐ Verify SSH access: ping 172.30.240.39
☐ Verify Node.js installed: node --version
☐ Verify npm installed: npm --version


⚡ QUICK START (Recommended):
════════════════════════════════════════════════════════════════════════════════

1. Open PowerShell in f:\Temp\ac1\AC

2. Run the deployment script:
   .\deploy.ps1

3. Wait for completion (should show ✓ Deployment Complete!)

4. Test in browser:
   https://csf.ru.ac.bd/iceaa/admin-dashboard
   (Should show /iceaa/admin-dashboard in URL, NOT just /admin-dashboard)


📊 EXPECTED RESULTS AFTER DEPLOYMENT:
════════════════════════════════════════════════════════════════════════════════

✅ URLs Correct:
   ✓ https://csf.ru.ac.bd/iceaa/
   ✓ https://csf.ru.ac.bd/iceaa/admin-dashboard
   ✓ https://csf.ru.ac.bd/iceaa/student-login
   ✓ https://csf.ru.ac.bd/iceaa/alumni-dashboard

✅ No 404 Errors:
   Assets load correctly with /iceaa/ prefix

✅ Email Still Works:
   Brevo emails continue to send successfully

✅ Nginx Status:
   sudo systemctl status nginx → active (running)

✅ Backend Status:
   systemctl status alumniconnect → active (running)


⚠️  POTENTIAL ISSUES & FIXES:
════════════════════════════════════════════════════════════════════════════════

Issue 1: Script requires npm - Node.js not installed
├─ Download: https://nodejs.org/ (LTS version)
└─ Verify: node --version && npm --version

Issue 2: SSH connection timeout
├─ Check: ping 172.30.240.39
├─ Verify SSH port: 36109
└─ Try: ssh -p 36109 root@172.30.240.39

Issue 3: URLs still show without /iceaa/ after deployment
├─ Solution 1: Hard refresh browser (Ctrl+Shift+Delete)
├─ Solution 2: Clear browser cache
├─ Solution 3: Open in Incognito/Private window
└─ Solution 4: Check DevTools (F12) Network tab for 404s

Issue 4: Getting 404 on /iceaa/ paths after deployment
├─ SSH to server
├─ Check: ls -la /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/
├─ Verify: test -f /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/index.html
└─ Run: sudo nginx -t (check for syntax errors)

Issue 5: Nginx reload fails
├─ SSH to server
├─ Run: sudo nginx -t (check error message)
├─ Fix the error
└─ Retry: sudo systemctl reload nginx


📞 TROUBLESHOOTING COMMANDS:
════════════════════════════════════════════════════════════════════════════════

SSH to server:
  ssh -p 36109 root@172.30.240.39

Check nginx syntax:
  sudo nginx -t

Reload nginx:
  sudo systemctl reload nginx

Restart backend:
  systemctl restart alumniconnect

Check backend status:
  systemctl status alumniconnect

View backend logs:
  journalctl -u alumniconnect -n 50 --no-pager

Check email logs:
  journalctl -u alumniconnect -n 50 --no-pager | grep EMAIL

View nginx error log:
  sudo tail -50 /var/log/nginx/error.log

Verify dist exists:
  ls -la /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/


🎯 SUCCESS CRITERIA:
════════════════════════════════════════════════════════════════════════════════

After running deploy.ps1, you should see:

  ✓ [1/5] Building React app ..................... DONE
  ✓ [2/5] Deploying React dist .................. DONE
  ✓ [3/5] Deploying nginx config ................ DONE
  ✓ [4/5] Applying configuration on server ...... DONE
  ✓ [5/5] Verifying deployment .................. DONE

  ✓ Deployment Complete!

  Services:
    nginx: active
    backend: active

  Test URLs working:
    https://csf.ru.ac.bd/iceaa/admin-dashboard ✅


════════════════════════════════════════════════════════════════════════════════

🚀 Ready to proceed? Run in PowerShell:

   .\deploy.ps1

════════════════════════════════════════════════════════════════════════════════
