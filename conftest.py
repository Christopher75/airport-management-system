"""
Pytest configuration and fixtures for the NAIA Airport Management System.

This file contains shared fixtures used across all test modules.
"""

import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.test import Client
from rest_framework.test import APIClient


# ============================================================================
# User Fixtures
# ============================================================================

@pytest.fixture
def user_password():
    """Common password for test users."""
    return "TestPass123!"


@pytest.fixture
def user(db, user_password):
    """Create a regular user for testing."""
    from accounts.models import CustomUser
    user = CustomUser.objects.create_user(
        email="testuser@example.com",
        password=user_password,
        first_name="Test",
        last_name="User"
    )
    return user


@pytest.fixture
def staff_user(db, user_password):
    """Create a staff user for testing."""
    from accounts.models import CustomUser
    user = CustomUser.objects.create_user(
        email="staff@example.com",
        password=user_password,
        first_name="Staff",
        last_name="User",
        is_staff=True
    )
    return user


@pytest.fixture
def admin_user(db, user_password):
    """Create an admin user for testing."""
    from accounts.models import CustomUser
    user = CustomUser.objects.create_superuser(
        email="admin@example.com",
        password=user_password,
        first_name="Admin",
        last_name="User"
    )
    return user


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, user, user_password):
    """Authenticated Django test client."""
    client.login(email=user.email, password=user_password)
    return client


@pytest.fixture
def staff_client(client, staff_user, user_password):
    """Authenticated staff client."""
    client.login(email=staff_user.email, password=user_password)
    return client


@pytest.fixture
def api_client():
    """DRF API test client."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Authenticated DRF API test client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def staff_api_client(api_client, staff_user):
    """Staff authenticated DRF API test client."""
    api_client.force_authenticate(user=staff_user)
    return api_client


# ============================================================================
# Airport & Airline Fixtures
# ============================================================================

@pytest.fixture
def airport_abuja(db):
    """Create Abuja airport."""
    from flights.models import Airport
    return Airport.objects.create(
        code="ABV",
        name="Nnamdi Azikiwe International Airport",
        city="Abuja",
        country="Nigeria",
        timezone="Africa/Lagos",
        is_active=True
    )


@pytest.fixture
def airport_lagos(db):
    """Create Lagos airport."""
    from flights.models import Airport
    return Airport.objects.create(
        code="LOS",
        name="Murtala Muhammed International Airport",
        city="Lagos",
        country="Nigeria",
        timezone="Africa/Lagos",
        is_active=True
    )


@pytest.fixture
def airport_london(db):
    """Create London Heathrow airport."""
    from flights.models import Airport
    return Airport.objects.create(
        code="LHR",
        name="London Heathrow Airport",
        city="London",
        country="United Kingdom",
        timezone="Europe/London",
        is_active=True
    )


@pytest.fixture
def airline(db):
    """Create a test airline."""
    from airlines.models import Airline
    return Airline.objects.create(
        name="Air Peace",
        code="P4",
        country="Nigeria",
        is_active=True
    )


@pytest.fixture
def aircraft(db, airline):
    """Create a test aircraft."""
    from airlines.models import Aircraft
    return Aircraft.objects.create(
        airline=airline,
        registration="5N-BUK",
        aircraft_type="B738",  # Boeing 737-800 code
        total_seats=189,
        economy_class_seats=165,
        business_class_seats=24,
        first_class_seats=0,
        is_active=True
    )


# ============================================================================
# Flight Fixtures
# ============================================================================

@pytest.fixture
def flight(db, airline, aircraft, airport_abuja, airport_lagos):
    """Create a test flight."""
    from flights.models import Flight, FlightStatus
    departure_time = timezone.now() + timedelta(days=7)
    arrival_time = departure_time + timedelta(hours=1, minutes=15)

    return Flight.objects.create(
        flight_number="P4101",
        airline=airline,
        aircraft=aircraft,
        origin=airport_abuja,
        destination=airport_lagos,
        scheduled_departure=departure_time,
        scheduled_arrival=arrival_time,
        status=FlightStatus.SCHEDULED,
        economy_price=Decimal("35000.00"),
        business_price=Decimal("85000.00"),
        first_class_price=Decimal("150000.00"),
        available_economy_seats=130,
        available_business_seats=20,
        available_first_class_seats=0
    )


@pytest.fixture
def international_flight(db, airline, aircraft, airport_lagos, airport_london):
    """Create an international test flight."""
    from flights.models import Flight, FlightStatus
    departure_time = timezone.now() + timedelta(days=14)
    arrival_time = departure_time + timedelta(hours=6, minutes=30)

    return Flight.objects.create(
        flight_number="P4501",
        airline=airline,
        aircraft=aircraft,
        origin=airport_lagos,
        destination=airport_london,
        scheduled_departure=departure_time,
        scheduled_arrival=arrival_time,
        status=FlightStatus.SCHEDULED,
        economy_price=Decimal("450000.00"),
        business_price=Decimal("1200000.00"),
        first_class_price=Decimal("2500000.00"),
        available_economy_seats=80,
        available_business_seats=15,
        available_first_class_seats=5,
        is_international=True
    )


# ============================================================================
# Booking Fixtures
# ============================================================================

@pytest.fixture
def booking(db, user, flight):
    """Create a test booking."""
    from bookings.models import Booking, BookingStatus, SeatClass, generate_booking_reference

    return Booking.objects.create(
        reference=generate_booking_reference(),
        user=user,
        flight=flight,
        status=BookingStatus.CONFIRMED,
        seat_class=SeatClass.ECONOMY,
        contact_email=user.email,
        contact_phone="+2348012345678",
        base_price=Decimal("35000.00"),
        taxes=Decimal("3500.00"),
        fees=Decimal("2000.00"),
        total_price=Decimal("40500.00")
    )


@pytest.fixture
def passenger(db, booking):
    """Create a test passenger."""
    from bookings.models import Passenger

    return Passenger.objects.create(
        booking=booking,
        title="MR",
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-15",
        nationality="Nigerian",
        passport_number="A12345678",
        passport_expiry="2028-12-31"
    )


# ============================================================================
# Payment Fixtures
# ============================================================================

@pytest.fixture
def payment(db, booking, user):
    """Create a test payment."""
    from payments.models import Payment, PaymentStatus, PaymentMethod

    return Payment.objects.create(
        booking=booking,
        user=user,
        amount=booking.total_price,
        currency="NGN",
        status=PaymentStatus.COMPLETED,
        payment_method=PaymentMethod.CARD,
        paystack_reference=f"PAY-{booking.reference}"
    )


# ============================================================================
# Notification Fixtures
# ============================================================================

@pytest.fixture
def notification(db, user, booking):
    """Create a test notification."""
    from notifications.models import Notification, NotificationType

    return Notification.objects.create(
        user=user,
        notification_type=NotificationType.BOOKING_CONFIRMATION,
        title="Booking Confirmed",
        message=f"Your booking {booking.reference} has been confirmed.",
        is_read=False
    )


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def mock_paystack_response():
    """Mock Paystack API response."""
    return {
        "status": True,
        "message": "Authorization URL created",
        "data": {
            "authorization_url": "https://checkout.paystack.com/test123",
            "access_code": "test_access_code",
            "reference": "test_reference_123"
        }
    }


@pytest.fixture
def mock_paystack_verify_response():
    """Mock Paystack verification response."""
    return {
        "status": True,
        "message": "Verification successful",
        "data": {
            "status": "success",
            "reference": "test_reference_123",
            "amount": 4050000,  # Amount in kobo
            "currency": "NGN",
            "paid_at": "2024-01-15T10:30:00.000Z"
        }
    }
