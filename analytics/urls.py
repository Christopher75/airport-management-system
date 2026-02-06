"""
URL configuration for analytics app.

Staff and admin analytics dashboards and reports.
"""

from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    # Main dashboard
    path("", views.AnalyticsDashboardView.as_view(), name="dashboard"),

    # Detailed reports
    path("revenue/", views.RevenueReportView.as_view(), name="revenue_report"),
    path("flights/", views.FlightReportView.as_view(), name="flight_report"),
    path("bookings/", views.BookingReportView.as_view(), name="booking_report"),

    # API endpoints for charts
    path("api/chart-data/", views.ChartDataAPIView.as_view(), name="chart_data"),
]
