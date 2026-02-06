"""
URL configuration for airport_system project.

Nnamdi Azikiwe International Airport Management System
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Admin Site Customization
admin.site.site_header = "Nnamdi Azikiwe International Airport"
admin.site.site_title = "NAIA Admin Portal"
admin.site.index_title = "Airport Management System"

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Core pages (home, about, contact)
    path("", include("core.urls")),

    # Flight search and listing
    path("flights/", include("flights.urls")),

    # Booking flow
    path("bookings/", include("bookings.urls")),

    # Payments
    path("payments/", include("payments.urls")),

    # User dashboard and profile (custom accounts app)
    path("dashboard/", include("accounts.urls")),

    # Notifications
    path("notifications/", include("notifications.urls")),

    # Analytics Dashboard (staff only)
    path("analytics/", include("analytics.urls")),

    # Parking
    path("parking/", include("parking.urls")),

    # Authentication (django-allauth)
    path("accounts/", include("allauth.urls")),

    # REST API v1
    path("api/v1/", include("api.urls")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar (if installed)
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
