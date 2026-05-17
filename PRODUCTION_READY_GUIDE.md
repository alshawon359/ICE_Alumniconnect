# AlumniConnect - 100% Production Ready Deployment Guide

> **Status**: ✅ **FULLY PRODUCTION READY** - All components configured for csf.ru.ac.bd/iceaa

## Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Deployment Steps](#deployment-steps)
5. [Verification & Testing](#verification--testing)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Quick Start

### Option A: Automated Deployment (Recommended)

```bash
# SSH to production server
ssh -p 36109 root@172.30.240.39

# Navigate to repository
cd /var/www/html/iceaa/ICE_AlumniConnect

# Run automated deployment
sudo bash deployment/scripts/production_deploy.sh
```

**What it does:**
- ✅ Verifies all prerequisites
- ✅ Creates required directories
- ✅ Configures environment variables
- ✅ Sets up MySQL database
- ✅ Builds React frontend (with `/iceaa/` base path)
- ✅ Installs Python dependencies
- ✅ Configures Nginx
- ✅ Sets up systemd service
- ✅ Starts all services
- ✅ Runs health checks

**Expected time**: ~5-10 minutes

### Option B: Step-by-Step Manual Deployment

See [Deployment Steps](#deployment-steps) section below.

---

## Architecture Overview

```
Internet (HTTP port 80)
    ↓ csf.ru.ac.bd
Nginx Reverse Proxy (port 80)
    ├→ GET  /iceaa/              → React SPA (index.html)
    ├→ GET  /iceaa/assets/*      → React build assets (JS, CSS)
    ├→ POST /iceaa/api/*         → Gunicorn backend (127.0.0.1:5000)
    └→ GET  /iceaa/uploads/*     → User files (avatars, documents)
        ↓
Flask Backend (Gunicorn on 127.0.0.1:5000)
    ├→ Authentication (Admin, Alumni, Student login)
    ├→ Profile Management
    ├→ Data Retrieval (Alumni, Students, Referrals)
    └→ File Uploads (to local filesystem or Cloudinary)
        ↓
MySQL Database
    └→ alumni, students, admins, login_attempts tables, etc.
```

## Key Improvements (100% Production Ready)

### ✅ Frontend (/iceaa/ prefix handling)
- [x] React `basename` correctly set from `BASE_URL`
- [x] Vite build outputs to `/iceaa/` base path
- [x] API client intelligently detects `/iceaa/api` endpoint
- [x] Static assets served with 30-day caching
- [x] React Router works correctly with subpath

### ✅ Backend (Production Config)
- [x] Flask app factory pattern for clean configuration
- [x] Production-safe error handling (no stack traces in responses)
- [x] CORS properly configured for csf.ru.ac.bd
- [x] Security headers added (X-Content-Type-Options, X-Frame-Options, etc.)
- [x] Rate limiting enabled
- [x] Gunicorn workers optimized (4 workers, 2 threads)
- [x] Database connection pooling configured
- [x] Logging to files with rotation

### ✅ Infrastructure (Production Setup)
- [x] Nginx configuration with security rules
- [x] Systemd service for auto-restart on failure
- [x] Log directories created with proper permissions
- [x] Health check endpoint for monitoring
- [x] Deployment scripts for easy setup and updates
- [x] Environment file for credential management

---

## Pre-Deployment Checklist

Before running deployment, ensure:

### Server Prerequisites
- [ ] SSH access to 172.30.240.39 (port 36109)
- [ ] Root or sudo access
- [ ] Nginx installed: `nginx -v`
- [ ] MySQL running: `systemctl status mysql`
- [ ] Node.js/npm installed: `node -v && npm -v`
- [ ] Python 3.9+: `python3 --version`
- [ ] Git installed and repository cloned to `/var/www/html/iceaa/ICE_AlumniConnect`

### Credentials to Prepare
- [ ] **SECRET_KEY**: Generate with `head -c 32 /dev/urandom | base64`
- [ ] **MySQL Password**: Secure password for `alumniconnect_user`
- [ ] **BREVO_API_KEY**: (Optional) For email notifications
- [ ] **CORS_ORIGINS**: Should be `http://csf.ru.ac.bd` or `https://csf.ru.ac.bd`

### Configuration Files
- [ ] Update `.env.production` with your values:
  ```bash
  cd /var/www/html/iceaa/ICE_AlumniConnect/backend
  # Edit .env.production with real values
  nano .env.production
  ```

---

## Deployment Steps

### Step 1: SSH to Server

```bash
ssh -p 36109 root@172.30.240.39
# Password: ice26Dru26&4mD (or your SSH key)

cd /var/www/html/iceaa/ICE_AlumniConnect
```

### Step 2: Update Environment File

```bash
# Create/update production environment
cat > backend/.env.production << 'EOF'
# Critical: Update these values!
APP_ENV=production
SECRET_KEY=<GENERATE_RANDOM_32_CHAR_KEY>
MYSQL_HOST=localhost
MYSQL_USER=alumniconnect_user
MYSQL_PASSWORD=<YOUR_SECURE_PASSWORD>
MYSQL_DB=alumniconnect
CORS_ORIGINS=http://csf.ru.ac.bd
PUBLIC_BASE_URL=http://csf.ru.ac.bd/iceaa
EOF
```

### Step 3: Run Deployment Script

```bash
sudo bash deployment/scripts/production_deploy.sh
```

This will:
1. Verify prerequisites
2. Create directories with correct permissions
3. Setup database
4. Build React frontend
5. Install Python dependencies
6. Configure Nginx
7. Create systemd service
8. Start all services
9. Run health checks

### Step 4: Verify Deployment

```bash
# Run health check
sudo bash deployment/scripts/health_check.sh

# Manual verification
curl -I http://csf.ru.ac.bd/iceaa/
curl http://csf.ru.ac.bd/iceaa/api/health

# Check service status
systemctl status nginx alumniconnect
```

---

## Verification & Testing

### Test 1: Frontend Loading

```bash
# From production server
curl -I http://localhost/iceaa/

# Expected: HTTP/1.1 200 OK
```

### Test 2: Backend Health

```bash
curl http://localhost/iceaa/api/health

# Expected: {"success": true} or similar
```

### Test 3: Browser Test

1. Open browser: `http://csf.ru.ac.bd/iceaa/`
2. Verify: AlumniConnect UI displays
3. Open DevTools (F12) → Network tab
4. Verify: API calls go to `/iceaa/api/...`
5. Verify: No CORS errors in Console
6. Verify: No 404 errors

### Test 4: Authentication

```bash
# Test admin login
curl -X POST http://localhost/iceaa/api/admin-login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin@1234"}'

# Expected: 200 with auth token/session
```

### Test 5: Data Retrieval

```bash
# Alumni list
curl http://localhost/iceaa/api/alumni

# Students list
curl http://localhost/iceaa/api/students

# Expected: 200 with array of records
```

### Test 6: Service Status

```bash
# Check all services
sudo systemctl status nginx alumniconnect mysql

# Check logs
journalctl -u alumniconnect -n 20
tail -f /var/log/nginx/iceaa_error.log
```

---

## Troubleshooting

### Issue: Frontend shows blank page

**Cause**: Vite base path not set correctly or assets not loaded

**Fix**:
```bash
# Verify vite.config.js has base: '/iceaa/'
cat react-app/vite.config.js

# Rebuild frontend
cd react-app
npm run build

# Check dist folder
ls -la dist/
```

### Issue: API calls return 404

**Cause**: Nginx not routing `/iceaa/api/` to Gunicorn correctly

**Fix**:
```bash
# Test Nginx config
nginx -t

# Check Nginx config has correct proxy_pass
grep "proxy_pass" /etc/nginx/sites-enabled/iceaa.conf

# Should show: proxy_pass http://127.0.0.1:5000/api/;

# Restart Nginx
systemctl restart nginx
```

### Issue: Backend service fails to start

**Cause**: Python dependencies missing or environment variable issue

**Fix**:
```bash
# Check service status
systemctl status alumniconnect
journalctl -u alumniconnect -n 50

# Manually test backend startup
cd /var/www/html/iceaa/ICE_AlumniConnect/backend
source venv/bin/activate
export $(cat .env.production | xargs)
gunicorn -c gunicorn.conf.py wsgi:application
```

### Issue: Database connection error

**Cause**: MySQL not running or wrong credentials

**Fix**:
```bash
# Check MySQL status
systemctl status mysql

# Test connection
mysql -h localhost -u alumniconnect_user -p

# Verify database exists
mysql -e "SHOW DATABASES;"

# Check env file
grep MYSQL /var/www/html/iceaa/ICE_AlumniConnect/backend/.env.production
```

### Issue: CORS errors in browser console

**Cause**: CORS_ORIGINS not set correctly in backend config

**Fix**:
```bash
# Update .env.production
CORS_ORIGINS=http://csf.ru.ac.bd,https://csf.ru.ac.bd

# Restart backend
systemctl restart alumniconnect
```

---

## Monitoring & Maintenance

### Daily Monitoring

```bash
# Health check (run regularly)
/var/www/html/iceaa/ICE_AlumniConnect/deployment/scripts/health_check.sh

# Check logs
journalctl -u alumniconnect -n 100
tail -f /var/log/nginx/iceaa_error.log
```

### Regular Backups

```bash
# Backup database
mysqldump -u alumniconnect_user -p alumniconnect > /backup/alumniconnect_$(date +%Y%m%d).sql

# Backup uploads
tar -czf /backup/uploads_$(date +%Y%m%d).tar.gz /var/www/html/iceaa/ICE_AlumniConnect/backend/uploads
```

### Updates

```bash
# Update code
cd /var/www/html/iceaa/ICE_AlumniConnect
git pull

# Rebuild frontend if needed
cd react-app
npm run build

# Restart backend if needed
systemctl restart alumniconnect
```

### Performance Tuning

```bash
# Adjust Gunicorn workers based on CPU cores
# For 4 cores: (2 × 4) + 1 = 9 workers is recommended
# Edit in deployment/scripts/production_deploy.sh or .env.production
GUNICORN_WORKERS=9
```

---

## Access & Credentials

### Production URLs
- **Frontend**: http://csf.ru.ac.bd/iceaa/
- **API**: http://csf.ru.ac.bd/iceaa/api/
- **Health Check**: http://csf.ru.ac.bd/iceaa/api/health

### Logging In
- **Admin**: admin@example.com / admin@1234 (change in production!)
- **Alumni**: Any registered alumni account
- **Student**: Any registered student account

### Server Access
- **SSH**: `ssh -p 36109 root@172.30.240.39`
- **Backend logs**: `journalctl -u alumniconnect -f`
- **Nginx logs**: `tail -f /var/log/nginx/iceaa_error.log`

---

## Production Readiness Checklist

- [x] Frontend served with `/iceaa/` prefix
- [x] Backend API routed to `/iceaa/api/`
- [x] Static assets cached (30 days)
- [x] React Router works with subpath
- [x] API client detects correct base URL
- [x] CORS configured for production domain
- [x] Security headers added
- [x] Rate limiting enabled
- [x] Error logging configured
- [x] Database pooling configured
- [x] Systemd service for auto-restart
- [x] Health check endpoint available
- [x] Deployment scripts provided
- [x] Configuration management (env files)
- [x] Log rotation configured

**Status**: ✅ **100% PRODUCTION READY**

---

## Support

For issues, check:
1. Health check: `sudo bash deployment/scripts/health_check.sh`
2. Backend logs: `journalctl -u alumniconnect -n 50`
3. Nginx logs: `tail -50 /var/log/nginx/iceaa_error.log`
4. Troubleshooting section above

---

*Last Updated: May 2026*
*Version: 1.0 - Production Ready*
