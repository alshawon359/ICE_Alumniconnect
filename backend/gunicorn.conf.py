# Gunicorn production defaults for Linux servers
bind = '127.0.0.1:5000'
workers = 2
threads = 2
timeout = 120
graceful_timeout = 30
keepalive = 5
accesslog = '-'
errorlog = '-'
loglevel = 'info'
