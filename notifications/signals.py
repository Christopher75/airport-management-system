"""
Django signals for automatic notification triggers.

Sends notifications when key events occur (booking confirmation, payment, etc.)
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from bookings.models import Booking, BookingStatus
from payments.models import Payment, PaymentStatus

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Booking)
def booking_status_changed(sender, instance, created, **kwargs):
    """
    Send notification when booking status changes.
    """
    # Import here to avoid circular imports
    from .services import notification_service
    from .models import NotificationType

    # Only process if booking was just confirmed
    if instance.status == BookingStatus.CONFIRMED:
        # Check if this is a status change (not just created)
        # We use update_fields to detect if this is a status update
        update_fields = kwargs.get('update_fields')

        # Send confirmation if booking just became confirmed
        if created or (update_fields and 'status' in update_fields):
            try:
                # Create in-app notification
                notification_service.notify_in_app(
                    user=instance.user,
                    notification_type=NotificationType.BOOKING_CONFIRMATION,
                    title="Booking Confirmed!",
                    message=f"Your booking {instance.reference} for flight {instance.flight.flight_number} "
                            f"from {instance.flight.origin.code} to {instance.flight.destination.code} "
                            f"on {instance.flight.scheduled_departure.strftime('%b %d, %Y')} has been confirmed.",
                    action_url=f"/dashboard/bookings/{instance.reference}/",
                    action_text="View Booking",
                    related_booking_id=instance.id,
                    related_flight_id=instance.flight.id,
                )

                # Send email
                notification_service.send_booking_confirmation(instance)

                logger.info(f"Booking confirmation sent for {instance.reference}")

            except Exception as e:
                logger.error(f"Failed to send booking confirmation for {instance.reference}: {e}")

    elif instance.status == BookingStatus.CANCELLED:
        try:
            notification_service.notify_in_app(
                user=instance.user,
                notification_type=NotificationType.BOOKING_CANCELLATION,
                title="Booking Cancelled",
                message=f"Your booking {instance.reference} has been cancelled. "
                        f"If you have any questions, please contact our support team.",
                action_url=f"/dashboard/bookings/{instance.reference}/",
                action_text="View Details",
                related_booking_id=instance.id,
            )

            logger.info(f"Booking cancellation notification sent for {instance.reference}")

        except Exception as e:
            logger.error(f"Failed to send booking cancellation for {instance.reference}: {e}")


@receiver(post_save, sender=Payment)
def payment_completed(sender, instance, created, **kwargs):
    """
    Send notification when payment is completed.
    """
    from .services import notification_service
    from .models import NotificationType

    if instance.status == PaymentStatus.COMPLETED:
        update_fields = kwargs.get('update_fields')

        # Send if payment just completed
        if not created and update_fields and 'status' in update_fields:
            try:
                # Create in-app notification
                notification_service.notify_in_app(
                    user=instance.user,
                    notification_type=NotificationType.PAYMENT_RECEIVED,
                    title="Payment Successful",
                    message=f"Your payment of NGN {instance.amount:,.2f} for booking "
                            f"{instance.booking.reference} has been received.",
                    action_url=f"/dashboard/bookings/{instance.booking.reference}/",
                    action_text="View Booking",
                    related_booking_id=instance.booking.id,
                    related_payment_id=instance.id,
                )

                # Send email receipt
                notification_service.send_payment_receipt(instance)

                logger.info(f"Payment receipt sent for {instance.paystack_reference}")

            except Exception as e:
                logger.error(f"Failed to send payment receipt for {instance.paystack_reference}: {e}")

    elif instance.status == PaymentStatus.FAILED:
        try:
            notification_service.notify_in_app(
                user=instance.user,
                notification_type=NotificationType.PAYMENT_FAILED,
                title="Payment Failed",
                message=f"Your payment for booking {instance.booking.reference} could not be processed. "
                        f"Please try again or use a different payment method.",
                action_url=f"/bookings/select/{instance.booking.flight.id}/",
                action_text="Retry Payment",
                related_booking_id=instance.booking.id,
            )

            logger.info(f"Payment failure notification sent for {instance.paystack_reference}")

        except Exception as e:
            logger.error(f"Failed to send payment failure notification: {e}")
