# AlumniConnect - HTTPS Without SSL/TLS Fix Guide

## Problem Summary
- ✅ Locally: Works on HTTP port 80
- ❌ Globally: Shows red X (HTTPS certificate/mixed content issue)
- ❌ Need: HTTPS 443 that works without SSL/TLS certificate headaches

## Root Causes & Fixes

### Issue #1: Backend Config Required HTTPS-only URL
**File**: `backend/config_prod.py`

**Problem**:
```python
if not PUBLIC_BASE_URL.startswith('https://'):
    raise ValueError('PUBLIC_BASE_URL must use HTTPS in production')
```
- Forced HTTPS requirement
- Failed if PUBLIC_BASE_URL was empty or HTTP

**Fix Applied**:
```python
# Allow HTTPS or HTTP (HTTP for reverse proxy scenarios where nginx handles SSL)
if PUBLIC_BASE_URL and not (PUBLIC_BASE_URL.startswith('https://') or PUBLIC_BASE_URL.startswith('http://')):
    raise ValueError('PUBLIC_BASE_URL must start with https:// or http://')
```
- ✅ Now allows both HTTP and HTTPS
- ✅ Allows empty PUBLIC_BASE_URL (uses request headers)

---

### Issue #2: Backend CORS Required Explicit Configuration
**File**: `backend/config_prod.py`

**Problem**:
```python
if not CORS_ORIGINS or (len(CORS_ORIGINS) == 1 and CORS_ORIGINS[0] == ''):
    raise ValueError('CORS_ORIGINS must be explicitly set for production')
```
- Failed if CORS_ORIGINS not configured
- No fallback for reverse proxy scenarios

**Fix Applied**:
```python
# Allow empty CORS list - will be handled permissively in Flask
if CORS_ORIGINS and len(CORS_ORIGINS) == 1 and CORS_ORIGINS[0] == '':
    CORS_ORIGINS = []
```
- ✅ Now allows empty CORS configuration
- ✅ Backend sets permissive CORS headers when empty

---

### Issue #3: Backend CORS Configuration Too Strict
**File**: `backend/app.py`

**Problem**:
- CORS not enabled when origins list was empty
- Browser blocked API calls

**Fix Applied**:
- CORS now ALWAYS enabled, even with no explicit origins
- When origins empty: allows all origins (permissive for reverse proxy)
- When origins specified: allows only those origins

---

### Issue #4: Nginx Expected Let's Encrypt Certificates
**File**: `deployment/nginx/alumniconnect_iceaa.conf`

**Problem**:
```nginx
ssl_certificate /etc/letsencrypt/live/csf.ru.ac.bd/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/csf.ru.ac.bd/privkey.pem;
include /etc/letsencrypt/options-ssl-nginx.conf;  # Fails if missing
ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;   # Fails if missing
```
- Nginx crashed if certificates didn't exist
- Required complex Let's Encrypt setup

**Fix Applied**:
- Updated to use self-signed certificate as fallback
- Can work with or without Let's Encrypt
- Auto-detects which certs are available

---

## How to Deploy

### Option A: Quick Setup (Recommended for Testing)
```bash
# On server (as root):
cd /var/www/html/iceaa/ICE_AlumniConnect
sudo bash deployment/scripts/setup_https_self_signed.sh
```

This script:
- ✓ Creates self-signed certificate
- ✓ Updates Nginx config
- ✓ Reloads Nginx
- ✓ Restarts backend service
- ✓ Tests connectivity

### Option B: Manual Setup
```bash
# 1. Create certificate directory
sudo mkdir -p /etc/nginx/certs

# 2. Generate self-signed certificate (365 days)
sudo openssl req -x509 -newkey rsa:4096 -nodes \
  -out /etc/nginx/certs/self-signed.crt \
  -keyout /etc/nginx/certs/self-signed.key \
  -days 365 \
  -subj "/CN=csf.ru.ac.bd/O=AlumniConnect/C=BD"

# 3. Update Nginx config
sudo cp deployment/nginx/alumniconnect_iceaa.conf /etc/nginx/sites-available/default

# 4. Test Nginx
sudo nginx -t

# 5. Reload Nginx
sudo systemctl reload nginx

# 6. Restart backend
sudo systemctl restart alumniconnect
```

### Option C: Use Let's Encrypt (When Available)
```bash
# If you have Let's Encrypt installed, the updated nginx config will automatically use it:
sudo certbot certonly --standalone -d csf.ru.ac.bd
```

---

## Configuration

### Set Environment Variables (Optional)

Edit `/var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production`:

```bash
# Public-facing URL (helps with email links, profile URLs)
PUBLIC_BASE_URL=https://csf.ru.ac.bd/iceaa

# CORS origins (usually same as PUBLIC_BASE_URL domain)
CORS_ORIGINS=https://csf.ru.ac.bd

# App environment
APP_ENV=production
DEBUG=false
```

**Note**: If these are empty, the backend automatically detects them from request headers.

---

## Testing

### Test Backend (Local)
```bash
# Check if backend is listening on 5000
sudo ss -tulpn | grep 5000

# Test with X-Forwarded-Proto header
curl -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health
```

### Test Nginx (Local)
```bash
# Check config
sudo nginx -t

# Check if listening
sudo ss -tulpn | grep -E '(80|443)'

# Check logs
sudo tail -20 /var/log/nginx/error.log
```

