# Nginx SPA Routing Solution - FIXED ✅

## Problem
When accessing `http://csf.ru.ac.bd/iceaa/student-dashboard`, the application was returning the default Nginx welcome page instead of routing to the React SPA.

## Root Causes
1. **Alias + Rewrite Conflict**: Nginx doesn't allow `alias` in locations where the URI has been rewritten
2. **try_files with Alias Issues**: `try_files $uri $uri/ /index.html` doesn't work reliably with `alias` directives
3. **Default Server**: Without a proper fallback, Nginx was serving its default page from `/usr/share/nginx/html/`

## Solution
Used `error_page 404 =200` instead of `try_files` for SPA routing - this is more reliable with `alias` directives.

### Final Working Nginx Configuration

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name csf.ru.ac.bd 172.30.240.39 localhost;

    client_max_body_size 100M;

    # Performance optimizations
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/javascript application/javascript 
               application/json application/xml application/xml+rss image/svg+xml;

    # Root redirect
    location = / {
        return 301 /iceaa/;
    }

    # Flask API proxy
    location /iceaa/api/ {
        proxy_pass http://127.0.0.1:5000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_connect_timeout 5s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Uploads proxy
    location /iceaa/uploads/ {
        proxy_pass http://127.0.0.1:5000/uploads/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type' always;
        add_header 'Cross-Origin-Resource-Policy' 'cross-origin' always;
        expires 30d;
        add_header Cache-Control "public, immutable";
        proxy_connect_timeout 5s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Static assets
    location /iceaa/assets/ {
        alias /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/assets/;
        access_log off;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # React SPA - CRITICAL: Uses error_page for fallback instead of try_files
    location /iceaa/ {
        alias /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/;
        error_page 404 =200 /iceaa/index.html;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Security rules
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    location ~* \.(env|git) {
        deny all;
    }

    access_log /var/log/nginx/iceaa_access.log;
    error_log  /var/log/nginx/iceaa_error.log;
}
```

## Key Points

### 1. Why `error_page 404 =200` Works Better for SPA
- When Nginx looks for `/iceaa/student-dashboard`, it doesn't find the actual file
- Instead of 404, it returns status 200 and serves `/iceaa/index.html`
- This lets React Router handle client-side routing properly
- **Avoids the alias+rewrite conflict**

### 2. React Configuration (Already Correct)
Your `vite.config.js` already has the correct base path:
```javascript
base: mode === 'production' ? '/iceaa/' : '/'
```
This ensures all assets and API calls are relative to `/iceaa/`

### 3. React App Settings
No changes needed to your React app:
- All routes are already configured for the `/iceaa/` subdirectory
- API calls use `/iceaa/api/` prefix
- Bootstrap and asset paths work automatically with the Vite base configuration

## Deployment Steps

### Option 1: Deploy via Git (Recommended)
```bash
cd /var/www/html/iceaa/ICE_AlumniConnect
git pull origin main
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Manual Update
```bash
sudo cp /path/to/correct/nginx/config /etc/nginx/sites-available/iceaa.conf
sudo nginx -t
sudo systemctl restart nginx
```

## Testing
✅ Routes now working:
- `http://csf.ru.ac.bd/iceaa/` - Home page
- `http://csf.ru.ac.bd/iceaa/student-dashboard` - Student dashboard
- `http://csf.ru.ac.bd/iceaa/api/...` - API endpoints
- Any other SPA route - automatically serves index.html

## Troubleshooting

### Still seeing default Nginx page?
1. Check `/etc/nginx/sites-enabled/` - ensure symlink points to updated config
2. Verify syntax: `sudo nginx -t`
3. Restart Nginx: `sudo systemctl restart nginx`
4. Clear browser cache: Ctrl+Shift+Delete

### Assets not loading (404 errors)?
1. Check `/iceaa/assets/` location block in config
2. Verify path: `/var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/assets/`
3. Ensure React build is up to date: `npm run build` in react-app directory

### Backend API errors?
1. Verify Flask/Gunicorn is running on port 5000: `curl http://127.0.0.1:5000/api/`
2. Check proxy headers are correct: X-Forwarded-Proto, X-Forwarded-Host
3. Check Flask app is handling subdirectory correctly

## Files Modified
- `/etc/nginx/sites-available/iceaa.conf` - Main Nginx configuration
- `deployment/nginx/alumniconnect_iceaa.conf` - Backup in repository

## Important Notes
⚠️ **Do NOT** go back to old configurations using:
- `try_files` with `alias` and `rewrite` together
- Named locations with `@fallback` and `alias`
- Multiple conflicting location blocks for the same path

The `error_page 404 =200` approach is the most reliable for SPA deployment with Nginx.
