"""
Security utilities for the Airport Management System.

Provides input validation, sanitization, and security checks.
"""

import html
import re
from functools import wraps

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseForbidden


# ============================================================================
# Input Sanitization
# ============================================================================

def sanitize_html(text):
    """
    Escape HTML entities to prevent XSS.

    Args:
        text: Input text to sanitize

    Returns:
        str: Sanitized text with HTML entities escaped
    """
    if not text:
        return text
    return html.escape(str(text))


def sanitize_sql(text):
    """
    Remove potential SQL injection characters.

    Args:
        text: Input text to sanitize

    Returns:
        str: Sanitized text
    """
    if not text:
        return text

    # Remove common SQL injection patterns
    dangerous_patterns = [
        r"--",
        r";",
        r"'",
        r'"',
        r"\*",
        r"xp_",
        r"UNION",
        r"SELECT",
        r"INSERT",
        r"UPDATE",
        r"DELETE",
        r"DROP",
        r"EXEC",
    ]

    result = str(text)
    for pattern in dangerous_patterns:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)

    return result


def sanitize_filename(filename):
    """
    Sanitize a filename to prevent path traversal.

    Args:
        filename: Original filename

    Returns:
        str: Safe filename
    """
    if not filename:
        return filename

    # Remove path separators and special characters
    filename = re.sub(r'[/\\:*?"<>|]', '', filename)

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')

    return filename


# ============================================================================
# Validation Functions
# ============================================================================

def validate_email_domain(email, allowed_domains=None, blocked_domains=None):
    """
    Validate email domain against allowed/blocked lists.

    Args:
        email: Email address to validate
        allowed_domains: List of allowed domains (if set, only these are allowed)
        blocked_domains: List of blocked domains

    Returns:
        bool: True if valid, False otherwise
    """
    if not email or '@' not in email:
        return False

    domain = email.split('@')[1].lower()

    if allowed_domains:
        return domain in [d.lower() for d in allowed_domains]

    if blocked_domains:
        return domain not in [d.lower() for d in blocked_domains]

    return True


def validate_phone_number(phone, country_code="NG"):
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate
        country_code: Country code for validation rules

    Returns:
        bool: True if valid, False otherwise
    """
    if not phone:
        return False

    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    if country_code == "NG":
        # Nigerian phone numbers
        patterns = [
            r'^\+234[789][01]\d{8}$',  # +234 format
            r'^234[789][01]\d{8}$',     # 234 format
            r'^0[789][01]\d{8}$',       # Local format
        ]
    else:
        # Generic international format
        patterns = [
            r'^\+\d{10,15}$',
        ]

    return any(re.match(pattern, cleaned) for pattern in patterns)


def validate_passport_number(passport_number, country="NG"):
    """
    Validate passport number format.

    Args:
        passport_number: Passport number to validate
        country: Country code for validation rules

    Returns:
        bool: True if valid, False otherwise
    """
    if not passport_number:
        return False

    # Remove spaces
    cleaned = passport_number.replace(' ', '').upper()

    if country == "NG":
        # Nigerian passport: 1 letter + 8 digits OR 9 alphanumeric
        patterns = [
            r'^[A-Z]\d{8}$',
            r'^[A-Z0-9]{9}$',
        ]
    else:
        # Generic: 6-9 alphanumeric characters
        patterns = [
            r'^[A-Z0-9]{6,9}$',
        ]

    return any(re.match(pattern, cleaned) for pattern in patterns)


# ============================================================================
# Security Decorators
# ============================================================================

def require_https(view_func):
    """
    Decorator to require HTTPS for a view.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.is_secure() and not request.META.get('HTTP_X_FORWARDED_PROTO') == 'https':
            if not request.get_host().startswith('localhost') and not request.get_host().startswith('127.0.0.1'):
                return HttpResponseForbidden("HTTPS required for this endpoint.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_staff(view_func):
    """
    Decorator to require staff status.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied("Staff access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def require_owner(model_class, lookup_field='pk'):
    """
    Decorator to require object ownership.

    Args:
        model_class: The model class to check ownership on
        lookup_field: The URL parameter containing the object ID
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            obj_id = kwargs.get(lookup_field)
            if obj_id:
                try:
                    obj = model_class.objects.get(pk=obj_id)
                    if hasattr(obj, 'user') and obj.user != request.user:
                        if not request.user.is_staff:
                            raise PermissionDenied("You don't have permission to access this resource.")
                except model_class.DoesNotExist:
                    pass
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# Security Checks
# ============================================================================

def check_suspicious_input(data):
    """
    Check input data for suspicious patterns.

    Args:
        data: Dictionary of input data

    Raises:
        SuspiciousOperation: If suspicious patterns are detected
    """
    suspicious_patterns = [
        r'<script[^>]*>',
        r'javascript:',
        r'on\w+\s*=',
        r'data:text/html',
        r'vbscript:',
    ]

    for key, value in data.items():
        if isinstance(value, str):
            for pattern in suspicious_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    raise SuspiciousOperation(
                        f"Suspicious input detected in field: {key}"
                    )


def log_security_event(event_type, user=None, ip=None, details=None):
    """
    Log a security event.

    Args:
        event_type: Type of security event
        user: User involved (if any)
        ip: IP address
        details: Additional details
    """
    import logging
    logger = logging.getLogger('security')

    message = f"SECURITY EVENT: {event_type}"
    if user:
        message += f" | User: {user}"
    if ip:
        message += f" | IP: {ip}"
    if details:
        message += f" | Details: {details}"

    logger.warning(message)


# ============================================================================
# Password Validation
# ============================================================================

def check_password_strength(password):
    """
    Check password strength.

    Args:
        password: Password to check

    Returns:
        tuple: (is_strong, list of issues)
    """
    issues = []

    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        issues.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        issues.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        issues.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        issues.append("Password must contain at least one special character")

    # Check for common patterns
    common_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'abc123',
    ]
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            issues.append("Password contains a common pattern")
            break

    return len(issues) == 0, issues
