import paramiko
import sys

hostname = "172.30.240.39"
port = 36109
username = "root"
password = "ice26Dru26&4mD"

commands = [
    "sudo nginx -t",
    "echo '---NGINX TEST COMPLETE---'",
    "sudo systemctl reload nginx",
    "echo '---NGINX RELOAD COMPLETE---'",
    "sudo systemctl restart alumniconnect",
    "echo '---ALUMNICONNECT RESTART COMPLETE---'",
    "ps aux | grep -E 'nginx|gunicorn'",
    "echo '---PROCESS CHECK COMPLETE---'",
    "curl http://127.0.0.1:5000/api/"
]

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password, timeout=30)
    
    for cmd in commands:
        stdin, stdout, stderr = client.exec_command(cmd)
        print(f"$ {cmd}")
        output = stdout.read().decode()
        if output:
            print(output)
        error = stderr.read().decode()
        if error:
            print(f"ERROR: {error}")
        print()
    
    client.close()
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
