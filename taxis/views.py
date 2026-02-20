"""
Airport Taxi & Transfer Booking Views.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TaxiBookingForm
from .models import TaxiBooking, VehicleCategory

VAT_RATE = Decimal("0.075")


def taxi_list(request):
    """
    Public listing of all vehicle categories with pricing.
    Passengers pick a vehicle type and proceed to book.
    """
    vehicles = VehicleCategory.objects.filter(is_active=True).order_by("price_per_km")
    return render(request, "taxis/taxi_list.html", {"vehicles": vehicles})


@login_required
def book_taxi(request, slug):
    """
    Booking form for a specific vehicle category.
    Calculates estimated fare dynamically.
    """
    vehicle = get_object_or_404(VehicleCategory, slug=slug, is_active=True)

    if request.method == "POST":
        form = TaxiBookingForm(request.POST, initial={"vehicle_category": vehicle})
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.vehicle_category = vehicle

            # Calculate pricing
            distance = booking.estimated_distance_km
            booking.base_fare = vehicle.estimate_fare(distance)
            booking.vat_amount = (booking.base_fare * VAT_RATE).quantize(Decimal("0.01"))
            booking.total_fare = booking.base_fare + booking.vat_amount

            # Pre-fill passenger info from user if blank
            if not booking.passenger_name and request.user.get_full_name():
                booking.passenger_name = request.user.get_full_name()
            if not booking.passenger_email:
                booking.passenger_email = request.user.email

            booking.save()
            messages.success(request, f"Taxi booked! Reference: {booking.reference}")
            return redirect("taxis:booking_confirmation", reference=booking.reference)
    else:
        initial = {
            "passenger_name": request.user.get_full_name(),
            "passenger_email": request.user.email,
        }
        form = TaxiBookingForm(initial=initial)

    return render(request, "taxis/book_taxi.html", {
        "vehicle": vehicle,
        "form": form,
        "vat_rate": int(VAT_RATE * 100),
    })


@login_required
def booking_confirmation(request, reference):
    """Confirmation page shown after a taxi booking is created."""
    booking = get_object_or_404(TaxiBooking, reference=reference, user=request.user)
    return render(request, "taxis/booking_confirmation.html", {"booking": booking})


@login_required
def my_taxi_bookings(request):
    """Dashboard: all taxi bookings for the logged-in user."""
    bookings = TaxiBooking.objects.filter(user=request.user).select_related("vehicle_category")
    return render(request, "taxis/my_bookings.html", {"bookings": bookings})


@login_required
def cancel_taxi_booking(request, reference):
    """Cancel a pending taxi booking."""
    booking = get_object_or_404(
        TaxiBooking, reference=reference, user=request.user,
        status__in=[TaxiBooking.BookingStatus.PENDING, TaxiBooking.BookingStatus.CONFIRMED],
    )
    if request.method == "POST":
        booking.status = TaxiBooking.BookingStatus.CANCELLED
        booking.save()
        messages.success(request, f"Booking {reference} has been cancelled.")
        return redirect("taxis:my_bookings")
    return render(request, "taxis/cancel_booking.html", {"booking": booking})
