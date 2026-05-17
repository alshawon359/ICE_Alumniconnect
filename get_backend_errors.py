#!/usr/bin/env python3
import paramiko
HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)

cmds = [
    "ls -la /var/www/html/iceaa/ICE_AlumniConnect/backend/logs || echo 'NO_LOG_DIR'",
    "stat -c '%U %G %a' /var/www/html/iceaa/ICE_AlumniConnect/backend/logs || true",
    "tail -n 200 /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/error.log 2>/dev/null || echo 'NO_ERROR_LOG'",
    "journalctl -u alumniconnect -n 200 --no-pager | tail -n 80",
    "/var/www/html/iceaa/ICE_AlumniConnect/backend/venv/bin/gunicorn --version || true",
]

for cmd in cmds:
    print('\n' + '='*60)
    print('$', cmd)
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
