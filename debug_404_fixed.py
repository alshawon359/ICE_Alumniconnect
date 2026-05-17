import paramiko

HOST = '172.30.240.39'
PORT = 36109
USER = 'root'
PASSWORD = 'ice26Dru26&4mD'

def execute_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    stdout.channel.recv_exit_status()
    return stdout.read().decode('utf-8', errors='ignore')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD, timeout=10)

print('Collecting debug info...')

debug_commands = [
    ('404 Errors from Nginx Error Log', 'tail -100 /var/log/nginx/error.log | grep -E "(404|error)" || echo "No errors"'),
    ('404 Errors from Access Log', 'tail -50 /var/log/nginx/access.log | grep " 404 " || echo "No 404s"'),
    ('Frontend Directory', 'ls -la /var/www/html/iceaa/ 2>&1'),
    ('React App Build', 'ls -la /var/www/html/iceaa/react-app/ 2>&1 | head -15'),
    ('Backend Status', 'systemctl status alumniconnect --no-pager 2>&1 | head -20'),
    ('Backend Logs - Last 20 errors', 'journalctl -u alumniconnect -n 50 --no-pager 2>&1 | grep -i error || echo "No errors in logs"'),
    ('Backend Health Endpoint', 'curl -s -H "X-Forwarded-Proto: https" http://127.0.0.1:5000/api/health 2>&1'),
    ('Nginx Config - /iceaa location', 'grep -A 20 "location /iceaa" /etc/nginx/sites-enabled/* 2>/dev/null || grep -A 20 "location /iceaa" /etc/nginx/conf.d/* 2>/dev/null'),
    ('Git Status', 'cd /var/www/html/iceaa/ICE_AlumniConnect && git status --short'),
    ('Index.html exists', 'test -f /var/www/html/iceaa/react-app/dist/index.html && echo "EXISTS" || echo "MISSING"'),
    ('React dist files', 'ls -la /var/www/html/iceaa/react-app/dist/ 2>&1 | head -20'),
]

local_path = './debug_404_report.txt'

with open(local_path, 'w', encoding='utf-8') as f:
    f.write('='*70 + '\n')
    f.write('AlumniConnect 404 Debug Report\n')
    f.write('='*70 + '\n\n')
    
    for title, cmd in debug_commands:
        f.write('\n' + '='*70 + '\n')
        f.write(title + '\n')
        f.write('='*70 + '\n')
        f.write('$ ' + cmd + '\n')
        f.write('-'*70 + '\n')
        output = execute_command(ssh, cmd)
        f.write(output[:2000] + ('\n... (truncated)' if len(output) > 2000 else ''))
        f.write('\n')

print('Report saved to ' + local_path)

ssh.close()

with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    print('\n' + content)
