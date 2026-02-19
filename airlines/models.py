"""
Airline and Aircraft models for the Airport Management System.

Manages airline companies, their fleets, and aircraft information.
Also includes Aircraft Parking Management (stands, rates, records).
"""

import random
import string
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel
from core.validators import validate_aircraft_registration, validate_airline_code


class Airline(TimeStampedModel):
    """
    Represents an airline operating at the airport.

    Stores airline company information including contact details,
    operational status, and branding.
    """

    name = models.CharField(
        _("airline name"),
        max_length=255,
        help_text=_("Official name of the airline"),
    )
    code = models.CharField(
        _("IATA code"),
        max_length=2,
        unique=True,
        validators=[validate_airline_code],
        help_text=_("2-letter IATA airline code (e.g., BA, W3, P4)"),
    )
    icao_code = models.CharField(
        _("ICAO code"),
        max_length=3,
        blank=True,
        help_text=_("3-letter ICAO airline code (e.g., BAW, ARA, APK)"),
    )
    country = models.CharField(
        _("country"),
        max_length=100,
        default="Nigeria",
        help_text=_("Country where the airline is based"),
    )
    headquarters = models.CharField(
        _("headquarters"),
        max_length=255,
        blank=True,
        help_text=_("City where the airline is headquartered"),
    )

    # Contact Information
    phone = models.CharField(
        _("phone"),
        max_length=20,
        blank=True,
    )
    email = models.EmailField(
        _("email"),
        blank=True,
    )
    website = models.URLField(
        _("website"),
        blank=True,
    )

    # Branding
    logo = models.ImageField(
        _("logo"),
        upload_to="airlines/logos/",
        null=True,
        blank=True,
    )
    primary_color = models.CharField(
        _("primary color"),
        max_length=7,
        blank=True,
        help_text=_("Hex color code (e.g., #FF0000)"),
    )

    # Operational Status
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Whether the airline is currently operating"),
    )
    alliance = models.CharField(
        _("alliance"),
        max_length=50,
        blank=True,
        choices=[
            ("STAR_ALLIANCE", "Star Alliance"),
            ("ONEWORLD", "oneworld"),
            ("SKYTEAM", "SkyTeam"),
            ("NONE", "None"),
        ],
        default="NONE",
        help_text=_("Airline alliance membership"),
    )

    # Description
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Brief description of the airline"),
    )

    class Meta:
        verbose_name = _("airline")
        verbose_name_plural = _("airlines")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class AircraftType(models.TextChoices):
    """Common aircraft types for selection."""

    # Boeing
    BOEING_737_800 = "B738", _("Boeing 737-800")
    BOEING_737_MAX_8 = "B38M", _("Boeing 737 MAX 8")
    BOEING_747_400 = "B744", _("Boeing 747-400")
    BOEING_777_300ER = "B77W", _("Boeing 777-300ER")
    BOEING_787_8 = "B788", _("Boeing 787-8 Dreamliner")
    BOEING_787_9 = "B789", _("Boeing 787-9 Dreamliner")

    # Airbus
    AIRBUS_A320 = "A320", _("Airbus A320")
    AIRBUS_A320NEO = "A20N", _("Airbus A320neo")
    AIRBUS_A321 = "A321", _("Airbus A321")
    AIRBUS_A330_300 = "A333", _("Airbus A330-300")
    AIRBUS_A350_900 = "A359", _("Airbus A350-900")
    AIRBUS_A380_800 = "A388", _("Airbus A380-800")

    # Embraer
    EMBRAER_E190 = "E190", _("Embraer E190")
    EMBRAER_E195 = "E195", _("Embraer E195")

    # ATR (Regional)
    ATR_72 = "AT72", _("ATR 72")

    # Other
    OTHER = "OTHR", _("Other")


