"""
Airport Lounge Booking Models.

Passengers can book day passes to airport lounges before their flight.
Lounges can be airline-specific (Business/First Class) or independent (Priority Pass style).
"""

import random
import string
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, TimeStampedUUIDModel


class AirportLounge(TimeStampedModel):
    """
    An airport lounge available for booking at NAIA.
    """

    class LoungeType(models.TextChoices):
        AIRLINE = "AIRLINE", _("Airline Lounge")
        INDEPENDENT = "INDEPENDENT", _("Independent / Priority Pass")
        VIP = "VIP", _("VIP / Government")
        TRANSIT = "TRANSIT", _("Transit Lounge")

    name = models.CharField(_("lounge name"), max_length=200)
    slug = models.SlugField(unique=True)
    lounge_type = models.CharField(
        _("lounge type"), max_length=15, choices=LoungeType.choices, default=LoungeType.INDEPENDENT
    )
    terminal = models.CharField(_("terminal"), max_length=5, default="T1")
    location_description = models.CharField(
        _("location"), max_length=200, help_text=_("e.g. Level 2, after Security Gate B")
    )
    description = models.TextField(_("description"))
    capacity = models.PositiveSmallIntegerField(_("capacity"), default=50)

    # Pricing
    day_pass_price = models.DecimalField(
        _("day pass price (₦)"), max_digits=10, decimal_places=2,
        help_text=_("Price per adult for one visit (up to 3 hours)"),
    )
    child_price = models.DecimalField(
        _("child price (₦)"), max_digits=10, decimal_places=2, default=Decimal("0"),
        help_text=_("Price per child under 12. Set 0 for free."),
    )

    # Amenities
    has_wifi = models.BooleanField(_("WiFi"), default=True)
    has_food = models.BooleanField(_("Food & Drinks"), default=True)
    has_shower = models.BooleanField(_("Shower Facilities"), default=False)
    has_spa = models.BooleanField(_("Spa / Wellness"), default=False)
    has_prayer_room = models.BooleanField(_("Prayer Room"), default=False)
    has_business_centre = models.BooleanField(_("Business Centre"), default=False)

    opening_time = models.TimeField(_("opens"), default="05:00")
    closing_time = models.TimeField(_("closes"), default="23:00")

    image = models.ImageField(_("image"), upload_to="lounges/", null=True, blank=True)
    is_active = models.BooleanField(_("active"), default=True)

    # Tax
    VAT_RATE = Decimal("0.075")

    class Meta:
        verbose_name = _("airport lounge")
        verbose_name_plural = _("airport lounges")
        ordering = ["terminal", "name"]

    def __str__(self):
        return f"{self.name} (Terminal {self.terminal})"

    def total_price_with_tax(self, num_adults=1, num_children=0):
        subtotal = self.day_pass_price * num_adults + self.child_price * num_children
        vat = (subtotal * self.VAT_RATE).quantize(Decimal("0.01"))
        return subtotal, vat, subtotal + vat


class LoungeBooking(TimeStampedUUIDModel):
    """
    A lounge day pass booking.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        CONFIRMED = "CONFIRMED", _("Confirmed")
        USED = "USED", _("Used / Entry Granted")
        EXPIRED = "EXPIRED", _("Expired")
        CANCELLED = "CANCELLED", _("Cancelled")

    reference = models.CharField(
        _("reference"), max_length=10, unique=True, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lounge_bookings",
    )
    lounge = models.ForeignKey(
        AirportLounge, on_delete=models.PROTECT, related_name="bookings"
    )

    # Visit details
    visit_date = models.DateField(_("visit date"))
    num_adults = models.PositiveSmallIntegerField(_("adults"), default=1)
    num_children = models.PositiveSmallIntegerField(_("children under 12"), default=0)

    # Guest
    guest_name = models.CharField(_("guest name"), max_length=200)
    guest_email = models.EmailField(_("email"))
    guest_phone = models.CharField(_("phone"), max_length=25, blank=True)
    flight_number = models.CharField(
        _("flight number"), max_length=10, blank=True,
        help_text=_("Optional: for entry verification"),
    )

    # Pricing
    subtotal = models.DecimalField(_("subtotal (₦)"), max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(_("VAT (₦)"), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_("total (₦)"), max_digits=10, decimal_places=2)

    # Payment
    is_paid = models.BooleanField(_("paid"), default=False)
    payment_reference = models.CharField(_("payment ref"), max_length=100, blank=True)

    # Access code (shown at lounge entrance)
    access_code = models.CharField(_("access code"), max_length=8, blank=True, editable=False)

    status = models.CharField(
        _("status"), max_length=12, choices=Status.choices, default=Status.PENDING
    )

    class Meta:
        verbose_name = _("lounge booking")
        verbose_name_plural = _("lounge bookings")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} – {self.lounge.name} ({self.visit_date})"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = "LNG-" + "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
        if not self.access_code:
            self.access_code = "".join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)
