import paramiko
import sys

HOST = "172.30.240.39"
PORT = 36109
USER = "root"
PASSWORD = "ice26Dru26&4mD"
APP_PATH = "/var/www/html/iceaa/ICE_AlumniConnect"
cmds = [
    ("Nginx access lines with admin-login", "grep -n 'admin-login' /var/log/nginx/access.log* 2>/dev/null || echo 'No matches in access logs'"),
    ("Nginx error lines with admin-login/404", r"grep -n 'admin-login\| 404 ' /var/log/nginx/error.log* 2>/dev/null || echo 'No matches in error logs'"),
    ("Recent 404s in access log", "tail -200 /var/log/nginx/access.log | grep ' 404 ' | tail -100 || echo 'No recent 404s'") ,
    ("Check /iceaa/admin-login (HTTPS local)", "curl -s -k -I https://localhost/iceaa/admin-login || true"),
    ("Check frontend index for /iceaa route", "curl -s -k -I https://localhost/iceaa/ | head -5"),
    ("Test backend API GET /api/admin-login (local)", "curl -s -H 'X-Forwarded-Proto: https' -I http://127.0.0.1:5000/api/admin-login || true"),
    ("Test backend API POST /api/admin-login (local)", "curl -s -H 'X-Forwarded-Proto: https' -d 'username=test&password=xx' -X POST -i http://127.0.0.1:5000/api/admin-login || true"),
    ("AlumniConnect service status", "systemctl status alumniconnect --no-pager || true"),
    ("AlumniConnect journal (last 200)", "journalctl -u alumniconnect -n 200 --no-pager || true"),
    ("Check backend routes in app.py", f"grep -n 'admin\\|admin-login\\|admin_login' -R {APP_PATH}/backend || true"),
    ("List react dist files", f"ls -la {APP_PATH}/react-app/dist || echo 'no dist'"),
    ("Nginx config snippets for /iceaa", "grep -R 'location /iceaa' /etc/nginx -n 2>/dev/null || true"),
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)
    print("Connected to server\n")

    report = []
    for title, cmd in cmds:
        print(f"--- {title} ---")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=20)
        exit_status = stdout.channel.recv_exit_status()
        out = stdout.read().decode('utf-8', errors='ignore')
        err = stderr.read().decode('utf-8', errors='ignore')
        if out.strip():
            print(out)
            report.append((title, out))
        if err.strip():
            print('STDERR:', err)
            report.append((title + ' (stderr)', err))
        print('\n')

    with open('admin_login_debug.txt', 'w', encoding='utf-8') as f:
        for title, content in report:
            f.write('='*60 + '\n')
            f.write(title + '\n')
            f.write('='*60 + '\n')
            f.write(content + '\n\n')

    sftp = ssh.open_sftp()
    try:
        sftp.get('/var/log/nginx/error.log', 'nginx_error.log')
    except Exception: pass
    try:
        sftp.get('/var/log/nginx/access.log', 'nginx_access.log')
    except Exception: pass
    sftp.close()
    print('Report saved to admin_login_debug.txt')
except Exception as e:
    print('Error:', e)
    sys.exit(1)
finally:
    ssh.close()
