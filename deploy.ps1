#!/usr/bin/env pwsh
# AlumniConnect Deployment Script
# Automates: Build + Deploy React app + Deploy nginx config + Restart services

param(
    [string]$SshUser = "root",
    [string]$SshHost = "172.30.240.39",
    [int]$SshPort = 36109,
    [string]$SshPassword = "ice26Dru26&4mD"
)

$ErrorActionPreference = "Stop"
$workspace = Split-Path $PSScriptRoot -Parent

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "AlumniConnect Deployment Script" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Target: $SshHost port $SshPort" -ForegroundColor Green
Write-Host "User: $SshUser" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 1: Build React App
# ============================================
Write-Host "[1/5] Building React app with /iceaa/ base path..." -ForegroundColor Yellow
Push-Location "$workspace\react-app"

if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host "Running npm run build..." -ForegroundColor Cyan
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "✓ Build successful" -ForegroundColor Green
Pop-Location

# ============================================
# STEP 2: Deploy React dist
# ============================================
Write-Host "[2/5] Deploying React dist to server..." -ForegroundColor Yellow
$scpDest = $SshUser + "@" + $SshHost + ":/var/www/html/iceaa/ICE_AlumniConnect/"
Write-Host "scp to $scpDest" -ForegroundColor Cyan

& scp -P $SshPort -r "$workspace\react-app\dist" "$scpDest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "SCP failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dist deployed" -ForegroundColor Green

# ============================================
# STEP 3: Deploy nginx config
# ============================================
Write-Host "[3/5] Deploying nginx config..." -ForegroundColor Yellow
$scpNginx = $SshUser + "@" + $SshHost + ":/etc/nginx/sites-available/"
Write-Host "scp nginx config..." -ForegroundColor Cyan

& scp -P $SshPort "$workspace\deployment\nginx\alumniconnect_iceaa.conf" "$scpNginx"

if ($LASTEXITCODE -ne 0) {
    Write-Host "SCP failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Nginx config deployed" -ForegroundColor Green

# ============================================
# STEP 4: Apply config on server
# ============================================
Write-Host "[4/5] Applying configuration on server..." -ForegroundColor Yellow

$sshCommands = @'
# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Restart backend service
systemctl restart alumniconnect
sleep 2

# Verify services
echo "=== Nginx Status ==="
systemctl is-active nginx
echo ""
echo "=== Backend Status ==="
systemctl is-active alumniconnect
'@

Write-Host "Executing remote commands on server..." -ForegroundColor Cyan
$sshCommands | & ssh -p $SshPort "$SshUser@$SshHost" "bash -s"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Remote commands failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Services configured and restarted" -ForegroundColor Green

# ============================================
# STEP 5: Final verification
# ============================================
Write-Host "[5/5] Verifying deployment..." -ForegroundColor Yellow

$verifyCmd = @'
echo "Checking nginx config syntax:"
sudo nginx -t

echo ""
echo "Checking dist folder:"
ls -lh /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/ | head -5

echo ""
echo "Checking index.html exists:"
test -f /var/www/html/iceaa/ICE_AlumniConnect/react-app/dist/index.html && echo "OK - index.html found" || echo "ERROR - index.html NOT found"
'@

$verifyCmd | & ssh -p $SshPort "$SshUser@$SshHost" "bash -s"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "✓ Deployment Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Test URLs:" -ForegroundColor Cyan
Write-Host "  Home: https://csf.ru.ac.bd/iceaa/" -ForegroundColor Green
Write-Host "  Admin: https://csf.ru.ac.bd/iceaa/admin-dashboard" -ForegroundColor Green
Write-Host "  Student: https://csf.ru.ac.bd/iceaa/student-login" -ForegroundColor Green
Write-Host ""
Write-Host "If URLs still show paths without /iceaa/:" -ForegroundColor Yellow
Write-Host "  1. Hard refresh: Ctrl+Shift+Delete" -ForegroundColor Yellow
Write-Host "  2. Clear browser cache" -ForegroundColor Yellow
Write-Host "  3. Refresh page" -ForegroundColor Yellow
Write-Host ""
