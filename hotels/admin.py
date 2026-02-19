"""
Admin configuration for the Hotel Booking app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Hotel, HotelBooking, RoomType


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1
    fields = ("name", "bed_type", "max_occupancy", "base_price_per_night", "total_rooms", "is_active")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "star_display", "distance_from_airport", "has_airport_shuttle", "is_active")
    list_filter = ("star_rating", "has_airport_shuttle", "is_active")
    search_fields = ("name", "address")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [RoomTypeInline]

    def star_display(self, obj):
        return obj.star_display
    star_display.short_description = _("Rating")


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "hotel", "bed_type", "max_occupancy", "base_price_per_night", "total_rooms", "is_active")
    list_filter = ("hotel", "bed_type", "is_active")
    search_fields = ("name", "hotel__name")


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "guest_full_name", "hotel", "room_type",
        "check_in_date", "check_out_date", "num_nights",
        "total_price", "is_paid", "status",
    )
    list_filter = ("status", "is_paid", "hotel")
    search_fields = ("reference", "guest_first_name", "guest_last_name", "guest_email")
    ordering = ("-created_at",)
    readonly_fields = (
        "reference", "subtotal", "vat_amount", "service_fee", "total_price",
        "created_at", "updated_at",
    )

    def guest_full_name(self, obj):
        return obj.guest_full_name
    guest_full_name.short_description = _("Guest")
