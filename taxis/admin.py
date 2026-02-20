from django.contrib import admin
from django.utils.html import format_html

from .models import TaxiBooking, VehicleCategory


@admin.register(VehicleCategory)
class VehicleCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "vehicle_type", "max_passengers", "price_per_km", "minimum_fare", "is_active")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("vehicle_type", "is_active")


@admin.register(TaxiBooking)
class TaxiBookingAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "passenger_name", "vehicle_category", "trip_type",
        "pickup_datetime", "total_fare", "status_badge", "is_paid",
    )
    list_filter = ("status", "trip_type", "is_paid", "vehicle_category")
    search_fields = ("reference", "passenger_name", "passenger_email", "flight_number")
    readonly_fields = ("reference", "created_at", "updated_at", "base_fare", "vat_amount", "total_fare")
    date_hierarchy = "pickup_datetime"

    fieldsets = (
        ("Booking", {"fields": ("reference", "user", "vehicle_category", "status")}),
        ("Trip Details", {"fields": ("trip_type", "pickup_location", "dropoff_location", "pickup_datetime", "flight_number", "num_passengers", "num_luggage", "estimated_distance_km", "special_requests")}),
        ("Passenger", {"fields": ("passenger_name", "passenger_email", "passenger_phone")}),
        ("Pricing", {"fields": ("base_fare", "vat_amount", "total_fare")}),
        ("Payment", {"fields": ("is_paid", "payment_reference", "paid_at")}),
        ("Driver Assignment", {"fields": ("driver_name", "driver_phone", "vehicle_plate", "vehicle_colour")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "PENDING": "#f59e0b",
            "CONFIRMED": "#3b82f6",
            "ASSIGNED": "#8b5cf6",
            "EN_ROUTE": "#06b6d4",
            "COMPLETED": "#16a34a",
            "CANCELLED": "#ef4444",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display(),
        )