class Aircraft(TimeStampedModel):
    """
    Represents an individual aircraft in an airline's fleet.

    Stores aircraft details including registration, type, capacity,
    and maintenance information.
    """

    airline = models.ForeignKey(
        Airline,
        on_delete=models.CASCADE,
        related_name="aircraft",
        help_text=_("Airline that owns/operates this aircraft"),
    )
    registration = models.CharField(
        _("registration number"),
        max_length=10,
        unique=True,
        validators=[validate_aircraft_registration],
        help_text=_("Aircraft registration (e.g., 5N-ABC for Nigerian)"),
    )
    aircraft_type = models.CharField(
        _("aircraft type"),
        max_length=4,
        choices=AircraftType.choices,
        default=AircraftType.BOEING_737_800,
    )
    model_name = models.CharField(
        _("model name"),
        max_length=100,
        blank=True,
        help_text=_("Specific model name if different from type"),
    )
    name = models.CharField(
        _("aircraft name"),
        max_length=100,
        blank=True,
        help_text=_("Optional nickname for the aircraft"),
    )

    # Capacity
    total_seats = models.PositiveIntegerField(
        _("total seats"),
        default=180,
        help_text=_("Total passenger capacity"),
    )
    first_class_seats = models.PositiveIntegerField(
        _("first class seats"),
        default=0,
    )
    business_class_seats = models.PositiveIntegerField(
        _("business class seats"),
        default=0,
    )
    economy_class_seats = models.PositiveIntegerField(
        _("economy class seats"),
        default=180,
    )

    # Aircraft Details
    year_manufactured = models.PositiveIntegerField(
        _("year manufactured"),
        null=True,
        blank=True,
    )
    serial_number = models.CharField(
        _("serial number"),
        max_length=50,
        blank=True,
    )

    # Maintenance
    last_maintenance_date = models.DateField(
        _("last maintenance date"),
        null=True,
        blank=True,
    )
    next_maintenance_date = models.DateField(
        _("next maintenance date"),
        null=True,
        blank=True,
    )

    # Status
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Whether the aircraft is currently in service"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=[
            ("ACTIVE", _("Active")),
            ("MAINTENANCE", _("In Maintenance")),
            ("GROUNDED", _("Grounded")),
            ("RETIRED", _("Retired")),
        ],
        default="ACTIVE",
    )

    class Meta:
        verbose_name = _("aircraft")
        verbose_name_plural = _("aircraft")
        ordering = ["airline", "registration"]
        indexes = [
            models.Index(fields=["registration"]),
            models.Index(fields=["airline", "is_active"]),
        ]

    def __str__(self):
        return f"{self.registration} ({self.airline.code} - {self.get_aircraft_type_display()})"

    @property
    def age(self):
        """Calculate the age of the aircraft in years."""
        if self.year_manufactured:
            from datetime import date

            return date.today().year - self.year_manufactured
        return None

    def save(self, *args, **kwargs):
        """Ensure total seats equals sum of class seats."""
        calculated_total = (
            self.first_class_seats + self.business_class_seats + self.economy_class_seats
        )
        if calculated_total > 0:
            self.total_seats = calculated_total
        super().save(*args, **kwargs)


# ============================================================
# Aircraft Parking Management
# ============================================================


class AircraftSizeCategory(models.TextChoices):
    """ICAO/IATA aircraft size classifications for parking fee calculation."""
    LIGHT = "LIGHT", _("Light (< 7,000 kg MTOW)")
    SMALL = "SMALL", _("Small (7,000–27,000 kg MTOW)")
    MEDIUM = "MEDIUM", _("Medium (27,000–136,000 kg MTOW)")
    LARGE = "LARGE", _("Large (136,000–300,000 kg MTOW)")
    HEAVY = "HEAVY", _("Heavy (> 300,000 kg MTOW)")


class StandType(models.TextChoices):
    CONTACT = "CONTACT", _("Contact Stand (Jetway)")
    REMOTE = "REMOTE", _("Remote Stand (Bus Transfer)")
    CARGO = "CARGO", _("Cargo Stand")
    MAINTENANCE = "MAINT", _("Maintenance Bay")


