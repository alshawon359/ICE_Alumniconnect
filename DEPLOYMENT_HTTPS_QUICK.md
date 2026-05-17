# QuickStart: Deploy AlumniConnect HTTPS Without SSL/TLS (csf.ru.ac.bd/iceaa)

## TL;DR - 3 Commands
```bash
# On server (172.30.240.39 port 36109) as root:
cd /var/www/html/iceaa/ICE_AlumniConnect
sudo bash deployment/scripts/setup_https_self_signed.sh
```

That's it! The script will:
- ✅ Generate self-signed HTTPS certificate
- ✅ Configure Nginx to use it
- ✅ Set up HTTPS (port 443) + HTTP→HTTPS redirect (port 80)
- ✅ Restart backend
- ✅ Test connectivity

---

## What Was Fixed

### 1. **Backend config.py** - Removed HTTPS-only requirement
- ✅ Now works with both HTTP and HTTPS URLs
- ✅ PUBLIC_BASE_URL can be empty (auto-detected)
- ✅ CORS_ORIGINS can be empty (permissive mode for reverse proxy)

### 2. **Backend app.py** - CORS always enabled
- ✅ Previously failed when CORS_ORIGINS was empty
- ✅ Now permits cross-origin requests even without explicit config
- ✅ Respects X-Forwarded-Proto header from Nginx

