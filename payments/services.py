"""
Paystack payment service for the Airport Management System.

Handles all interactions with the Paystack API.
"""

import hashlib
import hmac
import json
import logging
import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.utils import timezone

from .models import Payment, PaymentLog, PaymentStatus

logger = logging.getLogger(__name__)


class PaystackError(Exception):
    """Custom exception for Paystack errors."""

    pass


class PaystackService:
    """
    Service class for Paystack payment integration.

    Handles transaction initialization, verification, and webhook processing.
    """

    BASE_URL = "https://api.paystack.co"

    def __init__(self):
        self.secret_key = getattr(settings, "sk_test_fa2e18480fc85ab7fa0451a1c9e7e0003d3eb508", "")
        self.public_key = getattr(settings, "pk_test_f5719de7c38e7379359246b12ceac5e1e7e176b0", "")

        if not self.secret_key:
            logger.warning("sk_test_fa2e18480fc85ab7fa0451a1c9e7e0003d3eb508")

    @property
    def headers(self):
        """Return headers for Paystack API requests."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def generate_reference(self):
        """Generate a unique transaction reference."""
        return f"NAIA-{uuid.uuid4().hex[:12].upper()}"

    def initialize_transaction(self, payment: Payment, callback_url: str) -> dict:
        """
        Initialize a Paystack transaction.

        Args:
            payment: Payment model instance
            callback_url: URL to redirect after payment

        Returns:
            dict with authorization_url, access_code, and reference
        """
        url = f"{self.BASE_URL}/transaction/initialize"

        # Convert amount to kobo (smallest currency unit)
        amount_in_kobo = int(payment.amount * 100)

        # Generate reference if not exists
        if not payment.paystack_reference:
            payment.paystack_reference = self.generate_reference()
            payment.save(update_fields=["paystack_reference"])

        payload = {
            "email": payment.user.email,
            "amount": amount_in_kobo,
            "currency": payment.currency,
            "reference": payment.paystack_reference,
            "callback_url": callback_url,
            "metadata": {
                "booking_reference": payment.booking.reference,
                "payment_id": str(payment.id),
                "user_id": str(payment.user.id),
                "custom_fields": [
                    {
                        "display_name": "Booking Reference",
                        "variable_name": "booking_reference",
                        "value": payment.booking.reference,
                    },
                    {
                        "display_name": "Customer Name",
                        "variable_name": "customer_name",
                        "value": payment.user.get_full_name() or payment.user.email,
                    },
                ],
            },
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status"):
                result = data["data"]

                # Update payment with Paystack details
                payment.paystack_access_code = result.get("access_code", "")
                payment.paystack_authorization_url = result.get("authorization_url", "")
                payment.status = PaymentStatus.PROCESSING
                payment.save(update_fields=[
                    "paystack_access_code",
                    "paystack_authorization_url",
                    "status",
                ])

                # Log the event
                PaymentLog.objects.create(
                    payment=payment,
                    event_type=PaymentLog.EventType.INITIATED,
                    message="Transaction initialized with Paystack",
                    data=result,
                )

                return {
                    "authorization_url": result["authorization_url"],
                    "access_code": result["access_code"],
                    "reference": result["reference"],
                }
            else:
                raise PaystackError(data.get("message", "Failed to initialize transaction"))

        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack initialization error: {e}")
            PaymentLog.objects.create(
                payment=payment,
                event_type=PaymentLog.EventType.FAILED,
                message=f"Failed to initialize transaction: {str(e)}",
            )
            raise PaystackError(f"Failed to connect to payment gateway: {str(e)}")

    def verify_transaction(self, reference: str) -> dict:
        """
        Verify a Paystack transaction.

        Args:
            reference: Transaction reference

        Returns:
            dict with transaction details
        """
        url = f"{self.BASE_URL}/transaction/verify/{reference}"

        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status"):
                return data["data"]
            else:
                raise PaystackError(data.get("message", "Failed to verify transaction"))

        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack verification error: {e}")
            raise PaystackError(f"Failed to verify transaction: {str(e)}")

    def process_verification(self, payment: Payment) -> bool:
        """
        Verify and process a payment.

        Args:
            payment: Payment model instance

        Returns:
            True if payment was successful, False otherwise
        """
        try:
            data = self.verify_transaction(payment.paystack_reference)

            # Log verification
            PaymentLog.objects.create(
                payment=payment,
                event_type=PaymentLog.EventType.VERIFIED,
                message=f"Transaction verification: {data.get('status')}",
                data=data,
            )

            if data.get("status") == "success":
                # Update payment details
                payment.status = PaymentStatus.COMPLETED
                payment.paid_at = timezone.now()
                payment.gateway_response = data.get("gateway_response", "")
                payment.channel = data.get("channel", "")

                # Card details
                authorization = data.get("authorization", {})
                payment.card_last4 = authorization.get("last4", "")
                payment.card_type = authorization.get("card_type", "")
                payment.bank_name = authorization.get("bank", "")

                payment.metadata = data
                payment.save()

                # Log completion
                PaymentLog.objects.create(
                    payment=payment,
                    event_type=PaymentLog.EventType.COMPLETED,
                    message="Payment completed successfully",
                )

                return True

            elif data.get("status") == "failed":
                payment.status = PaymentStatus.FAILED
                payment.gateway_response = data.get("gateway_response", "Payment failed")
                payment.save(update_fields=["status", "gateway_response"])

                PaymentLog.objects.create(
                    payment=payment,
                    event_type=PaymentLog.EventType.FAILED,
                    message=f"Payment failed: {data.get('gateway_response')}",
                    data=data,
                )

                return False

            else:
                # Still pending or other status
                return False

        except PaystackError as e:
            logger.error(f"Payment verification failed: {e}")
            return False

    def validate_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Validate Paystack webhook signature.

        Args:
            payload: Raw request body
            signature: X-Paystack-Signature header value

        Returns:
            True if signature is valid
        """
        if not self.secret_key:
            return False

        expected = hmac.new(
            self.secret_key.encode("utf-8"),
            payload,
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def process_webhook(self, event_data: dict) -> bool:
        """
        Process a Paystack webhook event.

        Args:
            event_data: Webhook payload

        Returns:
            True if processed successfully
        """
        event = event_data.get("event")
        data = event_data.get("data", {})

        if event == "charge.success":
            reference = data.get("reference")
            if not reference:
                return False

            try:
                payment = Payment.objects.get(paystack_reference=reference)

                # Log webhook
                PaymentLog.objects.create(
                    payment=payment,
                    event_type=PaymentLog.EventType.WEBHOOK,
                    message=f"Webhook received: {event}",
                    data=data,
                )

                # Process if not already completed
                if payment.status != PaymentStatus.COMPLETED:
                    return self.process_verification(payment)

                return True

            except Payment.DoesNotExist:
                logger.warning(f"Payment not found for reference: {reference}")
                return False

        return True

    def initiate_refund(self, payment: Payment, amount: Decimal = None, reason: str = "") -> dict:
        """
        Initiate a refund for a payment.

        Args:
            payment: Payment to refund
            amount: Amount to refund (None for full refund)
            reason: Reason for refund

        Returns:
            dict with refund details
        """
        if not payment.is_refundable:
            raise PaystackError("Payment is not refundable")

        url = f"{self.BASE_URL}/refund"

        refund_amount = amount or payment.refundable_amount
        amount_in_kobo = int(refund_amount * 100)

        payload = {
            "transaction": payment.paystack_reference,
            "amount": amount_in_kobo,
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("status"):
                result = data["data"]

                # Update payment
                payment.refund_amount += refund_amount
                payment.refund_reason = reason
                payment.refunded_at = timezone.now()

                if payment.refund_amount >= payment.amount:
                    payment.status = PaymentStatus.REFUNDED
                else:
                    payment.status = PaymentStatus.PARTIALLY_REFUNDED

                payment.save()

                # Log refund
                PaymentLog.objects.create(
                    payment=payment,
                    event_type=PaymentLog.EventType.REFUND_INITIATED,
                    message=f"Refund initiated: ₦{refund_amount}",
                    data=result,
                )

                return result

            else:
                raise PaystackError(data.get("message", "Failed to initiate refund"))

        except requests.exceptions.RequestException as e:
            logger.error(f"Paystack refund error: {e}")
            raise PaystackError(f"Failed to initiate refund: {str(e)}")


# Singleton instance
paystack_service = PaystackService()
