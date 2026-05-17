#!/usr/bin/env python3
"""
Check backend virtualenv and systemd unit for alumniconnect
"""
import paramiko

HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"

commands = [
    ("List venv bin", "ls -la /var/www/html/iceaa/ICE_AlumniConnect/backend/venv/bin || echo 'VENV_MISSING'"),
    ("Check gunicorn executable", "test -x /var/www/html/iceaa/ICE_AlumniConnect/backend/venv/bin/gunicorn && echo 'GUNICORN_OK' || echo 'GUNICORN_MISSING'"),
    ("Gunicorn version", "/var/www/html/iceaa/ICE_AlumniConnect/backend/venv/bin/gunicorn --version 2>&1 || true"),
    ("Python in venv", "/var/www/html/iceaa/ICE_AlumniConnect/backend/venv/bin/python --version 2>&1 || true"),
    ("Cat systemd unit", "cat /etc/systemd/system/alumniconnect.service || echo 'UNIT_MISSING'"),
    ("Journal recent", "journalctl -u alumniconnect -n 200 --no-pager 2>&1 || true"),
    ("Check backend log files", "ls -la /var/www/html/iceaa/ICE_AlumniConnect/backend/logs || echo 'NO_LOG_DIR'"),
    ("Tail backend error log", "tail -n 80 /var/www/html/iceaa/ICE_AlumniConnect/backend/logs/error.log 2>/dev/null || echo 'NO_ERROR_LOG'"),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)

results = []
for title, cmd in commands:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    results.append((title, cmd, status, out, err))

ssh.close()
with open('backend_check.txt','w', encoding='utf-8') as f:
    for title, cmd, status, out, err in results:
        f.write('='*80 + '\n')
        f.write(title + '\n')
        f.write('$ ' + cmd + '\n')
        f.write('Exit: ' + str(status) + '\n')
        f.write(out + '\n')
        if err:
            f.write('STDERR:\n' + err + '\n')
print('Saved backend_check.txt')

for title, cmd, status, out, err in results:
    print('\n' + title + ':')
    print((out.strip().split('\n')[:8] if out.strip() else ['(no output)']))

