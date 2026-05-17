#!/usr/bin/env python3
"""
Debug 404 errors on AlumniConnect server
"""

import paramiko
import sys

HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
APP_PATH = "/var/www/html/iceaa/ICE_AlumniConnect"

def execute_command(ssh_client, command):
    """Execute command on remote server"""
    print(f"\n{'='*70}")
    print(f"$ {command}")
    print(f"{'='*70}")
    
    stdin, stdout, stderr = ssh_client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    output = stdout.read().decode('utf-8', errors='ignore')
    if output:
        print(output[:3000])  # First 3000 chars
    
    errors = stderr.read().decode('utf-8', errors='ignore')
    if errors:
        print("STDERR:", errors[:1000])
    
    return exit_status

def main():
    print("🔍 AlumniConnect - 404 Error Debugging\n")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
        print("✓ Connected to server\n")
        
        # Check Nginx error log for 404s
        print("[1] Recent 404 errors in Nginx:")
        execute_command(ssh, "tail -50 /var/log/nginx/error.log | grep -i 404 || echo 'No 404 errors in error log'")
        
        # Check Nginx access log for 404s
        print("\n[2] Recent 404 access attempts:")
        execute_command(ssh, "tail -30 /var/log/nginx/access.log | grep ' 404 ' || echo 'No 404 in access log'")
        
        # Check if frontend files exist
        print("\n[3] Frontend directory structure:")
        execute_command(ssh, "ls -la /var/www/html/iceaa/")
        
        print("\n[4] Check index.html exists:")
        execute_command(ssh, "ls -la /var/www/html/iceaa/react-app/ | head -20")
        
        # Check backend logs
        print("\n[5] Backend service status:")
        execute_command(ssh, "systemctl status alumniconnect --no-pager")
        
        print("\n[6] Backend recent errors:")
        execute_command(ssh, "journalctl -u alumniconnect -n 30 --no-pager")
        
        # Check if backend is responding
        print("\n[7] Test backend health endpoint:")
        execute_command(ssh, "curl -s -H 'X-Forwarded-Proto: https' http://127.0.0.1:5000/api/health | head -50")
        
        # Check Nginx config
        print("\n[8] Nginx config - check root/try_files:")
        execute_command(ssh, "grep -A5 'location /iceaa' /etc/nginx/sites-enabled/* 2>/dev/null | head -30")
        
        # Check if git pull was clean
        print("\n[9] Git status:")
        execute_command(ssh, f"cd {APP_PATH} && git status --short")
        
        # List recent files in react-app
        print("\n[10] React app build output:")
        execute_command(ssh, "find /var/www/html/iceaa/react-app -type f -name '*.html' -o -name '*.js' | head -20")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
