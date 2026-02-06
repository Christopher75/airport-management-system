"""
Custom middleware for the Airport Management System.

Provides performance monitoring, security headers, and request processing.
"""

import logging
import time

from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor request performance.

    Logs slow requests and adds timing headers in debug mode.
    """

    # Threshold for slow request warning (in seconds)
    SLOW_REQUEST_THRESHOLD = 1.0

    def process_request(self, request):
        """Record request start time."""
        request._start_time = time.time()

    def process_response(self, request, response):
        """Calculate request duration and log if slow."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time

            # Add timing header in debug mode
            if settings.DEBUG:
                response['X-Request-Duration'] = f"{duration:.3f}s"

            # Log slow requests
            if duration > self.SLOW_REQUEST_THRESHOLD:
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.3f}s"
                )

            # Log all requests in debug mode
            if settings.DEBUG:
                logger.debug(
                    f"{request.method} {request.path} - {response.status_code} "
                    f"({duration:.3f}s)"
                )

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """

    def process_response(self, request, response):
        """Add security headers."""
        # Skip CSP in development to avoid blocking CDN resources
        # In production, configure CSP properly via web server (nginx/apache)
        # if not response.has_header('Content-Security-Policy'):
        #     csp = (
        #         "default-src 'self'; "
        #         "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://unpkg.com https://js.paystack.co; "
        #         "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
        #         "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        #         "img-src 'self' data: https:; "
        #         "connect-src 'self' https://api.paystack.co; "
        #         "frame-src 'self' https://checkout.paystack.com; "
        #     )
        #     response['Content-Security-Policy'] = csp

        # Prevent content type sniffing
        if not response.has_header('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'

        # XSS Protection (legacy, but still useful)
        if not response.has_header('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'

        # Referrer Policy
        if not response.has_header('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy (formerly Feature-Policy)
        if not response.has_header('Permissions-Policy'):
            response['Permissions-Policy'] = (
                "accelerometer=(), camera=(), geolocation=(), "
                "gyroscope=(), magnetometer=(), microphone=(), "
                "payment=(self), usb=()"
            )

        return response


class RequestThrottlingMiddleware(MiddlewareMixin):
    """
    Simple IP-based request throttling middleware.

    Limits the number of requests from a single IP.
    """

    # Requests per minute limit
    RATE_LIMIT = 100
    RATE_WINDOW = 60  # seconds

    def process_request(self, request):
        """Check if request should be throttled."""
        # Skip for authenticated users and static files
        if request.user.is_authenticated:
            return None
        if request.path.startswith(('/static/', '/media/')):
            return None

        # Get client IP
        ip = self._get_client_ip(request)

        # Check rate limit using cache
        from django.core.cache import cache

        cache_key = f"throttle:{ip}"
        request_count = cache.get(cache_key, 0)

        if request_count >= self.RATE_LIMIT:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return HttpResponseForbidden(
                "Rate limit exceeded. Please try again later."
            )

        # Increment counter
        cache.set(cache_key, request_count + 1, self.RATE_WINDOW)

        return None

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to enable maintenance mode.

    When enabled, shows a maintenance page to all non-staff users.
    """

    def process_request(self, request):
        """Check if maintenance mode is enabled."""
        from django.shortcuts import render

        # Check if maintenance mode is enabled in settings or cache
        from django.core.cache import cache

        maintenance_mode = cache.get('maintenance_mode', False)

        if maintenance_mode:
            # Allow staff users and admin pages
            if request.user.is_staff or request.path.startswith('/admin/'):
                return None

            # Show maintenance page
            return render(request, 'maintenance.html', status=503)

        return None
