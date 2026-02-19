"""
Views for the Hotel Booking module.

Flow: hotel list → hotel detail → select room → guest details → review → confirmation.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import HotelBookingForm, HotelSearchForm
from .models import Hotel, HotelBooking, RoomType


def hotel_list(request):
    """Display all active hotels with optional search/filter."""
    form = HotelSearchForm(request.GET or None)
    hotels = Hotel.objects.filter(is_active=True).prefetch_related("room_types")

    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")
    num_rooms = request.GET.get("num_rooms", 1)
    num_adults = request.GET.get("num_adults", 1)

    context = {
        "hotels": hotels,
        "form": form,
        "check_in": check_in,
        "check_out": check_out,
        "num_rooms": num_rooms,
        "num_adults": num_adults,
        "page_title": "Partner Hotels",
    }
    return render(request, "hotels/hotel_list.html", context)


def hotel_detail(request, slug):
    """Hotel detail page with room types and booking form entry."""
    hotel = get_object_or_404(Hotel, slug=slug, is_active=True)
    room_types = hotel.room_types.filter(is_active=True)

    check_in = request.GET.get("check_in")
    check_out = request.GET.get("check_out")
    num_rooms = int(request.GET.get("num_rooms", 1))

    pricing = {}
    if check_in and check_out:
        from datetime import date
        try:
            ci = date.fromisoformat(check_in)
            co = date.fromisoformat(check_out)
            for rt in room_types:
                pricing[rt.pk] = HotelBooking.calculate_price(rt, ci, co, num_rooms)
        except (ValueError, TypeError):
            pass

    context = {
        "hotel": hotel,
        "room_types": room_types,
        "check_in": check_in,
        "check_out": check_out,
        "num_rooms": num_rooms,
        "pricing": pricing,
        "page_title": hotel.name,
    }
    return render(request, "hotels/hotel_detail.html", context)


@login_required
def book_room(request, room_type_id):
    """
    Step 1: Guest details form.
    Requires check_in, check_out, num_rooms in GET/POST params.
    """
    room_type = get_object_or_404(RoomType, pk=room_type_id, is_active=True)
    hotel = room_type.hotel

    check_in_str = request.GET.get("check_in") or request.POST.get("check_in")
    check_out_str = request.GET.get("check_out") or request.POST.get("check_out")
    num_rooms = int(request.GET.get("num_rooms", request.POST.get("num_rooms", 1)))

    from datetime import date
    try:
        check_in = date.fromisoformat(check_in_str)
        check_out = date.fromisoformat(check_out_str)
    except (TypeError, ValueError):
        messages.error(request, "Invalid check-in/check-out dates. Please search again.")
        return redirect("hotels:hotel_list")

    pricing = HotelBooking.calculate_price(room_type, check_in, check_out, num_rooms)

    if request.method == "POST":
        form = HotelBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.room_type = room_type
            booking.check_in_date = check_in
            booking.check_out_date = check_out
            booking.num_rooms = num_rooms
            booking.room_rate = pricing["room_rate"]
            booking.num_nights = pricing["num_nights"]
            booking.subtotal = pricing["subtotal"]
            booking.vat_amount = pricing["vat_amount"]
            booking.service_fee = pricing["service_fee"]
            booking.total_price = pricing["total_price"]
            booking.status = HotelBooking.Status.PENDING
            booking.save()

            # Store in session for review step
            request.session["hotel_booking_id"] = str(booking.pk)
            return redirect("hotels:booking_review", reference=booking.reference)
    else:
        # Pre-fill from user profile
        initial = {}
        if hasattr(request.user, "first_name"):
            initial["guest_first_name"] = request.user.first_name
            initial["guest_last_name"] = request.user.last_name
            initial["guest_email"] = request.user.email
        form = HotelBookingForm(initial=initial)

    context = {
        "form": form,
        "hotel": hotel,
        "room_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
        "num_rooms": num_rooms,
        "pricing": pricing,
        "page_title": f"Book – {room_type.name}",
    }
    return render(request, "hotels/book_room.html", context)


@login_required
def booking_review(request, reference):
    """
    Step 2: Review booking summary, then proceed to simulated payment.
    """
    booking = get_object_or_404(
        HotelBooking, reference=reference, user=request.user
    )

    if request.method == "POST":
        # Simulate payment confirmation (Paystack integration point)
        booking.is_paid = True
        booking.paid_at = timezone.now()
        booking.payment_reference = f"HTL-SIM-{booking.reference}"
        booking.status = HotelBooking.Status.CONFIRMED
        booking.save()
        messages.success(
            request,
            f"Hotel booking confirmed! Reference: {booking.reference}. "
            f"A confirmation will be sent to {booking.guest_email}.",
        )
        return redirect("hotels:booking_confirmation", reference=booking.reference)

    context = {
        "booking": booking,
        "page_title": "Review Your Booking",
    }
    return render(request, "hotels/booking_review.html", context)


@login_required
def booking_confirmation(request, reference):
    """Booking confirmation page."""
    booking = get_object_or_404(
        HotelBooking, reference=reference, user=request.user
    )
    context = {
        "booking": booking,
        "page_title": f"Booking Confirmed – {booking.reference}",
    }
    return render(request, "hotels/booking_confirmation.html", context)


@login_required
def my_hotel_bookings(request):
    """List all hotel bookings for the logged-in user."""
    bookings = HotelBooking.objects.filter(user=request.user).select_related(
        "hotel", "room_type"
    ).order_by("-created_at")
    context = {
        "bookings": bookings,
        "page_title": "My Hotel Bookings",
    }
    return render(request, "hotels/my_bookings.html", context)


@login_required
def cancel_hotel_booking(request, reference):
    """Cancel a hotel booking if within cancellation window."""
    booking = get_object_or_404(
        HotelBooking, reference=reference, user=request.user
    )

    if not booking.is_cancellable:
        messages.error(
            request,
            "This booking cannot be cancelled (it's within 24 hours of check-in or already completed).",
        )
        return redirect("hotels:my_bookings")

    if request.method == "POST":
        booking.status = HotelBooking.Status.CANCELLED
        booking.save()
        messages.success(request, f"Booking {booking.reference} has been cancelled.")
        return redirect("hotels:my_bookings")

    context = {"booking": booking, "page_title": "Cancel Booking"}
    return render(request, "hotels/cancel_booking.html", context)
