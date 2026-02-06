"""
Analytics views for the Airport Management System.

Provides dashboard and reporting functionality for staff and administrators.
"""

import json
from datetime import timedelta
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db import models
from django.db.models import Avg, Count, F, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView

from bookings.models import Booking, BookingStatus
from flights.models import Airport, Flight, FlightStatus
from payments.models import Payment, PaymentStatus


@method_decorator(staff_member_required, name='dispatch')
class AnalyticsDashboardView(TemplateView):
    """
    Main analytics dashboard for staff and administrators.
    Shows key metrics, charts, and recent activity.
    """

    template_name = "analytics/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()
        start_of_month = today.replace(day=1)
        start_of_week = today - timedelta(days=today.weekday())

        # === Key Metrics ===

        # Total bookings
        context["total_bookings"] = Booking.objects.count()
        context["bookings_today"] = Booking.objects.filter(
            created_at__date=today
        ).count()
        context["bookings_this_week"] = Booking.objects.filter(
            created_at__date__gte=start_of_week
        ).count()
        context["bookings_this_month"] = Booking.objects.filter(
            created_at__date__gte=start_of_month
        ).count()

        # Revenue metrics
        completed_payments = Payment.objects.filter(status=PaymentStatus.COMPLETED)
        context["total_revenue"] = completed_payments.aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0")

        context["revenue_today"] = completed_payments.filter(
            paid_at__date=today
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        context["revenue_this_month"] = completed_payments.filter(
            paid_at__date__gte=start_of_month
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # Flight statistics
        context["total_flights"] = Flight.objects.count()
        context["flights_today"] = Flight.objects.filter(
            scheduled_departure__date=today
        ).count()

        context["active_flights"] = Flight.objects.filter(
            status__in=[FlightStatus.IN_FLIGHT, FlightStatus.DEPARTED]
        ).count()

        context["delayed_flights"] = Flight.objects.filter(
            status=FlightStatus.DELAYED,
            scheduled_departure__date=today
        ).count()

        # Booking status breakdown
        context["confirmed_bookings"] = Booking.objects.filter(
            status=BookingStatus.CONFIRMED
        ).count()
        context["pending_bookings"] = Booking.objects.filter(
            status=BookingStatus.PENDING
        ).count()
        context["cancelled_bookings"] = Booking.objects.filter(
            status=BookingStatus.CANCELLED
        ).count()

        # Average booking value
        avg_booking = Booking.objects.filter(
            status=BookingStatus.CONFIRMED
        ).aggregate(avg=Avg("total_price"))
        context["avg_booking_value"] = avg_booking["avg"] or Decimal("0")

        # === Top Routes ===
        top_routes = Flight.objects.values(
            "origin__code", "origin__city",
            "destination__code", "destination__city"
        ).annotate(
            booking_count=Count("bookings")
        ).order_by("-booking_count")[:5]
        context["top_routes"] = top_routes

        # === Recent Bookings ===
        context["recent_bookings"] = Booking.objects.select_related(
            "user", "flight__origin", "flight__destination"
        ).order_by("-created_at")[:10]

        # === Payment Status Summary ===
        context["completed_payments_count"] = completed_payments.count()
        context["pending_payments_count"] = Payment.objects.filter(
            status=PaymentStatus.PENDING
        ).count()
        context["failed_payments_count"] = Payment.objects.filter(
            status=PaymentStatus.FAILED
        ).count()

        # === Flight Status Summary ===
        flight_status_data = Flight.objects.filter(
            scheduled_departure__date__gte=today,
            scheduled_departure__date__lte=today + timedelta(days=7)
        ).values("status").annotate(count=Count("id"))
        context["flight_status_data"] = list(flight_status_data)

        # Current time for display
        context["current_time"] = now

        return context


@method_decorator(staff_member_required, name='dispatch')
class RevenueReportView(TemplateView):
    """Detailed revenue reports and analytics."""

    template_name = "analytics/revenue_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Get date range from query params (default: last 30 days)
        days = int(self.request.GET.get("days", 30))
        start_date = now.date() - timedelta(days=days)

        # Daily revenue
        daily_revenue = Payment.objects.filter(
            status=PaymentStatus.COMPLETED,
            paid_at__date__gte=start_date
        ).annotate(
            date=TruncDate("paid_at")
        ).values("date").annotate(
            revenue=Sum("amount"),
            count=Count("id")
        ).order_by("date")

        context["daily_revenue"] = list(daily_revenue)

        # Monthly revenue (last 12 months)
        monthly_revenue = Payment.objects.filter(
            status=PaymentStatus.COMPLETED,
            paid_at__gte=now - timedelta(days=365)
        ).annotate(
            month=TruncMonth("paid_at")
        ).values("month").annotate(
            revenue=Sum("amount"),
            count=Count("id")
        ).order_by("month")

        context["monthly_revenue"] = list(monthly_revenue)

        # Revenue by seat class
        revenue_by_class = Booking.objects.filter(
            status=BookingStatus.CONFIRMED
        ).values("seat_class").annotate(
            revenue=Sum("total_price"),
            count=Count("id")
        )
        context["revenue_by_class"] = list(revenue_by_class)

        # Total for period
        context["period_revenue"] = Payment.objects.filter(
            status=PaymentStatus.COMPLETED,
            paid_at__date__gte=start_date
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        context["period_days"] = days
        context["start_date"] = start_date

        return context


@method_decorator(staff_member_required, name='dispatch')
class FlightReportView(TemplateView):
    """Flight operations reports and analytics."""

    template_name = "analytics/flight_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()

        # On-time performance
        completed_flights = Flight.objects.filter(
            status__in=[FlightStatus.ARRIVED, FlightStatus.LANDED],
            scheduled_departure__date__gte=today - timedelta(days=30)
        )
        total_completed = completed_flights.count()
        on_time = completed_flights.filter(
            actual_departure__lte=models.F("scheduled_departure") + timedelta(minutes=15)
        ).count() if total_completed > 0 else 0

        context["on_time_performance"] = (
            (on_time / total_completed * 100) if total_completed > 0 else 0
        )
        context["total_completed_flights"] = total_completed

        # Flights by status
        flights_by_status = Flight.objects.filter(
            scheduled_departure__date__gte=today,
            scheduled_departure__date__lte=today + timedelta(days=7)
        ).values("status").annotate(count=Count("id"))
        context["flights_by_status"] = list(flights_by_status)

        # Busiest routes
        busiest_routes = Flight.objects.values(
            "origin__code", "destination__code"
        ).annotate(
            flight_count=Count("id"),
            passenger_count=Count("bookings")
        ).order_by("-flight_count")[:10]
        context["busiest_routes"] = list(busiest_routes)

        # Average load factor
        context["avg_load_factor"] = 72.5  # Placeholder - calculate from actual data

        # Flights per day (last 7 days)
        flights_per_day = Flight.objects.filter(
            scheduled_departure__date__gte=today - timedelta(days=7),
            scheduled_departure__date__lte=today
        ).annotate(
            date=TruncDate("scheduled_departure")
        ).values("date").annotate(count=Count("id")).order_by("date")
        context["flights_per_day"] = list(flights_per_day)

        return context


@method_decorator(staff_member_required, name='dispatch')
class BookingReportView(TemplateView):
    """Booking analytics and reports."""

    template_name = "analytics/booking_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = now.date()

        # Bookings by status
        bookings_by_status = Booking.objects.values("status").annotate(
            count=Count("id")
        )
        context["bookings_by_status"] = list(bookings_by_status)

        # Bookings by seat class
        bookings_by_class = Booking.objects.values("seat_class").annotate(
            count=Count("id"),
            revenue=Sum("total_price")
        )
        context["bookings_by_class"] = list(bookings_by_class)

        # Daily bookings (last 30 days)
        daily_bookings = Booking.objects.filter(
            created_at__date__gte=today - timedelta(days=30)
        ).annotate(
            date=TruncDate("created_at")
        ).values("date").annotate(count=Count("id")).order_by("date")
        context["daily_bookings"] = list(daily_bookings)

        # Top destinations
        top_destinations = Booking.objects.values(
            "flight__destination__code",
            "flight__destination__city"
        ).annotate(
            count=Count("id")
        ).order_by("-count")[:10]
        context["top_destinations"] = list(top_destinations)

        # Booking conversion rate (simplified)
        total_started = Booking.objects.count()
        total_confirmed = Booking.objects.filter(
            status=BookingStatus.CONFIRMED
        ).count()
        context["conversion_rate"] = (
            (total_confirmed / total_started * 100) if total_started > 0 else 0
        )

        return context


# === API Views for Chart Data ===

@method_decorator(staff_member_required, name='dispatch')
class ChartDataAPIView(View):
    """API endpoint for chart data."""

    def get(self, request):
        chart_type = request.GET.get("type", "revenue")
        days = int(request.GET.get("days", 30))
        now = timezone.now()
        start_date = now.date() - timedelta(days=days)

        if chart_type == "revenue":
            data = self._get_revenue_data(start_date)
        elif chart_type == "bookings":
            data = self._get_bookings_data(start_date)
        elif chart_type == "flights":
            data = self._get_flights_data(start_date)
        elif chart_type == "status":
            data = self._get_status_data()
        else:
            data = {"error": "Invalid chart type"}

        return JsonResponse(data)

    def _get_revenue_data(self, start_date):
        """Get daily revenue data for charts."""
        daily_revenue = Payment.objects.filter(
            status=PaymentStatus.COMPLETED,
            paid_at__date__gte=start_date
        ).annotate(
            date=TruncDate("paid_at")
        ).values("date").annotate(
            revenue=Sum("amount")
        ).order_by("date")

        labels = []
        values = []
        for item in daily_revenue:
            labels.append(item["date"].strftime("%b %d"))
            values.append(float(item["revenue"]))

        return {
            "labels": labels,
            "datasets": [{
                "label": "Revenue (NGN)",
                "data": values,
                "borderColor": "#00A651",
                "backgroundColor": "rgba(0, 166, 81, 0.1)",
                "fill": True,
            }]
        }

    def _get_bookings_data(self, start_date):
        """Get daily bookings data for charts."""
        daily_bookings = Booking.objects.filter(
            created_at__date__gte=start_date
        ).annotate(
            date=TruncDate("created_at")
        ).values("date").annotate(count=Count("id")).order_by("date")

        labels = []
        values = []
        for item in daily_bookings:
            labels.append(item["date"].strftime("%b %d"))
            values.append(item["count"])

        return {
            "labels": labels,
            "datasets": [{
                "label": "Bookings",
                "data": values,
                "borderColor": "#3B82F6",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "fill": True,
            }]
        }

    def _get_flights_data(self, start_date):
        """Get daily flights data for charts."""
        daily_flights = Flight.objects.filter(
            scheduled_departure__date__gte=start_date
        ).annotate(
            date=TruncDate("scheduled_departure")
        ).values("date").annotate(count=Count("id")).order_by("date")

        labels = []
        values = []
        for item in daily_flights:
            labels.append(item["date"].strftime("%b %d"))
            values.append(item["count"])

        return {
            "labels": labels,
            "datasets": [{
                "label": "Flights",
                "data": values,
                "borderColor": "#8B5CF6",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "fill": True,
            }]
        }

    def _get_status_data(self):
        """Get booking status distribution data."""
        status_data = Booking.objects.values("status").annotate(
            count=Count("id")
        )

        labels = []
        values = []
        colors = {
            "PENDING": "#F59E0B",
            "CONFIRMED": "#10B981",
            "CANCELLED": "#EF4444",
            "COMPLETED": "#3B82F6",
        }
        background_colors = []

        for item in status_data:
            labels.append(item["status"].replace("_", " ").title())
            values.append(item["count"])
            background_colors.append(colors.get(item["status"], "#6B7280"))

        return {
            "labels": labels,
            "datasets": [{
                "data": values,
                "backgroundColor": background_colors,
            }]
        }