class AircraftStand(TimeStampedModel):
    """
    Represents an aircraft parking stand/bay at the airport.

    Each stand has a type, terminal assignment, and maximum aircraft size it can accommodate.
    """

    stand_number = models.CharField(_("stand number"), max_length=10, unique=True)
    terminal = models.CharField(_("terminal"), max_length=5, default="T1")
    stand_type = models.CharField(
        _("stand type"), max_length=10, choices=StandType.choices, default=StandType.CONTACT
    )
    max_aircraft_size = models.CharField(
        _("max aircraft size"),
        max_length=10,
        choices=AircraftSizeCategory.choices,
        default=AircraftSizeCategory.MEDIUM,
        help_text=_("Maximum aircraft size this stand can accommodate"),
    )
    has_jetway = models.BooleanField(_("has jetway"), default=False)
    has_gpu = models.BooleanField(
        _("Ground Power Unit (GPU)"), default=False,
        help_text=_("Provides ground electrical power to parked aircraft"),
    )
    has_pca = models.BooleanField(
        _("Pre-Conditioned Air (PCA)"), default=False,
        help_text=_("Provides climate-controlled air to parked aircraft"),
    )
    is_active = models.BooleanField(_("active"), default=True)
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("aircraft stand")
        verbose_name_plural = _("aircraft stands")
        ordering = ["terminal", "stand_number"]
        indexes = [models.Index(fields=["terminal", "is_active"])]

    def __str__(self):
        return f"Stand {self.stand_number} – Terminal {self.terminal}"

    @property
    def is_currently_occupied(self):
        return self.parking_records.filter(
            status=AircraftParkingRecord.Status.ACTIVE
        ).exists()


