"""
Booking-related models for the Airport Management System.

Manages flight bookings, passengers, and seat assignments.
"""

import random
import string
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from airlines.models import Aircraft
from core.models import TimeStampedModel, TimeStampedUUIDModel
from core.validators import validate_booking_reference, validate_passport_number, validate_seat_number
from flights.models import Flight


class BookingStatus(models.TextChoices):
    """Booking status choices."""

    PENDING = "PENDING", _("Pending Payment")
    CONFIRMED = "CONFIRMED", _("Confirmed")
    CHECKED_IN = "CHECKED_IN", _("Checked In")
    BOARDED = "BOARDED", _("Boarded")
    COMPLETED = "COMPLETED", _("Completed")
    CANCELLED = "CANCELLED", _("Cancelled")
    REFUNDED = "REFUNDED", _("Refunded")
    NO_SHOW = "NO_SHOW", _("No Show")


class SeatClass(models.TextChoices):
    """Seat class choices."""

    FIRST = "FIRST", _("First Class")
    BUSINESS = "BUSINESS", _("Business Class")
    ECONOMY = "ECONOMY", _("Economy Class")


def generate_booking_reference():
    """Generate a unique 6-character alphanumeric booking reference."""
    chars = string.ascii_uppercase + string.digits
    # Remove confusing characters
    chars = chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
    return "".join(random.choices(chars, k=6))


