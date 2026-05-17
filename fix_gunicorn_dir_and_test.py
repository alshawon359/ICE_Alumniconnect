#!/usr/bin/env python3
import paramiko
HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"

cmds = [
    "mkdir -p /var/www/.gunicorn",
    "chown www-data:www-data /var/www/.gunicorn || true",
    "chmod 755 /var/www/.gunicorn || true",
    "systemctl restart alumniconnect && sleep 2",
    "systemctl status alumniconnect --no-pager | head -20",
    "tail -n 60 /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/error.log || true",
    "curl -s -k -I https://localhost/iceaa/ 2>&1 | head -20",
    "curl -s -k -I https://localhost/iceaa/api/admin-login 2>&1 | head -20",
    "curl -s -H 'X-Forwarded-Proto: https' -I http://127.0.0.1:5000/api/admin-login 2>&1 | head -20",
    "test -f /var/www/html/iceaa/react-app/dist/index.html && echo 'INDEX_OK' || echo 'INDEX_MISSING'",
]

import time
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)

for cmd in cmds:
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
