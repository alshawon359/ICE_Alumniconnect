import os
from urllib.parse import urlparse, unquote, parse_qs

try:
	from dotenv import load_dotenv
except Exception:
	load_dotenv = None


def _load_dotenv_file(path):
	if not os.path.exists(path):
		return

	with open(path, 'r', encoding='utf-8') as f:
		for raw_line in f:
			line = raw_line.strip()
			if not line or line.startswith('#') or '=' not in line:
				continue

			key, value = line.split('=', 1)
			key = key.strip()
			value = value.strip()

			# Remove matching single or double quotes from values.
			if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
				value = value[1:-1]

			if key in _EXTERNALLY_DEFINED_ENV_KEYS:
				continue
			os.environ[key] = value


_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
_BACKEND_DIR = os.path.dirname(__file__)
_EXTERNALLY_DEFINED_ENV_KEYS = set(os.environ.keys())
_DOTENV_PATHS = [
	os.path.join(_ROOT_DIR, '.env'),
	os.path.join(_ROOT_DIR, '.env.local'),
	os.path.join(_BACKEND_DIR, '.env'),
	os.path.join(_BACKEND_DIR, '.env.local'),
]

# Load local env files if present.
# Earlier files can be overridden by later files, but already-exported OS env vars win.
for _dotenv_path in _DOTENV_PATHS:
	if load_dotenv is not None:
		load_dotenv(_dotenv_path, override=False)
	_load_dotenv_file(_dotenv_path)


def _read_dotenv_value(key):
	value = None
	for _dotenv_path in _DOTENV_PATHS:
		if not os.path.exists(_dotenv_path):
			continue
		with open(_dotenv_path, 'r', encoding='utf-8') as f:
			for raw_line in f:
				line = raw_line.strip()
				if not line or line.startswith('#') or '=' not in line:
					continue
				current_key, current_value = line.split('=', 1)
				if current_key.strip() != key:
					continue
				current_value = current_value.strip()
				if len(current_value) >= 2 and current_value[0] == current_value[-1] and current_value[0] in {'"', "'"}:
					current_value = current_value[1:-1]
				value = current_value
	return value


def _as_bool(value, default=False):
	if value is None:
		return default
	return str(value).strip().lower() in {'1', 'true', 'yes', 'on'}


def _as_int(value, default):
	try:
		return int(value)
	except (TypeError, ValueError):
		return default


def _as_float(value, default):
	try:
		return float(value)
	except (TypeError, ValueError):
		return default


def _as_list(value, default=''):
	raw = value if value is not None else default
	return [item.strip() for item in str(raw).split(',') if item.strip()]


def _parse_mysql_url(url):
	if not url:
		return {}
	parsed = urlparse(url)
	if parsed.scheme not in {'mysql', 'mysql+pymysql'}:
		return {}
	query = parse_qs(parsed.query or '')

	ssl_mode = None
	for key in ('ssl-mode', 'ssl_mode', 'sslmode'):
		if query.get(key):
			ssl_mode = str(query[key][0]).strip().lower()
			break

	if ssl_mode is None and query.get('ssl'):
		raw_ssl = str(query['ssl'][0]).strip().lower()
		if raw_ssl in {'1', 'true', 'yes', 'required'}:
			ssl_mode = 'required'

	ssl_ca = None
	for key in ('ssl-ca', 'ssl_ca', 'sslca'):
		if query.get(key):
			ssl_ca = str(query[key][0]).strip()
			break

	return {
		'host': parsed.hostname,
		'port': parsed.port,
		'user': unquote(parsed.username) if parsed.username else None,
		'password': unquote(parsed.password) if parsed.password else None,
		'database': parsed.path.lstrip('/') if parsed.path else None,
		'ssl_mode': ssl_mode,
		'ssl_ca': ssl_ca,
	}


