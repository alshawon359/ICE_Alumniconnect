# AlumniConnect - Deployment Package

This folder contains everything needed to deploy AlumniConnect to production.

## 📋 Files in This Package

### Installation & Setup
- **`install-ubuntu.sh`** - Automated one-command deployment for Ubuntu 20.04+
  - Installs all system dependencies
  - Sets up Python virtual environment
  - Configures MySQL database
  - Configures Gunicorn and Systemd
  - Enables SSL with Let's Encrypt
  
  **Usage**: `sudo bash install-ubuntu.sh`

### Environment Configuration
- **`.env.production.example`** - Production environment template
  - Copy to `backend/.env.production`
  - Fill in database credentials, API keys, etc.
  - Never commit this file

### Systemd Service
- **`systemd/alumniconnect.service`** - System service configuration
  - Enables application auto-restart
  - Manages Gunicorn workers
  - Handles logging and error recovery
  - Reverse proxy: Frontend static + Backend API
  - SSL/TLS configuration
  - Security headers
  - Gzip compression

---

## 🚀 Quick Deployment (3 commands)

```bash
# 1. Clone repository to server
git clone <your-repo-url> /var/www/alumniconnect
cd /var/www/alumniconnect

# 2. Run automated setup (as root)
sudo bash deployment/install-ubuntu.sh

# 3. Edit production config and fill in credentials
nano backend/.env.production
```

