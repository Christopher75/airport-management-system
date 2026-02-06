"""
Notification models for the Airport Management System.

Manages user notifications across multiple channels.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import TimeStampedModel, TimeStampedUUIDModel


class NotificationType(models.TextChoices):
    """Types of notifications in the system."""

    # Booking Related
    BOOKING_CONFIRMATION = "BOOKING_CONFIRMATION", _("Booking Confirmation")
    BOOKING_CANCELLATION = "BOOKING_CANCELLATION", _("Booking Cancellation")
    BOOKING_REMINDER = "BOOKING_REMINDER", _("Booking Reminder")

    # Payment Related
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED", _("Payment Received")
    PAYMENT_FAILED = "PAYMENT_FAILED", _("Payment Failed")
    REFUND_PROCESSED = "REFUND_PROCESSED", _("Refund Processed")

    # Flight Related
    FLIGHT_DELAY = "FLIGHT_DELAY", _("Flight Delay")
    FLIGHT_CANCELLATION = "FLIGHT_CANCELLATION", _("Flight Cancellation")
    FLIGHT_GATE_CHANGE = "FLIGHT_GATE_CHANGE", _("Gate Change")
    FLIGHT_BOARDING = "FLIGHT_BOARDING", _("Boarding Call")
    FLIGHT_DEPARTURE = "FLIGHT_DEPARTURE", _("Flight Departed")
    FLIGHT_ARRIVAL = "FLIGHT_ARRIVAL", _("Flight Arrived")

    # Check-in Related
    CHECKIN_OPEN = "CHECKIN_OPEN", _("Check-in Open")
    CHECKIN_REMINDER = "CHECKIN_REMINDER", _("Check-in Reminder")

    # Account Related
    ACCOUNT_WELCOME = "ACCOUNT_WELCOME", _("Welcome")
    ACCOUNT_PASSWORD_RESET = "ACCOUNT_PASSWORD_RESET", _("Password Reset")
    ACCOUNT_EMAIL_VERIFICATION = "ACCOUNT_EMAIL_VERIFICATION", _("Email Verification")

    # Promotional
    PROMOTION = "PROMOTION", _("Promotion")
    LOYALTY_POINTS = "LOYALTY_POINTS", _("Loyalty Points Update")

    # System
    SYSTEM_MAINTENANCE = "SYSTEM_MAINTENANCE", _("System Maintenance")
    GENERAL = "GENERAL", _("General")


class NotificationChannel(models.TextChoices):
    """Channels through which notifications can be sent."""

    EMAIL = "EMAIL", _("Email")
    SMS = "SMS", _("SMS")
    PUSH = "PUSH", _("Push Notification")
    IN_APP = "IN_APP", _("In-App Notification")


class NotificationPriority(models.TextChoices):
    """Priority levels for notifications."""

    LOW = "LOW", _("Low")
    NORMAL = "NORMAL", _("Normal")
    HIGH = "HIGH", _("High")
    URGENT = "URGENT", _("Urgent")


class Notification(TimeStampedUUIDModel):
    """
    Represents a notification sent to a user.

    Notifications can be sent through multiple channels and
    track read/delivery status.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    # Content
    notification_type = models.CharField(
        _("type"),
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL,
    )
    title = models.CharField(
        _("title"),
        max_length=255,
    )
    message = models.TextField(
        _("message"),
    )
    html_message = models.TextField(
        _("HTML message"),
        blank=True,
        help_text=_("HTML version of the message for email"),
    )

    # Channel
    channel = models.CharField(
        _("channel"),
        max_length=10,
        choices=NotificationChannel.choices,
        default=NotificationChannel.IN_APP,
    )

    # Priority
    priority = models.CharField(
        _("priority"),
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
    )

    # Status
    is_read = models.BooleanField(
        _("read"),
        default=False,
    )
    read_at = models.DateTimeField(
        _("read at"),
        null=True,
        blank=True,
    )
    is_sent = models.BooleanField(
        _("sent"),
        default=False,
    )
    sent_at = models.DateTimeField(
        _("sent at"),
        null=True,
        blank=True,
    )
    is_delivered = models.BooleanField(
        _("delivered"),
        default=False,
    )
    delivered_at = models.DateTimeField(
        _("delivered at"),
        null=True,
        blank=True,
    )

    # Related Objects (optional)
    related_booking_id = models.UUIDField(
        _("related booking"),
        null=True,
        blank=True,
    )
    related_flight_id = models.IntegerField(
        _("related flight"),
        null=True,
        blank=True,
    )
    related_payment_id = models.UUIDField(
        _("related payment"),
        null=True,
        blank=True,
    )

    # Action
    action_url = models.URLField(
        _("action URL"),
        blank=True,
        help_text=_("URL to navigate to when notification is clicked"),
    )
    action_text = models.CharField(
        _("action text"),
        max_length=50,
        blank=True,
        help_text=_("Text for the action button"),
    )

    # Metadata
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
    )

    # Error tracking
    error_message = models.TextField(
        _("error message"),
        blank=True,
        help_text=_("Error message if sending failed"),
    )

    class Meta:
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "notification_type"]),
            models.Index(fields=["channel", "is_sent"]),
        ]

    def __str__(self):
        return f"{self.notification_type} - {self.title}"

    def mark_as_read(self):
        """Mark the notification as read."""
        if not self.is_read:
            from django.utils import timezone

            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def mark_as_sent(self):
        """Mark the notification as sent."""
        if not self.is_sent:
            from django.utils import timezone

            self.is_sent = True
            self.sent_at = timezone.now()
            self.save(update_fields=["is_sent", "sent_at"])

    def mark_as_delivered(self):
        """Mark the notification as delivered."""
        if not self.is_delivered:
            from django.utils import timezone

            self.is_delivered = True
            self.delivered_at = timezone.now()
            self.save(update_fields=["is_delivered", "delivered_at"])


