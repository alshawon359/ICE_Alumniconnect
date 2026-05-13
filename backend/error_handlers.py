"""
Global error handlers for production-safe responses.
All errors return JSON with no stack traces in production.
"""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(400)
    def bad_request(error):
        """400: Bad Request."""
        logger.warning(f'Bad request: {error.description}')
        return jsonify({
            'success': False,
            'message': error.description or 'Bad request',
            'code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401: Unauthorized."""
        logger.warning(f'Unauthorized access attempt: {error.description}')
        return jsonify({
            'success': False,
            'message': 'Unauthorized',
            'code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """403: Forbidden."""
        logger.warning(f'Forbidden access: {error.description}')
        return jsonify({
            'success': False,
            'message': 'Forbidden',
            'code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """404: Not Found."""
        logger.debug(f'Endpoint not found: {error.description}')
        return jsonify({
            'success': False,
            'message': 'Endpoint not found',
            'code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """405: Method Not Allowed."""
        logger.debug(f'Method not allowed: {error.description}')
        return jsonify({
            'success': False,
            'message': 'Method not allowed',
            'code': 405
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """413: Payload Too Large."""
        logger.warning(f'File too large: {error.description}')
        return jsonify({
            'success': False,
            'message': 'File too large (max 32 MB)',
            'code': 413
        }), 413
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """429: Too Many Requests."""
        logger.warning(f'Rate limit exceeded: {error.description}')
        return jsonify({
            'success': False,
            'message': 'Too many requests. Please try again later.',
            'code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """500: Internal Server Error (no details in production)."""
        logger.error(f'Internal server error: {error}', exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Internal server error. Please try again later.',
            'code': 500
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """502: Bad Gateway."""
        logger.error(f'Bad gateway: {error}')
        return jsonify({
            'success': False,
            'message': 'Service temporarily unavailable',
            'code': 502
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """503: Service Unavailable."""
        logger.error(f'Service unavailable: {error}')
        return jsonify({
            'success': False,
            'message': 'Service temporarily unavailable',
            'code': 503
        }), 503
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Catch-all handler for unhandled exceptions."""
        logger.error(f'Unhandled exception: {error}', exc_info=True)
        
        # If it's an HTTP exception, use its status code
        if isinstance(error, HTTPException):
            status_code = error.code
        else:
            status_code = 500
        
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again later.',
            'code': status_code
        }), status_code


class ValidationError(Exception):
    """Custom validation error."""
    def __init__(self, message, status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code


class AuthenticationError(Exception):
    """Custom authentication error."""
    def __init__(self, message='Authentication failed'):
        super().__init__()
        self.message = message
        self.status_code = 401


class DatabaseError(Exception):
    """Custom database error."""
    def __init__(self, message='Database operation failed'):
        super().__init__()
        self.message = message
        self.status_code = 500