class Booking(TimeStampedUUIDModel):
    """
    Represents a flight booking made by a user.

    A booking can have multiple passengers and is linked to a flight
    and payment information.
    """

    # Reference
    reference = models.CharField(
        _("booking reference"),
        max_length=6,
        unique=True,
        validators=[validate_booking_reference],
        help_text=_("6-character booking reference (e.g., ABC123)"),
    )

    # User who made the booking
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    # Flight
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    # Status
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )

    # Seat Class
    seat_class = models.CharField(
        _("seat class"),
        max_length=20,
        choices=SeatClass.choices,
        default=SeatClass.ECONOMY,
    )

    # Pricing
    base_price = models.DecimalField(
        _("base price"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    taxes = models.DecimalField(
        _("taxes"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    fees = models.DecimalField(
        _("fees"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    discount = models.DecimalField(
        _("discount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total_price = models.DecimalField(
        _("total price"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Contact Information (for non-registered passengers)
    contact_email = models.EmailField(
        _("contact email"),
        blank=True,
    )
    contact_phone = models.CharField(
        _("contact phone"),
        max_length=20,
        blank=True,
    )

    # Additional Info
    special_requests = models.TextField(
        _("special requests"),
        blank=True,
        help_text=_("Any special requests or notes"),
    )

    # Timestamps
    booked_at = models.DateTimeField(
        _("booked at"),
        auto_now_add=True,
    )
    confirmed_at = models.DateTimeField(
        _("confirmed at"),
        null=True,
        blank=True,
    )
    cancelled_at = models.DateTimeField(
        _("cancelled at"),
        null=True,
        blank=True,
    )
    cancellation_reason = models.TextField(
        _("cancellation reason"),
        blank=True,
    )

    class Meta:
        verbose_name = _("booking")
        verbose_name_plural = _("bookings")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["user"]),
            models.Index(fields=["flight"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.flight.flight_number}"

    def save(self, *args, **kwargs):
        """Generate booking reference if not provided."""
        if not self.reference:
            # Generate a unique reference
            for _ in range(10):  # Try up to 10 times
                ref = generate_booking_reference()
                if not Booking.objects.filter(reference=ref).exists():
                    self.reference = ref
                    break
            else:
                raise ValueError("Unable to generate unique booking reference")

        # Calculate total price
        self.total_price = (
            self.base_price + self.taxes + self.fees - self.discount
        )

        super().save(*args, **kwargs)

    @property
    def passenger_count(self):
        """Return the number of passengers in this booking."""
        return self.passengers.count()

    @property
    def is_confirmed(self):
        """Check if booking is confirmed."""
        return self.status == BookingStatus.CONFIRMED

    @property
    def is_cancellable(self):
        """Check if booking can be cancelled."""
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]


class Passenger(TimeStampedModel):
    """
    Represents a passenger in a booking.

    Stores passenger details required for ticketing and boarding.
    """

    class Title(models.TextChoices):
        MR = "MR", _("Mr.")
        MRS = "MRS", _("Mrs.")
        MS = "MS", _("Ms.")
        DR = "DR", _("Dr.")
        MSTR = "MSTR", _("Master")
        MISS = "MISS", _("Miss")

    class PassengerType(models.TextChoices):
        ADULT = "ADULT", _("Adult")
        CHILD = "CHILD", _("Child (2-11)")
        INFANT = "INFANT", _("Infant (0-2)")

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="passengers",
    )

    # Personal Information
    title = models.CharField(
        _("title"),
        max_length=10,
        choices=Title.choices,
        default=Title.MR,
    )
    first_name = models.CharField(
        _("first name"),
        max_length=100,
    )
    last_name = models.CharField(
        _("last name"),
        max_length=100,
    )
    date_of_birth = models.DateField(
        _("date of birth"),
    )
    passenger_type = models.CharField(
        _("passenger type"),
        max_length=10,
        choices=PassengerType.choices,
        default=PassengerType.ADULT,
    )

    # Travel Documents
    passport_number = models.CharField(
        _("passport number"),
        max_length=20,
        blank=True,
        validators=[validate_passport_number],
    )
    passport_expiry = models.DateField(
        _("passport expiry"),
        null=True,
        blank=True,
    )
    passport_country = models.CharField(
        _("passport country"),
        max_length=100,
        default="Nigeria",
    )
    nationality = models.CharField(
        _("nationality"),
        max_length=100,
        default="Nigerian",
    )

    # Seat Assignment
    seat_number = models.CharField(
        _("seat number"),
        max_length=5,
        blank=True,
        validators=[validate_seat_number],
    )

    # Check-in Status
    is_checked_in = models.BooleanField(
        _("checked in"),
        default=False,
    )
    checked_in_at = models.DateTimeField(
        _("checked in at"),
        null=True,
        blank=True,
    )

    # Boarding Status
    has_boarded = models.BooleanField(
        _("boarded"),
        default=False,
    )
    boarded_at = models.DateTimeField(
        _("boarded at"),
        null=True,
        blank=True,
    )

    # Special Requirements
    meal_preference = models.CharField(
        _("meal preference"),
        max_length=50,
        choices=[
            ("REGULAR", "Regular"),
            ("VEGETARIAN", "Vegetarian"),
            ("VEGAN", "Vegan"),
            ("HALAL", "Halal"),
            ("KOSHER", "Kosher"),
            ("GLUTEN_FREE", "Gluten Free"),
        ],
        default="REGULAR",
    )
    special_assistance = models.TextField(
        _("special assistance"),
        blank=True,
    )

    # Baggage
    checked_baggage = models.PositiveIntegerField(
        _("checked baggage (kg)"),
        default=23,
    )

    class Meta:
        verbose_name = _("passenger")
        verbose_name_plural = _("passengers")
        ordering = ["booking", "last_name", "first_name"]

    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Return full name with title."""
        return f"{self.get_title_display()} {self.first_name} {self.last_name}"


class SeatPosition(models.TextChoices):
    """Seat position in the row."""

    WINDOW = "WINDOW", _("Window")
    MIDDLE = "MIDDLE", _("Middle")
    AISLE = "AISLE", _("Aisle")


class Seat(TimeStampedModel):
    """
    Represents a seat on an aircraft.

    Defines seat configuration including class, position, and features.
    """

    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.CASCADE,
        related_name="seats",
    )
    seat_number = models.CharField(
        _("seat number"),
        max_length=5,
        validators=[validate_seat_number],
        help_text=_("Seat number (e.g., 12A, 1F)"),
    )
    seat_class = models.CharField(
        _("seat class"),
        max_length=20,
        choices=SeatClass.choices,
        default=SeatClass.ECONOMY,
    )
    position = models.CharField(
        _("position"),
        max_length=10,
        choices=SeatPosition.choices,
    )
    row_number = models.PositiveIntegerField(
        _("row number"),
    )

    # Features
    has_extra_legroom = models.BooleanField(
        _("extra legroom"),
        default=False,
    )
    is_exit_row = models.BooleanField(
        _("exit row"),
        default=False,
    )
    has_power_outlet = models.BooleanField(
        _("power outlet"),
        default=False,
    )
    is_blocked = models.BooleanField(
        _("blocked"),
        default=False,
        help_text=_("Seat is blocked and cannot be booked"),
    )

    class Meta:
        verbose_name = _("seat")
        verbose_name_plural = _("seats")
        ordering = ["aircraft", "row_number", "seat_number"]
        unique_together = ["aircraft", "seat_number"]

    def __str__(self):
        return f"{self.aircraft.registration} - Seat {self.seat_number}"
