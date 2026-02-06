"""
URL configuration for the REST API.

API Version 1 endpoints.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

app_name = "api"

# Create router for viewsets
router = DefaultRouter()
router.register(r"airports", views.AirportViewSet, basename="airport")
router.register(r"airlines", views.AirlineViewSet, basename="airline")
router.register(r"flights", views.FlightViewSet, basename="flight")
router.register(r"bookings", views.BookingViewSet, basename="booking")
router.register(r"payments", views.PaymentViewSet, basename="payment")
router.register(r"notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    # JWT Authentication
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # User registration and profile
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/profile/", views.ProfileView.as_view(), name="profile"),

    # Dashboard
    path("dashboard/stats/", views.DashboardStatsView.as_view(), name="dashboard_stats"),
    path("dashboard/upcoming-flights/", views.UpcomingFlightsView.as_view(), name="upcoming_flights"),

    # Router URLs (viewsets)
    path("", include(router.urls)),
]