That's it! The script handles:
- ✅ Ubuntu packages (Python, MySQL, SSL)
- ✅ Python dependencies
- ✅ Database initialization
- ✅ SSL certificate (Let's Encrypt)
- ✅ Systemd service
- ✅ Gunicorn configuration

---

## 📝 Manual Deployment (Step by Step)

If you prefer manual control:

1. **System Setup**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.10 python3.10-venv mysql-server
   ```

2. **Application Setup**
   ```bash
   cd /var/www/alumniconnect
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

3. **Database**
   ```bash
   sudo mysql < backend/schema.sql
   ```

4. **Configuration**
   ```bash
   cp .env.production.example backend/.env.production
   nano backend/.env.production  # Fill in credentials
   ```

5. **Frontend Build**
   ```bash
   cd react-app
   npm install
   npm run build
   ```

6. **SSL Certificate**
   ```bash
   sudo certbot certonly --standalone -d your-domain.com
   ```

7. **Start Application**
   ```bash
   sudo cp deployment/systemd/alumniconnect.service /etc/systemd/system/
   sudo systemctl enable alumniconnect
   sudo systemctl start alumniconnect
   ```

---

## ✅ Verification Checklist

After deployment, verify everything works:

- [ ] Health check: `curl http://localhost:5000/api/health`
- [ ] Frontend loads: `curl http://localhost/`
- [ ] Application running: `sudo systemctl status alumniconnect`
- [ ] Database responsive: `mysql ... -e "SELECT 1;"`
- [ ] Logs clean: `sudo journalctl -u alumniconnect -n 20`
- [ ] Email works: Send test email
- [ ] No errors: `sudo grep -i error /var/log/alumniconnect/error.log`

---

## 🔧 Environment Variables

**Required variables in `.env.production`:**

```
APP_ENV=production
SECRET_KEY=<32-character-random-string>
MYSQL_USER=ac_user
MYSQL_PASSWORD=<strong-password>
MYSQL_HOST=localhost
MYSQL_DB=alumniconnect
BREVO_API_KEY=<from-brevo-dashboard>
SMTP_FROM_EMAIL=noreply@your-domain.com
CORS_ORIGINS=https://your-domain.com
```

**To generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser (Client)                                   │
│  https://your-domain.com                            │
└────────────────────┬────────────────────────────────┘
                     │ HTTPS (Port 443)
                     ▼
┌─────────────────────────────────────────────────────┐
│  Gunicorn WSGI Server (Systemd Service)             │
│  - Static files (React dist/)                       │
│  - Serve /api/* → Flask backend                     │
│  - SSL/TLS termination (via Certbot)                │
│  - Gzip compression                                 │
│  - Security headers                                 │
│  Listen: 127.0.0.1:5000 (Systemd managed)          │
│  Workers: 4, Threads: 2 per worker                 │
└────────────────────┬────────────────────────────────┘
                     │ HTTP :5000 (internal)
                     ▼
          ┌─────────────────────────────┐
          │ Flask Application           │
          │ - Routes & API endpoints    │
          │ - Authentication            │
          │ - Business logic            │
          └────────────┬────────────────┘
                       │
                       ▼
          ┌─────────────────────────────┐
          │ MySQL Database              │
          │ - User data                 │
          │ - Events                    │
          │ - Alumni info               │
          │ Port: 3306 (local only)     │
          └─────────────────────────────┘
```

---

## 🛠️ Common Commands

**View Logs**
```bash
sudo journalctl -u alumniconnect -f           # Real-time logs
sudo tail -f /var/log/alumniconnect/app.log  # Application log
```

**Restart Application**
```bash
sudo systemctl restart alumniconnect
```

**Update Code**
```bash
cd /var/www/alumniconnect
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
npm run build --prefix react-app
sudo systemctl restart alumniconnect
```

**Backup Database**
```bash
mysqldump -u alumni_user -p alumniconnect > backup-$(date +%Y%m%d).sql
```

---

## 📞 Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u alumniconnect -n 50

# Check environment file
grep -v '^#' backend/.env.production | grep -v '^$'

# Test Flask directly
cd backend
source ../venv/bin/activate
python -c "from app import app; print('OK')"
```

### Database connection error
```bash
# Test connection
mysql -u alumni_user -p -e "SELECT 1;"

# Check credentials
grep MYSQL backend/.env.production
```

### Gunicorn connection error
```bash
# Check Gunicorn running
ps aux | grep gunicorn

# Check port listening
sudo netstat -tlnp | grep 5000

# Restart Gunicorn
sudo systemctl restart alumniconnect
```

---

## 📚 Documentation

- **`PRODUCTION_DEPLOYMENT_GUIDE.md`** - Full deployment walkthrough
- **`PRODUCTION_CHECKLIST.md`** - Pre-deployment verification
- **`EMERGENCY_ROLLBACK.md`** - Disaster recovery procedures
- **`../README.md`** - Project overview

---

## ⚡ Performance Tips

1. **Database Indexes** - Check MySQL slow query log
   ```bash
   mysql -u alumni_user -p -e "SELECT * FROM performance_schema.events_statements_summary_global_by_event_name LIMIT 10;"
   ```

2. **Frontend Bundle** - Keep under 500 KB
   ```bash
   cd react-app && npm run build && du -h dist/assets/
   ```

3. **Cache Static Assets** - Browser caching enabled (1 year for hashed files)

4. **Gzip Compression** - Gunicorn configured for compression

5. **Connection Pooling** - SQLAlchemy pool size configured for load

---

## 🔒 Security Reminders

- ✅ Never commit `.env.production` file
- ✅ Use strong passwords (min 16 characters)
- ✅ Keep SECRET_KEY secret and unique per deployment
- ✅ Rotate API keys regularly
- ✅ Enable 2FA on Brevo, Cloudinary, hosting accounts
- ✅ Use SSH keys (not passwords) for server access
- ✅ Keep system packages updated: `sudo apt-get upgrade`

---

## 📞 Support

If you encounter issues:

1. Check logs: `sudo journalctl -u alumniconnect -f`
2. Review PRODUCTION_DEPLOYMENT_GUIDE.md
3. Check EMERGENCY_ROLLBACK.md for recovery
4. Contact your system administrator

---

**Version**: 1.0  
**Last Updated**: May 2026  
**Environment**: Production  

