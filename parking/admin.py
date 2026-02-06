"""
Admin configuration for the Parking app.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ParkingZone, ParkingSpot, ParkingPricing,
    ParkingReservation, ParkingService, ReservationService
)


class ParkingSpotInline(admin.TabularInline):
    """Inline admin for parking spots."""
    model = ParkingSpot
    extra = 0
    fields = ['spot_number', 'vehicle_type', 'is_covered', 'is_accessible', 'is_ev_charging', 'is_occupied', 'is_active']


class ParkingPricingInline(admin.TabularInline):
    """Inline admin for parking pricing."""
    model = ParkingPricing
    extra = 0
    fields = ['vehicle_type', 'hourly_rate', 'daily_rate', 'weekly_rate', 'monthly_rate', 'online_booking_discount', 'is_active']


@admin.register(ParkingZone)
class ParkingZoneAdmin(admin.ModelAdmin):
    """Admin for ParkingZone model."""
    list_display = [
        'name', 'code', 'zone_type', 'terminal', 'total_spots',
        'available_spots_display', 'occupancy_display', 'features_display', 'is_active'
    ]
    list_filter = ['zone_type', 'terminal', 'is_active', 'is_covered', 'has_ev_charging']
    search_fields = ['name', 'code', 'terminal']
    ordering = ['name']
    inlines = [ParkingPricingInline, ParkingSpotInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'zone_type', 'description')
        }),
        ('Capacity', {
            'fields': ('total_spots', 'available_spots')
        }),
        ('Location', {
            'fields': ('terminal', 'floor_level', 'distance_to_terminal')
        }),
        ('Features', {
            'fields': (
                'is_covered', 'has_cctv', 'has_security',
                'has_shuttle', 'has_ev_charging', 'has_car_wash', 'has_valet'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def available_spots_display(self, obj):
        """Display available spots with color coding."""
        percentage = obj.get_occupancy_percentage()
        if percentage >= 90:
            color = 'red'
        elif percentage >= 70:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{} / {}</span>',
            color, obj.available_spots, obj.total_spots
        )
    available_spots_display.short_description = 'Available'

    def occupancy_display(self, obj):
        """Display occupancy percentage with progress bar."""
        percentage = obj.get_occupancy_percentage()
        if percentage >= 90:
            color = '#dc3545'
        elif percentage >= 70:
            color = '#ffc107'
        else:
            color = '#28a745'
        return format_html(
            '''<div style="width:100px;background:#e9ecef;border-radius:3px;">
                <div style="width:{}%;background:{};height:18px;border-radius:3px;text-align:center;color:white;font-size:11px;line-height:18px;">
                    {}%
                </div>
            </div>''',
            percentage, color, percentage
        )
    occupancy_display.short_description = 'Occupancy'

    def features_display(self, obj):
        """Display available features as badges."""
        features = []
        if obj.is_covered:
            features.append('<span style="background:#17a2b8;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">Covered</span>')
        if obj.has_ev_charging:
            features.append('<span style="background:#28a745;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">EV</span>')
        if obj.has_shuttle:
            features.append('<span style="background:#6f42c1;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">Shuttle</span>')
        if obj.has_valet:
            features.append('<span style="background:#fd7e14;color:white;padding:2px 6px;border-radius:3px;font-size:10px;">Valet</span>')
        return format_html(' '.join(features)) if features else '-'
    features_display.short_description = 'Features'


@admin.register(ParkingSpot)
class ParkingSpotAdmin(admin.ModelAdmin):
    """Admin for ParkingSpot model."""
    list_display = ['__str__', 'zone', 'vehicle_type', 'is_covered', 'is_accessible', 'is_occupied', 'is_active']
    list_filter = ['zone', 'vehicle_type', 'is_covered', 'is_accessible', 'is_ev_charging', 'is_occupied', 'is_active']
    search_fields = ['spot_number', 'zone__name', 'zone__code']
    ordering = ['zone', 'spot_number']


@admin.register(ParkingPricing)
class ParkingPricingAdmin(admin.ModelAdmin):
    """Admin for ParkingPricing model."""
    list_display = [
        'zone', 'vehicle_type', 'hourly_rate_display', 'daily_rate_display',
        'weekly_rate_display', 'online_booking_discount', 'is_active'
    ]
    list_filter = ['zone', 'vehicle_type', 'is_active']
    search_fields = ['zone__name', 'zone__code']
    ordering = ['zone', 'vehicle_type']

    def hourly_rate_display(self, obj):
        return f"₦{obj.hourly_rate:,.2f}"
    hourly_rate_display.short_description = 'Hourly Rate'

    def daily_rate_display(self, obj):
        return f"₦{obj.daily_rate:,.2f}"
    daily_rate_display.short_description = 'Daily Rate'

    def weekly_rate_display(self, obj):
        return f"₦{obj.weekly_rate:,.2f}" if obj.weekly_rate else '-'
    weekly_rate_display.short_description = 'Weekly Rate'


class ReservationServiceInline(admin.TabularInline):
    """Inline admin for reservation services."""
    model = ReservationService
    extra = 0
    fields = ['service', 'quantity', 'price', 'is_completed']


@admin.register(ParkingReservation)
class ParkingReservationAdmin(admin.ModelAdmin):
    """Admin for ParkingReservation model."""
    list_display = [
        'reservation_code', 'user', 'zone', 'vehicle_registration',
        'check_in_date', 'check_out_date', 'duration_display',
        'total_price_display', 'status_display', 'is_paid'
    ]
    list_filter = ['status', 'zone', 'vehicle_type', 'is_paid', 'created_at']
    search_fields = ['reservation_code', 'vehicle_registration', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['reservation_code', 'created_at', 'updated_at']
    inlines = [ReservationServiceInline]

    fieldsets = (
        ('Reservation Info', {
            'fields': ('reservation_code', 'user', 'status')
        }),
        ('Parking Details', {
            'fields': ('zone', 'spot', 'flight_number')
        }),
        ('Vehicle Information', {
            'fields': ('vehicle_type', 'vehicle_registration', 'vehicle_make', 'vehicle_model', 'vehicle_color')
        }),
        ('Dates', {
            'fields': ('check_in_date', 'check_out_date', 'actual_check_in', 'actual_check_out')
        }),
        ('Pricing', {
            'fields': ('base_price', 'discount_amount', 'service_charges', 'total_price')
        }),
        ('Payment', {
            'fields': ('is_paid', 'payment_reference', 'paid_at')
        }),
        ('Contact', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Notes', {
            'fields': ('special_requests', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def duration_display(self, obj):
        return obj.get_duration_display()
    duration_display.short_description = 'Duration'

    def total_price_display(self, obj):
        return f"₦{obj.total_price:,.2f}"
    total_price_display.short_description = 'Total Price'

    def status_display(self, obj):
        """Display status with color coding."""
        colors = {
            'PENDING': '#ffc107',
            'CONFIRMED': '#17a2b8',
            'ACTIVE': '#28a745',
            'COMPLETED': '#6c757d',
            'CANCELLED': '#dc3545',
            'NO_SHOW': '#343a40',
            'EXPIRED': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:3px;font-size:11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    actions = ['mark_as_confirmed', 'mark_as_cancelled']

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='CONFIRMED')
        self.message_user(request, f'{updated} reservation(s) marked as confirmed.')
    mark_as_confirmed.short_description = 'Mark selected as Confirmed'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.filter(status__in=['PENDING', 'CONFIRMED']).update(status='CANCELLED')
        self.message_user(request, f'{updated} reservation(s) marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected as Cancelled'


@admin.register(ParkingService)
class ParkingServiceAdmin(admin.ModelAdmin):
    """Admin for ParkingService model."""
    list_display = ['name', 'code', 'price_display', 'duration_display', 'zones_display', 'is_active']
    list_filter = ['is_active', 'available_zones']
    search_fields = ['name', 'code']
    ordering = ['name']
    filter_horizontal = ['available_zones']

    def price_display(self, obj):
        return f"₦{obj.price:,.2f}"
    price_display.short_description = 'Price'

    def duration_display(self, obj):
        if obj.duration_minutes:
            if obj.duration_minutes >= 60:
                hours = obj.duration_minutes // 60
                mins = obj.duration_minutes % 60
                return f"{hours}h {mins}m" if mins else f"{hours}h"
            return f"{obj.duration_minutes}m"
        return '-'
    duration_display.short_description = 'Duration'

    def zones_display(self, obj):
        zones = obj.available_zones.all()[:3]
        count = obj.available_zones.count()
        if count == 0:
            return 'All Zones'
        names = ', '.join([z.code for z in zones])
        if count > 3:
            names += f' +{count - 3} more'
        return names
    zones_display.short_description = 'Available In'


@admin.register(ReservationService)
class ReservationServiceAdmin(admin.ModelAdmin):
    """Admin for ReservationService model."""
    list_display = ['reservation', 'service', 'quantity', 'price_display', 'total_display', 'is_completed']
    list_filter = ['service', 'is_completed']
    search_fields = ['reservation__reservation_code', 'service__name']

    def price_display(self, obj):
        return f"₦{obj.price:,.2f}"
    price_display.short_description = 'Unit Price'

    def total_display(self, obj):
        return f"₦{obj.get_total():,.2f}"
    total_display.short_description = 'Total'
