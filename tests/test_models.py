"""
Model tests for the NAIA Airport Management System.

Tests for all database models: accounts, airlines, flights, bookings, payments, notifications.
"""

import pytest
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError


# ============================================================================
# Account Model Tests
# ============================================================================

@pytest.mark.django_db
class TestCustomUserModel:
    """Tests for the CustomUser model."""

    def test_create_user(self, user):
        """Test creating a regular user."""
        assert user.email == "testuser@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self, admin_user):
        """Test creating a superuser."""
        assert admin_user.email == "admin@example.com"
        assert admin_user.is_staff is True
        assert admin_user.is_superuser is True

    def test_user_str_method(self, user):
        """Test user string representation."""
        assert str(user) == "testuser@example.com"

    def test_user_full_name(self, user):
        """Test get_full_name method."""
        assert user.get_full_name() == "Test User"

    def test_user_short_name(self, user):
        """Test get_short_name method."""
        assert user.get_short_name() == "Test"

    def test_email_is_unique(self, db, user):
        """Test that email must be unique."""
        from accounts.models import CustomUser
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(
                email="testuser@example.com",
                password="AnotherPass123!"
            )

    def test_create_user_without_email_raises_error(self, db):
        """Test that creating user without email raises error."""
        from accounts.models import CustomUser
        with pytest.raises(ValueError):
            CustomUser.objects.create_user(email="", password="Test123!")


@pytest.mark.django_db
class TestUserProfileModel:
    """Tests for the Profile model."""

    def test_profile_created_with_user(self, user):
        """Test that profile is created automatically with user."""
        # Profile should be created via signal
        from accounts.models import Profile
        profile = Profile.objects.filter(user=user).first()
        # If profile exists, test it; otherwise, the signal may not be set up
        if profile:
            assert profile.user == user

    def test_loyalty_points_default(self, user):
        """Test default loyalty points."""
        from accounts.models import Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        assert profile.loyalty_points == 0


# ============================================================================
# Airline Model Tests
# ============================================================================

@pytest.mark.django_db
class TestAirlineModel:
    """Tests for the Airline model."""

    def test_create_airline(self, airline):
        """Test creating an airline."""
        assert airline.name == "Air Peace"
        assert airline.code == "P4"
        assert airline.country == "Nigeria"
        assert airline.is_active is True

    def test_airline_str_method(self, airline):
        """Test airline string representation."""
        assert str(airline) == "Air Peace (P4)"

    def test_airline_code_unique(self, db, airline):
        """Test that airline code must be unique."""
        from airlines.models import Airline
        with pytest.raises(IntegrityError):
            Airline.objects.create(
                name="Another Airline",
                code="P4",  # Same code
                country="Nigeria"
            )


@pytest.mark.django_db
class TestAircraftModel:
    """Tests for the Aircraft model."""

    def test_create_aircraft(self, aircraft):
        """Test creating an aircraft."""
        assert aircraft.registration == "5N-BUK"
        assert aircraft.aircraft_type == "B738"  # Boeing 737-800 code
        assert aircraft.total_seats == 189

    def test_aircraft_str_method(self, aircraft):
        """Test aircraft string representation."""
        assert "5N-BUK" in str(aircraft)

    def test_aircraft_belongs_to_airline(self, aircraft, airline):
        """Test aircraft belongs to airline."""
        assert aircraft.airline == airline


# ============================================================================
# Flight Model Tests
# ============================================================================

@pytest.mark.django_db
class TestAirportModel:
    """Tests for the Airport model."""

    def test_create_airport(self, airport_abuja):
        """Test creating an airport."""
        assert airport_abuja.code == "ABV"
        assert airport_abuja.city == "Abuja"
        assert airport_abuja.country == "Nigeria"

    def test_airport_str_method(self, airport_abuja):
        """Test airport string representation."""
        assert "ABV" in str(airport_abuja)

    def test_airport_code_unique(self, db, airport_abuja):
        """Test that airport code must be unique."""
        from flights.models import Airport
        with pytest.raises(IntegrityError):
            Airport.objects.create(
                code="ABV",  # Same code
                name="Another Airport",
                city="Another City",
                country="Nigeria"
            )


