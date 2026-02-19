"""
Views for Airport Lounge Booking.
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import AirportLounge, LoungeBooking


def lounge_list(request):
    """Show all available lounges."""
    lounges = AirportLounge.objects.filter(is_active=True)
    context = {
        "lounges": lounges,
        "page_title": "Airport Lounges",
    }
    return render(request, "lounge/lounge_list.html", context)


@login_required
def book_lounge(request, pk):
    """Book a lounge day pass."""
    lounge = get_object_or_404(AirportLounge, pk=pk, is_active=True)
    today = timezone.now().date()

    if request.method == "POST":
        visit_date_str = request.POST.get("visit_date")
        num_adults = int(request.POST.get("num_adults", 1))
        num_children = int(request.POST.get("num_children", 0))
        guest_name = request.POST.get("guest_name", "").strip()
        guest_email = request.POST.get("guest_email", "").strip()
        guest_phone = request.POST.get("guest_phone", "").strip()
        flight_number = request.POST.get("flight_number", "").strip()

        from datetime import date
        try:
            visit_date = date.fromisoformat(visit_date_str)
        except (TypeError, ValueError):
            messages.error(request, "Invalid visit date.")
            return redirect("lounge:book_lounge", pk=pk)

        if visit_date < today:
            messages.error(request, "Visit date cannot be in the past.")
            return redirect("lounge:book_lounge", pk=pk)

        if not guest_name or not guest_email:
            messages.error(request, "Guest name and email are required.")
            return redirect("lounge:book_lounge", pk=pk)

        subtotal, vat, total = lounge.total_price_with_tax(num_adults, num_children)

        booking = LoungeBooking.objects.create(
            user=request.user,
            lounge=lounge,
            visit_date=visit_date,
            num_adults=num_adults,
            num_children=num_children,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            flight_number=flight_number,
            subtotal=subtotal,
            vat_amount=vat,
            total_price=total,
            is_paid=True,  # Simulated payment
            payment_reference=f"LNG-SIM-{request.user.pk}",
            status=LoungeBooking.Status.CONFIRMED,
        )
        messages.success(
            request,
            f"Lounge pass booked! Reference: {booking.reference}. "
            f"Show your access code ({booking.access_code}) at the lounge entrance.",
        )
        return redirect("lounge:booking_confirmation", reference=booking.reference)

    # GET
    num_adults = int(request.GET.get("num_adults", 1))
    num_children = int(request.GET.get("num_children", 0))
    subtotal, vat, total = lounge.total_price_with_tax(num_adults, num_children)

    context = {
        "lounge": lounge,
        "today": today,
        "num_adults": num_adults,
        "num_children": num_children,
        "subtotal": subtotal,
        "vat": vat,
        "total": total,
        "page_title": f"Book – {lounge.name}",
        "user": request.user,
    }
    return render(request, "lounge/book_lounge.html", context)


@login_required
def booking_confirmation(request, reference):
    """Lounge booking confirmation with access code."""
    booking = get_object_or_404(LoungeBooking, reference=reference, user=request.user)
    context = {"booking": booking, "page_title": "Lounge Pass Confirmed"}
    return render(request, "lounge/booking_confirmation.html", context)


@login_required
def my_lounge_bookings(request):
    """List user's lounge bookings."""
    bookings = LoungeBooking.objects.filter(user=request.user).select_related("lounge").order_by("-created_at")
    context = {"bookings": bookings, "page_title": "My Lounge Passes"}
    return render(request, "lounge/my_bookings.html", context)
