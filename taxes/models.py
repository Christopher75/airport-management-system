"""
Airport Taxes Management Models.

Defines the types of government and airport-mandated taxes and levies,
and tracks their collection per booking/service.
"""

import random
import string
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


def generate_tax_invoice_number():
    prefix = "TAX"
    digits = "".join(random.choices(string.digits, k=7))
    return f"{prefix}-{digits}"


class TaxCategory(models.TextChoices):
    PASSENGER_SERVICE_CHARGE = "PSC", _("Passenger Service Charge (PSC)")
    AIRPORT_DEVELOPMENT_LEVY = "ADL", _("Airport Development Levy (ADL)")
    SECURITY_FEE = "SEC", _("Security & Safety Fee")
    DEPARTURE_TAX = "DEP", _("Departure Tax")
    VALUE_ADDED_TAX = "VAT", _("Value Added Tax (VAT 7.5%)")
    FUEL_SURCHARGE = "FUEL", _("Fuel Surcharge")
    TRANSIT_TAX = "TRANSIT", _("Transit Passenger Tax")
    INTERNATIONAL_SURCHARGE = "INTL", _("International Route Surcharge")
    CUSTOMS_STAMP_DUTY = "CSD", _("Customs & Stamp Duty")


class RateType(models.TextChoices):
    FIXED = "FIXED", _("Fixed Amount (₦ per passenger)")
    PERCENTAGE = "PERCENT", _("Percentage of base fare (%)")


class ApplicabilityType(models.TextChoices):
    DOMESTIC = "DOMESTIC", _("Domestic Flights Only")
    INTERNATIONAL = "INTERNATIONAL", _("International Flights Only")
    ALL = "ALL", _("All Flights")


class TaxType(models.Model):
    """
    Defines a specific type of airport tax or levy.
    Created by airport management; drives automatic fee calculation.
    """

    name = models.CharField(_("tax name"), max_length=150)
    code = models.CharField(_("code"), max_length=10, unique=True,
                            help_text="Short identifier, e.g. ADL, PSC, VAT")
    category = models.CharField(
        _("category"), max_length=10,
        choices=TaxCategory.choices,
        default=TaxCategory.PASSENGER_SERVICE_CHARGE,
    )
    description = models.TextField(_("description"), blank=True)
    rate_type = models.CharField(
        _("rate type"), max_length=10,
        choices=RateType.choices,
        default=RateType.FIXED,
    )
    rate = models.DecimalField(
        _("rate / amount"), max_digits=10, decimal_places=2,
        help_text="Enter a ₦ amount for FIXED, or percentage (e.g. 7.5) for PERCENTAGE",
    )
    applicability = models.CharField(
        _("applicability"), max_length=15,
        choices=ApplicabilityType.choices,
        default=ApplicabilityType.ALL,
    )
    is_mandatory = models.BooleanField(
        _("mandatory"), default=True,
        help_text="Mandatory taxes are automatically added to all applicable bookings",
    )
    is_active = models.BooleanField(_("active"), default=True)
    effective_from = models.DateField(_("effective from"))
    effective_until = models.DateField(_("effective until"), blank=True, null=True)

    class Meta:
        verbose_name = _("tax type")
        verbose_name_plural = _("tax types")
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.code} – {self.name}"

    def calculate_amount(self, base_fare: Decimal) -> Decimal:
        """Return the tax amount for a given base fare."""
        if self.rate_type == RateType.PERCENTAGE:
            return (base_fare * self.rate / Decimal("100")).quantize(Decimal("0.01"))
        return self.rate


class TaxInvoice(models.Model):
    """
    A tax invoice generated for a specific booking or service.
    Tracks all airport taxes owed and their payment status.
    """

    class ServiceType(models.TextChoices):
        FLIGHT = "FLIGHT", _("Flight Booking")
        HOTEL = "HOTEL", _("Hotel Booking")
        LOUNGE = "LOUNGE", _("Lounge Access")
        PARKING = "PARKING", _("Vehicle Parking")
        AIRCRAFT_PARKING = "AIRCRAFT", _("Aircraft Parking")

    class InvoiceStatus(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        ISSUED = "ISSUED", _("Issued")
        PAID = "PAID", _("Paid")
        OVERDUE = "OVERDUE", _("Overdue")
        CANCELLED = "CANCELLED", _("Cancelled")

    invoice_number = models.CharField(
        _("invoice number"), max_length=20, unique=True, editable=False,
    )
    service_type = models.CharField(
        _("service type"), max_length=15,
        choices=ServiceType.choices,
        default=ServiceType.FLIGHT,
    )
    # Link to the booking reference (works across different booking types)
    booking_reference = models.CharField(
        _("booking reference"), max_length=20,
        help_text="Reference number from the related booking (flight, hotel, etc.)",
    )
    # Passenger / guest details (denormalised for independence)
    passenger_name = models.CharField(_("passenger / guest name"), max_length=200)
    passenger_email = models.EmailField(_("email"))
    flight_route = models.CharField(
        _("route / service description"), max_length=100, blank=True,
        help_text="e.g. ABV → LOS or Hotel: Sheraton Abuja",
    )
    # Financial
    base_amount = models.DecimalField(
        _("base amount (₦)"), max_digits=12, decimal_places=2,
        help_text="The base fare/price before taxes",
    )
    total_tax_amount = models.DecimalField(
        _("total tax (₦)"), max_digits=12, decimal_places=2, default=Decimal("0"),
    )
    # Payment
    is_paid = models.BooleanField(_("paid"), default=False)
    payment_reference = models.CharField(_("payment reference"), max_length=100, blank=True)
    paid_at = models.DateTimeField(_("paid at"), blank=True, null=True)
    status = models.CharField(
        _("status"), max_length=12,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.ISSUED,
    )
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="tax_invoices_created",
        verbose_name=_("created by"),
    )
    notes = models.TextField(_("notes"), blank=True)

    class Meta:
        verbose_name = _("tax invoice")
        verbose_name_plural = _("tax invoices")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["booking_reference"], name="taxes_taxinvoice_ref_idx"),
            models.Index(fields=["status"], name="taxes_taxinvoice_status_idx"),
            models.Index(fields=["service_type", "is_paid"], name="taxes_taxinvoice_svc_paid_idx"),
        ]

    def __str__(self):
        return f"{self.invoice_number} | {self.booking_reference} | ₦{self.total_tax_amount}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            while True:
                num = generate_tax_invoice_number()
                if not TaxInvoice.objects.filter(invoice_number=num).exists():
                    self.invoice_number = num
                    break
        super().save(*args, **kwargs)


class TaxInvoiceItem(models.Model):
    """
    A single line item on a tax invoice — one entry per tax type applied.
    """

    invoice = models.ForeignKey(
        TaxInvoice, on_delete=models.CASCADE, related_name="items",
        verbose_name=_("invoice"),
    )
    tax_type = models.ForeignKey(
        TaxType, on_delete=models.PROTECT, related_name="invoice_items",
        verbose_name=_("tax type"),
    )
    description = models.CharField(_("description"), max_length=200)
    quantity = models.PositiveSmallIntegerField(_("quantity / passengers"), default=1)
    unit_amount = models.DecimalField(_("unit amount (₦)"), max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(_("total (₦)"), max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _("tax invoice item")
        verbose_name_plural = _("tax invoice items")

    def __str__(self):
        return f"{self.invoice.invoice_number} – {self.tax_type.code}: ₦{self.total_amount}"

    def save(self, *args, **kwargs):
        self.total_amount = (self.unit_amount * self.quantity).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)
