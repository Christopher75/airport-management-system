"""
Caching utilities for the Airport Management System.

Provides caching decorators and helpers for optimizing performance.
"""

import hashlib
import json
from functools import wraps

from django.core.cache import cache
from django.conf import settings


# Cache timeout constants (in seconds)
CACHE_SHORT = 60  # 1 minute
CACHE_MEDIUM = 300  # 5 minutes
CACHE_LONG = 3600  # 1 hour
CACHE_DAY = 86400  # 24 hours


def make_cache_key(prefix, *args, **kwargs):
    """
    Generate a cache key from prefix and arguments.

    Args:
        prefix: Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key

    Returns:
        str: Cache key
    """
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
    return f"{prefix}:{key_hash}"


def cache_result(timeout=CACHE_MEDIUM, key_prefix=None):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds
        key_prefix: Custom key prefix (defaults to function name)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or f"func:{func.__module__}.{func.__name__}"
            cache_key = make_cache_key(prefix, *args, **kwargs)

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern):
    """
    Invalidate cache keys matching a pattern.

    Note: This is a simple implementation. For Redis, use delete_pattern.

    Args:
        pattern: Key pattern to invalidate
    """
    # For Redis backend
    if hasattr(cache, 'delete_pattern'):
        cache.delete_pattern(pattern)
    else:
        # For other backends, we need to track keys manually
        pass


class CacheManager:
    """
    Manages cache for different model types.
    """

    # Cache key prefixes
    AIRPORT_LIST = "airports:list"
    AIRPORT_DETAIL = "airports:detail"
    AIRLINE_LIST = "airlines:list"
    FLIGHT_LIST = "flights:list"
    FLIGHT_DETAIL = "flights:detail"
    FLIGHT_STATUS = "flights:status"

    @classmethod
    def get_airports(cls):
        """Get cached list of active airports."""
        from flights.models import Airport

        result = cache.get(cls.AIRPORT_LIST)
        if result is None:
            result = list(
                Airport.objects.filter(is_active=True).values(
                    "id", "code", "name", "city", "country"
                ).order_by("name")
            )
            cache.set(cls.AIRPORT_LIST, result, CACHE_LONG)
        return result

    @classmethod
    def get_airlines(cls):
        """Get cached list of active airlines."""
        from airlines.models import Airline

        result = cache.get(cls.AIRLINE_LIST)
        if result is None:
            result = list(
                Airline.objects.filter(is_active=True).values(
                    "id", "code", "name", "country"
                ).order_by("name")
            )
            cache.set(cls.AIRLINE_LIST, result, CACHE_LONG)
        return result

    @classmethod
    def get_flight_detail(cls, flight_id):
        """Get cached flight details."""
        from flights.models import Flight

        cache_key = f"{cls.FLIGHT_DETAIL}:{flight_id}"
        result = cache.get(cache_key)

        if result is None:
            try:
                flight = Flight.objects.select_related(
                    "airline", "origin", "destination", "aircraft"
                ).get(pk=flight_id)
                result = {
                    "id": flight.id,
                    "flight_number": flight.flight_number,
                    "airline": flight.airline.name,
                    "origin": flight.origin.code,
                    "destination": flight.destination.code,
                    "scheduled_departure": flight.scheduled_departure.isoformat(),
                    "scheduled_arrival": flight.scheduled_arrival.isoformat(),
                    "status": flight.status,
                }
                cache.set(cache_key, result, CACHE_SHORT)
            except Flight.DoesNotExist:
                result = None

        return result

    @classmethod
    def invalidate_flight(cls, flight_id):
        """Invalidate cached flight data."""
        cache.delete(f"{cls.FLIGHT_DETAIL}:{flight_id}")

    @classmethod
    def invalidate_airports(cls):
        """Invalidate airports cache."""
        cache.delete(cls.AIRPORT_LIST)

    @classmethod
    def invalidate_airlines(cls):
        """Invalidate airlines cache."""
        cache.delete(cls.AIRLINE_LIST)


def cache_page_for_user(timeout=CACHE_MEDIUM):
    """
    Cache decorator for views that vary by user.

    Caches the response for each user separately.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Don't cache for staff users
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)

            # Create cache key based on user and path
            user_id = request.user.id if request.user.is_authenticated else "anon"
            cache_key = f"view:{request.path}:user:{user_id}"

            response = cache.get(cache_key)
            if response is None:
                response = view_func(request, *args, **kwargs)
                if hasattr(response, 'render'):
                    response.render()
                cache.set(cache_key, response, timeout)

            return response
        return wrapper
    return decorator
