# Gunicorn production defaults for Linux servers
import os

# Binding
bind = os.getenv('GUNICORN_BIND', '127.0.0.1:5000')

# Worker configuration
workers = int(os.getenv('GUNICORN_WORKERS', 4))  # Production default: 4 workers
worker_class = 'sync'  # Sync workers for compatibility
threads = int(os.getenv('GUNICORN_THREADS', 2))
max_requests = 1000  # Restart worker after 1000 requests to prevent memory leaks
max_requests_jitter = 100  # Add randomness to prevent thundering herd

# Timeouts
timeout = 120  # 2 minutes for long-running operations
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', '-')  # stdout
errorlog = os.getenv('GUNICORN_ERROR_LOG', '-')  # stderr
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'alumniconnect'

# Server mechanics
daemon = False  # Let systemd manage daemonization
pidfile = None
umask = 0
user = None
group = None

# Server socket
backlog = 2048
preload_app = True  # Load app before spawning workers (better for memory)
