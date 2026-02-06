"""
Admin configuration for the flights app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Airport, Flight, FlightStatus, Gate


class GateInline(admin.TabularInline):
    """Inline admin for Gates within Airport admin."""

    model = Gate
    extra = 0
    fields = ("terminal", "gate_number", "status", "is_international")


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    """Admin configuration for Airport model."""

    inlines = [GateInline]

    list_display = (
        "code",
        "name",
        "city",
        "country",
        "is_international",
        "is_active",
        "gate_count",
    )
    list_filter = ("is_international", "is_active", "country")
    search_fields = ("name", "code", "icao_code", "city")
    ordering = ("name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "code"),
                    "icao_code",
                )
            },
        ),
        (
            _("Location"),
            {
                "fields": (
                    ("city", "country"),
                    "timezone",
                    ("latitude", "longitude"),
                )
            },
        ),
        (
            _("Contact"),
            {
                "fields": (
                    "phone",
                    "website",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    ("is_international", "is_active"),
                )
            },
        ),
    )

    def gate_count(self, obj):
        """Return the number of gates for this airport."""
        return obj.gates.count()

    gate_count.short_description = _("Gates")


@admin.register(Gate)
class GateAdmin(admin.ModelAdmin):
    """Admin configuration for Gate model."""

    list_display = (
        "airport",
        "terminal",
        "gate_number",
        "status_badge",
        "is_international",
    )
    list_filter = ("airport", "terminal", "status", "is_international")
    search_fields = ("airport__name", "airport__code", "gate_number")
    ordering = ("airport", "terminal", "gate_number")

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "AVAILABLE": "#28a745",
            "OCCUPIED": "#007bff",
            "BOARDING": "#ffc107",
            "MAINTENANCE": "#dc3545",
            "CLOSED": "#6c757d",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")
    status_badge.admin_order_field = "status"


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Admin configuration for Flight model."""

    list_display = (
        "flight_number",
        "airline",
        "route_display",
        "scheduled_departure",
        "duration",
        "status_badge",
        "available_seats",
        "economy_price",
    )
    list_filter = (
        "status",
        "airline",
        "is_international",
        "origin",
        "destination",
        "scheduled_departure",
    )
    search_fields = (
        "flight_number",
        "airline__name",
        "airline__code",
        "origin__code",
        "destination__code",
    )
    ordering = ("-scheduled_departure",)
    date_hierarchy = "scheduled_departure"
    raw_id_fields = ("airline", "aircraft", "origin", "destination")

    fieldsets = (
        (
            _("Flight Identification"),
            {
                "fields": (
                    ("flight_number", "airline"),
                    "aircraft",
                )
            },
        ),
        (
            _("Route"),
            {
                "fields": (
                    ("origin", "destination"),
                    "is_international",
                )
            },
        ),
        (
            _("Schedule"),
            {
                "fields": (
                    ("scheduled_departure", "scheduled_arrival"),
                    ("actual_departure", "actual_arrival"),
                )
            },
        ),
        (
            _("Gates"),
            {
                "fields": (
                    ("departure_gate", "arrival_gate"),
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "status",
                    "delay_reason",
                )
            },
        ),
        (
            _("Pricing (Nigerian Naira)"),
            {
                "fields": (
                    ("economy_price", "business_price", "first_class_price"),
                )
            },
        ),
        (
            _("Availability"),
            {
                "fields": (
                    (
                        "available_economy_seats",
                        "available_business_seats",
                        "available_first_class_seats",
                    ),
                )
            },
        ),
        (
            _("Amenities"),
            {
                "fields": (
                    ("meal_service", "wifi_available"),
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["mark_as_delayed", "mark_as_cancelled", "mark_as_boarding"]

    def route_display(self, obj):
        """Display route as origin -> destination."""
        return f"{obj.origin.code} → {obj.destination.code}"

    route_display.short_description = _("Route")

    def available_seats(self, obj):
        """Display total available seats."""
        return obj.total_available_seats

    available_seats.short_description = _("Seats")

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "SCHEDULED": "#6c757d",
            "CHECK_IN_OPEN": "#17a2b8",
            "BOARDING": "#ffc107",
            "GATE_CLOSED": "#fd7e14",
            "DEPARTED": "#007bff",
            "IN_FLIGHT": "#007bff",
            "LANDED": "#20c997",
            "ARRIVED": "#28a745",
            "DELAYED": "#dc3545",
            "CANCELLED": "#343a40",
            "DIVERTED": "#e83e8c",
        }
        color = colors.get(obj.status, "#6c757d")
        text_color = "black" if obj.status == "BOARDING" else "white"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            text_color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")
    status_badge.admin_order_field = "status"

    @admin.action(description=_("Mark selected flights as Delayed"))
    def mark_as_delayed(self, request, queryset):
        updated = queryset.update(status=FlightStatus.DELAYED)
        self.message_user(request, f"{updated} flight(s) marked as delayed.")

    @admin.action(description=_("Mark selected flights as Cancelled"))
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status=FlightStatus.CANCELLED)
        self.message_user(request, f"{updated} flight(s) marked as cancelled.")

    @admin.action(description=_("Mark selected flights as Boarding"))
    def mark_as_boarding(self, request, queryset):
        updated = queryset.update(status=FlightStatus.BOARDING)
        self.message_user(request, f"{updated} flight(s) marked as boarding.")
