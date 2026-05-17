#!/usr/bin/env python3
import paramiko
HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
paths = [
    "/var/www/html/iceaa/react-app/dist",
    "/var/www/html/iceaa/ICE_AlumniConnect/react-app/dist",
    "/var/www/html/iceaa/ICE_AlumniConnect/dist",
]
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
for p in paths:
    print('\n$ ls -la ' + p)
    stdin, stdout, stderr = ssh.exec_command(f"ls -la {p} 2>/dev/null || echo 'MISSING'")
    out = stdout.read().decode('utf-8', errors='ignore')
    print(out)
ssh.close()
print('\nDone')
