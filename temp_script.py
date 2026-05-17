import paramiko

host = '172.30.240.39'
port = 36109
user = 'root'
password = 'ice26Dru26&4mD'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=port, username=user, password=password, timeout=10)

# Save to file with UTF-8 encoding
with open('remote_output.txt', 'w', encoding='utf-8') as f:
    # Command 1: journalctl
    f.write('=== JOURNALCTL OUTPUT ===\n')
    stdin, stdout, stderr = client.exec_command('sudo journalctl -u alumniconnect -n 100')
    f.write(stdout.read().decode('utf-8', errors='replace'))
    
    # Command 2: ps aux | grep gunicorn
    f.write('\n=== PS AUX | GREP GUNICORN OUTPUT ===\n')
    stdin, stdout, stderr = client.exec_command('ps aux | grep gunicorn')
    f.write(stdout.read().decode('utf-8', errors='replace'))

client.close()
print('Output saved to remote_output.txt')
