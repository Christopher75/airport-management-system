"""
Notification service for the Airport Management System.

Handles sending notifications via multiple channels (email, SMS, in-app).
"""

import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from .models import (
    Notification,
    NotificationChannel,
    NotificationPreference,
    NotificationPriority,
    NotificationType,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for creating and sending notifications.
    """

    def __init__(self):
        self.from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL", "noreply@naia.ng"
        )

    def create_notification(
        self,
        user,
        notification_type: str,
        title: str,
        message: str,
        channel: str = NotificationChannel.IN_APP,
        priority: str = NotificationPriority.NORMAL,
        html_message: str = "",
        action_url: str = "",
        action_text: str = "",
        related_booking_id=None,
        related_flight_id=None,
        related_payment_id=None,
        metadata: dict = None,
    ) -> Notification:
        """
        Create a notification record.

        Args:
            user: The user to notify
            notification_type: Type of notification
            title: Notification title
            message: Plain text message
            channel: Notification channel
            priority: Notification priority
            html_message: HTML version of message
            action_url: URL for action button
            action_text: Text for action button
            related_booking_id: Related booking UUID
            related_flight_id: Related flight ID
            related_payment_id: Related payment UUID
            metadata: Additional data

        Returns:
            Notification instance
        """
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            html_message=html_message,
            channel=channel,
            priority=priority,
            action_url=action_url,
            action_text=action_text,
            related_booking_id=related_booking_id,
            related_flight_id=related_flight_id,
            related_payment_id=related_payment_id,
            metadata=metadata or {},
        )

        return notification

    def send_email(
        self,
        user,
        subject: str,
        template_name: str,
        context: dict,
        notification_type: str = NotificationType.GENERAL,
    ) -> bool:
        """
        Send an email notification.

        Args:
            user: User to send email to
            subject: Email subject
            template_name: Name of email template
            context: Template context
            notification_type: Type for logging

        Returns:
            True if sent successfully
        """
        # Check user preferences
        if not self._should_send_email(user, notification_type):
            logger.info(f"Email disabled for {user.email}: {notification_type}")
            return False

        try:
            # Add common context
            context.update({
                "user": user,
                "site_name": "Nnamdi Azikiwe International Airport",
                "site_url": getattr(settings, "SITE_URL", "http://localhost:8000"),
                "support_email": "support@naia.ng",
                "support_phone": "+234 9 123 4567",
            })

            # Render templates
            html_content = render_to_string(
                f"notifications/email/{template_name}.html", context
            )
            text_content = strip_tags(html_content)

            # Create email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[user.email],
            )
            email.attach_alternative(html_content, "text/html")

            # Send
            email.send(fail_silently=False)

            # Create notification record
            self.create_notification(
                user=user,
                notification_type=notification_type,
                title=subject,
                message=text_content[:500],
                html_message=html_content,
                channel=NotificationChannel.EMAIL,
                is_sent=True,
                sent_at=timezone.now(),
            )

            logger.info(f"Email sent to {user.email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")
            return False

    def send_booking_confirmation(self, booking) -> bool:
        """Send booking confirmation email."""
        context = {
            "booking": booking,
            "flight": booking.flight,
            "passengers": booking.passengers.all(),
        }

        return self.send_email(
            user=booking.user,
            subject=f"Booking Confirmed - {booking.reference}",
            template_name="booking_confirmation",
            context=context,
            notification_type=NotificationType.BOOKING_CONFIRMATION,
        )

    def send_payment_receipt(self, payment) -> bool:
        """Send payment receipt email."""
        context = {
            "payment": payment,
            "booking": payment.booking,
        }

        return self.send_email(
            user=payment.user,
            subject=f"Payment Receipt - {payment.paystack_reference}",
            template_name="payment_receipt",
            context=context,
            notification_type=NotificationType.PAYMENT_RECEIVED,
        )

    def send_flight_update(self, booking, update_type: str, message: str) -> bool:
        """Send flight update notification."""
        # Create in-app notification
        self.create_notification(
            user=booking.user,
            notification_type=update_type,
            title=f"Flight Update - {booking.flight.flight_number}",
            message=message,
            channel=NotificationChannel.IN_APP,
            priority=NotificationPriority.HIGH,
            action_url=f"/dashboard/bookings/{booking.reference}/",
            action_text="View Booking",
            related_booking_id=booking.id,
            related_flight_id=booking.flight.id,
        )

        # Send email
        context = {
            "booking": booking,
            "flight": booking.flight,
            "update_type": update_type,
            "update_message": message,
        }

        return self.send_email(
            user=booking.user,
            subject=f"Flight Update - {booking.flight.flight_number}",
            template_name="flight_update",
            context=context,
            notification_type=update_type,
        )

    def send_checkin_reminder(self, booking) -> bool:
        """Send check-in reminder notification."""
        message = (
            f"Online check-in is now available for your flight "
            f"{booking.flight.flight_number} to {booking.flight.destination.city}. "
            f"Check in now to select your seats."
        )

        # Create in-app notification
        self.create_notification(
            user=booking.user,
            notification_type=NotificationType.CHECKIN_OPEN,
            title="Check-in Now Open",
            message=message,
            channel=NotificationChannel.IN_APP,
            priority=NotificationPriority.HIGH,
            action_url=f"/dashboard/bookings/{booking.reference}/",
            action_text="Check In",
            related_booking_id=booking.id,
        )

        context = {
            "booking": booking,
            "flight": booking.flight,
        }

        return self.send_email(
            user=booking.user,
            subject=f"Check-in Open - {booking.flight.flight_number}",
            template_name="checkin_reminder",
            context=context,
            notification_type=NotificationType.CHECKIN_OPEN,
        )

    def notify_in_app(
        self,
        user,
        notification_type: str,
        title: str,
        message: str,
        action_url: str = "",
        action_text: str = "",
        priority: str = NotificationPriority.NORMAL,
        **kwargs,
    ) -> Notification:
        """
        Create an in-app notification.

        Args:
            user: User to notify
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            action_url: Optional action URL
            action_text: Optional action button text
            priority: Notification priority

        Returns:
            Notification instance
        """
        return self.create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=NotificationChannel.IN_APP,
            priority=priority,
            action_url=action_url,
            action_text=action_text,
            **kwargs,
        )

    def _should_send_email(self, user, notification_type: str) -> bool:
        """Check if user has email enabled for notification type."""
        try:
            prefs = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            # Default to True if no preferences set
            return True

        # Map notification types to preference fields
        type_to_pref = {
            NotificationType.BOOKING_CONFIRMATION: "email_booking",
            NotificationType.BOOKING_CANCELLATION: "email_booking",
            NotificationType.BOOKING_REMINDER: "email_booking",
            NotificationType.PAYMENT_RECEIVED: "email_payment",
            NotificationType.PAYMENT_FAILED: "email_payment",
            NotificationType.REFUND_PROCESSED: "email_payment",
            NotificationType.FLIGHT_DELAY: "email_flight_updates",
            NotificationType.FLIGHT_CANCELLATION: "email_flight_updates",
            NotificationType.FLIGHT_GATE_CHANGE: "email_flight_updates",
            NotificationType.FLIGHT_BOARDING: "email_flight_updates",
            NotificationType.CHECKIN_OPEN: "email_flight_updates",
            NotificationType.CHECKIN_REMINDER: "email_flight_updates",
            NotificationType.ACCOUNT_WELCOME: "email_account",
            NotificationType.ACCOUNT_PASSWORD_RESET: "email_account",
            NotificationType.PROMOTION: "email_promotions",
            NotificationType.LOYALTY_POINTS: "email_promotions",
        }

        pref_field = type_to_pref.get(notification_type)
        if pref_field:
            return getattr(prefs, pref_field, True)

        return True

    def get_unread_count(self, user) -> int:
        """Get count of unread in-app notifications."""
        return Notification.objects.filter(
            user=user,
            channel=NotificationChannel.IN_APP,
            is_read=False,
        ).count()

    def get_recent_notifications(self, user, limit: int = 10):
        """Get recent in-app notifications for user."""
        return Notification.objects.filter(
            user=user,
            channel=NotificationChannel.IN_APP,
        ).order_by("-created_at")[:limit]

    def mark_as_read(self, notification_id, user) -> bool:
        """Mark a notification as read."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=user,
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    def mark_all_as_read(self, user) -> int:
        """Mark all notifications as read for user."""
        count = Notification.objects.filter(
            user=user,
            channel=NotificationChannel.IN_APP,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )
        return count


# Singleton instance
notification_service = NotificationService()
