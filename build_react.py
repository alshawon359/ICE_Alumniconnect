#!/usr/bin/env python3
"""
Build React app on AlumniConnect server and fix 404 errors
"""

import paramiko
import time

HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
APP_PATH = "/var/www/html/iceaa/ICE_AlumniConnect"

def execute_command(ssh_client, command, timeout_seconds=300, wait=True):
    """Execute command on remote server"""
    print(f"\n{'='*70}")
    print(f"$ {command}")
    print(f"{'='*70}")
    
    stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout_seconds)
    
    if wait:
        exit_status = stdout.channel.recv_exit_status()
        print(f"Exit Code: {exit_status}\n")
    else:
        exit_status = 0
    
    # Stream output
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.rstrip())
    
    errors = stderr.read().decode('utf-8', errors='ignore')
    if errors and "npm warn" not in errors.lower():
        print("STDERR:", errors[:1000])
    
    return exit_status

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "Build React App - Fix 404 Errors" + " "*20 + "║")
    print("╚" + "="*68 + "╝\n")
    
    ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
    print("✓ Connected to server\n")
    
    # Step 1: Check Node.js and npm
    print("\n[STEP 1] Check Node.js and npm:")
    execute_command(ssh, "node --version && npm --version")
    
    # Step 2: Navigate to react-app
    print("\n[STEP 2] Check react-app directory:")
    execute_command(ssh, f"ls -la {APP_PATH}/react-app/ | head -20")
    
    # Step 3: Install dependencies
    print("\n[STEP 3] Installing npm dependencies (this may take 1-2 minutes)...")
    execute_command(ssh, f"cd {APP_PATH}/react-app && npm install 2>&1 | tail -30", timeout_seconds=300)
    
    # Step 4: Build React app
    print("\n[STEP 4] Building React app (this may take 1-2 minutes)...")
    execute_command(ssh, f"cd {APP_PATH}/react-app && npm run build 2>&1 | tail -50", timeout_seconds=300)
    
    # Step 5: Verify build output
    print("\n[STEP 5] Verify dist directory was created:")
    execute_command(ssh, f"ls -la {APP_PATH}/react-app/dist/ | head -20")
    
    # Step 6: Check if assets exist
    print("\n[STEP 6] Check assets in dist:")
    execute_command(ssh, f"ls -la {APP_PATH}/react-app/dist/assets/ 2>&1 | head -15")
    
    # Step 7: Check if index.html was created
    print("\n[STEP 7] Verify index.html exists:")
    execute_command(ssh, f"ls -la {APP_PATH}/react-app/dist/index.html")
    
    # Step 8: Check Nginx config
    print("\n[STEP 8] Verify Nginx config for /iceaa/assets/:")
    execute_command(ssh, "grep -n 'assets' /etc/nginx/sites-enabled/* 2>/dev/null || grep -n 'assets' /etc/nginx/conf.d/* 2>/dev/null")
    
    # Step 9: Reload Nginx
    print("\n[STEP 9] Reload Nginx:")
    execute_command(ssh, "systemctl reload nginx")
    
    # Step 10: Verify Nginx is running
    print("\n[STEP 10] Check Nginx status:")
    execute_command(ssh, "systemctl status nginx --no-pager | head -10")
    
    # Step 11: Test frontend endpoint
    print("\n[STEP 11] Test HTTPS endpoint (should return HTML):")
    execute_command(ssh, "curl -s -k https://localhost/iceaa/ 2>&1 | head -20")
    
    # Step 12: Test assets
    print("\n[STEP 12] Test asset endpoint:")
    execute_command(ssh, "curl -s -k https://localhost/iceaa/index.html 2>&1 | head -20")
    
    print("\n" + "="*70)
    print("✓ React App Build Complete!")
    print("="*70)
    print("\nAccess your application:")
    print("  🌐 HTTPS: https://csf.ru.ac.bd/iceaa/")
    print("\nIf you still see 404 errors:")
    print("  - Clear browser cache (Ctrl+Shift+Delete)")
    print("  - Hard refresh (Ctrl+Shift+R)")
    print("  - Check browser console for exact 404 paths")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
    print("\n✓ Connection closed")
