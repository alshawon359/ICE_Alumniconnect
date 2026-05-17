#!/usr/bin/env python3
"""
Collect targeted logs and run tests for /iceaa/admin-login
"""
import paramiko
import sys

HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"

cmds = [
    ("Nginx access lines for admin-login", "grep '/iceaa/admin-login' /var/log/nginx/access.log || echo 'No access lines for admin-login'") ,
    ("Nginx access lines with /api/admin-login", "grep '/api/admin-login' /var/log/nginx/access.log || echo 'No api admin-login lines'") ,
    ("Nginx access last 50 lines (show 404s)", "tail -n 200 /var/log/nginx/access.log | grep ' 404 ' | tail -n 50 || echo 'No recent 404s in access log'") ,
    ("Nginx error last 200 lines", "tail -n 200 /var/log/nginx/error.log || echo 'No nginx error log or empty'") ,
    ("Backend service status", "systemctl status alumniconnect --no-pager || true") ,
    ("Backend recent journal (grep 404 or admin)", "journalctl -u alumniconnect -n 200 --no-pager | grep -Ei '404|admin|error' || echo 'No relevant lines in backend logs'") ,
    ("Curl frontend admin-login (localhost)", "curl -s -k -I https://localhost/iceaa/admin-login || true") ,
    ("Curl frontend admin-login (public)", "curl -s -k -I https://csf.ru.ac.bd/iceaa/admin-login || true") ,
    ("Curl backend API internal", "curl -s -I -H 'X-Forwarded-Proto: https' http://127.0.0.1:5000/api/admin-login || true") ,
    ("Curl backend API via nginx", "curl -s -k -I https://localhost/iceaa/api/admin-login || true") ,
    ("Check react dist index exists", "test -f /var/www/html/iceaa/react-app/dist/index.html && echo 'INDEX_EXISTS' || echo 'INDEX_MISSING'") ,
    ("Check asset path double-occurrence", "ls -la /var/www/html/iceaa/react-app/dist/assets | sed -n '1,120p' || echo 'assets missing'") ,
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
    out = []
    for title, cmd in cmds:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        exit_status = stdout.channel.recv_exit_status()
        text = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        out.append((title, cmd, exit_status, text, err))
    # Save to local file
    with open('admin_login_debug.txt','w', encoding='utf-8') as f:
        for title, cmd, status, text, err in out:
            f.write('='*80 + "\n")
            f.write(title + "\n")
            f.write('$ ' + cmd + "\n")
            f.write('Exit: ' + str(status) + "\n")
            f.write(text + ("\n" if not text.endswith('\n') else ''))
            if err:
                f.write('STDERR:\n' + err + "\n")
    print('Saved report to admin_login_debug.txt')
    # Print summary lines
    for title, cmd, status, text, err in out:
        print('\n' + title + ':')
        first = text.strip().split('\n')[:8]
        for line in first:
            print('  ' + line)
        if not text.strip():
            print('  (no output)')
finally:
    ssh.close()

