"""
Views for the Airlines app — Aircraft Parking Management.

Airline staff can view their aircraft's parking records, register new stands,
and pay outstanding parking invoices. Airport admins see all records.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AircraftParkingRecordForm, MarkPaidForm
from .models import (
    AircraftParkingRate,
    AircraftParkingRecord,
    AircraftStand,
)


@login_required
def aircraft_parking_dashboard(request):
    """
    Dashboard showing all parking records for the airline (staff) or all airlines (admin/airport staff).
    """
    user = request.user

    if user.is_staff or getattr(user, "role", None) in ("AIRPORT_STAFF", "ADMIN"):
        records = AircraftParkingRecord.objects.select_related(
            "aircraft", "airline", "stand"
        ).all()
        is_admin_view = True
    elif getattr(user, "role", None) == "AIRLINE_STAFF" and user.airline:
        records = AircraftParkingRecord.objects.select_related(
            "aircraft", "airline", "stand"
        ).filter(airline=user.airline)
        is_admin_view = False
    else:
        messages.error(request, "You do not have permission to access aircraft parking management.")
        return redirect("core:home")

    active_count = records.filter(status=AircraftParkingRecord.Status.ACTIVE).count()
    unpaid_qs = records.filter(is_paid=False).exclude(
        status=AircraftParkingRecord.Status.CANCELLED
    )
    unpaid_count = unpaid_qs.count()
    unpaid_total = sum(r.total_due for r in unpaid_qs)

    context = {
        "records": records.order_by("-scheduled_arrival")[:50],
        "active_count": active_count,
        "unpaid_count": unpaid_count,
        "unpaid_total": unpaid_total,
        "is_admin_view": is_admin_view,
        "stands": AircraftStand.objects.filter(is_active=True),
        "page_title": "Aircraft Parking Management",
    }
    return render(request, "airlines/parking_dashboard.html", context)


@login_required
def register_aircraft_parking(request):
    """
    Form to register an aircraft at a stand (schedule its parking).
    """
    user = request.user
    airline = None

    if getattr(user, "role", None) == "AIRLINE_STAFF" and user.airline:
        airline = user.airline
    elif not (user.is_staff or getattr(user, "role", None) in ("AIRPORT_STAFF", "ADMIN")):
        messages.error(request, "You do not have permission to register aircraft parking.")
        return redirect("core:home")

    if request.method == "POST":
        form = AircraftParkingRecordForm(request.POST, airline=airline)
        if form.is_valid():
            record = form.save(commit=False)
            if airline:
                record.airline = airline
            else:
                record.airline = record.aircraft.airline
            record.save()
            record.calculate_and_save_fees()
            messages.success(
                request,
                f"Aircraft parking registered: {record.record_number}. "
                f"Estimated fee: ₦{record.total_due:,.2f}",
            )
            return redirect("airlines:parking_detail", pk=record.pk)
    else:
        form = AircraftParkingRecordForm(airline=airline)

    rates = AircraftParkingRate.objects.all()
    context = {
        "form": form,
        "rates": rates,
        "page_title": "Register Aircraft Parking",
    }
    return render(request, "airlines/register_parking.html", context)


@login_required
def aircraft_parking_detail(request, pk):
    """
    Detail view for a single parking record with fee breakdown and payment option.
    """
    user = request.user
    record = get_object_or_404(AircraftParkingRecord, pk=pk)

    if not (
        user.is_staff
        or getattr(user, "role", None) in ("AIRPORT_STAFF", "ADMIN")
        or (getattr(user, "role", None) == "AIRLINE_STAFF" and user.airline == record.airline)
    ):
        messages.error(request, "Access denied.")
        return redirect("airlines:parking_dashboard")

    paid_form = None
    if not record.is_paid and record.status != AircraftParkingRecord.Status.CANCELLED:
        if request.method == "POST" and "mark_paid" in request.POST:
            paid_form = MarkPaidForm(request.POST)
            if paid_form.is_valid():
                record.is_paid = True
                record.payment_date = timezone.now()
                record.payment_reference = paid_form.cleaned_data["payment_reference"]
                if record.status == AircraftParkingRecord.Status.OVERDUE:
                    record.status = AircraftParkingRecord.Status.COMPLETED
                record.save()
                messages.success(
                    request,
                    f"Payment of ₦{record.total_due:,.2f} recorded for {record.record_number}.",
                )
                return redirect("airlines:parking_detail", pk=pk)
        else:
            paid_form = MarkPaidForm()

    if request.method == "POST" and "update_status" in request.POST:
        new_status = request.POST.get("new_status")
        valid_statuses = [s.value for s in AircraftParkingRecord.Status]
        if new_status in valid_statuses and (
            user.is_staff or getattr(user, "role", None) in ("AIRPORT_STAFF", "ADMIN")
        ):
            record.status = new_status
            if new_status == AircraftParkingRecord.Status.ACTIVE:
                record.actual_arrival_time = timezone.now()
            elif new_status == AircraftParkingRecord.Status.COMPLETED:
                if not record.actual_departure_time:
                    record.actual_departure_time = timezone.now()
                record.calculate_and_save_fees()
            record.save()
            messages.success(request, f"Status updated to {record.get_status_display()}.")
            return redirect("airlines:parking_detail", pk=pk)

    context = {
        "record": record,
        "paid_form": paid_form,
        "page_title": f"Parking Record – {record.record_number}",
        "can_manage": user.is_staff or getattr(user, "role", None) in ("AIRPORT_STAFF", "ADMIN"),
        "status_choices": AircraftParkingRecord.Status.choices,
    }
    return render(request, "airlines/parking_detail.html", context)


@login_required
def parking_rates(request):
    """Public rate card — shows current fee schedule for all aircraft sizes."""
    rates = AircraftParkingRate.objects.all().order_by("aircraft_size")
    stands = AircraftStand.objects.filter(is_active=True).order_by("terminal", "stand_number")
    context = {
        "rates": rates,
        "stands": stands,
        "page_title": "Aircraft Parking Rates",
    }
    return render(request, "airlines/parking_rates.html", context)