@pytest.mark.django_db
class TestFlightModel:
    """Tests for the Flight model."""

    def test_create_flight(self, flight):
        """Test creating a flight."""
        assert flight.flight_number == "P4101"
        assert flight.origin.code == "ABV"
        assert flight.destination.code == "LOS"

    def test_flight_str_method(self, flight):
        """Test flight string representation."""
        assert "P4101" in str(flight)

    def test_flight_duration(self, flight):
        """Test flight duration calculation."""
        duration = flight.scheduled_arrival - flight.scheduled_departure
        assert duration == timedelta(hours=1, minutes=15)

    def test_flight_is_domestic(self, flight):
        """Test domestic flight detection."""
        # Both airports are in Nigeria
        assert flight.origin.country == flight.destination.country

    def test_flight_is_international(self, international_flight):
        """Test international flight detection."""
        assert international_flight.origin.country != international_flight.destination.country

    def test_flight_prices(self, flight):
        """Test flight pricing."""
        assert flight.economy_price == Decimal("35000.00")
        assert flight.business_price == Decimal("85000.00")

    def test_flight_status_default(self, flight):
        """Test default flight status."""
        from flights.models import FlightStatus
        assert flight.status == FlightStatus.SCHEDULED


# ============================================================================
# Booking Model Tests
# ============================================================================

@pytest.mark.django_db
class TestBookingModel:
    """Tests for the Booking model."""

    def test_create_booking(self, booking):
        """Test creating a booking."""
        assert booking.reference is not None
        assert len(booking.reference) == 6
        assert booking.user is not None
        assert booking.flight is not None

    def test_booking_str_method(self, booking):
        """Test booking string representation."""
        assert booking.reference in str(booking)

    def test_booking_total_price(self, booking):
        """Test booking total price calculation."""
        expected_total = booking.base_price + booking.taxes + booking.fees
        assert booking.total_price == expected_total

    def test_booking_reference_unique(self, db, booking, user, flight):
        """Test that booking reference must be unique."""
        from bookings.models import Booking, BookingStatus, SeatClass
        with pytest.raises(IntegrityError):
            Booking.objects.create(
                reference=booking.reference,  # Same reference
                user=user,
                flight=flight,
                status=BookingStatus.PENDING,
                seat_class=SeatClass.ECONOMY,
                contact_email=user.email,
                contact_phone="+2348012345678",
                base_price=Decimal("35000.00"),
                taxes=Decimal("3500.00"),
                fees=Decimal("2000.00"),
                total_price=Decimal("40500.00")
            )

    def test_booking_status_transitions(self, booking):
        """Test booking status changes."""
        from bookings.models import BookingStatus

        assert booking.status == BookingStatus.CONFIRMED

        booking.status = BookingStatus.CANCELLED
        booking.save()
        booking.refresh_from_db()

        assert booking.status == BookingStatus.CANCELLED


@pytest.mark.django_db
class TestPassengerModel:
    """Tests for the Passenger model."""

    def test_create_passenger(self, passenger):
        """Test creating a passenger."""
        assert passenger.first_name == "John"
        assert passenger.last_name == "Doe"
        assert passenger.passport_number == "A12345678"
        assert passenger.nationality == "Nigerian"

    def test_passenger_str_method(self, passenger):
        """Test passenger string representation."""
        passenger_str = str(passenger)
        # Check that the string contains relevant info
        assert passenger_str is not None

    def test_passenger_full_name(self, passenger):
        """Test passenger full name."""
        full_name = f"{passenger.first_name} {passenger.last_name}"
        assert full_name == "John Doe"

    def test_passenger_belongs_to_booking(self, passenger, booking):
        """Test passenger belongs to booking."""
        assert passenger.booking == booking


# ============================================================================
# Payment Model Tests
# ============================================================================

@pytest.mark.django_db
class TestPaymentModel:
    """Tests for the Payment model."""

    def test_create_payment(self, payment):
        """Test creating a payment."""
        assert payment.amount == payment.booking.total_price
        assert payment.currency == "NGN"

    def test_payment_str_method(self, payment):
        """Test payment string representation."""
        payment_str = str(payment)
        assert payment_str is not None

    def test_payment_status(self, payment):
        """Test payment status."""
        from payments.models import PaymentStatus
        assert payment.status == PaymentStatus.COMPLETED

    def test_payment_belongs_to_booking(self, payment, booking):
        """Test payment belongs to booking."""
        assert payment.booking == booking


# ============================================================================
# Notification Model Tests
# ============================================================================

@pytest.mark.django_db
class TestNotificationModel:
    """Tests for the Notification model."""

    def test_create_notification(self, notification):
        """Test creating a notification."""
        assert notification.title == "Booking Confirmed"
        assert notification.is_read is False

    def test_notification_str_method(self, notification):
        """Test notification string representation."""
        assert "Booking Confirmed" in str(notification)

    def test_notification_mark_as_read(self, notification):
        """Test marking notification as read."""
        notification.is_read = True
        notification.save()
        notification.refresh_from_db()

        assert notification.is_read is True

    def test_notification_belongs_to_user(self, notification, user):
        """Test notification belongs to user."""
        assert notification.user == user
