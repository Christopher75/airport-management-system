"""
Hotel Booking Models for the Airport Management System.

Provides partner hotel listings near the airport and a full
booking flow with room types, tax & service fee calculation.
"""

import random
import string
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, TimeStampedUUIDModel


class Hotel(TimeStampedModel):
    """
    A partner hotel near the airport.
    """

    name = models.CharField(_("hotel name"), max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(_("description"))
    star_rating = models.PositiveSmallIntegerField(
        _("star rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=3,
    )
    address = models.TextField(_("address"))
    distance_from_airport = models.DecimalField(
        _("distance from airport (km)"),
        max_digits=5,
        decimal_places=1,
        help_text=_("Walking/driving distance from the airport terminal"),
    )
    phone = models.CharField(_("phone"), max_length=25)
    email = models.EmailField(_("email"), blank=True)
    website = models.URLField(_("website"), blank=True)

    # Amenities stored as JSON list (e.g. ["wifi", "pool", "gym", "restaurant"])
    amenities = models.JSONField(_("amenities"), default=list, blank=True)

    has_airport_shuttle = models.BooleanField(
        _("airport shuttle"), default=False,
        help_text=_("Free shuttle service between hotel and airport"),
    )
    check_in_time = models.TimeField(_("check-in time"), default="14:00")
    check_out_time = models.TimeField(_("check-out time"), default="12:00")

    image = models.ImageField(
        _("main image"), upload_to="hotels/", null=True, blank=True
    )
    is_active = models.BooleanField(_("active"), default=True)

    # Tax rates applied on top of room price
    VAT_RATE = Decimal("0.075")          # 7.5% VAT
    SERVICE_FEE_RATE = Decimal("0.05")   # 5% service charge

    class Meta:
        verbose_name = _("hotel")
        verbose_name_plural = _("hotels")
        ordering = ["-star_rating", "name"]
        indexes = [models.Index(fields=["is_active", "star_rating"])]

    def __str__(self):
        return f"{self.name} ({self.star_rating}★)"

    @property
    def star_display(self):
        return "★" * self.star_rating + "☆" * (5 - self.star_rating)


class RoomType(TimeStampedModel):
    """
    A category of rooms within a hotel (e.g. Standard, Deluxe, Suite).
    """

    hotel = models.ForeignKey(
        Hotel, on_delete=models.CASCADE, related_name="room_types"
    )
    name = models.CharField(_("room name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    bed_type = models.CharField(
        _("bed type"),
        max_length=50,
        choices=[
            ("Single", "Single Bed"),
            ("Double", "Double Bed"),
            ("Twin", "Twin Beds"),
            ("King", "King Size"),
            ("Queen", "Queen Size"),
        ],
        default="Double",
    )
    max_occupancy = models.PositiveSmallIntegerField(_("max occupancy"), default=2)
    base_price_per_night = models.DecimalField(
        _("base price per night (₦)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Price before taxes and fees"),
    )
    total_rooms = models.PositiveSmallIntegerField(_("total rooms"), default=10)
    amenities = models.JSONField(_("room amenities"), default=list, blank=True)
    image = models.ImageField(
        _("room image"), upload_to="hotels/rooms/", null=True, blank=True
    )
    is_active = models.BooleanField(_("available"), default=True)

    class Meta:
        verbose_name = _("room type")
        verbose_name_plural = _("room types")
        ordering = ["hotel", "base_price_per_night"]

    def __str__(self):
        return f"{self.hotel.name} – {self.name}"


class HotelBooking(TimeStampedUUIDModel):
    """
    A hotel room reservation made through the airport system.

    Pricing breakdown:
      subtotal = room_rate × num_nights × num_rooms
      vat = subtotal × 7.5%
      service_fee = subtotal × 5%
      total = subtotal + vat + service_fee
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending Payment")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        CHECKED_IN = "CHECKED_IN", _("Checked In")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")
        NO_SHOW = "NO_SHOW", _("No Show")

    reference = models.CharField(
        _("booking reference"), max_length=10, unique=True, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="hotel_bookings",
    )
    hotel = models.ForeignKey(
        Hotel, on_delete=models.PROTECT, related_name="bookings"
    )
    room_type = models.ForeignKey(
        RoomType, on_delete=models.PROTECT, related_name="bookings"
    )

    # Stay details
    check_in_date = models.DateField(_("check-in date"))
    check_out_date = models.DateField(_("check-out date"))
    num_rooms = models.PositiveSmallIntegerField(_("number of rooms"), default=1)
    num_adults = models.PositiveSmallIntegerField(_("adults"), default=1)
    num_children = models.PositiveSmallIntegerField(_("children"), default=0)

    # Guest info
    guest_first_name = models.CharField(_("first name"), max_length=100)
    guest_last_name = models.CharField(_("last name"), max_length=100)
    guest_email = models.EmailField(_("email"))
    guest_phone = models.CharField(_("phone"), max_length=25)
    special_requests = models.TextField(_("special requests"), blank=True)

    # Pricing (stored after calculation)
    room_rate = models.DecimalField(
        _("room rate per night (₦)"), max_digits=10, decimal_places=2
    )
    num_nights = models.PositiveSmallIntegerField(_("number of nights"), default=1)
    subtotal = models.DecimalField(_("subtotal (₦)"), max_digits=12, decimal_places=2)
    vat_amount = models.DecimalField(_("VAT 7.5% (₦)"), max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(
        _("service fee 5% (₦)"), max_digits=10, decimal_places=2
    )
    total_price = models.DecimalField(_("total price (₦)"), max_digits=12, decimal_places=2)

    # Payment
    is_paid = models.BooleanField(_("paid"), default=False)
    payment_reference = models.CharField(_("payment reference"), max_length=100, blank=True)
    paid_at = models.DateTimeField(_("paid at"), null=True, blank=True)

    status = models.CharField(
        _("status"), max_length=15, choices=Status.choices, default=Status.PENDING
    )

    # Optional: link to a flight booking for transit guests
    related_flight_ref = models.CharField(
        _("related flight booking ref"),
        max_length=10,
        blank=True,
        help_text=_("Optional: link to a flight booking (for transit guests)"),
    )

    class Meta:
        verbose_name = _("hotel booking")
        verbose_name_plural = _("hotel bookings")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["reference"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.reference} – {self.hotel.name} ({self.check_in_date} to {self.check_out_date})"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "HTL-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
        super().save(*args, **kwargs)

    @property
    def guest_full_name(self):
        return f"{self.guest_first_name} {self.guest_last_name}"

    @property
    def is_cancellable(self):
        from django.utils import timezone
        from datetime import timedelta
        return (
            self.status in (self.Status.PENDING, self.Status.CONFIRMED)
            and self.check_in_date > (timezone.now().date() + timedelta(days=1))
        )

    @classmethod
    def calculate_price(cls, room_type, check_in, check_out, num_rooms=1):
        """
        Return a pricing dict for a proposed booking.
        Uses Hotel.VAT_RATE and Hotel.SERVICE_FEE_RATE.
        """
        nights = (check_out - check_in).days
        if nights < 1:
            nights = 1
        rate = room_type.base_price_per_night
        subtotal = rate * Decimal(nights) * Decimal(num_rooms)
        vat = (subtotal * Hotel.VAT_RATE).quantize(Decimal("0.01"))
        svc = (subtotal * Hotel.SERVICE_FEE_RATE).quantize(Decimal("0.01"))
        total = subtotal + vat + svc
        return {
            "room_rate": rate,
            "num_nights": nights,
            "num_rooms": num_rooms,
            "subtotal": subtotal,
            "vat_amount": vat,
            "service_fee": svc,
            "total_price": total,
        }