# App runtime
APP_ENV = (os.getenv('APP_ENV') or os.getenv('FLASK_ENV') or 'development').strip().lower()
DEBUG = _as_bool(os.getenv('DEBUG'), False)
PORT = _as_int(os.getenv('PORT'), 5000)
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
PUBLIC_BASE_URL = (os.getenv('PUBLIC_BASE_URL') or '').rstrip('/')

# CORS
_default_cors_origins = 'http://localhost:5173,http://127.0.0.1:5173' if APP_ENV != 'production' else ''
# Production-safe default: deny cross-origin requests unless explicitly configured.
# For local development, allow common Vite origins.
CORS_ORIGINS = _as_list(os.getenv('CORS_ORIGINS'), _default_cors_origins)

# Admin credentials
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')

# SMTP email configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = _as_int(os.getenv('SMTP_PORT'), 587)
SMTP_USE_TLS = _as_bool(os.getenv('SMTP_USE_TLS'), True)
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = (os.getenv('SMTP_PASSWORD', '') or '').replace(' ', '')
SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL') or SMTP_USERNAME
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'AlumniConnect Admin')
MAIL_REPLY_TO = os.getenv('MAIL_REPLY_TO', SMTP_FROM_EMAIL).strip()
MAIL_UNSUBSCRIBE_EMAIL = (os.getenv('MAIL_UNSUBSCRIBE_EMAIL') or SMTP_FROM_EMAIL).strip()
MAIL_UNSUBSCRIBE_URL = (os.getenv('MAIL_UNSUBSCRIBE_URL') or '').strip()
MAIL_BULK_TAG = (os.getenv('MAIL_BULK_TAG') or 'alumniconnect-broadcast').strip()
MAIL_LIST_ID = (os.getenv('MAIL_LIST_ID') or 'alumniconnect.ru.ac.bd').strip()
MAIL_FEEDBACK_ID = (os.getenv('MAIL_FEEDBACK_ID') or 'alumniconnect:transactional:ru.ac.bd').strip()
MAIL_FOOTER_TEXT = (os.getenv('MAIL_FOOTER_TEXT') or 'You are receiving this email because you are part of AlumniConnect communications.').strip()
MAIL_PROVIDER = (os.getenv('MAIL_PROVIDER') or 'auto').strip().lower()
BREVO_EMAIL = (os.getenv('BREVO_EMAIL') or SMTP_FROM_EMAIL).strip()
BREVO_API_KEY = (os.getenv('BREVO_API_KEY') or '').strip()
BREVO_API_URL = (os.getenv('BREVO_API_URL') or 'https://api.brevo.com/v3/smtp/email').strip()
BREVO_TIMEOUT = _as_int(os.getenv('BREVO_TIMEOUT'), 20)
BREVO_SMTP_HOST = (os.getenv('BREVO_SMTP_HOST') or 'smtp-relay.brevo.com').strip()
BREVO_SMTP_PORT = _as_int(os.getenv('BREVO_SMTP_PORT'), 587)
BREVO_SMTP_USE_TLS = _as_bool(os.getenv('BREVO_SMTP_USE_TLS'), True)

# Prefer Brevo settings from the workspace env files so a stale shell session cannot
# keep an outdated key alive after the .env file is updated.
SMTP_FROM_EMAIL = _read_dotenv_value('SMTP_FROM_EMAIL') or SMTP_FROM_EMAIL
SMTP_FROM_NAME = _read_dotenv_value('SMTP_FROM_NAME') or SMTP_FROM_NAME
MAIL_PROVIDER = (_read_dotenv_value('MAIL_PROVIDER') or MAIL_PROVIDER).strip().lower()
BREVO_EMAIL = (_read_dotenv_value('BREVO_EMAIL') or BREVO_EMAIL).strip()
BREVO_API_KEY = (_read_dotenv_value('BREVO_API_KEY') or BREVO_API_KEY).strip()
BREVO_API_URL = (_read_dotenv_value('BREVO_API_URL') or BREVO_API_URL).strip()
BREVO_TIMEOUT = _as_int(_read_dotenv_value('BREVO_TIMEOUT'), BREVO_TIMEOUT)
BREVO_SMTP_HOST = (_read_dotenv_value('BREVO_SMTP_HOST') or BREVO_SMTP_HOST).strip()
BREVO_SMTP_PORT = _as_int(_read_dotenv_value('BREVO_SMTP_PORT'), BREVO_SMTP_PORT)
BREVO_SMTP_USE_TLS = _as_bool(_read_dotenv_value('BREVO_SMTP_USE_TLS'), BREVO_SMTP_USE_TLS)
MAIL_FORCE_SMTP_DOMAINS = _as_list(os.getenv('MAIL_FORCE_SMTP_DOMAINS'), 'ru.ac.bd')
MAIL_PLAIN_ONLY_DOMAINS = _as_list(os.getenv('MAIL_PLAIN_ONLY_DOMAINS'), 'ru.ac.bd')

