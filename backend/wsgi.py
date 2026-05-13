"""
WSGI entry point for production servers (Gunicorn).
Uses app factory pattern for proper configuration management.
"""
import os
from app_factory import create_app

# Create app with appropriate config
app_env = os.getenv('APP_ENV', 'development')
application = create_app(app_env)