class AircraftParkingRate(TimeStampedModel):
    """
    Fee schedule for aircraft parking based on size category.

    Set by airport management; used to auto-calculate charges when
    an aircraft parking record is created or completed.
    """

    aircraft_size = models.CharField(
        _("aircraft size category"),
        max_length=10,
        choices=AircraftSizeCategory.choices,
        unique=True,
    )
    landing_fee = models.DecimalField(
        _("landing fee (₦)"), max_digits=12, decimal_places=2, default=Decimal("0"),
        help_text=_("One-time fee charged when aircraft lands"),
    )
    hourly_rate = models.DecimalField(
        _("hourly parking rate (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )
    daily_rate = models.DecimalField(
        _("daily parking rate (₦)"), max_digits=12, decimal_places=2, default=Decimal("0"),
        help_text=_("Applied for stays exceeding 24 hours"),
    )
    weekly_rate = models.DecimalField(
        _("weekly parking rate (₦)"), max_digits=12, decimal_places=2, default=Decimal("0"),
        help_text=_("Applied for stays exceeding 7 days"),
    )
    gpu_hourly_rate = models.DecimalField(
        _("GPU hourly rate (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )
    pca_hourly_rate = models.DecimalField(
        _("PCA hourly rate (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )
    effective_from = models.DateField(_("effective from"), default=timezone.now)
    effective_until = models.DateField(_("effective until"), null=True, blank=True)

    class Meta:
        verbose_name = _("aircraft parking rate")
        verbose_name_plural = _("aircraft parking rates")

    def __str__(self):
        return f"Rates for {self.get_aircraft_size_display()}"

    def calculate_parking_fee(self, duration_hours: float) -> Decimal:
        """Calculate parking fee based on total duration in hours."""
        if duration_hours <= 0:
            return Decimal("0")
        duration = Decimal(str(duration_hours))
        weeks = int(duration_hours // 168)
        remaining = duration_hours % 168
        days = int(remaining // 24)
        hours = remaining % 24

        fee = (
            Decimal(weeks) * self.weekly_rate
            + Decimal(days) * self.daily_rate
            + Decimal(str(hours)) * self.hourly_rate
        )
        return fee.quantize(Decimal("0.01"))


class AircraftParkingRecord(TimeStampedModel):
    """
    Records an aircraft's stay at a stand including calculated fees and payment status.

    Airlines are billed for: landing fee + parking duration fee + ground services (GPU/PCA).
    """

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", _("Scheduled")
        ACTIVE = "ACTIVE", _("Active (On Stand)")
        COMPLETED = "COMPLETED", _("Completed")
        OVERDUE = "OVERDUE", _("Overdue – Unpaid")
        CANCELLED = "CANCELLED", _("Cancelled")

    record_number = models.CharField(
        _("record number"), max_length=20, unique=True, editable=False
    )
    aircraft = models.ForeignKey(
        Aircraft, on_delete=models.PROTECT, related_name="parking_records"
    )
    airline = models.ForeignKey(
        Airline, on_delete=models.PROTECT, related_name="parking_records"
    )
    stand = models.ForeignKey(
        AircraftStand, on_delete=models.PROTECT, related_name="parking_records"
    )
    aircraft_size = models.CharField(
        _("aircraft size"), max_length=10, choices=AircraftSizeCategory.choices
    )

    # Timing
    scheduled_arrival = models.DateTimeField(_("scheduled arrival"))
    scheduled_departure = models.DateTimeField(_("scheduled departure"))
    actual_arrival_time = models.DateTimeField(_("actual arrival"), null=True, blank=True)
    actual_departure_time = models.DateTimeField(_("actual departure"), null=True, blank=True)

    # Ground services
    gpu_requested = models.BooleanField(_("GPU requested"), default=False)
    pca_requested = models.BooleanField(_("PCA requested"), default=False)

    # Fees (auto-calculated)
    landing_fee = models.DecimalField(
        _("landing fee (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )
    parking_fee = models.DecimalField(
        _("parking fee (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )
    service_fee = models.DecimalField(
        _("ground services fee (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )
    total_due = models.DecimalField(
        _("total due (₦)"), max_digits=12, decimal_places=2, default=Decimal("0")
    )

    # Payment
    is_paid = models.BooleanField(_("paid"), default=False)
    payment_date = models.DateTimeField(_("payment date"), null=True, blank=True)
    payment_reference = models.CharField(_("payment reference"), max_length=100, blank=True)
    invoice_number = models.CharField(_("invoice number"), max_length=30, blank=True)

    status = models.CharField(
        _("status"), max_length=15, choices=Status.choices, default=Status.SCHEDULED
    )
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("aircraft parking record")
        verbose_name_plural = _("aircraft parking records")
        ordering = ["-scheduled_arrival"]
        indexes = [
            models.Index(fields=["airline", "status"]),
            models.Index(fields=["stand", "status"]),
            models.Index(fields=["is_paid"]),
        ]

    def __str__(self):
        return f"{self.record_number} – {self.aircraft.registration} @ Stand {self.stand.stand_number}"

    def save(self, *args, **kwargs):
        if not self.record_number:
            self.record_number = "APR-" + "".join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    @property
    def duration_hours(self) -> float:
        """Return duration in hours using actual times if available, else scheduled."""
        start = self.actual_arrival_time or self.scheduled_arrival
        end = self.actual_departure_time or self.scheduled_departure
        if start and end and end > start:
            return (end - start).total_seconds() / 3600
        return 0.0

    @property
    def duration_display(self) -> str:
        hours = self.duration_hours
        days = int(hours // 24)
        remaining_hours = int(hours % 24)
        if days:
            return f"{days}d {remaining_hours}h"
        return f"{int(hours)}h"

    def calculate_and_save_fees(self):
        """Recalculate all fees based on current rates and save."""
        try:
            rate = AircraftParkingRate.objects.get(aircraft_size=self.aircraft_size)
        except AircraftParkingRate.DoesNotExist:
            return

        self.landing_fee = rate.landing_fee
        self.parking_fee = rate.calculate_parking_fee(self.duration_hours)

        svc = Decimal("0")
        if self.gpu_requested:
            svc += rate.gpu_hourly_rate * Decimal(str(self.duration_hours))
        if self.pca_requested:
            svc += rate.pca_hourly_rate * Decimal(str(self.duration_hours))
        self.service_fee = svc.quantize(Decimal("0.01"))
        self.total_due = self.landing_fee + self.parking_fee + self.service_fee
        self.save()