# MySQL configuration
MYSQL_URL = (
	os.getenv('MYSQL_URL')
	or os.getenv('DATABASE_URL')
	or os.getenv('AIVEN_MYSQL_URL')
	or os.getenv('AIVEN_SERVICE_URI')
	or os.getenv('AIVEN_URI')
)

MYSQL_HOST = os.getenv('MYSQL_HOST') or os.getenv('MYSQLHOST') or os.getenv('AIVEN_HOST') or '127.0.0.1'
MYSQL_USER = os.getenv('MYSQL_USER') or os.getenv('MYSQLUSER') or os.getenv('AIVEN_USER') or 'root'
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD') or os.getenv('MYSQLPASSWORD') or os.getenv('AIVEN_PASSWORD') or ''
MYSQL_DB = os.getenv('MYSQL_DB') or os.getenv('MYSQLDATABASE') or os.getenv('AIVEN_DB') or os.getenv('AIVEN_DATABASE') or 'alumniconnect'
MYSQL_PORT = _as_int(os.getenv('MYSQL_PORT') or os.getenv('MYSQLPORT') or os.getenv('AIVEN_PORT'), 3306)
MYSQL_SSL_MODE = (os.getenv('MYSQL_SSL_MODE') or '').strip().lower()
MYSQL_SSL_CA = (os.getenv('MYSQL_SSL_CA') or '').strip()
MYSQL_CONNECT_TIMEOUT = _as_int(os.getenv('MYSQL_CONNECT_TIMEOUT'), 10)
MYSQL_READ_TIMEOUT = _as_int(os.getenv('MYSQL_READ_TIMEOUT'), 30)
MYSQL_WRITE_TIMEOUT = _as_int(os.getenv('MYSQL_WRITE_TIMEOUT'), 30)
DB_CONNECT_RETRIES = _as_int(os.getenv('DB_CONNECT_RETRIES'), 5)
DB_RETRY_BASE_DELAY = _as_float(os.getenv('DB_RETRY_BASE_DELAY'), 0.6)
DB_RETRY_MAX_DELAY = _as_float(os.getenv('DB_RETRY_MAX_DELAY'), 8.0)

_parsed_mysql = _parse_mysql_url(MYSQL_URL)
if _parsed_mysql:
	MYSQL_HOST = _parsed_mysql.get('host') or MYSQL_HOST
	MYSQL_USER = _parsed_mysql.get('user') or MYSQL_USER
	MYSQL_PASSWORD = _parsed_mysql.get('password') if _parsed_mysql.get('password') is not None else MYSQL_PASSWORD
	MYSQL_DB = _parsed_mysql.get('database') or MYSQL_DB
	MYSQL_PORT = _parsed_mysql.get('port') or MYSQL_PORT
	if not MYSQL_SSL_MODE:
		MYSQL_SSL_MODE = _parsed_mysql.get('ssl_mode') or MYSQL_SSL_MODE
	if not MYSQL_SSL_CA:
		MYSQL_SSL_CA = _parsed_mysql.get('ssl_ca') or MYSQL_SSL_CA

# Auto-create database/tables from schema.sql on startup
AUTO_INIT_DB = _as_bool(os.getenv('AUTO_INIT_DB'), True)
