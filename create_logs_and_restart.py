#!/usr/bin/env python3
import paramiko
HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"

commands = [
    "mkdir -p /var/www/html/iceaa/ICE_AlumniConnect/backend/logs",
    "chown -R www-data:www-data /var/www/html/iceaa/ICE_AlumniConnect/backend/logs || true",
    "chmod 750 /var/www/html/iceaa/ICE_AlumniConnect/backend/logs || true",
    "touch /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/error.log /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/access.log || true",
    "chown www-data:www-data /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/*.log || true",
    "systemctl restart alumniconnect && sleep 2",
    "systemctl status alumniconnect --no-pager | head -20",
    "tail -n 50 /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/error.log || echo 'no error log'",
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
for cmd in commands:
    print('\n$ ' + cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print('Exit:', status)
    if out.strip():
        print(out)
    if err.strip():
        print('ERR:', err)
ssh.close()
print('\nDone')
