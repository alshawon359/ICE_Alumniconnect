"""
Request validation and input sanitization for security.
Prevents injection attacks and enforces data constraints.
"""
import re
import logging
from html import escape
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation error with HTTP status code."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def sanitize_string(value, max_length=None, allow_html=False):
    """
    Sanitize string input.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_html: Allow HTML (will escape if False)
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        raise ValidationError(f'Expected string, got {type(value).__name__}')
    
    # Strip whitespace
    value = value.strip()
    
    # Check length
    if max_length and len(value) > max_length:
        raise ValidationError(f'String exceeds maximum length of {max_length}')
    
    # Escape HTML unless explicitly allowed
    if not allow_html:
        value = escape(value)
    
    return value


def sanitize_email(value):
    """
    Validate and sanitize email address.
    
    Args:
        value: Email address
    
    Returns:
        Sanitized email
    """
    value = sanitize_string(value, max_length=254)
    
    # Basic email regex (RFC 5322 simplified)
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError('Invalid email address')
    
    return value.lower()


def sanitize_phone(value):
    """
    Validate and sanitize phone number.
    
    Args:
        value: Phone number
    
    Returns:
        Sanitized phone (digits only)
    """
    value = sanitize_string(value, max_length=20)
    
    # Remove non-digit characters
    digits_only = re.sub(r'\D', '', value)
    
    # Check length (min 7 digits, max 15 digits)
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValidationError('Invalid phone number format')
    
    return digits_only


def sanitize_integer(value, min_val=None, max_val=None):
    """
    Validate and sanitize integer input.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
    
    Returns:
        Integer value
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError('Expected integer value')
    
    if min_val is not None and value < min_val:
        raise ValidationError(f'Value must be >= {min_val}')
    
    if max_val is not None and value > max_val:
        raise ValidationError(f'Value must be <= {max_val}')
    
    return value


def sanitize_url(value):
    """
    Validate and sanitize URL.
    Prevents javascript: and data: URIs.
    
    Args:
        value: URL to sanitize
    
    Returns:
        Sanitized URL
    """
    value = sanitize_string(value, max_length=2048)
    
    # Block dangerous protocols
    dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
    lower_value = value.lower()
    
    for protocol in dangerous_protocols:
        if lower_value.startswith(protocol):
            raise ValidationError('Invalid URL protocol')
    
    return value


def validate_request_json(*required_fields):
    """
    Decorator to validate JSON request body.
    
    Usage:
        @app.route('/api/users', methods=['POST'])
        @validate_request_json('name', 'email')
        def create_user():
            data = request.json
            # data is guaranteed to have 'name' and 'email'
    
    Args:
        *required_fields: Field names that must be present
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json(silent=True)
            if data is None:
                return jsonify({
                    'success': False,
                    'message': 'Invalid JSON'
                }), 400
            
            # Check required fields
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'Missing required field: {field}'
                    }), 400
                
                if data[field] is None:
                    return jsonify({
                        'success': False,
                        'message': f'Field cannot be null: {field}'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_pagination(max_limit=100):
    """
    Decorator to validate pagination parameters.
    
    Ensures 'page' and 'limit' are valid integers.
    
    Args:
        max_limit: Maximum allowed limit
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                page = sanitize_integer(
                    request.args.get('page', 1),
                    min_val=1
                )
                limit = sanitize_integer(
                    request.args.get('limit', 20),
                    min_val=1,
                    max_val=max_limit
                )
                
                # Store in request context
                request.pagination = {'page': page, 'limit': limit}
            except ValidationError as e:
                return jsonify({
                    'success': False,
                    'message': e.message
                }), e.status_code
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# SQL injection prevention helpers
def prevent_sql_injection(value):
    """
    Helper to check for obvious SQL injection attempts.
    Note: Always use parameterized queries instead of string formatting.
    
    Args:
        value: Value to check
    
    Returns:
        Boolean indicating if value might be SQL injection
    """
    if not isinstance(value, str):
        return False
    
    # Check for common SQL keywords in suspicious patterns
    injection_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bOR\b.*=.*)",
        r"(\bDROP\b.*\b)",
        r"(\bINSERT\b.*\bVALUES\b)",
        r"(\bDELETE\b.*\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(';.*--)",
        r'(";.*--)',
    ]
    
    lower_value = value.lower()
    for pattern in injection_patterns:
        if re.search(pattern, lower_value, re.IGNORECASE):
            return True
    
    return False
