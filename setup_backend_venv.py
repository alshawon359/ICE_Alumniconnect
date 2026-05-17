#!/usr/bin/env python3
"""
Create backend virtualenv, install requirements, and restart alumniconnect service
"""
import paramiko
import time

HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
APP_BACKEND = "/var/www/html/iceaa/ICE_AlumniConnect/backend"

commands = [
    ("Make venv", f"cd {APP_BACKEND} && python3 -m venv venv"),
    ("Upgrade pip", f"{APP_BACKEND}/venv/bin/pip install --upgrade pip setuptools wheel"),
    ("Install requirements", f"{APP_BACKEND}/venv/bin/pip install -r {APP_BACKEND}/requirements.txt"),
    ("Check gunicorn", f"test -x {APP_BACKEND}/venv/bin/gunicorn && echo 'GUNICORN_OK' || echo 'GUNICORN_MISSING'"),
    ("Restart service", "systemctl restart alumniconnect && sleep 2"),
    ("Service status", "systemctl status alumniconnect --no-pager | head -20"),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)

for title, cmd in commands:
    print('\n' + '='*60)
    print(title)
    print('$', cmd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='ignore')
    err = stderr.read().decode('utf-8', errors='ignore')
    print('Exit:', exit_status)
    if out.strip():
        print(out)
    if err.strip():
        print('ERR:', err)

ssh.close()
print('\nDone')
