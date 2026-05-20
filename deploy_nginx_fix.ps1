# ============================================
# AlumniConnect Nginx Config Deployment Script
# Fixes: SPA routing 404 and page refresh issues
# Port 80 Only (HTTP)
# ============================================

param(
    [string]$ServerIP = "172.30.240.39",
    [int]$SSHPort = 36109,
    [string]$Username = "root"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "AlumniConnect Nginx Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$configPath = "deployment\nginx\alumniconnect_iceaa.conf"

if (-not (Test-Path $configPath)) {
    Write-Host "ERROR: Config file not found at $configPath" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Local config: $configPath" -ForegroundColor Green
Write-Host "🖥️  Target server: $Username@$ServerIP (Port $SSHPort)" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Uploading nginx config to server..." -ForegroundColor Yellow
$targetHost = "$Username@$ServerIP"
Write-Host "  Command: scp -P $SSHPort `"$configPath`" $targetHost`:/etc/nginx/sites-available/default"
Write-Host ""

# Use SCP to upload file
scp -P $SSHPort "$configPath" "${targetHost}:/etc/nginx/sites-available/default"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: File upload failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ File uploaded successfully" -ForegroundColor Green

Write-Host "`nStep 2: Validating nginx config..." -ForegroundColor Yellow
ssh -p $SSHPort "$Username@$ServerIP" "sudo nginx -t"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Nginx config validation failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Config validation passed" -ForegroundColor Green

Write-Host "`nStep 3: Reloading nginx..." -ForegroundColor Yellow
ssh -p $SSHPort "$Username@$ServerIP" "sudo systemctl reload nginx"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Nginx reload failed" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Nginx reloaded successfully" -ForegroundColor Green

Write-Host "`nStep 4: Verifying nginx status..." -ForegroundColor Yellow
ssh -p $SSHPort "$Username@$ServerIP" "sudo systemctl status nginx"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Your app should now work at:" -ForegroundColor Cyan
Write-Host "   • http://csf.ru.ac.bd/iceaa/" -ForegroundColor White
Write-Host "   • http://csf.ru.ac.bd/iceaa/admin" -ForegroundColor White
Write-Host "   • http://172.30.240.39/iceaa/" -ForegroundColor White
Write-Host ""
Write-Host "✅ Fixed issues:" -ForegroundColor Green
Write-Host "   ✓ Contract page 404 error" -ForegroundColor White
Write-Host "   ✓ Page refresh on /admin" -ForegroundColor White
Write-Host "   ✓ SPA routing on all nested routes" -ForegroundColor White
Write-Host ""
