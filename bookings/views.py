"""
Booking views for the Airport Management System.

Implements multi-step booking flow:
1. Select Flight
2. Passenger Details
3. Seat Selection (Optional)
4. Review & Confirm
5. Payment
6. Confirmation
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, TemplateView

from flights.models import Flight, FlightStatus

from .forms import PassengerForm, PassengerFormSet
from .models import Booking, BookingStatus, Passenger, SeatClass


class SelectFlightView(View):
    """
    Step 1: Select flight and cabin class.
    Initializes booking session.
    """

    template_name = "bookings/select_flight.html"

    def get(self, request, flight_id):
        flight = get_object_or_404(Flight, pk=flight_id)

        # Check if flight is bookable
        if not flight.is_bookable:
            messages.error(request, "This flight is no longer available for booking.")
            return redirect("flights:search")

        # Get parameters
        seat_class = request.GET.get("seat_class", "ECONOMY")
        passengers = int(request.GET.get("passengers", 1))

        # Validate seat class and availability
        if seat_class == "ECONOMY" and flight.available_economy_seats < passengers:
            messages.error(request, "Not enough economy seats available.")
            return redirect("flights:detail", pk=flight_id)
        elif seat_class == "BUSINESS" and flight.available_business_seats < passengers:
            messages.error(request, "Not enough business seats available.")
            return redirect("flights:detail", pk=flight_id)
        elif seat_class == "FIRST" and flight.available_first_class_seats < passengers:
            messages.error(request, "Not enough first class seats available.")
            return redirect("flights:detail", pk=flight_id)

        # Get price based on class
        if seat_class == "BUSINESS":
            unit_price = flight.business_price
        elif seat_class == "FIRST":
            unit_price = flight.first_class_price
        else:
            unit_price = flight.economy_price

        # Calculate totals
        base_price = unit_price * passengers
        taxes = base_price * Decimal("0.10")  # 10% tax
        fees = Decimal("2000.00")  # Service fee
        total = base_price + taxes + fees

        context = {
            "flight": flight,
            "seat_class": seat_class,
            "passengers": passengers,
            "unit_price": unit_price,
            "base_price": base_price,
            "taxes": taxes,
            "fees": fees,
            "total": total,
        }

        return render(request, self.template_name, context)

    def post(self, request, flight_id):
        flight = get_object_or_404(Flight, pk=flight_id)

        if not flight.is_bookable:
            messages.error(request, "This flight is no longer available for booking.")
            return redirect("flights:search")

        seat_class = request.POST.get("seat_class", "ECONOMY")
        passengers = int(request.POST.get("passengers", 1))

        # Get price
        if seat_class == "BUSINESS":
            unit_price = flight.business_price
        elif seat_class == "FIRST":
            unit_price = flight.first_class_price
        else:
            unit_price = flight.economy_price

        # Calculate totals
        base_price = unit_price * passengers
        taxes = base_price * Decimal("0.10")
        fees = Decimal("2000.00")
        total = base_price + taxes + fees

        # Store in session
        request.session["booking"] = {
            "flight_id": flight.pk,
            "seat_class": seat_class,
            "passenger_count": passengers,
            "unit_price": str(unit_price),
            "base_price": str(base_price),
            "taxes": str(taxes),
            "fees": str(fees),
            "total": str(total),
            "passengers": [],
        }

        return redirect("bookings:passengers")


class PassengerDetailsView(LoginRequiredMixin, View):
    """
    Step 2: Enter passenger details.
    """

    template_name = "bookings/passengers.html"
    login_url = "/accounts/login/"

    def get(self, request):
        booking_data = request.session.get("booking")
        if not booking_data:
            messages.error(request, "Please select a flight first.")
            return redirect("flights:search")

        flight = get_object_or_404(Flight, pk=booking_data["flight_id"])
        passenger_count = booking_data["passenger_count"]

        # Pre-fill first passenger with user's data if available
        initial_data = []
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data.append({
                "title": profile.title,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "date_of_birth": profile.date_of_birth,
                "passport_number": profile.passport_number,
                "passport_expiry": profile.passport_expiry,
                "passport_country": profile.passport_country,
                "nationality": profile.nationality,
            })

        # Create formset
        formset = PassengerFormSet(
            initial=initial_data,
            prefix="passenger",
        )

        context = {
            "flight": flight,
            "booking_data": booking_data,
            "formset": formset,
            "passenger_count": passenger_count,
            "is_international": flight.is_international,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        booking_data = request.session.get("booking")
        if not booking_data:
            messages.error(request, "Please select a flight first.")
            return redirect("flights:search")

        flight = get_object_or_404(Flight, pk=booking_data["flight_id"])
        passenger_count = booking_data["passenger_count"]

        formset = PassengerFormSet(
            request.POST,
            prefix="passenger",
        )

        # Validate only the required number of forms
        valid_forms = []
        for i, form in enumerate(formset):
            if i < passenger_count:
                if form.is_valid():
                    valid_forms.append(form.cleaned_data)
                else:
                    context = {
                        "flight": flight,
                        "booking_data": booking_data,
                        "formset": formset,
                        "passenger_count": passenger_count,
                        "is_international": flight.is_international,
                    }
                    return render(request, self.template_name, context)

        if len(valid_forms) < passenger_count:
            messages.error(request, "Please fill in all passenger details.")
            context = {
                "flight": flight,
                "booking_data": booking_data,
                "formset": formset,
                "passenger_count": passenger_count,
                "is_international": flight.is_international,
            }
            return render(request, self.template_name, context)

        # Store passenger data in session
        passengers_data = []
        for data in valid_forms:
            passenger_dict = {
                "title": data["title"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "date_of_birth": data["date_of_birth"].isoformat() if data.get("date_of_birth") else None,
                "passenger_type": data.get("passenger_type", "ADULT"),
                "passport_number": data.get("passport_number", ""),
                "passport_expiry": data["passport_expiry"].isoformat() if data.get("passport_expiry") else None,
                "passport_country": data.get("passport_country", "Nigeria"),
                "nationality": data.get("nationality", "Nigerian"),
            }
            passengers_data.append(passenger_dict)

        # Update contact info
        booking_data["passengers"] = passengers_data
        booking_data["contact_email"] = request.POST.get("contact_email", request.user.email)
        booking_data["contact_phone"] = request.POST.get("contact_phone", "")
        request.session["booking"] = booking_data
        request.session.modified = True

        return redirect("bookings:review")


class BookingReviewView(LoginRequiredMixin, View):
    """
    Step 3: Review booking details before payment.
    """

    template_name = "bookings/review.html"
    login_url = "/accounts/login/"

    def get(self, request):
        booking_data = request.session.get("booking")
        if not booking_data or not booking_data.get("passengers"):
            messages.error(request, "Please complete all booking steps.")
            return redirect("flights:search")

        flight = get_object_or_404(Flight, pk=booking_data["flight_id"])

        context = {
            "flight": flight,
            "booking_data": booking_data,
            "passengers": booking_data["passengers"],
        }

        return render(request, self.template_name, context)

    def post(self, request):
        booking_data = request.session.get("booking")
        if not booking_data or not booking_data.get("passengers"):
            messages.error(request, "Please complete all booking steps.")
            return redirect("flights:search")

        # Check terms acceptance
        if not request.POST.get("accept_terms"):
            messages.error(request, "Please accept the terms and conditions.")
            return redirect("bookings:review")

        return redirect("bookings:payment")


class PaymentView(LoginRequiredMixin, View):
    """
    Step 4: Payment processing.
    Supports both demo mode (instant) and real Paystack payments.
    """

    template_name = "bookings/payment.html"
    login_url = "/accounts/login/"

    def get(self, request):
        booking_data = request.session.get("booking")
        if not booking_data or not booking_data.get("passengers"):
            messages.error(request, "Please complete all booking steps.")
            return redirect("flights:search")

        flight = get_object_or_404(Flight, pk=booking_data["flight_id"])

        context = {
            "flight": flight,
            "booking_data": booking_data,
            "total": Decimal(booking_data["total"]),
        }

        return render(request, self.template_name, context)

    def post(self, request):
        booking_data = request.session.get("booking")
        if not booking_data or not booking_data.get("passengers"):
            messages.error(request, "Please complete all booking steps.")
            return redirect("flights:search")

        flight = get_object_or_404(Flight, pk=booking_data["flight_id"])

        # Verify flight is still bookable
        if not flight.is_bookable:
            messages.error(request, "This flight is no longer available.")
            return redirect("flights:search")

        payment_method = request.POST.get("payment_method", "demo")

        # Handle Paystack payment
        if payment_method in ["paystack", "card", "bank_transfer"]:
            return self._process_paystack_payment(request, flight, booking_data)

        # Handle demo payment (instant confirmation)
        return self._process_demo_payment(request, flight, booking_data)

    def _process_demo_payment(self, request, flight, booking_data):
        """Process demo payment - instant booking confirmation."""
        try:
            booking = self._create_booking(request, flight, booking_data, confirmed=True)

            # Clear booking session
            del request.session["booking"]
            request.session.modified = True

            messages.success(request, "Booking confirmed successfully! (Demo Mode)")
            return redirect("bookings:confirmation", reference=booking.reference)

        except Exception as e:
            messages.error(request, "An error occurred while processing your booking. Please try again.")
            return redirect("bookings:review")

    def _process_paystack_payment(self, request, flight, booking_data):
        """Process real Paystack payment."""
        from payments.models import Payment, PaymentStatus
        from payments.services import PaystackError, paystack_service

        try:
            # Create pending booking first
            booking = self._create_booking(request, flight, booking_data, confirmed=False)

            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                user=request.user,
                amount=booking.total_price,
                currency="NGN",
                status=PaymentStatus.PENDING,
                ip_address=self._get_client_ip(request),
            )

            # Build callback URL
            callback_url = request.build_absolute_uri(
                reverse("payments:verify", kwargs={"reference": payment.paystack_reference})
            )

            # Initialize Paystack transaction
            result = paystack_service.initialize_transaction(payment, callback_url)

            # Store booking reference in session for potential recovery
            request.session["pending_booking"] = booking.reference
            request.session.modified = True

            # Clear main booking session (we have the booking in DB now)
            del request.session["booking"]

            # Redirect to Paystack
            return redirect(result["authorization_url"])

        except PaystackError as e:
            messages.error(request, f"Payment initialization failed: {str(e)}")
            # Don't delete booking - user can retry
            return redirect("bookings:review")

        except Exception as e:
            messages.error(request, "An error occurred while processing your payment. Please try again.")
            return redirect("bookings:review")

    def _create_booking(self, request, flight, booking_data, confirmed=False):
        """Create booking and passengers."""
        from datetime import datetime

        status = BookingStatus.CONFIRMED if confirmed else BookingStatus.PENDING

        booking = Booking.objects.create(
            user=request.user,
            flight=flight,
            seat_class=booking_data["seat_class"],
            base_price=Decimal(booking_data["base_price"]),
            taxes=Decimal(booking_data["taxes"]),
            fees=Decimal(booking_data["fees"]),
            total_price=Decimal(booking_data["total"]),
            contact_email=booking_data.get("contact_email", request.user.email),
            contact_phone=booking_data.get("contact_phone", ""),
            status=status,
            confirmed_at=timezone.now() if confirmed else None,
        )

        # Create passengers
        for pax_data in booking_data["passengers"]:
            dob = None
            if pax_data.get("date_of_birth"):
                dob = datetime.fromisoformat(pax_data["date_of_birth"]).date()

            passport_exp = None
            if pax_data.get("passport_expiry"):
                passport_exp = datetime.fromisoformat(pax_data["passport_expiry"]).date()

            Passenger.objects.create(
                booking=booking,
                title=pax_data["title"],
                first_name=pax_data["first_name"],
                last_name=pax_data["last_name"],
                date_of_birth=dob,
                passenger_type=pax_data.get("passenger_type", "ADULT"),
                passport_number=pax_data.get("passport_number", ""),
                passport_expiry=passport_exp,
                passport_country=pax_data.get("passport_country", "Nigeria"),
                nationality=pax_data.get("nationality", "Nigerian"),
            )

        # Update flight seat availability only if confirmed
        if confirmed:
            seat_class = booking_data["seat_class"]
            passenger_count = booking_data["passenger_count"]
            if seat_class == "ECONOMY":
                flight.available_economy_seats -= passenger_count
            elif seat_class == "BUSINESS":
                flight.available_business_seats -= passenger_count
            elif seat_class == "FIRST":
                flight.available_first_class_seats -= passenger_count
            flight.save()

        return booking

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class BookingConfirmationView(LoginRequiredMixin, DetailView):
    """
    Step 5: Booking confirmation page.
    """

    template_name = "bookings/confirmation.html"
    context_object_name = "booking"
    login_url = "/accounts/login/"

    def get_object(self):
        return get_object_or_404(
            Booking.objects.select_related("flight", "flight__airline", "flight__origin", "flight__destination"),
            reference=self.kwargs["reference"],
            user=self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["passengers"] = self.object.passengers.all()
        return context


class ManageBookingView(View):
    """
    Search for booking by reference and last name.
    """

    template_name = "bookings/manage.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        reference = request.POST.get("reference", "").upper().strip()
        last_name = request.POST.get("last_name", "").strip()

        if not reference or not last_name:
            messages.error(request, "Please enter both booking reference and last name.")
            return render(request, self.template_name)

        try:
            booking = Booking.objects.select_related(
                "flight", "flight__airline"
            ).get(reference=reference)

            # Verify last name matches any passenger
            if not booking.passengers.filter(last_name__iexact=last_name).exists():
                messages.error(request, "No booking found with this reference and last name.")
                return render(request, self.template_name)

            return redirect("bookings:detail", reference=booking.reference)

        except Booking.DoesNotExist:
            messages.error(request, "No booking found with this reference.")
            return render(request, self.template_name)


class BookingDetailPublicView(DetailView):
    """
    Public booking detail view (via reference search).
    """

    template_name = "bookings/detail_public.html"
    context_object_name = "booking"

    def get_object(self):
        return get_object_or_404(
            Booking.objects.select_related("flight", "flight__airline", "flight__origin", "flight__destination"),
            reference=self.kwargs["reference"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["passengers"] = self.object.passengers.all()
        return context


class DownloadETicketView(LoginRequiredMixin, View):
    """
    Download e-ticket PDF for a confirmed booking.
    """

    login_url = "/accounts/login/"

    def get(self, request, reference):
        # Get the booking
        booking = get_object_or_404(
            Booking.objects.select_related(
                "flight", "flight__airline", "flight__origin", "flight__destination",
                "flight__departure_gate", "user"
            ).prefetch_related("passengers"),
            reference=reference,
            user=request.user,
        )

        # Check if booking is confirmed
        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.COMPLETED]:
            messages.error(request, "E-ticket is only available for confirmed bookings.")
            return redirect("accounts:booking_detail", reference=reference)

        # Generate PDF
        from django.http import HttpResponse
        from .eticket import generate_eticket_pdf

        try:
            pdf_buffer = generate_eticket_pdf(booking)

            # Create HTTP response with PDF
            response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="eticket_{booking.reference}.pdf"'
            return response

        except Exception as e:
            messages.error(request, f"Unable to generate e-ticket: {str(e)}")
            return redirect("accounts:booking_detail", reference=reference)


class CancelBookingView(LoginRequiredMixin, View):
    """
    Cancel a booking (only for PENDING or CONFIRMED status).
    """

    login_url = "/accounts/login/"

    def post(self, request, reference):
        booking = get_object_or_404(
            Booking,
            reference=reference,
            user=request.user,
        )

        # Check if booking can be cancelled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            messages.error(request, "This booking cannot be cancelled.")
            return redirect("accounts:booking_detail", reference=reference)

        # Check if flight hasn't departed
        if booking.flight.scheduled_departure <= timezone.now():
            messages.error(request, "Cannot cancel booking for a flight that has already departed.")
            return redirect("accounts:booking_detail", reference=reference)

        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = request.POST.get("reason", "Cancelled by user")
        booking.save()

        # Restore seat availability if booking was confirmed
        if booking.status == BookingStatus.CONFIRMED:
            passenger_count = booking.passengers.count()
            flight = booking.flight
            if booking.seat_class == SeatClass.ECONOMY:
                flight.available_economy_seats += passenger_count
            elif booking.seat_class == SeatClass.BUSINESS:
                flight.available_business_seats += passenger_count
            elif booking.seat_class == SeatClass.FIRST:
                flight.available_first_class_seats += passenger_count
            flight.save()

        messages.success(request, f"Booking {booking.reference} has been cancelled successfully.")
        return redirect("accounts:bookings")


class DownloadETicketPublicView(View):
    """
    Download e-ticket PDF for a booking (public access with verification).
    """

    def get(self, request, reference):
        # Get the booking
        booking = get_object_or_404(
            Booking.objects.select_related(
                "flight", "flight__airline", "flight__origin", "flight__destination",
                "flight__departure_gate", "user"
            ).prefetch_related("passengers"),
            reference=reference,
        )

        # Check if booking is confirmed
        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN, BookingStatus.COMPLETED]:
            messages.error(request, "E-ticket is only available for confirmed bookings.")
            return redirect("bookings:detail", reference=reference)

        # Verify access - must have last name in query param
        last_name = request.GET.get("last_name", "").strip()
        if not last_name or not booking.passengers.filter(last_name__iexact=last_name).exists():
            messages.error(request, "Invalid access. Please provide correct passenger last name.")
            return redirect("bookings:manage")

        # Generate PDF
        from django.http import HttpResponse
        from .eticket import generate_eticket_pdf

        try:
            pdf_buffer = generate_eticket_pdf(booking)

            response = HttpResponse(pdf_buffer.read(), content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="eticket_{booking.reference}.pdf"'
            return response

        except Exception as e:
            messages.error(request, f"Unable to generate e-ticket: {str(e)}")
            return redirect("bookings:detail", reference=reference)
