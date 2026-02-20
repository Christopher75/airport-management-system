"""
Airport Taxi & Car Transfer Booking Models.

Passengers can pre-book taxis and private transfers from/to the airport.
Vehicle categories range from economy saloons to VIP executive cars.
"""

import random
import string
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_taxi_reference():
    return "TXI-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


class VehicleCategory(models.Model):
    """
    A class of vehicle available for airport transfers.
    e.g. Economy Sedan, Executive SUV, Minivan, Luxury Limousine.
    """

    class VehicleType(models.TextChoices):
        SEDAN = "SEDAN", _("Economy Sedan")
        SUV = "SUV", _("Standard SUV")
        LUXURY = "LUXURY", _("Luxury / Executive")
        MINIVAN = "MINIVAN", _("Minivan")
        BUS = "BUS", _("Shuttle / Minibus")

    name = models.CharField(_("vehicle name"), max_length=100)
    slug = models.SlugField(unique=True)
    vehicle_type = models.CharField(
        _("vehicle type"), max_length=10,
        choices=VehicleType.choices, default=VehicleType.SEDAN,
    )
    description = models.TextField(_("description"), blank=True)
    max_passengers = models.PositiveSmallIntegerField(_("max passengers"), default=4)
    max_luggage = models.PositiveSmallIntegerField(
        _("max luggage bags"), default=3,
        help_text="Maximum number of standard-sized bags"
    )
    price_per_km = models.DecimalField(
        _("price per km (₦)"), max_digits=8, decimal_places=2,
        help_text="Rate charged per kilometre of the journey"
    )
    minimum_fare = models.DecimalField(
        _("minimum fare (₦)"), max_digits=10, decimal_places=2,
        help_text="Minimum charge regardless of distance"
    )
    waiting_charge_per_hour = models.DecimalField(
        _("waiting charge per hour (₦)"), max_digits=8, decimal_places=2,
        default=Decimal("2000.00"),
    )
    features = models.JSONField(
        _("features"), default=list, blank=True,
        help_text="List of features, e.g. ['AC', 'WiFi', 'Meet & Greet']"
    )
    image = models.ImageField(
        _("vehicle image"), upload_to="taxis/vehicles/", blank=True, null=True
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("vehicle category")
        verbose_name_plural = _("vehicle categories")
        ordering = ["price_per_km"]

    def __str__(self):
        return f"{self.name} (max {self.max_passengers} pax)"

    def estimate_fare(self, distance_km: Decimal) -> Decimal:
        """Calculate estimated fare for a given distance."""
        fare = self.price_per_km * distance_km
        return max(fare, self.minimum_fare).quantize(Decimal("0.01"))


class TaxiBooking(models.Model):
    """
    A pre-booked airport taxi or car transfer.
    """

    class BookingStatus(models.TextChoices):
        PENDING = "PENDING", _("Pending Payment")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        DRIVER_ASSIGNED = "ASSIGNED", _("Driver Assigned")
        EN_ROUTE = "EN_ROUTE", _("Driver En Route")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    class TripType(models.TextChoices):
        ARRIVAL = "ARRIVAL", _("Airport Arrival (Airport → Destination)")
        DEPARTURE = "DEPARTURE", _("Airport Departure (Origin → Airport)")
        TRANSFER = "TRANSFER", _("Point-to-Point Transfer")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(
        _("booking reference"), max_length=12, unique=True, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="taxi_bookings",
        verbose_name=_("user"),
    )
    vehicle_category = models.ForeignKey(
        VehicleCategory, on_delete=models.PROTECT,
        related_name="bookings", verbose_name=_("vehicle category"),
    )

    # Trip details
    trip_type = models.CharField(
        _("trip type"), max_length=10,
        choices=TripType.choices, default=TripType.ARRIVAL,
    )
    pickup_location = models.CharField(_("pickup location"), max_length=255)
    dropoff_location = models.CharField(_("drop-off location"), max_length=255)
    pickup_datetime = models.DateTimeField(_("pickup date & time"))
    flight_number = models.CharField(
        _("flight number"), max_length=10, blank=True,
        help_text="Optional: helps driver monitor your flight for delays"
    )
    num_passengers = models.PositiveSmallIntegerField(_("number of passengers"), default=1)
    num_luggage = models.PositiveSmallIntegerField(_("number of bags"), default=1)
    special_requests = models.TextField(_("special requests"), blank=True)

    # Pricing
    estimated_distance_km = models.DecimalField(
        _("estimated distance (km)"), max_digits=6, decimal_places=1, default=Decimal("10.0")
    )
    base_fare = models.DecimalField(_("base fare (₦)"), max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(_("VAT 7.5% (₦)"), max_digits=10, decimal_places=2)
    total_fare = models.DecimalField(_("total fare (₦)"), max_digits=10, decimal_places=2)

    # Guest contact
    passenger_name = models.CharField(_("passenger name"), max_length=200)
    passenger_email = models.EmailField(_("email"))
    passenger_phone = models.CharField(_("phone"), max_length=25)

    # Payment
    is_paid = models.BooleanField(_("paid"), default=False)
    payment_reference = models.CharField(_("payment reference"), max_length=100, blank=True)
    paid_at = models.DateTimeField(_("paid at"), blank=True, null=True)

    # Driver info (assigned after confirmation)
    driver_name = models.CharField(_("driver name"), max_length=100, blank=True)
    driver_phone = models.CharField(_("driver phone"), max_length=25, blank=True)
    vehicle_plate = models.CharField(_("vehicle plate"), max_length=20, blank=True)
    vehicle_colour = models.CharField(_("vehicle colour"), max_length=30, blank=True)

    status = models.CharField(
        _("status"), max_length=12,
        choices=BookingStatus.choices, default=BookingStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("taxi booking")
        verbose_name_plural = _("taxi bookings")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"], name="taxis_taxibooking_ref_idx"),
            models.Index(fields=["user", "status"], name="taxis_taxibooking_usr_idx"),
            models.Index(fields=["pickup_datetime"], name="taxis_taxibooking_dt_idx"),
        ]

    def __str__(self):
        return f"{self.reference} | {self.passenger_name} | {self.pickup_datetime:%d %b %Y %H:%M}"

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                ref = generate_taxi_reference()
                if not TaxiBooking.objects.filter(reference=ref).exists():
                    self.reference = ref
                    break
        super().save(*args, **kwargs)
