"""
URL configuration for accounts app.

User dashboard, profile, and booking management.
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("bookings/", views.BookingListView.as_view(), name="bookings"),
    path("bookings/<str:reference>/", views.BookingDetailView.as_view(), name="booking_detail"),
]
