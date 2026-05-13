# Staging-Ready Local Production Guide

This guide prepares the current project for a production-style local test before server deployment.

## 1) Environment separation

Create real env files from examples.

```powershell
Copy-Item .\react-app\.env.development.example .\react-app\.env.development
Copy-Item .\react-app\.env.production.example .\react-app\.env.production
Copy-Item .\backend\.env.example .\backend\.env
```

Then edit values in `backend/.env` and `react-app/.env.production`.

## 2) Backend production mode (Flask + Gunicorn config)

Required backend env values:
- `APP_ENV=production`
- `DEBUG=false`
- `CORS_ORIGINS=https://your-domain.com`
- `SECRET_KEY=<long-random-secret>`
- `MAIL_PROVIDER=brevo`
- `BREVO_API_KEY=<brevo-api-key>`
- `MYSQL_*` credentials

Run local production-style backend test (Windows-friendly, still Flask runtime):

```powershell
$env:APP_ENV='production'
$env:DEBUG='false'
$env:CORS_ORIGINS='https://your-domain.com'
& .\.venv\Scripts\python.exe .\backend\app.py
```

Gunicorn command for Linux staging/server:

```bash
cd backend
gunicorn -c gunicorn.conf.py wsgi:application
```

## 3) Frontend production build

```powershell
Set-Location .\react-app
npm ci
npm run build
npm run preview -- --host 127.0.0.1 --port 4173
```

Check that API requests point to your configured `VITE_API_BASE_URL`.

## 4) MySQL production-safe config

Use a dedicated DB user (do not use root in staging/production):

```sql
CREATE USER 'ac_user'@'%' IDENTIFIED BY 'strong_password_here';
GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,ALTER,INDEX,DROP ON alumniconnect.* TO 'ac_user'@'%';
FLUSH PRIVILEGES;
```

Set backend env:
- `MYSQL_USER=ac_user`
- `MYSQL_PASSWORD=strong_password_here`
- `AUTO_INIT_DB=false` after first schema setup

Import schema once:

```powershell
& 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe' --host=127.0.0.1 --port=3307 --user=ac_user --password=strong_password_here alumniconnect < .\backend\schema.sql
```

## 5) API integration checks in production mode

Run backend and frontend in production-style mode, then verify:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/api/health | Select-Object -ExpandProperty Content
```

Open frontend preview and test login + one data fetch endpoint.

## 6) Security checklist before server upload

- `DEBUG=false`
- Strong `SECRET_KEY`
- Strict `CORS_ORIGINS` (no `*`)
- No localhost hardcoded in production env
- Brevo key only in env/secrets, not in repo
- DB uses non-root account
- `AUTO_INIT_DB=false`
- HTTPS domain configured (`PUBLIC_BASE_URL`)

## 7) Final pre-deploy checklist

- Frontend build succeeds (`npm run build`)
- Backend starts with production env
- `/api/health` returns success
- React app can call backend API in preview mode
- Email test via Brevo passes
- No secrets committed to git