class NotificationPreference(TimeStampedModel):
    """
    User preferences for receiving notifications.

    Allows users to customize which notification types they receive
    on which channels.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    # Email Preferences
    email_booking = models.BooleanField(
        _("booking emails"),
        default=True,
    )
    email_flight_updates = models.BooleanField(
        _("flight update emails"),
        default=True,
    )
    email_payment = models.BooleanField(
        _("payment emails"),
        default=True,
    )
    email_promotions = models.BooleanField(
        _("promotional emails"),
        default=False,
    )
    email_account = models.BooleanField(
        _("account emails"),
        default=True,
    )

    # SMS Preferences
    sms_booking = models.BooleanField(
        _("booking SMS"),
        default=True,
    )
    sms_flight_updates = models.BooleanField(
        _("flight update SMS"),
        default=True,
    )
    sms_payment = models.BooleanField(
        _("payment SMS"),
        default=False,
    )
    sms_promotions = models.BooleanField(
        _("promotional SMS"),
        default=False,
    )

    # Push Notification Preferences
    push_booking = models.BooleanField(
        _("booking push notifications"),
        default=True,
    )
    push_flight_updates = models.BooleanField(
        _("flight update push notifications"),
        default=True,
    )
    push_payment = models.BooleanField(
        _("payment push notifications"),
        default=True,
    )
    push_promotions = models.BooleanField(
        _("promotional push notifications"),
        default=False,
    )

    # In-App Preferences
    in_app_all = models.BooleanField(
        _("all in-app notifications"),
        default=True,
    )

    # Quiet Hours
    quiet_hours_enabled = models.BooleanField(
        _("quiet hours enabled"),
        default=False,
    )
    quiet_hours_start = models.TimeField(
        _("quiet hours start"),
        null=True,
        blank=True,
        help_text=_("Start time for quiet hours (no notifications)"),
    )
    quiet_hours_end = models.TimeField(
        _("quiet hours end"),
        null=True,
        blank=True,
        help_text=_("End time for quiet hours"),
    )

    class Meta:
        verbose_name = _("notification preference")
        verbose_name_plural = _("notification preferences")

    def __str__(self):
        return f"Notification Preferences for {self.user.email}"
