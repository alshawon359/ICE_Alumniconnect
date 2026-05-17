# Production Deployment Commands for ICE Alumni Connect
# Server: csf.ru.ac.bd (172.30.240.39)
# Application Path: /var/www/html/iceaa/ICE_AlumniConnect

## 1. TEST NGINX CONFIGURATION (SAFE - NO CHANGES)
```bash
sudo nginx -t
# Output should be: "nginx: configuration file test is successful"
```

## 2. RELOAD NGINX (RESTARTS WEB SERVICE)
```bash
sudo systemctl reload nginx
# or
sudo service nginx reload
```

## 3. CHECK FLASK/GUNICORN STATUS
```bash
# If using systemd service
sudo systemctl status alumniconnect

# Or check if process is running
ps aux | grep gunicorn
ps aux | grep "python.*app.py"
```

## 4. START/RESTART GUNICORN (if using systemd)
```bash
# Restart
sudo systemctl restart alumniconnect

# Stop
sudo systemctl stop alumniconnect

# Start
sudo systemctl start alumniconnect

# View logs
sudo journalctl -u alumniconnect -f
```

## 5. MANUAL START GUNICORN (for testing)
```bash
cd /var/www/html/iceaa/ICE_AlumniConnect/backend
gunicorn -c gunicorn.conf.py wsgi:app
```

## 6. VERIFY DEPLOYMENT (TEST CONNECTIVITY)
```bash
# From server (localhost test)
curl http://127.0.0.1:5000/api/
curl http://127.0.0.1/iceaa/api/  # Through Nginx

# From remote (HTTPS)
curl https://csf.ru.ac.bd/iceaa/api/

# Check Nginx access logs
sudo tail -f /var/log/nginx/access.log | grep iceaa

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

## 7. SYSTEMD SERVICE FILE (if needed)
Location: `/etc/systemd/system/alumniconnect.service`

Should contain:
```ini
[Unit]
Description=ICE Alumni Connect Flask Application
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/html/iceaa/ICE_AlumniConnect/backend
ExecStart=gunicorn -c gunicorn.conf.py wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 8. NGINX CONFIG LOCATION
File: `/etc/nginx/sites-available/default` or `/etc/nginx/conf.d/alumniconnect.conf`

The `/iceaa/api/` and `/iceaa/` location blocks are already in place ✅

## 9. FIREWALL/PORT CHECK
```bash
# Check if port 5000 is listening on localhost
netstat -tlnp | grep 5000

# Check if port 80/443 open
netstat -tlnp | grep nginx

# Check if port 3306 (MySQL) is listening
netstat -tlnp | grep 3306
```

## 10. DATABASE CONNECTION TEST
```bash
cd /var/www/html/iceaa/ICE_AlumniConnect/backend
mysql -h 127.0.0.1 -P 3306 -u $MYSQL_USER -p $MYSQL_PASSWORD $MYSQL_DB -e "SELECT 1;"
```

## 11. PYTHON ENVIRONMENT CHECK
```bash
# Verify Python and dependencies
python3 --version
pip3 list | grep -E "flask|gunicorn|mysql|pymysql"

# Test Flask import
python3 -c "from app import app; print('Flask OK')"
```

## 12. PERMISSIONS FIX (if needed)
```bash
# Ensure web server user owns the app
sudo chown -R www-data:www-data /var/www/html/iceaa/ICE_AlumniConnect

# Permissions
sudo chmod -R 755 /var/www/html/iceaa/ICE_AlumniConnect
sudo chmod -R 755 /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist
sudo chmod -R 750 /var/www/html/iceaa/ICE_AlumniConnect/backend
```

## FULL DEPLOYMENT SEQUENCE (SAFE ORDER)

```bash
# 1. Test Nginx config first (NO CHANGES)
sudo nginx -t

# 2. Ensure permissions are correct
sudo chown -R www-data:www-data /var/www/html/iceaa/ICE_AlumniConnect
sudo chmod -R 755 /var/www/html/iceaa/ICE_AlumniConnect

# 3. Install/update dependencies
cd /var/www/html/iceaa/ICE_AlumniConnect/backend
pip3 install -r requirements.txt

# 4. Verify database connection
python3 -c "import config; import pymysql; pymysql.connect(host=config.MYSQL_HOST, user=config.MYSQL_USER, password=config.MYSQL_PASSWORD, database=config.MYSQL_DB); print('DB OK')"

# 5. Test Flask app
python3 -c "from app import app; print('Flask OK')"

# 6. Reload Nginx
sudo systemctl reload nginx

# 7. Restart Gunicorn
sudo systemctl restart alumniconnect

# 8. Verify running
ps aux | grep gunicorn
ps aux | grep nginx

# 9. Test locally
curl http://127.0.0.1:5000/api/
curl https://csf.ru.ac.bd/iceaa/api/

# 10. Check logs for errors
sudo journalctl -u alumniconnect -n 20
sudo tail -20 /var/log/nginx/error.log
```

## TROUBLESHOOTING

### Port 5000 already in use
```bash
sudo lsof -i :5000
# Kill the process if needed
sudo kill -9 <PID>
```

### Nginx 502 Bad Gateway (can't reach Flask)
```bash
# Check if Flask is running
ps aux | grep gunicorn

# Check if Nginx can reach Flask socket
telnet 127.0.0.1 5000

# Check Nginx error log
sudo tail -50 /var/log/nginx/error.log

# Try restarting Flask
sudo systemctl restart alumniconnect
sudo systemctl restart nginx
```

### Permission denied errors
```bash
# Run as sudo with proper user
sudo -u www-data python3 app.py
```

### MySQL connection failed
```bash
# Test connectivity
mysql -h 127.0.0.1 -u $MYSQL_USER -p -e "SELECT 1;"
# Check credentials in /backend/config.py
```

## MONITORING COMMANDS

```bash
# Real-time monitoring
watch 'ps aux | grep -E "gunicorn|nginx" | grep -v grep'

# Memory usage
ps aux | grep gunicorn | awk '{print $6}' | paste -sd+ | bc

# Request count
sudo tail /var/log/nginx/access.log | wc -l

# Errors in last hour
sudo grep "error" /var/log/nginx/error.log | tail -20
```

---

**IMPORTANT NOTES:**
- Current port configuration: **Flask = 5000, Nginx = 80/443**
- Do NOT change to port 80 for Flask (port conflicts with Nginx)
- All SSL/HTTPS handled by Nginx + Let's Encrypt
- Existing projects on csf.ru.ac.bd are unaffected
- Use `/iceaa/` path for all browser access
- API endpoints at `/iceaa/api/*`

