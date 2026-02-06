"""
Custom validators for the Airport Management System.

Provides validation functions for phone numbers, passport numbers,
airline codes, airport codes, and other domain-specific fields.
"""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_phone_number(value):
    """
    Validate phone number format.

    Accepts international format with country code (e.g., +234 for Nigeria)
    or local Nigerian format.
    """
    # Remove spaces, dashes, and parentheses for validation
    cleaned = re.sub(r"[\s\-\(\)]", "", value)

    # Nigerian phone pattern: +234XXXXXXXXXX or 0XXXXXXXXXX
    nigerian_pattern = r"^(\+234|0)[789][01]\d{8}$"

    # International pattern: + followed by 7-15 digits
    international_pattern = r"^\+\d{7,15}$"

    if not (re.match(nigerian_pattern, cleaned) or re.match(international_pattern, cleaned)):
        raise ValidationError(
            _("Enter a valid phone number. Nigerian format: +234XXXXXXXXXX or 0XXXXXXXXXX"),
            code="invalid_phone",
        )


def validate_passport_number(value):
    """
    Validate passport number format.

    Nigerian passports: A followed by 8 digits (e.g., A12345678)
    Also accepts international formats (alphanumeric, 6-9 characters).
    """
    # Nigerian passport pattern
    nigerian_pattern = r"^[A-Z]\d{8}$"

    # General international passport pattern
    international_pattern = r"^[A-Z0-9]{6,9}$"

    value_upper = value.upper()
    if not (re.match(nigerian_pattern, value_upper) or re.match(international_pattern, value_upper)):
        raise ValidationError(
            _("Enter a valid passport number (6-9 alphanumeric characters)"),
            code="invalid_passport",
        )


def validate_airline_code(value):
    """
    Validate IATA airline code format.

    IATA airline codes are 2 characters (letters or letters + digit).
    Examples: BA (British Airways), W3 (Arik Air), P4 (Air Peace)
    """
    pattern = r"^[A-Z0-9]{2}$"
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Enter a valid 2-character IATA airline code (e.g., BA, W3)"),
            code="invalid_airline_code",
        )


def validate_airport_code(value):
    """
    Validate IATA airport code format.

    IATA airport codes are exactly 3 uppercase letters.
    Examples: ABV (Abuja), LOS (Lagos), LHR (London Heathrow)
    """
    pattern = r"^[A-Z]{3}$"
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Enter a valid 3-letter IATA airport code (e.g., ABV, LOS, LHR)"),
            code="invalid_airport_code",
        )


def validate_flight_number(value):
    """
    Validate flight number format.

    Flight numbers consist of airline code (2 chars) + flight number (1-4 digits).
    Examples: W3101 (Arik Air), BA75 (British Airways)
    """
    pattern = r"^[A-Z0-9]{2}\d{1,4}$"
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Enter a valid flight number (e.g., W3101, BA75)"),
            code="invalid_flight_number",
        )


def validate_aircraft_registration(value):
    """
    Validate aircraft registration number format.

    Nigerian registrations: 5N-XXX (5N- followed by 3 alphanumeric)
    International: Country code + alphanumeric (varies by country)
    """
    # Nigerian pattern
    nigerian_pattern = r"^5N-[A-Z]{3}$"

    # General international pattern (allows common formats)
    international_pattern = r"^[A-Z0-9]{1,2}-[A-Z0-9]{3,5}$"

    value_upper = value.upper()
    if not (re.match(nigerian_pattern, value_upper) or re.match(international_pattern, value_upper)):
        raise ValidationError(
            _("Enter a valid aircraft registration (e.g., 5N-ABC for Nigerian)"),
            code="invalid_registration",
        )


def validate_seat_number(value):
    """
    Validate seat number format.

    Seat numbers consist of row number (1-99) + seat letter (A-K).
    Examples: 12A, 1F, 35K
    """
    pattern = r"^\d{1,2}[A-K]$"
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Enter a valid seat number (e.g., 12A, 1F)"),
            code="invalid_seat",
        )


def validate_booking_reference(value):
    """
    Validate booking reference format.

    Booking references are 6 alphanumeric characters (uppercase).
    Example: ABC123
    """
    pattern = r"^[A-Z0-9]{6}$"
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _("Booking reference must be 6 alphanumeric characters"),
            code="invalid_booking_reference",
        )


def validate_positive_decimal(value):
    """
    Validate that a decimal value is positive.
    """
    if value <= 0:
        raise ValidationError(
            _("Value must be greater than zero"),
            code="invalid_positive_decimal",
        )
