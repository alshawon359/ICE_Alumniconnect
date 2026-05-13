"""
Flask Application Factory
Creates and configures Flask app with all production features.
Enables modularity, testability, and clean configuration management.

This factory pattern provides:
- Proper configuration management (dev/prod/test)
- Logging system setup
- Security headers
- Error handlers
- Rate limiting
"""
import os
import logging
from dotenv import load_dotenv


# Load environment variables with proper precedence
def load_env_variables():
    """Load env variables with proper precedence."""
    env_files = [
        os.path.join(os.path.dirname(__file__), '.env.production'),
        os.path.join(os.path.dirname(__file__), '.env.local'),
        os.path.join(os.path.dirname(__file__), '.env'),
    ]
    
    for env_file in env_files:
        if os.path.exists(env_file):
            load_dotenv(env_file, override=True)
            break


def create_app(config_name=None):
    """
    Create and configure Flask application.
    
    Wraps the existing app.py with factory pattern and production features.
    
    Args:
        config_name: 'development', 'production', or 'testing'
                   If None, uses APP_ENV environment variable
    
    Returns:
        Configured Flask application
    """
    # Load environment variables first
    load_env_variables()
    
    # Determine config name
    if config_name is None:
        config_name = os.getenv('APP_ENV', 'development')
    
    # Set environment for subsequent imports
    os.environ['APP_ENV'] = config_name
    
    # Import config module
    from config_prod import get_config
    config = get_config()
    
    # Setup logging BEFORE importing app
    from logging_config import setup_logging
    logger = setup_logging(config)
    logger.info(f'Creating Flask app in {config_name} mode')
    
    # NOW import the existing app.py
    # This uses the config we just set up
    from app import app
    
    # Apply production config
    app.config.from_object(config)
    
    # Override CORS settings for production safety
    from flask_cors import CORS
    cors_origins = config.CORS_ORIGINS
    logger.info(f'CORS allowed origins: {cors_origins}')
    
    # Remove old CORS and apply new one
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Setup rate limiting
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=config.RATELIMIT_STORAGE_URL,
        default_limits=["200 per day", "50 per hour"],
    )
    
    # Register error handlers
    from error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Setup security headers (override app.py if it has any)
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        if config.ENV == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    logger.info(f'Flask app initialized successfully')
    
    return app