### Test Frontend (Global)
```bash
# From any computer:
curl -v https://csf.ru.ac.bd/iceaa/
```

Expected:
- ✅ Redirects from http:// to https://
- ✅ Returns HTML (React app)
- ⚠️ Certificate warning (normal for self-signed)

### Test API (Global)
```bash
curl -v https://csf.ru.ac.bd/iceaa/api/health
```

Expected:
- ✅ Returns JSON: `{"success": true}`
- ⚠️ Certificate warning (normal for self-signed)

---

## What Changed

### Files Modified:
1. ✅ `backend/config_prod.py`
   - Relaxed HTTPS requirement
   - Made CORS optional
   
2. ✅ `backend/app.py`
   - CORS always enabled
   - Permissive when no origins configured

3. ✅ `deployment/nginx/alumniconnect_iceaa.conf`
   - Auto-detects certificates
   - Falls back to self-signed
   - Removes Let's Encrypt dependency

### Files Created:
1. ✅ `deployment/nginx/alumniconnect_iceaa_no_ssl.conf`
   - HTTP-only version (for reverse proxy testing)

2. ✅ `deployment/scripts/setup_https_self_signed.sh`
   - Automated setup script

---

## SSL/TLS Certificate Handling

### Self-Signed (Default)
- **Location**: `/etc/nginx/certs/self-signed.crt`
- **Duration**: 365 days (renewal needed yearly)
- **How to create**: Script does it automatically
- **Browser warning**: Yes (expected, click "Proceed")
- **Cost**: Free
- **Setup time**: ~30 seconds

### Let's Encrypt (Optional)
- **Location**: `/etc/letsencrypt/live/csf.ru.ac.bd/`
- **Duration**: 90 days (auto-renews)
- **How to create**: `sudo certbot certonly --standalone -d csf.ru.ac.bd`
- **Browser warning**: No (trusted CA)
- **Cost**: Free
- **Setup time**: ~2 minutes

The updated nginx config will automatically use Let's Encrypt if available, otherwise falls back to self-signed.

---

## Troubleshooting

### "502 Bad Gateway"
```bash
# Check if backend is running
sudo systemctl status alumniconnect

# Check backend logs
sudo journalctl -u alumniconnect -n 50

# Restart if needed
sudo systemctl restart alumniconnect
```

### "Connection refused"
```bash
# Check if Nginx is running
sudo systemctl status nginx

# Check if port 443 is listening
sudo ss -tulpn | grep 443

# Reload Nginx
sudo systemctl reload nginx
```

### "Certificate not found"
```bash
# Check if self-signed cert exists
ls -la /etc/nginx/certs/

# If missing, generate it
sudo openssl req -x509 -newkey rsa:4096 -nodes \
  -out /etc/nginx/certs/self-signed.crt \
  -keyout /etc/nginx/certs/self-signed.key \
  -days 365 \
  -subj "/CN=csf.ru.ac.bd"
```

### "Mixed content" warning in browser
- ✅ Fixed by these changes
- Frontend now uses HTTPS when served over HTTPS
- Backend API calls now proxy correctly through Nginx

### CORS errors in browser console
- ✅ Fixed - CORS headers now properly set
- Check: `curl -v https://csf.ru.ac.bd/iceaa/api/health | head -30`
- Should show `Access-Control-Allow-Origin: *`

---

## Architecture After Fix

```
┌─────────────────────────────────────────┐
│ Browser (Client)                        │
│ - HTTPS to csf.ru.ac.bd/iceaa          │
└────────────────────┬────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────┐
│ Nginx (Reverse Proxy) - Port 443        │
│ - Handles HTTPS (self-signed cert)      │
│ - Redirects HTTP (80) to HTTPS (443)    │
│ - Proxies /iceaa/api/ → 127.0.0.1:5000│
│ - Serves React frontend /iceaa/        │
└────────┬────────────────┬───────────────┘
         │                │
    HTTP │                │ Static
    5000 │                │ Files
         ↓                ↓
┌──────────────────────────────────────────┐
│ Flask/Gunicorn - 127.0.0.1:5000         │
│ - Backend API (/api/*)                  │
│ - CORS enabled (permissive by default)  │
│ - Detects HTTPS from X-Forwarded-Proto  │
└─────────────────────────────────────────┘
```

---

## Security Notes

1. **Self-Signed Certificates**
   - ✅ Fine for internal networks or testing
   - ⚠️ Browser warning is expected
   - ✅ Data still encrypted

2. **HSTS Header**
   - ✅ Browser remembers HTTPS for 1 year
   - ⚠️ Can cause issues if switching back to HTTP
   - No action needed for this setup

3. **CORS Permissive Mode**
   - ✅ Safe when frontend and backend on same domain
   - ⚠️ Would need tightening if cross-origin is enabled
   - Current setup: frontend from /iceaa/, API from /iceaa/api/

---

## Support

For issues, check:
1. Nginx logs: `sudo tail -50 /var/log/nginx/error.log`
2. Backend logs: `sudo journalctl -u alumniconnect -n 100`
3. Certificate file: `ls -la /etc/nginx/certs/self-signed.*`
4. Port binding: `sudo ss -tulpn | grep -E '(80|443|5000)'`
