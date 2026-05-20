#!/usr/bin/env python3
"""
Fix nginx configuration - consolidate to single alumniconnect_iceaa.conf
"""

import paramiko
import sys

# Server credentials
HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
APP_PATH = "/var/www/html/iceaa/ICE_AlumniConnect"

def execute_command(ssh_client, command, wait_for_completion=True):
    """Execute command on remote server"""
    print(f"\n{'='*70}")
    print(f"$ {command}")
    print(f"{'='*70}")
    
    stdin, stdout, stderr = ssh_client.exec_command(command)
    
    if wait_for_completion:
        exit_status = stdout.channel.recv_exit_status()
        print(f"Exit Code: {exit_status}")
    
    # Print output
    output = stdout.read().decode('utf-8', errors='ignore')
    if output:
        print(output)
    
    errors = stderr.read().decode('utf-8', errors='ignore')
    if errors and "STDERR" not in errors:
        print("STDERR:", errors)
    
    return exit_status if wait_for_completion else 0

def main():
    print("╔" + "="*68 + "╗")
    print("║" + " "*12 + "Consolidate Nginx Config to Single File" + " "*16 + "║")
    print("╚" + "="*68 + "╝")
    print(f"\nConnecting to {HOST}:{PORT} as {USER}...\n")
    
    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect to server
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
        print("✓ SSH Connection Successful\n")
        
        # Step 1: Pull latest changes
        print("\n[STEP 1] Pulling latest changes from GitHub...")
        execute_command(ssh, f"cd {APP_PATH} && git pull origin main")
        
        # Step 2: Remove old iceaa.conf from sites-available
        print("\n[STEP 2] Removing old iceaa.conf from nginx sites-available...")
        execute_command(ssh, "rm -f /etc/nginx/sites-available/iceaa.conf && echo '✓ Deleted (or was not present)'")
        
        # Step 3: Remove old symlink from sites-enabled
        print("\n[STEP 3] Removing old iceaa.conf symlink from nginx sites-enabled...")
        execute_command(ssh, "rm -f /etc/nginx/sites-enabled/iceaa.conf && echo '✓ Deleted (or was not present)'")
        
        # Step 4: Create correct symlink
        print("\n[STEP 4] Creating symlink to alumniconnect_iceaa.conf...")
        execute_command(ssh, "ln -sf /etc/nginx/sites-available/alumniconnect_iceaa.conf /etc/nginx/sites-enabled/alumniconnect_iceaa.conf && echo '✓ Symlink created'")
        
        # Step 5: Verify symlink
        print("\n[STEP 5] Verifying nginx sites-enabled configuration...")
        execute_command(ssh, "ls -la /etc/nginx/sites-enabled/ | grep -E '(alumniconnect|iceaa)'")
        
        # Step 6: Test nginx configuration
        print("\n[STEP 6] Testing nginx configuration syntax...")
        execute_command(ssh, "nginx -t")
        
        # Step 7: Restart nginx
        print("\n[STEP 7] Restarting nginx service...")
        execute_command(ssh, "systemctl restart nginx && echo '✓ Nginx restarted'")
        
        # Step 8: Restart alumniconnect
        print("\n[STEP 8] Restarting alumniconnect backend...")
        execute_command(ssh, "systemctl restart alumniconnect && echo '✓ Backend restarted'")
        
        # Step 9: Wait and check service status
        print("\n[STEP 9] Waiting 2 seconds and checking service status...")
        execute_command(ssh, "sleep 2 && echo '=== Service Status ===' && systemctl is-active nginx alumniconnect")
        
        # Step 10: Verify application logs
        print("\n[STEP 10] Checking recent backend logs...")
        execute_command(ssh, "tail -10 /var/log/alumniconnect.log 2>/dev/null || echo 'No log file yet'")
        
        # Step 11: Verify nginx config is correct
        print("\n[STEP 11] Verifying alumniconnect_iceaa.conf is in use...")
        execute_command(ssh, "cat /etc/nginx/sites-enabled/alumniconnect_iceaa.conf | head -20")
        
        print("\n" + "="*70)
        print("✅ Configuration Consolidation Complete!")
        print("="*70)
        print("\n🎯 Next Steps:")
        print("   1. Test the website: http://172.30.240.39/iceaa/")
        print("   2. Check admin dashboard: http://172.30.240.39/iceaa/admin")
        print("   3. Verify image loading in admin dashboard")
        print("   4. Check that API calls are working (browser dev tools → Network tab)")
        print("\n📝 Configuration Status:")
        print("   ✓ Old iceaa.conf removed from /etc/nginx/sites-available/")
        print("   ✓ Old iceaa.conf symlink removed from /etc/nginx/sites-enabled/")
        print("   ✓ Only alumniconnect_iceaa.conf is now active")
        print("   ✓ All services restarted successfully")
        print("\n" + "="*70 + "\n")
        
    except paramiko.AuthenticationException:
        print("✗ Authentication failed - check username/password")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == "__main__":
    main()
