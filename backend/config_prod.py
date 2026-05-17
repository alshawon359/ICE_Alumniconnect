"""
Production environment configuration.
Strict defaults: assume minimal trust, require explicit opt-in for everything.
"""
import os
from datetime import timedelta

# ============= APP RUNTIME =============
class ProductionConfig:
    """Production environment settings."""
    
    # Flask core
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY or len(SECRET_KEY) < 32:
        raise ValueError('SECRET_KEY must be set and at least 32 characters in production')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    # Allow empty CORS list in production - will be inferred from request origin
    # This is safe because: frontend is served from same domain, and explicit CORS headers are set by nginx
    if CORS_ORIGINS and len(CORS_ORIGINS) == 1 and CORS_ORIGINS[0] == '':
        CORS_ORIGINS = []
    
    # Server
    PORT = int(os.getenv('PORT', 5000))
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', '')
    # Allow HTTPS or HTTP (HTTP for reverse proxy scenarios where nginx handles SSL)
    # If PUBLIC_BASE_URL is not set, will be inferred from request headers
    if PUBLIC_BASE_URL and not (PUBLIC_BASE_URL.startswith('https://') or PUBLIC_BASE_URL.startswith('http://')):
        raise ValueError('PUBLIC_BASE_URL must start with https:// or http://')
    
    # ============= DATABASE =============
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        # Build from components
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = os.getenv('MYSQL_PORT', 3306)
        db = os.getenv('MYSQL_DB', 'alumniconnect')
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
    
    SQLALCHEMY_ECHO = False  # No query logging in production
    SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', 10))
    SQLALCHEMY_POOL_RECYCLE = 3600  # Recycle connections every hour
    SQLALCHEMY_POOL_PRE_PING = True  # Test connections before using
    SQLALCHEMY_MAX_OVERFLOW = 20
    
    # ============= EMAIL (BREVO) =============
    MAIL_PROVIDER = 'brevo'
    BREVO_API_KEY = os.getenv('BREVO_API_KEY')
    BREVO_API_URL = 'https://api.brevo.com/v3/smtp/email'
    BREVO_TIMEOUT = 30
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'AlumniConnect')
    
    if not BREVO_API_KEY:
        raise ValueError('BREVO_API_KEY must be set in production')
    if not SMTP_FROM_EMAIL:
        raise ValueError('SMTP_FROM_EMAIL must be set in production')
    
    # ============= LOGGING =============
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/alumniconnect/app.log')
    LOG_ERROR_FILE = os.getenv('LOG_ERROR_FILE', '/var/log/alumniconnect/error.log')
    LOG_MAX_BYTES = 10485760  # 10 MB
    LOG_BACKUP_COUNT = 10
    
    # ============= RATE LIMITING =============
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # ============= SECURITY =============
    # Disable file upload to /tmp outside production
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max upload
    
    # ============= ADMIN =============
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
    ADMIN_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 days


class DevelopmentConfig:
    """Development environment settings (permissive for local work)."""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    PORT = int(os.getenv('PORT', 5000))
    PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL', 'http://localhost:5173')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost:3307/alumniconnect')
    SQLALCHEMY_ECHO = True  # Log queries in development
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_PRE_PING = True
    SQLALCHEMY_MAX_OVERFLOW = 10
    
    # Email
    MAIL_PROVIDER = os.getenv('MAIL_PROVIDER', 'local')
    BREVO_API_KEY = os.getenv('BREVO_API_KEY', '')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL', 'dev@localhost')
    SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'AlumniConnect Dev')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    LOG_ERROR_FILE = os.getenv('LOG_ERROR_FILE', './logs/error.log')
    LOG_MAX_BYTES = 5242880  # 5 MB
    LOG_BACKUP_COUNT = 5
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'
    
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024
    
    # Admin
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin')
    ADMIN_TOKEN_MAX_AGE = 30 * 24 * 60 * 60


class TestingConfig:
    """Testing environment settings."""
    
    DEBUG = True
    TESTING = True
    ENV = 'testing'
    
    SECRET_KEY = 'test-secret-key'
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    
    CORS_ORIGINS = ['http://localhost:3000']
    
    MAIL_PROVIDER = 'local'
    BREVO_API_KEY = ''
    SMTP_FROM_EMAIL = 'test@example.com'
    
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = None
    LOG_ERROR_FILE = None
    
    RATELIMIT_ENABLED = False
    
    ADMIN_USERNAME = 'test_admin'
    ADMIN_PASSWORD = 'test_password'


# Config selector
def get_config():
    """Get config based on APP_ENV environment variable."""
    env = os.getenv('APP_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
