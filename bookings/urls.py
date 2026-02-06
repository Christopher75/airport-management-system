"""
URL configuration for bookings app.

Multi-step booking flow URLs.
"""

from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    # Booking flow
    path("select/<int:flight_id>/", views.SelectFlightView.as_view(), name="select_flight"),
    path("passengers/", views.PassengerDetailsView.as_view(), name="passengers"),
    path("review/", views.BookingReviewView.as_view(), name="review"),
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("confirmation/<str:reference>/", views.BookingConfirmationView.as_view(), name="confirmation"),

    # Manage booking
    path("manage/", views.ManageBookingView.as_view(), name="manage"),
    path("detail/<str:reference>/", views.BookingDetailPublicView.as_view(), name="detail"),

    # E-ticket download
    path("eticket/<str:reference>/", views.DownloadETicketView.as_view(), name="eticket"),
    path("eticket/<str:reference>/public/", views.DownloadETicketPublicView.as_view(), name="eticket_public"),

    # Cancel booking
    path("cancel/<str:reference>/", views.CancelBookingView.as_view(), name="cancel"),
]