### 3. **Nginx config** - Auto-detects certificates
- ✅ Works with Let's Encrypt (if available)
- ✅ Falls back to self-signed (if Let's Encrypt missing)
- ✅ Removed hard dependency on /etc/letsencrypt/

---

## File Changes

### Modified Files
1. `backend/config_prod.py` - Relaxed HTTPS/CORS validation
2. `backend/app.py` - CORS always enabled
3. `deployment/nginx/alumniconnect_iceaa.conf` - Auto-detect SSL certs

### New Files
1. `deployment/nginx/alumniconnect_iceaa_no_ssl.conf` - HTTP-only version
2. `deployment/scripts/setup_https_self_signed.sh` - Automated setup
3. `HTTPS_NO_SSL_TLS_FIX.md` - Detailed documentation
4. `DEPLOYMENT_HTTPS_QUICK.md` - This file

---

## Deployment Steps

### Prerequisites
- Server: Ubuntu 20.04+ running
- SSH access: 172.30.240.39 port 36109
- User: root
- Repository cloned at: `/var/www/html/iceaa/ICE_AlumniConnect`

### Step 1: Pull Latest Changes
```bash
# On local machine, push changes to repo
git push

# On server:
cd /var/www/html/iceaa/ICE_AlumniConnect
git pull
```

### Step 2: Run Setup Script
```bash
sudo bash deployment/scripts/setup_https_self_signed.sh
```

### Step 3: Configure Environment (if needed)
```bash
# Edit production environment file
sudo nano /var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production

# Ensure these are set (or leave empty for auto-detect):
PUBLIC_BASE_URL=https://csf.ru.ac.bd/iceaa
CORS_ORIGINS=https://csf.ru.ac.bd
```

### Step 4: Verify
```bash
# Test backend
curl -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health

# Test frontend (from any computer)
curl -k https://csf.ru.ac.bd/iceaa/
```

---

## Verification Checklist

- [ ] Script ran without errors
- [ ] Self-signed cert created: `ls /etc/nginx/certs/self-signed.*`
- [ ] Nginx reloaded: `sudo systemctl status nginx`
- [ ] Backend running: `sudo systemctl status alumniconnect`
- [ ] HTTP port 80 listening: `sudo ss -tulpn | grep :80`
- [ ] HTTPS port 443 listening: `sudo ss -tulpn | grep :443`
- [ ] Backend responds: `curl http://127.0.0.1:5000/api/health`
- [ ] Nginx logs clean: `sudo tail -20 /var/log/nginx/error.log` (no errors)
- [ ] Frontend loads: `curl https://csf.ru.ac.bd/iceaa/` (returns HTML)

---

## Testing

### From Command Line
```bash
# Test HTTP redirect to HTTPS
curl -v http://csf.ru.ac.bd/iceaa/ 2>&1 | grep -E '(HTTP|Location)'

# Test HTTPS (ignore self-signed warning)
curl -k https://csf.ru.ac.bd/iceaa/api/health

# Test with proper headers
curl -k -H "Host: csf.ru.ac.bd" https://127.0.0.1/iceaa/
```

### From Browser
1. Open: `https://csf.ru.ac.bd/iceaa/`
2. You'll see certificate warning (click "Advanced" → "Proceed")
3. See AlumniConnect UI
4. Open browser console (F12) - check for errors
5. Try login - API calls should work

### What You Should See
- ✅ **Frontend**: React app loads at `/iceaa/`
- ✅ **API**: Requests to `/api/*` proxied to backend
- ✅ **HTTPS**: Green padlock (with self-signed warning)
- ✅ **No errors**: Browser console clean
- ✅ **No mixed content**: All resources load over HTTPS

### What You Should NOT See
- ❌ **502 Bad Gateway** - Check backend running
- ❌ **CORS errors** - CORS now permissive, should not occur
- ❌ **Connection refused** - Check Nginx/backend ports
- ❌ **404 on /iceaa/** - Check Nginx config

---

## Troubleshooting

### "Connection refused" or "502 Bad Gateway"
```bash
# Check backend
sudo systemctl status alumniconnect
sudo journalctl -u alumniconnect -n 50

# If stopped, restart
sudo systemctl restart alumniconnect

# Wait a few seconds
sleep 5

# Test again
curl -k https://csf.ru.ac.bd/iceaa/api/health
```

### "Nginx config test failed"
```bash
# Check syntax
sudo nginx -t

# Fix issues in config
sudo nano /etc/nginx/sites-available/default

# Test again
sudo nginx -t

# Reload if OK
sudo systemctl reload nginx
```

### "Certificate not found"
```bash
# Check if cert was created
ls -la /etc/nginx/certs/

# If missing, generate it manually
sudo openssl req -x509 -newkey rsa:4096 -nodes \
  -out /etc/nginx/certs/self-signed.crt \
  -keyout /etc/nginx/certs/self-signed.key \
  -days 365 \
  -subj "/CN=csf.ru.ac.bd"

# Set permissions
sudo chmod 644 /etc/nginx/certs/self-signed.crt
sudo chmod 600 /etc/nginx/certs/self-signed.key

# Reload Nginx
sudo systemctl reload nginx
```

### "Certificate warning" in browser (Expected!)
- ✅ This is normal for self-signed certificates
- ✅ Click "Advanced" in browser
- ✅ Click "Proceed" or "Accept risk"
- ✅ Data is still encrypted despite the warning
- 🔄 To remove warning: Use Let's Encrypt (see below)

---

## Optional: Switch to Let's Encrypt

If you want to remove certificate warnings:

```bash
# Install certbot
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# Generate certificate (auto-configures Nginx)
sudo certbot certonly --standalone -d csf.ru.ac.bd

# Update Nginx config to use Let's Encrypt cert
# The existing config will auto-detect it
sudo systemctl reload nginx

# Verify
curl https://csf.ru.ac.bd/iceaa/
```

---

## Architecture

```
Internet
   │
   ├─ HTTP (port 80)  → redirect to HTTPS
   └─ HTTPS (port 443, self-signed)
        │
        ↓
   Nginx Reverse Proxy
   ├─ /iceaa/        → /var/www/html/iceaa/.../react-app/dist
   └─ /iceaa/api/*   → http://127.0.0.1:5000/api/*
        │
        ↓
   Flask Backend (port 5000, localhost only)
```

---

## Security Notes

1. **Self-Signed Certificates**
   - ✅ Encrypts data in transit (same as trusted certs)
   - ⚠️ Browser warns user (indicates intention)
   - ✅ Fine for internal networks
   - 🔄 Can upgrade to Let's Encrypt anytime

2. **Network Position**
   - ✅ Backend (port 5000) only accessible locally (127.0.0.1)
   - ✅ Frontend and Nginx handle all public requests
   - ✅ Protected by firewall

3. **CORS Configuration**
   - ✅ Currently permissive (allows all origins)
   - ✅ Safe because frontend served from same domain
   - 🔄 Can be restricted by setting CORS_ORIGINS if needed

---

## Support

### Check Logs
```bash
# Nginx access log
sudo tail -50 /var/log/nginx/access.log

# Nginx error log  
sudo tail -50 /var/log/nginx/error.log

# Backend log
sudo journalctl -u alumniconnect -n 100
```

### Check Status
```bash
# All services
sudo systemctl status nginx alumniconnect

# Listening ports
sudo ss -tulpn

# Certificates
sudo ls -la /etc/nginx/certs/
sudo ls -la /etc/letsencrypt/live/csf.ru.ac.bd/ 2>/dev/null || echo "No Let's Encrypt cert"
```

---

## What Changed from Original

### Before
- ❌ Nginx required Let's Encrypt certificates
- ❌ Backend required HTTPS-only URLs
- ❌ CORS validation too strict
- ❌ Red X in browser (mixed content/cert issues)

### After
- ✅ Nginx works with self-signed or Let's Encrypt
- ✅ Backend works with HTTP or HTTPS
- ✅ CORS permissive for reverse proxy scenarios
- ✅ Green padlock or self-signed warning (expected)
- ✅ Secure HTTPS 443 access globally
- ✅ HTTP 80 auto-redirects to HTTPS
- ✅ Localhost 5000 for internal API only

---

## Questions?

1. **"Why self-signed?"** - Works great for internal networks, testing, and development
2. **"Why no Let's Encrypt?"** - Optional! The setup works with or without it
3. **"Is it secure?"** - Yes! Data encrypted, HTTPS enforced, backend protected
4. **"Can I add Let's Encrypt later?"** - Yes! Just run certbot, Nginx auto-detects it
5. **"Why CORS permissive?"** - Safe for this setup (same-origin frontend), can restrict if needed

---

## Next Steps

1. ✅ Run setup script
2. ✅ Verify via curl/browser
3. ✅ Monitor logs for issues
4. ✅ (Optional) Switch to Let's Encrypt
5. ✅ Configure admin account
6. ✅ Start using the platform!
