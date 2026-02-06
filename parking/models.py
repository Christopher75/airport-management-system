"""
Parking models for the NAIA Airport Management System.

This module contains models for airport parking management including:
- ParkingZone: Different parking areas/lots
- ParkingSpot: Individual parking spaces
- ParkingPricing: Pricing tiers for different zones/durations
- ParkingReservation: Booking/reservation for parking
- ParkingService: Additional services (car wash, valet, etc.)
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
import random
import string


class ParkingZoneType(models.TextChoices):
    """Types of parking zones."""
    SHORT_TERM = "SHORT_TERM", "Short Term (Hourly)"
    LONG_TERM = "LONG_TERM", "Long Term (Daily/Weekly)"
    PREMIUM = "PREMIUM", "Premium/VIP"
    ECONOMY = "ECONOMY", "Economy"
    VALET = "VALET", "Valet Parking"
    DISABLED = "DISABLED", "Disabled/Accessible"
    ELECTRIC = "ELECTRIC", "Electric Vehicle"
    MOTORCYCLE = "MOTORCYCLE", "Motorcycle"


class VehicleType(models.TextChoices):
    """Types of vehicles."""
    CAR = "CAR", "Car/Sedan"
    SUV = "SUV", "SUV/Crossover"
    VAN = "VAN", "Van/Minivan"
    TRUCK = "TRUCK", "Truck/Pickup"
    MOTORCYCLE = "MOTORCYCLE", "Motorcycle"
    ELECTRIC = "ELECTRIC", "Electric Vehicle"


class ReservationStatus(models.TextChoices):
    """Reservation status options."""
    PENDING = "PENDING", "Pending"
    CONFIRMED = "CONFIRMED", "Confirmed"
    ACTIVE = "ACTIVE", "Active (Checked In)"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    NO_SHOW = "NO_SHOW", "No Show"
    EXPIRED = "EXPIRED", "Expired"


def generate_reservation_code():
    """Generate a unique parking reservation code."""
    prefix = "PRK"
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{random_part}"


class ParkingZone(models.Model):
    """
    Represents a parking zone/lot at the airport.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    zone_type = models.CharField(
        max_length=20,
        choices=ParkingZoneType.choices,
        default=ParkingZoneType.SHORT_TERM
    )
    description = models.TextField(blank=True)

    # Capacity
    total_spots = models.PositiveIntegerField(default=100)
    available_spots = models.PositiveIntegerField(default=100)

    # Location
    terminal = models.CharField(max_length=50, blank=True, help_text="Associated terminal (e.g., Domestic, International)")
    floor_level = models.CharField(max_length=20, blank=True, help_text="Floor/Level (e.g., Ground, Level 1)")
    distance_to_terminal = models.PositiveIntegerField(
        default=0,
        help_text="Walking distance to terminal in meters"
    )

    # Features
    is_covered = models.BooleanField(default=False, help_text="Is the parking area covered?")
    has_cctv = models.BooleanField(default=True, help_text="24/7 CCTV surveillance")
    has_security = models.BooleanField(default=True, help_text="Security patrol")
    has_shuttle = models.BooleanField(default=False, help_text="Free shuttle service to terminal")
    has_ev_charging = models.BooleanField(default=False, help_text="EV charging stations")
    has_car_wash = models.BooleanField(default=False, help_text="Car wash service available")
    has_valet = models.BooleanField(default=False, help_text="Valet service available")

    # Status
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Parking Zone"
        verbose_name_plural = "Parking Zones"

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_occupancy_percentage(self):
        """Calculate current occupancy percentage."""
        if self.total_spots == 0:
            return 0
        occupied = self.total_spots - self.available_spots
        return round((occupied / self.total_spots) * 100, 1)

    def is_full(self):
        """Check if parking zone is full."""
        return self.available_spots == 0

    def update_availability(self, spots_change):
        """Update available spots (positive = spots freed, negative = spots taken)."""
        new_available = self.available_spots + spots_change
        self.available_spots = max(0, min(new_available, self.total_spots))
        self.save(update_fields=['available_spots'])


class ParkingSpot(models.Model):
    """
    Individual parking spot within a zone.
    """
    zone = models.ForeignKey(
        ParkingZone,
        on_delete=models.CASCADE,
        related_name='spots'
    )
    spot_number = models.CharField(max_length=20)

    # Spot characteristics
    is_covered = models.BooleanField(default=False)
    is_accessible = models.BooleanField(default=False, help_text="Disabled accessible spot")
    is_ev_charging = models.BooleanField(default=False, help_text="Has EV charging")
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.CAR
    )

    # Status
    is_occupied = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['zone', 'spot_number']
        unique_together = ['zone', 'spot_number']
        verbose_name = "Parking Spot"
        verbose_name_plural = "Parking Spots"

    def __str__(self):
        return f"{self.zone.code}-{self.spot_number}"


