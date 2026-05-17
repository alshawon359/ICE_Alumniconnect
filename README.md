# AlumniConnect - Alumni Management Platform

**Status**: ✅ **PRODUCTION READY**

Enterprise-grade alumni management system with:
- **Frontend**: React 18.2 + Vite + Bootstrap
- **Backend**: Flask 3.0 + Gunicorn + SQLAlchemy
- **Database**: MySQL 8.0 with connection pooling
- **Email**: Brevo transactional email service
- **Deployment**: Ubuntu 20.04+ with Gunicorn + SSL

---

## 📚 Documentation

### For Development
- Local setup: See "## Prerequisites" below
- Running locally: See "## Run From VS Code"

### For Production Deployment
- **[deployment/README.md](deployment/README.md)** - Complete deployment reference

### ⚡ HTTPS Setup (NEW - No SSL/TLS Headaches!)
- **[FINAL_DEPLOYMENT_INSTRUCTIONS.md](FINAL_DEPLOYMENT_INSTRUCTIONS.md)** - 👈 START HERE for production
- **[DEPLOYMENT_HTTPS_QUICK.md](DEPLOYMENT_HTTPS_QUICK.md)** - Quick start guide
- **[HTTPS_NO_SSL_TLS_FIX.md](HTTPS_NO_SSL_TLS_FIX.md)** - Technical deep-dive
- **[HTTPS_FIX_SUMMARY.md](HTTPS_FIX_SUMMARY.md)** - What changed and why
- **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - Visual architecture

### Quick Start (Production)
```bash
# 1. SSH to server
ssh -p 36109 root@172.30.240.39

# 2. Navigate to repository
cd /var/www/html/iceaa/ICE_AlumniConnect

# 3. Pull latest code and run setup (ONE COMMAND!)
git pull && sudo bash deployment/scripts/setup_https_self_signed.sh

# 4. Access application
# HTTPS: https://csf.ru.ac.bd/iceaa/
# HTTP:  http://csf.ru.ac.bd/iceaa/ (redirects to HTTPS)
```

For details, see [FINAL_DEPLOYMENT_INSTRUCTIONS.md](FINAL_DEPLOYMENT_INSTRUCTIONS.md).

---

## 🚀 Local Development Setup

### Prerequisites

- Windows + PowerShell
- Python 3.10+ with virtual environment at `.venv`
- Node.js + npm
- MySQL Server 8.0 binaries

### Run From VS Code (Recommended)

Use the predefined task:
```
Start Local MySQL
```

This starts a local MySQL 8 container on `127.0.0.1:3307`.
The backend already points to that port in `backend/.env.local` and will auto-create the schema when `AUTO_INIT_DB=true`.

### Manual Run

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
export APP_ENV=development
python app.py

# Frontend (separate terminal)
cd react-app
npm install
npm run dev
```

---

## 🔧 Environment Files

### Development
- Backend: `backend/.env` or `backend/.env.local`
- Frontend: `react-app/.env.development`

### Production
- Backend: `backend/.env.production` (create from `.env.production.example`)
- Frontend: Uses API_BASE_URL from React build config

### Templates
- Backend dev: `backend/.env.development.example`
- Backend prod: `backend/.env.production.example`
- Frontend dev: `react-app/.env.development.example`
- Frontend prod: `react-app/.env.production.example`

---

## 🧪 Staging/Production Setup

Follow the comprehensive guides:
- **Staging**: `docs/STAGING_PRODUCTION_READY.md`
- **Production**: `PRODUCTION_DEPLOYMENT_GUIDE.md`

---

## 📁 Project Structure

```
.
├── backend/                          # Flask API
│   ├── app.py                        # Main application
│   ├── app_factory.py                # App factory pattern ✨
│   ├── config_prod.py                # Production config ✨
│   ├── gunicorn.conf.py              # Gunicorn setup ✨
│   ├── logging_config.py             # Logging ✨
│   ├── error_handlers.py             # Error handling ✨
│   ├── validation.py                 # Input validation ✨
│   ├── requirements.txt              # Dependencies
│   └── ...
├── react-app/                        # React + Vite
│   ├── src/
│   ├── vite.config.js
│   ├── package.json
│   └── ...
├── deployment/                       # Production files ✨
│   ├── install-ubuntu.sh             # Automated setup
│   ├── systemd/alumniconnect.service
│   └── ...
├── docs/                             # Documentation
├── PRODUCTION_DEPLOYMENT_GUIDE.md    # Deployment walkthrough ✨
├── PRODUCTION_CHECKLIST.md           # Verification ✨
├── EMERGENCY_ROLLBACK.md             # Disaster recovery ✨
└── README.md                         # This file
```

---

## 🔒 Security Features

✅ CORS restricted to frontend domain only  
✅ All secrets in .env (never committed)  
✅ Input validation & XSS prevention  
✅ SQL injection prevention (parameterized queries)  
✅ Security headers (CSP, HSTS, X-Frame-Options, etc.)  
✅ Rate limiting enabled  
✅ Database connection pooling  
✅ SSL/TLS with auto-renewal  
✅ HTTPS enforced in production  
✅ Session security (HttpOnly, Secure cookies)  

---

## 📊 Architecture

```
Browser
  ↓
