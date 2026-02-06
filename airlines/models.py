"""
Airline and Aircraft models for the Airport Management System.

Manages airline companies, their fleets, and aircraft information.
"""

from django.db import models
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
