"""
Flight-related models for the Airport Management System.

Manages airports, gates, and flight schedules.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from airlines.models import Aircraft, Airline
from core.models import TimeStampedModel
from core.validators import validate_airport_code, validate_flight_number


class Airport(TimeStampedModel):
    """
    Represents an airport that flights can depart from or arrive at.

    Stores airport details including location, timezone, and facilities.
    """

    name = models.CharField(
        _("airport name"),
        max_length=255,
        help_text=_("Official name of the airport"),
    )
    code = models.CharField(
        _("IATA code"),
        max_length=3,
        unique=True,
        validators=[validate_airport_code],
        help_text=_("3-letter IATA airport code (e.g., ABV, LOS, LHR)"),
    )
    icao_code = models.CharField(
        _("ICAO code"),
        max_length=4,
        blank=True,
        help_text=_("4-letter ICAO airport code (e.g., DNAA, DNMM, EGLL)"),
    )

    # Location
    city = models.CharField(
        _("city"),
        max_length=100,
    )
    country = models.CharField(
        _("country"),
        max_length=100,
        default="Nigeria",
    )
    timezone = models.CharField(
        _("timezone"),
        max_length=50,
        default="Africa/Lagos",
        help_text=_("IANA timezone identifier"),
    )

    # Coordinates for maps
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    # Contact
    phone = models.CharField(
        _("phone"),
        max_length=20,
        blank=True,
    )
    website = models.URLField(
        _("website"),
        blank=True,
    )

    # Classification
    is_international = models.BooleanField(
        _("international"),
        default=True,
        help_text=_("Whether the airport handles international flights"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    class Meta:
        verbose_name = _("airport")
        verbose_name_plural = _("airports")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class GateStatus(models.TextChoices):
    """Gate status choices."""

    AVAILABLE = "AVAILABLE", _("Available")
    OCCUPIED = "OCCUPIED", _("Occupied")
    BOARDING = "BOARDING", _("Boarding")
    MAINTENANCE = "MAINTENANCE", _("Under Maintenance")
    CLOSED = "CLOSED", _("Closed")


class Gate(TimeStampedModel):
    """
    Represents a gate at an airport terminal.

    Gates are assigned to flights for boarding passengers.
    """

    airport = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="gates",
    )
    terminal = models.CharField(
        _("terminal"),
        max_length=10,
        help_text=_("Terminal identifier (e.g., T1, A, International)"),
    )
    gate_number = models.CharField(
        _("gate number"),
        max_length=10,
        help_text=_("Gate number (e.g., A1, B12)"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=GateStatus.choices,
        default=GateStatus.AVAILABLE,
    )
    is_international = models.BooleanField(
        _("international gate"),
        default=True,
        help_text=_("Whether this gate handles international flights"),
    )

    class Meta:
        verbose_name = _("gate")
        verbose_name_plural = _("gates")
        ordering = ["airport", "terminal", "gate_number"]
        unique_together = ["airport", "terminal", "gate_number"]
        indexes = [
            models.Index(fields=["airport", "status"]),
        ]

    def __str__(self):
        return f"{self.airport.code} - Terminal {self.terminal} Gate {self.gate_number}"


class FlightStatus(models.TextChoices):
    """Flight status choices."""

    SCHEDULED = "SCHEDULED", _("Scheduled")
    CHECK_IN_OPEN = "CHECK_IN_OPEN", _("Check-in Open")
    BOARDING = "BOARDING", _("Boarding")
    GATE_CLOSED = "GATE_CLOSED", _("Gate Closed")
    DEPARTED = "DEPARTED", _("Departed")
    IN_FLIGHT = "IN_FLIGHT", _("In Flight")
    LANDED = "LANDED", _("Landed")
    ARRIVED = "ARRIVED", _("Arrived")
    DELAYED = "DELAYED", _("Delayed")
    CANCELLED = "CANCELLED", _("Cancelled")
    DIVERTED = "DIVERTED", _("Diverted")


class Flight(TimeStampedModel):
    """
    Represents a scheduled flight between two airports.

    Contains all flight details including schedule, pricing, and status.
    """

    # Flight Identification
    flight_number = models.CharField(
        _("flight number"),
        max_length=10,
        validators=[validate_flight_number],
        help_text=_("Flight number (e.g., W3101, BA75)"),
    )
    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="flights",
    )
    aircraft = models.ForeignKey(
        Aircraft,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="flights",
    )

    # Route
    origin = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="departing_flights",
        verbose_name=_("origin"),
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="arriving_flights",
        verbose_name=_("destination"),
    )

    # Schedule
    scheduled_departure = models.DateTimeField(
        _("scheduled departure"),
    )
    scheduled_arrival = models.DateTimeField(
        _("scheduled arrival"),
    )
    actual_departure = models.DateTimeField(
        _("actual departure"),
        null=True,
        blank=True,
    )
    actual_arrival = models.DateTimeField(
        _("actual arrival"),
        null=True,
        blank=True,
    )

    # Gate Assignment
    departure_gate = models.ForeignKey(
        Gate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departure_flights",
        verbose_name=_("departure gate"),
    )
    arrival_gate = models.ForeignKey(
        Gate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="arrival_flights",
        verbose_name=_("arrival gate"),
    )

    # Status
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=FlightStatus.choices,
        default=FlightStatus.SCHEDULED,
    )
    delay_reason = models.TextField(
        _("delay reason"),
        blank=True,
        help_text=_("Reason for delay if applicable"),
    )

    # Pricing (in Nigerian Naira)
    economy_price = models.DecimalField(
        _("economy price"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("50000.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("Price in Nigerian Naira"),
    )
    business_price = models.DecimalField(
        _("business price"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("150000.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    first_class_price = models.DecimalField(
        _("first class price"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("300000.00"),
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    # Capacity Tracking
    available_economy_seats = models.PositiveIntegerField(
        _("available economy seats"),
        default=0,
    )
    available_business_seats = models.PositiveIntegerField(
        _("available business seats"),
        default=0,
    )
    available_first_class_seats = models.PositiveIntegerField(
        _("available first class seats"),
        default=0,
    )

    # Additional Info
    is_international = models.BooleanField(
        _("international flight"),
        default=False,
    )
    meal_service = models.BooleanField(
        _("meal service"),
        default=True,
    )
    wifi_available = models.BooleanField(
        _("WiFi available"),
        default=False,
    )

    class Meta:
        verbose_name = _("flight")
        verbose_name_plural = _("flights")
        ordering = ["scheduled_departure"]
        indexes = [
            models.Index(fields=["flight_number"]),
            models.Index(fields=["scheduled_departure"]),
            models.Index(fields=["origin", "destination"]),
            models.Index(fields=["status"]),
            models.Index(fields=["airline", "scheduled_departure"]),
        ]

    def __str__(self):
        return f"{self.flight_number} ({self.origin.code} → {self.destination.code})"

    @property
    def duration(self):
        """Calculate flight duration."""
        if self.scheduled_arrival and self.scheduled_departure:
            delta = self.scheduled_arrival - self.scheduled_departure
            hours, remainder = divmod(delta.seconds, 3600)
            minutes = remainder // 60
            return f"{hours}h {minutes}m"
        return None

    @property
    def is_delayed(self):
        """Check if flight is delayed."""
        return self.status == FlightStatus.DELAYED

    @property
    def is_cancelled(self):
        """Check if flight is cancelled."""
        return self.status == FlightStatus.CANCELLED

    @property
    def is_bookable(self):
        """Check if flight can still be booked."""
        if self.status in [FlightStatus.CANCELLED, FlightStatus.DEPARTED, FlightStatus.IN_FLIGHT]:
            return False
        if self.scheduled_departure < timezone.now():
            return False
        return self.total_available_seats > 0

    @property
    def total_available_seats(self):
        """Return total available seats across all classes."""
        return (
            self.available_economy_seats
            + self.available_business_seats
            + self.available_first_class_seats
        )

    def save(self, *args, **kwargs):
        """Initialize available seats from aircraft capacity if new flight."""
        if not self.pk and self.aircraft:
            if self.available_economy_seats == 0:
                self.available_economy_seats = self.aircraft.economy_class_seats
            if self.available_business_seats == 0:
                self.available_business_seats = self.aircraft.business_class_seats
            if self.available_first_class_seats == 0:
                self.available_first_class_seats = self.aircraft.first_class_seats

        # Determine if international based on countries
        if self.origin and self.destination:
            self.is_international = self.origin.country != self.destination.country

        super().save(*args, **kwargs)

    def clean(self):
        """Validate flight data."""
        from django.core.exceptions import ValidationError

        if self.origin and self.destination and self.origin == self.destination:
            raise ValidationError(_("Origin and destination cannot be the same airport."))

        if self.scheduled_departure and self.scheduled_arrival:
            if self.scheduled_arrival <= self.scheduled_departure:
                raise ValidationError(
                    _("Scheduled arrival must be after scheduled departure.")
                )
