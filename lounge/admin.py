from django.contrib import admin
from .models import AirportLounge, LoungeBooking


@admin.register(AirportLounge)
class AirportLoungeAdmin(admin.ModelAdmin):
    list_display = ("name", "terminal", "lounge_type", "day_pass_price", "capacity", "is_active")
    list_filter = ("terminal", "lounge_type", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(LoungeBooking)
class LoungeBookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "lounge", "guest_name", "visit_date", "num_adults", "total_price", "status", "access_code")
    list_filter = ("status", "lounge")
    search_fields = ("reference", "guest_name", "guest_email", "access_code")
    readonly_fields = ("reference", "access_code", "subtotal", "vat_amount", "total_price")
