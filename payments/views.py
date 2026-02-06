"""
Payment views for the Airport Management System.

Handles payment initialization, verification, and webhooks.
"""

import json
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, TemplateView

from bookings.models import Booking, BookingStatus

from .models import Payment, PaymentLog, PaymentStatus
from .services import PaystackError, paystack_service

logger = logging.getLogger(__name__)


class InitiatePaymentView(LoginRequiredMixin, View):
    """
    Initiate payment for a booking.
    """

    login_url = "/accounts/login/"

    def get(self, request, reference):
        booking = get_object_or_404(
            Booking.objects.select_related("flight", "flight__airline"),
            reference=reference,
            user=request.user,
        )

        # Check if booking can be paid
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            messages.error(request, "This booking cannot be paid for.")
            return redirect("accounts:booking_detail", reference=reference)

        # Check for existing pending/completed payment
        existing_payment = Payment.objects.filter(
            booking=booking,
            status__in=[PaymentStatus.COMPLETED, PaymentStatus.PROCESSING]
        ).first()

        if existing_payment:
            if existing_payment.status == PaymentStatus.COMPLETED:
                messages.info(request, "This booking has already been paid for.")
                return redirect("accounts:booking_detail", reference=reference)
            else:
                # Redirect to existing payment
                return redirect(existing_payment.paystack_authorization_url)

        # Create new payment
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.total_price,
            currency="NGN",
            status=PaymentStatus.PENDING,
            ip_address=self.get_client_ip(request),
        )

        # Build callback URL
        callback_url = request.build_absolute_uri(
            reverse("payments:verify", kwargs={"reference": payment.paystack_reference})
        )

        try:
            result = paystack_service.initialize_transaction(payment, callback_url)
            return redirect(result["authorization_url"])

        except PaystackError as e:
            messages.error(request, f"Payment initialization failed: {str(e)}")
            payment.status = PaymentStatus.FAILED
            payment.gateway_response = str(e)
            payment.save()
            return redirect("bookings:payment")

    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class VerifyPaymentView(View):
    """
    Verify payment after Paystack redirect.
    """

    def get(self, request, reference):
        payment = get_object_or_404(Payment, paystack_reference=reference)

        # Verify with Paystack
        success = paystack_service.process_verification(payment)

        if success:
            # Update booking status
            booking = payment.booking
            booking.status = BookingStatus.CONFIRMED
            booking.payment_status = "COMPLETED"
            booking.payment_reference = payment.paystack_reference
            booking.confirmed_at = timezone.now()
            booking.save()

            messages.success(request, "Payment successful! Your booking is confirmed.")
            return redirect("bookings:confirmation", reference=booking.reference)
        else:
            messages.error(
                request,
                "Payment verification failed. Please try again or contact support."
            )
            return redirect("payments:failed", reference=reference)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """
    Payment success page.
    """

    template_name = "payments/success.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reference = self.kwargs.get("reference")

        payment = get_object_or_404(
            Payment.objects.select_related("booking", "booking__flight"),
            paystack_reference=reference,
            user=self.request.user,
        )

        context["payment"] = payment
        context["booking"] = payment.booking
        return context


class PaymentFailedView(TemplateView):
    """
    Payment failed page.
    """

    template_name = "payments/failed.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reference = self.kwargs.get("reference")

        try:
            payment = Payment.objects.select_related("booking").get(
                paystack_reference=reference
            )
            context["payment"] = payment
            context["booking"] = payment.booking
        except Payment.DoesNotExist:
            pass

        return context


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """
    View user's payment history.
    """

    template_name = "payments/history.html"
    context_object_name = "payments"
    paginate_by = 10
    login_url = "/accounts/login/"

    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user
        ).select_related(
            "booking", "booking__flight", "booking__flight__airline"
        ).order_by("-created_at")


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """
    View payment details.
    """

    template_name = "payments/detail.html"
    context_object_name = "payment"
    login_url = "/accounts/login/"

    def get_object(self):
        return get_object_or_404(
            Payment.objects.select_related(
                "booking", "booking__flight", "booking__flight__airline"
            ),
            id=self.kwargs["pk"],
            user=self.request.user,
        )


@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(View):
    """
    Handle Paystack webhook events.
    """

    def post(self, request):
        # Get signature
        signature = request.headers.get("X-Paystack-Signature", "")

        # Validate signature
        if not paystack_service.validate_webhook_signature(request.body, signature):
            logger.warning("Invalid Paystack webhook signature")
            return HttpResponse(status=400)

        try:
            payload = json.loads(request.body)
            logger.info(f"Paystack webhook: {payload.get('event')}")

            # Process the webhook
            paystack_service.process_webhook(payload)

            return HttpResponse(status=200)

        except json.JSONDecodeError:
            logger.error("Invalid JSON in Paystack webhook")
            return HttpResponse(status=400)

        except Exception as e:
            logger.error(f"Error processing Paystack webhook: {e}")
            return HttpResponse(status=500)


class CheckPaymentStatusView(LoginRequiredMixin, View):
    """
    AJAX endpoint to check payment status.
    """

    login_url = "/accounts/login/"

    def get(self, request, reference):
        try:
            payment = Payment.objects.get(
                paystack_reference=reference,
                user=request.user,
            )

            return JsonResponse({
                "status": payment.status,
                "is_completed": payment.status == PaymentStatus.COMPLETED,
                "message": payment.gateway_response or payment.get_status_display(),
            })

        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)


class RetryPaymentView(LoginRequiredMixin, View):
    """
    Retry a failed payment.
    """

    login_url = "/accounts/login/"

    def post(self, request, reference):
        payment = get_object_or_404(
            Payment,
            paystack_reference=reference,
            user=request.user,
            status__in=[PaymentStatus.FAILED, PaymentStatus.CANCELLED],
        )

        # Create a new payment for the same booking
        new_payment = Payment.objects.create(
            booking=payment.booking,
            user=request.user,
            amount=payment.booking.total_price,
            currency="NGN",
            status=PaymentStatus.PENDING,
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        # Build callback URL
        callback_url = request.build_absolute_uri(
            reverse("payments:verify", kwargs={"reference": new_payment.paystack_reference})
        )

        try:
            result = paystack_service.initialize_transaction(new_payment, callback_url)
            return redirect(result["authorization_url"])

        except PaystackError as e:
            messages.error(request, f"Payment initialization failed: {str(e)}")
            new_payment.status = PaymentStatus.FAILED
            new_payment.gateway_response = str(e)
            new_payment.save()
            return redirect("payments:failed", reference=payment.paystack_reference)
