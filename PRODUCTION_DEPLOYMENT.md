# Production Deployment Guide - AlumniConnect at csf.ru.ac.bd/iceaa

## Server Details
- **Domain:** https://csf.ru.ac.bd/iceaa
- **IP:** 172.30.240.39 (SSH Port: 36109)
- **App Path:** /var/www/html/iceaa/ICE_AlumniConnect
- **Backend Port:** 127.0.0.1:5000 (internal only)
- **SSL:** Handled by Nginx at port 443

---

## 1️⃣ Flask Configuration (app.py - PRODUCTION)

**Current setting is CORRECT. No changes needed.**

```python
if __name__ == '__main__':
    _run_migrations()
    # Production: Debug disabled, uses config.PORT (default 5000)
    app.run(host='0.0.0.0', debug=config.DEBUG, port=config.PORT, use_reloader=False)
```

**Confirmed in config.py:**
```python
PORT = _as_int(os.getenv('PORT'), 5000)  # Default: 5000
DEBUG = False  # Production setting
```

---

## 2️⃣ Gunicorn Production Configuration (CORRECT)

**File:** `backend/gunicorn.conf.py`

```python
# Production Gunicorn Settings
bind = '127.0.0.1:5000'          # Listen on localhost only (secure)
workers = 2                       # Adjust based on server CPU cores
threads = 2                       # Thread pool per worker
timeout = 120                     # Timeout for long-running requests
graceful_timeout = 30             # Graceful shutdown
keepalive = 5                     # Keep-alive timeout
accesslog = '-'                   # Log to stdout
errorlog = '-'                    # Log to stderr
loglevel = 'info'                 # Log level
```

**Production start command:**
```bash
cd /var/www/html/iceaa/ICE_AlumniConnect
gunicorn -c backend/gunicorn.conf.py backend.app:app
```

Or with systemd service (recommended):
```bash
systemctl start alumniconnect
systemctl status alumniconnect
```

---

## 3️⃣ Nginx Configuration (PRODUCTION - ALREADY SET)

**File:** `/etc/nginx/sites-available/default`

Your configuration is **CORRECT and COMPLETE**. The reverse proxy block already exists:

```nginx
# Proxy API requests to Gunicorn backend (127.0.0.1:5000)
location /iceaa/api/ {
    proxy_pass http://127.0.0.1:5000/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;
    proxy_connect_timeout 5s;
    proxy_read_timeout 120s;
    proxy_send_timeout 120s;
}

# Main SPA location - serves React app
location /iceaa/ {
    alias /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/;
    try_files $uri $uri/ /index.html;
    expires -1;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

---

## 4️⃣ **Server-Side Commands (SSH to 172.30.240.39)**

### **A. Verify Nginx Configuration (SAFE - READ ONLY)**
```bash
# Check syntax
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### **B. Reload Nginx (Apply Changes)**
```bash
# Graceful reload (keeps existing connections)
sudo systemctl reload nginx

# OR
sudo service nginx reload

# Verify it's running
sudo systemctl status nginx
```

### **C. Start/Restart Gunicorn (Flask Backend)**
```bash
# Using systemd (if available)
sudo systemctl start alumniconnect
sudo systemctl status alumniconnect

# OR manually (development/testing)
cd /var/www/html/iceaa/ICE_AlumniConnect
gunicorn -c backend/gunicorn.conf.py backend.app:app &
```

### **D. Health Checks**

**Check if Flask is listening on port 5000:**
```bash
# Should show: LISTEN 127.0.0.1:5000
sudo ss -tulpn | grep 5000
# OR
sudo netstat -tulpn | grep 5000
```

**Test API endpoint:**
```bash
# From server
curl -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health

# From local (test HTTPS path)
curl -H "X-Forwarded-Proto: https" https://csf.ru.ac.bd/iceaa/api/health
```

**Check Nginx logs:**
```bash
# Real-time tail
sudo tail -f /var/log/nginx/access.log | grep iceaa
sudo tail -f /var/log/nginx/error.log

# Recent errors
sudo grep error /var/log/nginx/error.log | tail -20
```

---

## 5️⃣ **Database Setup (If Needed)**

```bash
# Start MySQL
docker compose -f deployment/docker/docker-compose.local.yml up -d db

# Verify MySQL is running
docker ps | grep mysql

# Stop MySQL
docker compose -f deployment/docker/docker-compose.local.yml down
```

---

## 🔒 **Security Checklist**

- ✅ Flask runs on **127.0.0.1:5000** (localhost only, not exposed)
- ✅ Nginx listens on **0.0.0.0:443** (global HTTPS)
- ✅ HTTP traffic redirected to HTTPS
- ✅ SSL certificate: Let's Encrypt at `/etc/letsencrypt/live/csf.ru.ac.bd/`
- ✅ Existing projects untouched (only `/iceaa/` location modified)
- ✅ Debug mode disabled in production

---

## 📌 **Common Issues & Solutions**

### Issue: "502 Bad Gateway" error
**Solution:**
```bash
# Check if Gunicorn is running on 5000
sudo ss -tulpn | grep 5000

# If not, start it
cd /var/www/html/iceaa/ICE_AlumniConnect
gunicorn -c backend/gunicorn.conf.py backend.app:app

# Check logs
tail -f /var/log/nginx/error.log
```

### Issue: Nginx won't reload
**Solution:**
```bash
# Test config first
sudo nginx -t

# If error, fix it then:
sudo systemctl reload nginx
```

### Issue: CORS errors in browser console
**Solution:** Already handled in Flask with CORS headers. Check:
```python
# backend/app.py has proper CORS configuration
CORS(app, resources={r"/api/*": {"origins": _cors_origins}}, ...)
```

---

## ✅ **Deployment Verification Steps**

**On Server (SSH 172.30.240.39):**

1. Check Nginx config:
   ```bash
   sudo nginx -t
   ```

2. Check Gunicorn running:
   ```bash
   sudo ss -tulpn | grep 5000
   ```

3. Test API locally:
   ```bash
   curl http://127.0.0.1:5000/api/health
   ```

4. Test from browser:
   - Visit: https://csf.ru.ac.bd/iceaa
   - Should show React SPA with HTTPS lock
   - API calls should work

5. Check logs:
   ```bash
   sudo tail -20 /var/log/nginx/error.log
   sudo tail -20 /var/log/nginx/access.log | grep iceaa
   ```

---

## 🚀 **Ready to Deploy**

Your configuration is **production-ready**. All components are correctly configured:
- ✅ Flask: port 5000, no SSL, debug off
- ✅ Gunicorn: localhost-only, proper config
- ✅ Nginx: reverse proxy with SSL, proper headers
- ✅ React SPA: served at /iceaa/

**Next step:** Run verification commands on server.
