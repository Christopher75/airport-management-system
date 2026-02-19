"""
Admin configuration for the airlines app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    Aircraft,
    Airline,
    AircraftParkingRate,
    AircraftParkingRecord,
    AircraftStand,
)


class AircraftInline(admin.TabularInline):
    """Inline admin for Aircraft within Airline admin."""

    model = Aircraft
    extra = 0
    fields = (
        "registration",
        "aircraft_type",
        "total_seats",
        "status",
        "is_active",
    )
    readonly_fields = ("total_seats",)


@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    """Admin configuration for Airline model."""

    inlines = [AircraftInline]

    list_display = (
        "name",
        "code",
        "country",
        "alliance",
        "aircraft_count",
        "is_active",
        "logo_preview",
    )
    list_filter = ("is_active", "country", "alliance")
    search_fields = ("name", "code", "icao_code", "country")
    ordering = ("name",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("name", "code"),
                    ("icao_code", "country"),
                    "headquarters",
                )
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": (
                    "phone",
                    "email",
                    "website",
                )
            },
        ),
        (
            _("Branding"),
            {
                "fields": (
                    "logo",
                    "primary_color",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    "is_active",
                    "alliance",
                )
            },
        ),
        (
            _("Description"),
            {
                "fields": ("description",),
                "classes": ("collapse",),
            },
        ),
    )

    def aircraft_count(self, obj):
        """Return the number of aircraft for this airline."""
        return obj.aircraft.count()

    aircraft_count.short_description = _("Fleet Size")

    def logo_preview(self, obj):
        """Display a small preview of the airline logo."""
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height: 30px; max-width: 60px;" />',
                obj.logo.url,
            )
        return "-"

    logo_preview.short_description = _("Logo")


@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    """Admin configuration for Aircraft model."""

    list_display = (
        "registration",
        "airline",
        "aircraft_type",
        "total_seats",
        "status_badge",
        "is_active",
        "age",
    )
    list_filter = ("airline", "aircraft_type", "status", "is_active")
    search_fields = ("registration", "airline__name", "airline__code", "serial_number")
    ordering = ("airline", "registration")
    raw_id_fields = ("airline",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "airline",
                    ("registration", "aircraft_type"),
                    ("model_name", "name"),
                )
            },
        ),
        (
            _("Capacity"),
            {
                "fields": (
                    ("first_class_seats", "business_class_seats", "economy_class_seats"),
                    "total_seats",
                )
            },
        ),
        (
            _("Aircraft Details"),
            {
                "fields": (
                    ("year_manufactured", "serial_number"),
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Maintenance"),
            {
                "fields": (
                    ("last_maintenance_date", "next_maintenance_date"),
                )
            },
        ),
        (
            _("Status"),
            {
                "fields": (
                    ("status", "is_active"),
                )
            },
        ),
    )

    readonly_fields = ("total_seats",)

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "ACTIVE": "#28a745",
            "MAINTENANCE": "#ffc107",
            "GROUNDED": "#dc3545",
            "RETIRED": "#6c757d",
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

    def age(self, obj):
        """Display the aircraft age."""
        age = obj.age
        if age is not None:
            return f"{age} years"
        return "-"

    age.short_description = _("Age")


# ============================================================
# Aircraft Parking Management Admin
# ============================================================

@admin.register(AircraftStand)
class AircraftStandAdmin(admin.ModelAdmin):
    list_display = ("stand_number", "terminal", "stand_type", "max_aircraft_size", "has_jetway", "has_gpu", "has_pca", "is_active")
    list_filter = ("terminal", "stand_type", "max_aircraft_size", "is_active")
    search_fields = ("stand_number", "terminal")
    ordering = ("terminal", "stand_number")


@admin.register(AircraftParkingRate)
class AircraftParkingRateAdmin(admin.ModelAdmin):
    list_display = ("aircraft_size", "landing_fee", "hourly_rate", "daily_rate", "weekly_rate", "effective_from")
    ordering = ("aircraft_size",)


@admin.register(AircraftParkingRecord)
class AircraftParkingRecordAdmin(admin.ModelAdmin):
    list_display = (
        "record_number", "airline", "aircraft", "stand",
        "aircraft_size", "scheduled_arrival", "duration_display",
        "total_due", "is_paid", "status",
    )
    list_filter = ("status", "is_paid", "aircraft_size", "airline")
    search_fields = ("record_number", "aircraft__registration", "airline__name", "payment_reference")
    ordering = ("-scheduled_arrival",)
    readonly_fields = ("record_number", "duration_display", "total_due", "landing_fee", "parking_fee", "service_fee")
    actions = ["recalculate_fees"]

    def recalculate_fees(self, request, queryset):
        for record in queryset:
            record.calculate_and_save_fees()
        self.message_user(request, f"Fees recalculated for {queryset.count()} record(s).")
    recalculate_fees.short_description = "Recalculate fees for selected records"

    def duration_display(self, obj):
        return obj.duration_display
    duration_display.short_description = _("Duration")
