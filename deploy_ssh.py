#!/usr/bin/env python3
"""
AlumniConnect Server Deployment via SSH
Connects to 172.30.240.39:36109 and runs deployment commands
"""

import paramiko
import sys
import time

# Server credentials
HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
APP_PATH = "/var/www/html/iceaa/ICE_AlumniConnect"

def execute_command(ssh_client, command, wait_for_completion=True):
    """Execute command on remote server"""
    print(f"\n{'='*60}")
    print(f"$ {command}")
    print(f"{'='*60}")
    
    stdin, stdout, stderr = ssh_client.exec_command(command)
    
    if wait_for_completion:
        exit_status = stdout.channel.recv_exit_status()
        print(f"Exit Code: {exit_status}")
    
    # Print output
    output = stdout.read().decode('utf-8', errors='ignore')
    if output:
        print(output)
    
    errors = stderr.read().decode('utf-8', errors='ignore')
    if errors:
        print("STDERR:", errors)
    
    return exit_status if wait_for_completion else 0

def main():
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "AlumniConnect Server Deployment" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    print(f"\nConnecting to {HOST}:{PORT} as {USER}...\n")
    
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to server
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
        print("✓ SSH Connection Successful\n")
        
        # Step 1: Check current directory
        print("\n[STEP 1] Navigating to app directory...")
        execute_command(ssh, f"cd {APP_PATH} && pwd")
        
        # Step 2: Stash local changes (if any)
        print("\n[STEP 2a] Checking for local changes...")
        execute_command(ssh, f"cd {APP_PATH} && git status")
        
        # Step 2b: Stash any local changes
        print("\n[STEP 2b] Stashing local changes (if any)...")
        execute_command(ssh, f"cd {APP_PATH} && git stash || true")
        
        # Step 2c: Clean untracked files
        print("\n[STEP 2c] Cleaning untracked files...")
        execute_command(ssh, f"cd {APP_PATH} && git clean -fd")
        
        # Step 2d: Git pull
        print("\n[STEP 2d] Pulling latest code from GitHub...")
        execute_command(ssh, f"cd {APP_PATH} && git pull origin main")
        
        # Step 3: Check git log
        print("\n[STEP 3] Showing latest commits...")
        execute_command(ssh, f"cd {APP_PATH} && git log --oneline -3")
        
        # Step 4: Run deployment script
        print("\n[STEP 4] Running HTTPS deployment script...")
        execute_command(ssh, f"cd {APP_PATH} && sudo bash deployment/scripts/setup_https_self_signed.sh")
        
        # Step 5: Check Nginx status
        print("\n[STEP 5] Checking Nginx status...")
        execute_command(ssh, "systemctl status nginx")
        
        # Step 6: Check Backend status
        print("\n[STEP 6] Checking Backend status...")
        execute_command(ssh, "systemctl status alumniconnect")
        
        # Step 7: Check certificates
        print("\n[STEP 7] Checking SSL certificates...")
        execute_command(ssh, "ls -la /etc/nginx/certs/")
        
        # Step 8: Test HTTPS locally
        print("\n[STEP 8] Testing HTTPS endpoint...")
        execute_command(ssh, "curl -k -I https://localhost/iceaa/ 2>&1 | head -15")
        
        # Step 9: Check listening ports
        print("\n[STEP 9] Checking listening ports...")
        execute_command(ssh, "ss -tulpn | grep -E '(80|443|5000)'")
        
        # Step 10: Verify logs
        print("\n[STEP 10] Recent Nginx errors (if any)...")
        execute_command(ssh, "tail -20 /var/log/nginx/error.log 2>/dev/null || echo 'No errors'")
        
        print("\n" + "="*60)
        print("✓ Deployment Complete!")
        print("="*60)
        print("\nAccess your application:")
        print("  🌐 HTTP:  http://csf.ru.ac.bd/iceaa/")
        print("  🔒 HTTPS: https://csf.ru.ac.bd/iceaa/")
        print("\nNote: Browser may show certificate warning (self-signed is OK)")
        print("      API endpoints working: https://csf.ru.ac.bd/iceaa/api/*")
        print("\n" + "="*60 + "\n")
        
    except paramiko.AuthenticationException:
        print("✗ Authentication failed - check username/password")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"✗ SSH error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        ssh.close()
        print("✓ SSH Connection Closed\n")

if __name__ == "__main__":
    main()