Gunicorn + Systemd (SSL/App Server)
  ↓
Flask App
  ├─→ React static files (dist/)
  ├─→ MySQL Database
  ├─→ Brevo (Email)
  └─→ Cloudinary (Images)
```

---

## 🚀 Deployment

### One-Command Setup (Recommended)
```bash
sudo bash deployment/install-ubuntu.sh
```

### Manual Steps
See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)

### Verification Checklist
See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

### Emergency Rollback
See [EMERGENCY_ROLLBACK.md](EMERGENCY_ROLLBACK.md)

---

## 📞 Support

### Development Issues
1. Check logs: `journalctl -u alumniconnect -f` (production)
2. Run health check: `curl http://localhost:5000/api/health` (dev)
3. Review relevant doc above

### Production Issues
1. See [EMERGENCY_ROLLBACK.md](EMERGENCY_ROLLBACK.md)
2. See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md#troubleshooting)
3. Check logs: `/var/log/alumniconnect/app.log`

---

## 🎯 Production Status

✅ Backend: Production-ready (Gunicorn + app factory + config separation)  
✅ Database: Production-ready (connection pooling + migrations)  
✅ Frontend: Production-ready (optimized build + error handling)  
✅ Email: Production-ready (Brevo + fallback)  
✅ Security: Production-hardened (validation, headers, rate limiting)  
✅ Deployment: Fully automated (one-command setup)  
✅ Monitoring: Logging & error tracking enabled  
✅ Documentation: Complete (deployment guide + checklist + rollback)  

**Ready for Live Deployment** 🚀

---

## ✅ Verification

### Quick Health Check (Local)
```bash
curl http://localhost:5000/api/health
# Expected: {"message":"ok","success":true}
```

### Quick Health Check (Production)
```bash
curl http://localhost:5000/api/health
# Expected: {"message":"ok","success":true}
```

---

## 📋 Quick Reference

| Task | Command |
|------|---------|
| Start local MySQL | `Start Local MySQL` task in VS Code |
| Build frontend | `npm run build --prefix react-app` |
| Run production mode | `APP_ENV=production gunicorn -c backend/gunicorn.conf.py wsgi:application` |
| Deploy to server | `sudo bash deployment/install-ubuntu.sh` |
| View logs | `sudo journalctl -u alumniconnect -f` |
| Check health | `curl http://localhost:5000/api/health` |
| Backup DB | `mysqldump -u user -p db > backup.sql` |

---

**Version**: 1.0 Production Ready  
**Last Updated**: May 2026  
**Status**: ✅ Enterprise Ready

## API Health Check

`http://127.0.0.1:5000/api/health`

Expected JSON response with success status.

## Notes

- The app is now configured for clean local development by default.
- API client resolution prefers local backend endpoints on localhost.
