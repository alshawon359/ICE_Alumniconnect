# AlumniConnect Production Deployment Checklist

## ✅ Pre-Deployment (Local Development)

- [x] Flask app.py configured with:
  - Host: `0.0.0.0`
  - Port: `5000` (from config.py)
  - Debug: `False` (production)
  - No SSL in Flask (Nginx handles SSL)
  - Use reloader: `False`

- [x] Gunicorn configuration checked:
  - Bind: `127.0.0.1:5000` (localhost only)
  - Workers: `2`
  - Timeout: `120s`
  - Graceful: `30s`

- [x] Nginx configuration verified:
  - SSL certificate: `/etc/letsencrypt/live/csf.ru.ac.bd/`
  - HTTP (port 80) redirects to HTTPS (port 443)
  - Location `/iceaa/api/` proxies to `127.0.0.1:5000`
  - Location `/iceaa/` serves React SPA from `/var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/`
  - Security headers: STS, CSP, X-Frame-Options set
  - Gzip compression enabled

---

## 🚀 Production Deployment Steps (On Server 172.30.240.39)

### Step 1: SSH Access
```bash
ssh -p 36109 root@172.30.240.39
```

### Step 2: Verify Nginx Configuration
```bash
# Test syntax (doesn't apply changes)
sudo nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 3: Reload Nginx
```bash
# Graceful reload (keeps existing connections alive)
sudo systemctl reload nginx

# Verify
sudo systemctl status nginx
```

### Step 4: Start/Restart Gunicorn Backend
```bash
# Navigate to app directory
cd /var/www/html/iceaa/ICE_AlumniConnect

# Start Gunicorn with production config
gunicorn -c backend/gunicorn.conf.py backend.app:app &

# OR if systemd service exists:
sudo systemctl start alumniconnect
sudo systemctl status alumniconnect

# Verify it's listening
sudo ss -tulpn | grep 5000
```

### Step 5: Verify Deployment
```bash
# 1. Test API locally (from server)
curl http://127.0.0.1:5000/api/health

# 2. Test public HTTPS endpoint (from anywhere)
curl -H "X-Forwarded-Proto: https" https://csf.ru.ac.bd/iceaa/api/health

# 3. Check logs for errors
sudo tail -20 /var/log/nginx/error.log
sudo tail -20 /var/log/nginx/access.log | grep iceaa
```

### Step 6: Monitor Logs (In Separate Terminal)
```bash
# Real-time access log
sudo tail -f /var/log/nginx/access.log | grep iceaa

# Real-time error log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔍 Health Check Commands

### Is Nginx running?
```bash
sudo systemctl status nginx
# OR
ps aux | grep nginx
```

### Is Gunicorn running?
```bash
sudo ss -tulpn | grep 5000
# OR
ps aux | grep gunicorn
```

### Is MySQL running? (if needed)
```bash
docker ps | grep mysql
# OR
sudo systemctl status mysql
```

### Test connectivity:
```bash
# Local test (from server)
curl http://127.0.0.1:5000/api/health

# Remote test (from anywhere)
curl https://csf.ru.ac.bd/iceaa/api/health

# With verbose output for debugging
curl -vv https://csf.ru.ac.bd/iceaa/api/health
```

---

## ⚠️ Troubleshooting

### "502 Bad Gateway" or "Connection Refused"

**Problem:** Nginx can't reach Gunicorn on port 5000

```bash
# Check if Gunicorn is running
sudo ss -tulpn | grep 5000

# If not, start it
cd /var/www/html/iceaa/ICE_AlumniConnect
gunicorn -c backend/gunicorn.conf.py backend.app:app

# Check for errors
tail -20 /var/log/nginx/error.log
```

### "Connection Timeout"

**Problem:** Firewall or network issue

```bash
# Check if port 5000 is open locally
sudo ss -tulpn | grep 5000

# Check if Nginx is forwarding to correct address
sudo nginx -T | grep -A5 "location /iceaa/api"
```

### "SSL Certificate Error"

**Problem:** Certificate not found or expired

```bash
# Check certificate
ls -la /etc/letsencrypt/live/csf.ru.ac.bd/

# Renew if needed
sudo certbot renew --dry-run
sudo certbot renew
```

### "Port already in use"

**Problem:** Another process using port 5000

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill it (if safe)
sudo kill -9 <PID>

# Then start Gunicorn
gunicorn -c backend/gunicorn.conf.py backend.app:app
```

---

## 📊 Configuration Summary

| Component | Configuration | Status |
|-----------|---------------|--------|
| **Flask** | host=0.0.0.0, port=5000, debug=False | ✅ Ready |
| **Gunicorn** | bind=127.0.0.1:5000, workers=2 | ✅ Ready |
| **Nginx** | port 443 (HTTPS), SSL enabled | ✅ Ready |
| **Proxy** | /iceaa/api/ → 127.0.0.1:5000 | ✅ Ready |
| **SPA** | /iceaa/ → React dist | ✅ Ready |
| **Domain** | csf.ru.ac.bd/iceaa | ✅ Ready |
| **Certificate** | Let's Encrypt (auto-renew) | ✅ Ready |

---

## 🎯 Final Verification Checklist

- [ ] Nginx syntax test passes: `sudo nginx -t`
- [ ] Nginx status is active: `sudo systemctl status nginx`
- [ ] Gunicorn is listening on 5000: `sudo ss -tulpn | grep 5000`
- [ ] API responds locally: `curl http://127.0.0.1:5000/api/health`
- [ ] HTTPS is accessible: `curl https://csf.ru.ac.bd/iceaa/`
- [ ] No errors in nginx logs: `sudo tail /var/log/nginx/error.log`
- [ ] React app loads at https://csf.ru.ac.bd/iceaa
- [ ] API calls work from browser
- [ ] HTTPS lock icon shows in browser
- [ ] Existing projects still working (check other routes)

---

## 📞 Support

**If issues occur:**

1. Check all 3 services are running:
   - `sudo systemctl status nginx`
   - `sudo ss -tulpn | grep 5000` (Gunicorn)
   - `docker ps | grep mysql` (MySQL, if needed)

2. Review logs in order:
   - Nginx: `sudo tail -20 /var/log/nginx/error.log`
   - Nginx access: `sudo tail -20 /var/log/nginx/access.log | grep iceaa`
   - Application: Check Flask stdout/stderr

3. Verify network connectivity:
   - `sudo ss -tulpn` - see all listening ports
   - `sudo netstat -an | grep LISTEN` - alternative view

4. Test each layer:
   - **Flask layer:** `curl http://127.0.0.1:5000/api/health`
   - **Nginx layer:** `curl -H "Host: csf.ru.ac.bd" http://127.0.0.1/iceaa/api/health`
   - **Public access:** `curl https://csf.ru.ac.bd/iceaa/api/health`

---

**Last Updated:** May 17, 2026
**Status:** ✅ Production Ready
