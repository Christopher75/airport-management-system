"""
Admin configuration for the bookings app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Booking, BookingStatus, Passenger, Seat


class PassengerInline(admin.TabularInline):
    """Inline admin for Passengers within Booking admin."""

    model = Passenger
    extra = 0
    fields = (
        "title",
        "first_name",
        "last_name",
        "passenger_type",
        "seat_number",
        "is_checked_in",
    )
    readonly_fields = ("is_checked_in",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for Booking model."""

    inlines = [PassengerInline]

    list_display = (
        "reference",
        "user",
        "flight",
        "seat_class",
        "passenger_count",
        "formatted_total",
        "status_badge",
        "booked_at",
    )
    list_filter = ("status", "seat_class", "flight__airline", "booked_at")
    search_fields = (
        "reference",
        "user__email",
        "user__first_name",
        "user__last_name",
        "flight__flight_number",
        "contact_email",
    )
    ordering = ("-booked_at",)
    date_hierarchy = "booked_at"
    raw_id_fields = ("user", "flight")

    fieldsets = (
        (
            _("Booking Information"),
            {
                "fields": (
                    ("reference", "status"),
                    ("user", "flight"),
                    "seat_class",
                )
            },
        ),
        (
            _("Pricing"),
            {
                "fields": (
                    ("base_price", "taxes", "fees"),
                    ("discount", "total_price"),
                )
            },
        ),
        (
            _("Contact"),
            {
                "fields": (
                    ("contact_email", "contact_phone"),
                )
            },
        ),
        (
            _("Additional Information"),
            {
                "fields": ("special_requests",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    ("booked_at", "confirmed_at"),
                    ("cancelled_at", "cancellation_reason"),
                ),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("reference", "booked_at", "total_price")

    actions = ["confirm_bookings", "cancel_bookings"]

    def passenger_count(self, obj):
        """Return the number of passengers."""
        return obj.passenger_count

    passenger_count.short_description = _("Passengers")

    def formatted_total(self, obj):
        """Display total price formatted as currency."""
        return f"₦{obj.total_price:,.2f}"

    formatted_total.short_description = _("Total")
    formatted_total.admin_order_field = "total_price"

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "PENDING": "#ffc107",
            "CONFIRMED": "#28a745",
            "CHECKED_IN": "#17a2b8",
            "BOARDED": "#007bff",
            "COMPLETED": "#6c757d",
            "CANCELLED": "#dc3545",
            "REFUNDED": "#fd7e14",
            "NO_SHOW": "#343a40",
        }
        color = colors.get(obj.status, "#6c757d")
        text_color = "black" if obj.status == "PENDING" else "white"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            text_color,
            obj.get_status_display(),
        )

    status_badge.short_description = _("Status")
    status_badge.admin_order_field = "status"

    @admin.action(description=_("Confirm selected bookings"))
    def confirm_bookings(self, request, queryset):
        from django.utils import timezone

        updated = queryset.filter(status=BookingStatus.PENDING).update(
            status=BookingStatus.CONFIRMED,
            confirmed_at=timezone.now(),
        )
        self.message_user(request, f"{updated} booking(s) confirmed.")

    @admin.action(description=_("Cancel selected bookings"))
    def cancel_bookings(self, request, queryset):
        from django.utils import timezone

        cancellable = queryset.filter(
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        )
        updated = cancellable.update(
            status=BookingStatus.CANCELLED,
            cancelled_at=timezone.now(),
        )
        self.message_user(request, f"{updated} booking(s) cancelled.")


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    """Admin configuration for Passenger model."""

    list_display = (
        "full_name",
        "booking",
        "passenger_type",
        "seat_number",
        "is_checked_in",
        "has_boarded",
    )
    list_filter = ("passenger_type", "is_checked_in", "has_boarded", "meal_preference")
    search_fields = (
        "first_name",
        "last_name",
        "booking__reference",
        "passport_number",
    )
    ordering = ("booking", "last_name", "first_name")
    raw_id_fields = ("booking",)

    fieldsets = (
        (
            _("Personal Information"),
            {
                "fields": (
                    "booking",
                    ("title", "first_name", "last_name"),
                    ("date_of_birth", "passenger_type"),
                    "nationality",
                )
            },
        ),
        (
            _("Travel Documents"),
            {
                "fields": (
                    ("passport_number", "passport_expiry"),
                    "passport_country",
                )
            },
        ),
        (
            _("Seat & Baggage"),
            {
                "fields": (
                    "seat_number",
                    "checked_baggage",
                )
            },
        ),
        (
            _("Check-in & Boarding"),
            {
                "fields": (
                    ("is_checked_in", "checked_in_at"),
                    ("has_boarded", "boarded_at"),
                )
            },
        ),
        (
            _("Special Requirements"),
            {
                "fields": (
                    "meal_preference",
                    "special_assistance",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    """Admin configuration for Seat model."""

    list_display = (
        "seat_number",
        "aircraft",
        "seat_class",
        "position",
        "has_extra_legroom",
        "is_exit_row",
        "is_blocked",
    )
    list_filter = (
        "aircraft__airline",
        "seat_class",
        "position",
        "has_extra_legroom",
        "is_exit_row",
        "is_blocked",
    )
    search_fields = ("seat_number", "aircraft__registration")
    ordering = ("aircraft", "row_number", "seat_number")
    raw_id_fields = ("aircraft",)
