"""
Payment models for the Airport Management System.

Manages payment processing and transaction records for Paystack integration.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from bookings.models import Booking
from core.models import TimeStampedUUIDModel


class PaymentStatus(models.TextChoices):
    """Payment status choices."""

    PENDING = "PENDING", _("Pending")
    PROCESSING = "PROCESSING", _("Processing")
    COMPLETED = "COMPLETED", _("Completed")
    FAILED = "FAILED", _("Failed")
    CANCELLED = "CANCELLED", _("Cancelled")
    REFUNDED = "REFUNDED", _("Refunded")
    PARTIALLY_REFUNDED = "PARTIALLY_REFUNDED", _("Partially Refunded")


class PaymentMethod(models.TextChoices):
    """Payment method choices."""

    CARD = "CARD", _("Card")
    BANK_TRANSFER = "BANK_TRANSFER", _("Bank Transfer")
    USSD = "USSD", _("USSD")
    QR = "QR", _("QR Code")
    MOBILE_MONEY = "MOBILE_MONEY", _("Mobile Money")
    PAYSTACK = "PAYSTACK", _("Paystack")


class Payment(TimeStampedUUIDModel):
    """
    Represents a payment transaction for a booking.

    Stores payment details including gateway references, amounts,
    and transaction status for Paystack integration.
    """

    # Booking Reference
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    # User who made the payment
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    # Amount
    amount = models.DecimalField(
        _("amount"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text=_("Payment amount in Nigerian Naira"),
    )
    currency = models.CharField(
        _("currency"),
        max_length=3,
        default="NGN",
    )

    # Payment Method
    payment_method = models.CharField(
        _("payment method"),
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.PAYSTACK,
    )

    # Status
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    # Paystack References
    paystack_reference = models.CharField(
        _("Paystack reference"),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Unique transaction reference from Paystack"),
    )
    paystack_access_code = models.CharField(
        _("Paystack access code"),
        max_length=100,
        blank=True,
        help_text=_("Access code for Paystack checkout"),
    )
    paystack_authorization_url = models.URLField(
        _("Paystack authorization URL"),
        blank=True,
        help_text=_("URL to redirect user for payment"),
    )

    # Transaction Details
    card_last4 = models.CharField(
        _("card last 4 digits"),
        max_length=4,
        blank=True,
    )
    card_type = models.CharField(
        _("card type"),
        max_length=20,
        blank=True,
        help_text=_("e.g., visa, mastercard"),
    )
    bank_name = models.CharField(
        _("bank name"),
        max_length=100,
        blank=True,
    )
    channel = models.CharField(
        _("payment channel"),
        max_length=50,
        blank=True,
        help_text=_("e.g., card, bank, ussd"),
    )

    # Gateway Response
    gateway_response = models.TextField(
        _("gateway response"),
        blank=True,
        help_text=_("Response message from payment gateway"),
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
    )

    # Timestamps
    paid_at = models.DateTimeField(
        _("paid at"),
        null=True,
        blank=True,
    )

    # Refund Information
    refund_amount = models.DecimalField(
        _("refund amount"),
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    refunded_at = models.DateTimeField(
        _("refunded at"),
        null=True,
        blank=True,
    )
    refund_reason = models.TextField(
        _("refund reason"),
        blank=True,
    )

    # Metadata
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional payment data from gateway"),
    )

    class Meta:
        verbose_name = _("payment")
        verbose_name_plural = _("payments")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["paystack_reference"]),
            models.Index(fields=["booking"]),
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.booking.reference} - ₦{self.amount}"

    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_refundable(self):
        """Check if payment can be refunded."""
        if self.status != PaymentStatus.COMPLETED:
            return False
        if self.refund_amount >= self.amount:
            return False
        return True

    @property
    def refundable_amount(self):
        """Return the amount that can still be refunded."""
        return self.amount - self.refund_amount


class PaymentLog(TimeStampedUUIDModel):
    """
    Logs payment events and webhook callbacks.

    Provides audit trail for payment processing and debugging.
    """

    class EventType(models.TextChoices):
        INITIATED = "INITIATED", _("Payment Initiated")
        WEBHOOK = "WEBHOOK", _("Webhook Received")
        VERIFIED = "VERIFIED", _("Payment Verified")
        COMPLETED = "COMPLETED", _("Payment Completed")
        FAILED = "FAILED", _("Payment Failed")
        REFUND_INITIATED = "REFUND_INITIATED", _("Refund Initiated")
        REFUND_COMPLETED = "REFUND_COMPLETED", _("Refund Completed")

    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    event_type = models.CharField(
        _("event type"),
        max_length=20,
        choices=EventType.choices,
    )
    message = models.TextField(
        _("message"),
        blank=True,
    )
    data = models.JSONField(
        _("data"),
        default=dict,
        blank=True,
        help_text=_("Raw data from event"),
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("payment log")
        verbose_name_plural = _("payment logs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.payment.id} - {self.event_type} - {self.created_at}"