class ParkingPricing(models.Model):
    """
    Pricing tiers for parking zones.
    """
    zone = models.ForeignKey(
        ParkingZone,
        on_delete=models.CASCADE,
        related_name='pricing'
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.CAR
    )

    # Pricing (in Naira)
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    weekly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )
    monthly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True
    )

    # Grace period and max rates
    grace_period_minutes = models.PositiveIntegerField(
        default=15,
        help_text="Free grace period in minutes"
    )
    max_daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        null=True,
        blank=True,
        help_text="Maximum charge per day"
    )

    # Discounts
    online_booking_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Percentage discount for online booking"
    )
    loyalty_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Percentage discount for loyalty members"
    )

    # Validity
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['zone', 'vehicle_type']
        unique_together = ['zone', 'vehicle_type']
        verbose_name = "Parking Pricing"
        verbose_name_plural = "Parking Pricing"

    def __str__(self):
        return f"{self.zone.name} - {self.get_vehicle_type_display()}"

    def calculate_price(self, hours, apply_online_discount=False):
        """Calculate total price for given hours."""
        # Convert hours to Decimal for proper arithmetic
        hours = Decimal(str(hours))

        if hours <= (Decimal(str(self.grace_period_minutes)) / Decimal('60')):
            return Decimal('0.00')

        days = int(hours // Decimal('24'))
        remaining_hours = hours % Decimal('24')

        # Calculate base price
        if self.weekly_rate and days >= 7:
            weeks = days // 7
            remaining_days = days % 7
            total = (Decimal(str(weeks)) * self.weekly_rate) + (Decimal(str(remaining_days)) * self.daily_rate)
        else:
            total = Decimal(str(days)) * self.daily_rate

        # Add hourly rate for remaining hours
        hourly_charge = remaining_hours * self.hourly_rate
        if self.max_daily_rate and hourly_charge > self.max_daily_rate:
            hourly_charge = self.max_daily_rate
        total += hourly_charge

        # Apply online discount
        if apply_online_discount:
            discount = total * (self.online_booking_discount / Decimal('100'))
            total -= discount

        return total.quantize(Decimal('0.01'))


class ParkingReservation(models.Model):
    """
    Parking reservation/booking.
    """
    # Reference
    reservation_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_reservation_code
    )

    # User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='parking_reservations'
    )

    # Parking details
    zone = models.ForeignKey(
        ParkingZone,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    spot = models.ForeignKey(
        ParkingSpot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations'
    )

    # Vehicle details
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.CAR
    )
    vehicle_registration = models.CharField(max_length=20)
    vehicle_make = models.CharField(max_length=50, blank=True)
    vehicle_model = models.CharField(max_length=50, blank=True)
    vehicle_color = models.CharField(max_length=30, blank=True)

    # Booking period
    check_in_date = models.DateTimeField()
    check_out_date = models.DateTimeField()
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)

    # Flight association (optional)
    flight_number = models.CharField(max_length=20, blank=True, help_text="Associated flight number")

    # Pricing
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    service_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=ReservationStatus.choices,
        default=ReservationStatus.PENDING
    )

    # Payment
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Contact
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)

    # Notes
    special_requests = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Parking Reservation"
        verbose_name_plural = "Parking Reservations"

    def __str__(self):
        return f"{self.reservation_code} - {self.vehicle_registration}"

    def get_duration_hours(self):
        """Get booking duration in hours."""
        if self.actual_check_out and self.actual_check_in:
            delta = self.actual_check_out - self.actual_check_in
        else:
            delta = self.check_out_date - self.check_in_date
        return delta.total_seconds() / 3600

    def get_duration_display(self):
        """Get human-readable duration."""
        hours = self.get_duration_hours()
        if hours < 24:
            return f"{int(hours)} hours"
        days = int(hours // 24)
        remaining_hours = int(hours % 24)
        if remaining_hours:
            return f"{days} days, {remaining_hours} hours"
        return f"{days} days"

    def is_overdue(self):
        """Check if reservation is overdue for checkout."""
        if self.status == ReservationStatus.ACTIVE:
            return timezone.now() > self.check_out_date
        return False

    def can_cancel(self):
        """Check if reservation can be cancelled."""
        if self.status in [ReservationStatus.PENDING, ReservationStatus.CONFIRMED]:
            # Allow cancellation up to 2 hours before check-in
            return timezone.now() < (self.check_in_date - timezone.timedelta(hours=2))
        return False

    def check_in(self, spot=None):
        """Process check-in."""
        self.status = ReservationStatus.ACTIVE
        self.actual_check_in = timezone.now()
        if spot:
            self.spot = spot
            spot.is_occupied = True
            spot.save()
        self.zone.update_availability(-1)
        self.save()

    def check_out(self):
        """Process check-out."""
        self.status = ReservationStatus.COMPLETED
        self.actual_check_out = timezone.now()
        if self.spot:
            self.spot.is_occupied = False
            self.spot.is_reserved = False
            self.spot.save()
        self.zone.update_availability(1)
        self.save()


class ParkingService(models.Model):
    """
    Additional parking services (car wash, valet, etc.).
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Duration (for time-based services)
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Service duration in minutes (0 if not applicable)"
    )

    # Availability
    is_active = models.BooleanField(default=True)
    available_zones = models.ManyToManyField(
        ParkingZone,
        related_name='available_services',
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Parking Service"
        verbose_name_plural = "Parking Services"

    def __str__(self):
        return f"{self.name} - ₦{self.price:,.2f}"


class ReservationService(models.Model):
    """
    Links services to reservations.
    """
    reservation = models.ForeignKey(
        ParkingReservation,
        on_delete=models.CASCADE,
        related_name='services'
    )
    service = models.ForeignKey(
        ParkingService,
        on_delete=models.CASCADE,
        related_name='reservation_services'
    )

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reservation Service"
        verbose_name_plural = "Reservation Services"

    def __str__(self):
        return f"{self.reservation.reservation_code} - {self.service.name}"

    def get_total(self):
        """Get total price for this service."""
        return self.price * self.quantity
