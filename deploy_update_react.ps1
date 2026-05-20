# Deploy React dist to production server
$Server = "172.30.240.39"
$Port = "36109"
$User = "root"
$Password = "ice26Dru26&4mD"
$RemotePath = "/var/www/html/iceaa/ICE_AlumniConnect"
$LocalDistPath = "react-app\dist"

Write-Host "Starting React deployment to $Server..." -ForegroundColor Green

# Check local dist exists
if (-not (Test-Path $LocalDistPath)) {
    Write-Host "ERROR: Local dist folder not found at $LocalDistPath" -ForegroundColor Red
    exit 1
}

Write-Host "Local dist folder verified. Size: $(Get-ChildItem $LocalDistPath -Recurse | Measure-Object -Sum Length | Select-Object -ExpandProperty Sum) bytes" -ForegroundColor Yellow

# Use scp to copy the dist folder (requires sshpass on server or key-based auth)
Write-Host "Copying dist folder to server..." -ForegroundColor Yellow

# Create tar of dist folder for faster transfer
$TarFile = "react-dist-$(Get-Date -Format 'yyyyMMdd-HHmmss').tar.gz"

Write-Host "Creating backup and deploying..." -ForegroundColor Yellow

# Commands to run on server
$ServerCmds = @"
#!/bin/bash
cd $RemotePath
# Backup current dist
if [ -d "dist" ]; then
    mv dist dist.backup-\$(date +%Y%m%d-%H%M%S)
    echo "Backed up current dist"
fi
# Extract new dist
tar -xzf /tmp/$TarFile
echo "Extracted new dist files"
# Fix permissions
chown -R www-data:www-data dist
echo "Fixed permissions"
# Clear old backups (keep last 3)
ls -t dist.backup-* 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null
echo "Cleaned up old backups"
# Restart nginx
systemctl reload nginx
echo "Nginx reloaded"
"@

# Create tar locally and upload
Write-Host "Creating tar archive..." -ForegroundColor Yellow
$OrigLocation = Get-Location
Set-Location "react-app"
tar -czf "..\$TarFile" "dist" 2>&1 | Out-Null
Set-Location $OrigLocation

if (-not (Test-Path $TarFile)) {
    Write-Host "ERROR: Failed to create tar file" -ForegroundColor Red
    exit 1
}

$TarSize = (Get-Item $TarFile).Length
Write-Host "Tar file created: $TarFile ($('{0:N0}' -f $TarSize) bytes)" -ForegroundColor Yellow

# Upload using PowerShell remoting via SSH
Write-Host "Uploading to server..." -ForegroundColor Yellow
$scp = "scp -P $Port $TarFile $($User)@$($Server):/tmp/"
Write-Host "Running: $scp" -ForegroundColor Gray

# For Windows, we'll use Posh-SSH or fall back to direct SSH commands
try {
    # Try using OpenSSH if available
    & scp -P $Port $TarFile "$($User)@$($Server):/tmp/" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: SCP copy failed" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "ERROR: SCP command failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "File uploaded successfully" -ForegroundColor Green

# Execute remote commands
Write-Host "Executing deployment on server..." -ForegroundColor Yellow

# Create a temp script on server
$RemoteScriptPath = "/tmp/deploy_react_$((Get-Date -Format 'yyyyMMddHHmmss')).sh"

# Using here-string for remote commands
$cmd = @"
ssh -p $Port $User@$Server 'bash -c "
cd $RemotePath
if [ -d 'dist' ]; then
    mv dist dist.backup-\$(date +%Y%m%d-%H%M%S)
    echo 'Backed up current dist'
fi
cd /tmp
tar -xzf $TarFile
mv dist $RemotePath/
chown -R www-data:www-data $RemotePath/dist
echo 'Permissions fixed'
systemctl reload nginx
echo 'Nginx reloaded'
rm -f $TarFile
echo 'Cleanup complete'
"'
"@

Write-Host "Running remote deployment..." -ForegroundColor Gray
Invoke-Expression $cmd

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Cleaning up local tar file..." -ForegroundColor Yellow
Remove-Item $TarFile -Force -ErrorAction SilentlyContinue

Write-Host "`nDeployment Summary:" -ForegroundColor Green
Write-Host "✓ React build deployed to $Server" -ForegroundColor Green
Write-Host "✓ Nginx reloaded" -ForegroundColor Green
Write-Host "✓ Access the site at: http://$Server/iceaa/" -ForegroundColor Green
