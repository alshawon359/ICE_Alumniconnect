# Server Deployment Instructions
## AlumniConnect HTTPS Fix - Deploy to Production

### Quick Summary
✅ All code fixes committed and pushed to GitHub  
✅ Hardcoded API keys removed  
✅ Nginx auto-certificate support enabled  
✅ Ready for server deployment

---

## How to Deploy to 172.30.240.39:36109

### Option 1: SSH + Manual Commands (Recommended)

```bash
# 1. SSH to server
ssh -p 36109 root@172.30.240.39

# 2. Navigate to app directory
cd /var/www/html/iceaa/ICE_AlumniConnect

# 3. Pull latest code from GitHub
git pull origin main

# 4. Run setup script (creates certs, configures HTTPS)
sudo bash deployment/scripts/setup_https_self_signed.sh

# 5. Test the deployment
curl -k https://csf.ru.ac.bd/iceaa/
```

**Password:** ice26Dru26&4mD

---

### Option 2: Use Automated Deployment Script

```bash
# 1. SSH to server
ssh -p 36109 root@172.30.240.39

# 2. Run the unified deployment script
bash /var/www/html/iceaa/ICE_AlumniConnect/deployment/scripts/server_deploy.sh
```

This script will:
- Pull latest code from GitHub
- Run HTTPS setup
- Verify all services are running
- Check certificate status
- Test backend health

---

## What Gets Deployed

### Backend Changes (backend/app.py)
- ✅ Removed hardcoded Brevo API key
- ✅ Uses environment variables instead
- ✅ CORS always enabled (no blocking)
- ✅ HTTP/HTTPS auto-detection with X-Forwarded-Proto

### Backend Changes (backend/config_prod.py)
- ✅ Relaxed PUBLIC_BASE_URL validation (accepts HTTP or HTTPS)
- ✅ Made CORS_ORIGINS optional
- ✅ More permissive defaults for reverse proxy scenarios

### Nginx Config (deployment/nginx/alumniconnect_iceaa.conf)
- ✅ Auto-detect SSL certificates (Let's Encrypt → self-signed fallback)
- ✅ HTTP 80 → HTTPS 443 redirect
- ✅ No hard dependency on specific cert paths
- ✅ X-Forwarded-Proto headers for protocol detection

### Automated Setup (deployment/scripts/setup_https_self_signed.sh)
- ✅ Creates self-signed certificate if missing
- ✅ Configures Nginx with proper headers
- ✅ Reloads services
- ✅ Tests connectivity

---

## After Deployment

### Expected Results
```
✓ HTTP  (port 80)  → auto-redirects to HTTPS 443
✓ HTTPS (port 443) → loads with self-signed cert
✓ Frontend        → accessible at https://csf.ru.ac.bd/iceaa/
✓ Backend API     → accessible at https://csf.ru.ac.bd/iceaa/api/*
✓ CORS            → enabled globally
```

### Browser Warning
When accessing HTTPS:
- Browser shows "Not Secure" / "Certificate Warning"
- This is normal with self-signed certs
- Click "Proceed" / "Advanced" → "Accept" to continue

### Verify Deployment

```bash
# Test HTTP → HTTPS redirect
curl -I http://csf.ru.ac.bd/iceaa/
# Should show: HTTP/1.1 301 Moved Permanently
# Location: https://csf.ru.ac.bd/iceaa/

# Test HTTPS endpoint
curl -k https://csf.ru.ac.bd/iceaa/api/health
# Should return JSON with status: "success" or "ok"

# Check Nginx status
systemctl status nginx

# Check backend status
systemctl status alumniconnect

# View Nginx errors (if any)
tail -50 /var/log/nginx/error.log

# View backend logs (if any)
journalctl -u alumniconnect -n 50
```

---

## Troubleshooting

### "Certificate rejected" or "Connection refused"

```bash
# Check if self-signed cert was created
ls -la /etc/nginx/certs/self-signed.crt

# Check Nginx config validity
nginx -t

# Reload Nginx manually
systemctl reload nginx
```

### "API returning CORS errors"

```bash
# Check backend is running
systemctl status alumniconnect

# Restart backend
systemctl restart alumniconnect

# Check backend logs
journalctl -u alumniconnect -n 100
```

### "Can't connect to 172.30.240.39:36109"

```bash
# Check SSH is running
systemctl status ssh

# Check firewall
ufw status
```

---

## GitHub Repository
- **URL:** https://github.com/alshawon359/ICE_Alumniconnect.git
- **Branch:** main
- **Latest Commit:** 92fed5b - "Fix: Enable HTTPS 443 with self-signed certs (no SSL/TLS complexity)"
- **What Changed:** 43 files, 5316 insertions, 112 deletions

---

## Support

If issues occur during deployment:

1. Check service logs:
   ```bash
   systemctl status nginx
   systemctl status alumniconnect
   ```

2. View error logs:
   ```bash
   tail -100 /var/log/nginx/error.log
   journalctl -u alumniconnect -n 100
   ```

3. Test backend directly:
   ```bash
   curl -v http://127.0.0.1:5000/api/health
   ```

4. Verify DNS resolution:
   ```bash
   nslookup csf.ru.ac.bd
   ```

---

## Timeline

| Step | Time | Command |
|------|------|---------|
| SSH Connect | <1min | `ssh -p 36109 root@172.30.240.39` |
| Git Pull | 1-2min | `git pull origin main` |
| Setup HTTPS | ~30sec | `sudo bash deployment/scripts/setup_https_self_signed.sh` |
| Verification | <1min | Manual tests |
| **Total** | **~3-4 min** | Complete deployment |

---

## What NOT to Do

❌ Don't edit hardcoded values in app.py (use .env.production instead)  
❌ Don't modify Nginx config (auto-detection handles it)  
❌ Don't delete or replace certificate manually  
❌ Don't force HTTP connections (redirect handles it)  
❌ Don't restart services without reason (may interrupt requests)  

---

## Success Criteria

When deployment is complete, verify:
- [ ] HTTPS works at https://csf.ru.ac.bd/iceaa/
- [ ] HTTP redirects to HTTPS at http://csf.ru.ac.bd/iceaa/
- [ ] API endpoints respond at https://csf.ru.ac.bd/iceaa/api/*
- [ ] No CORS errors in browser console
- [ ] Self-signed certificate present at /etc/nginx/certs/self-signed.crt
- [ ] Git log shows latest commit (92fed5b)

---

**Status:** ✅ Ready for Production Deployment
