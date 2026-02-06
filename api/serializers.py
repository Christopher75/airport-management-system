"""
API Serializers for the Airport Management System.

Defines serializers for all API endpoints.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from airlines.models import Aircraft, Airline
from bookings.models import Booking, Passenger, SeatClass
from flights.models import Airport, Flight, FlightStatus, Gate
from notifications.models import Notification
from payments.models import Payment

User = get_user_model()


# ============================================================================
# User Serializers
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "phone_number", "date_of_birth", "nationality",
            "date_joined", "is_active"
        ]
        read_only_fields = ["id", "email", "date_joined", "is_active"]

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "password", "password_confirm",
            "first_name", "last_name", "phone_number"
        ]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone_number",
            "date_of_birth", "nationality", "passport_number",
            "passport_expiry", "passport_country"
        ]


# ============================================================================
# Airline Serializers
# ============================================================================

class AirlineSerializer(serializers.ModelSerializer):
    """Serializer for Airline model."""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Airline
        fields = [
            "id", "name", "code", "logo_url", "country",
            "is_active", "website"
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class AircraftSerializer(serializers.ModelSerializer):
    """Serializer for Aircraft model."""

    airline_name = serializers.CharField(source="airline.name", read_only=True)

    class Meta:
        model = Aircraft
        fields = [
            "id", "airline", "airline_name", "registration", "model",
            "manufacturer", "economy_class_seats", "business_class_seats",
            "first_class_seats", "total_seats", "is_active"
        ]


# ============================================================================
# Flight Serializers
# ============================================================================

class AirportSerializer(serializers.ModelSerializer):
    """Serializer for Airport model."""

    class Meta:
        model = Airport
        fields = [
            "id", "name", "code", "icao_code", "city", "country",
            "timezone", "latitude", "longitude", "is_international", "is_active"
        ]


class AirportMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Airport (for nested use)."""

    class Meta:
        model = Airport
        fields = ["code", "name", "city", "country"]


class GateSerializer(serializers.ModelSerializer):
    """Serializer for Gate model."""

    airport_code = serializers.CharField(source="airport.code", read_only=True)

    class Meta:
        model = Gate
        fields = [
            "id", "airport", "airport_code", "terminal",
            "gate_number", "status", "is_international"
        ]


class FlightListSerializer(serializers.ModelSerializer):
    """Serializer for Flight list view (minimal data)."""

    airline = AirlineSerializer(read_only=True)
    origin = AirportMinimalSerializer(read_only=True)
    destination = AirportMinimalSerializer(read_only=True)
    duration = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()

    class Meta:
        model = Flight
        fields = [
            "id", "flight_number", "airline", "origin", "destination",
            "scheduled_departure", "scheduled_arrival", "duration",
            "status", "economy_price", "business_price", "first_class_price",
            "available_economy_seats", "available_business_seats",
            "available_first_class_seats", "is_bookable", "is_international"
        ]


class FlightDetailSerializer(serializers.ModelSerializer):
    """Serializer for Flight detail view (full data)."""

    airline = AirlineSerializer(read_only=True)
    origin = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    aircraft = AircraftSerializer(read_only=True)
    departure_gate = GateSerializer(read_only=True)
    arrival_gate = GateSerializer(read_only=True)
    duration = serializers.ReadOnlyField()
    is_bookable = serializers.ReadOnlyField()
    total_available_seats = serializers.ReadOnlyField()

    class Meta:
        model = Flight
        fields = [
            "id", "flight_number", "airline", "aircraft",
            "origin", "destination", "departure_gate", "arrival_gate",
            "scheduled_departure", "scheduled_arrival",
            "actual_departure", "actual_arrival", "duration",
            "status", "delay_reason",
            "economy_price", "business_price", "first_class_price",
            "available_economy_seats", "available_business_seats",
            "available_first_class_seats", "total_available_seats",
            "is_bookable", "is_international", "meal_service", "wifi_available",
            "created_at", "updated_at"
        ]


class FlightSearchSerializer(serializers.Serializer):
    """Serializer for flight search parameters."""

    origin = serializers.CharField(max_length=3, required=False)
    destination = serializers.CharField(max_length=3, required=False)
    departure_date = serializers.DateField(required=False)
    return_date = serializers.DateField(required=False)
    passengers = serializers.IntegerField(min_value=1, max_value=9, default=1)
    seat_class = serializers.ChoiceField(
        choices=SeatClass.choices,
        default=SeatClass.ECONOMY
    )


# ============================================================================
# Booking Serializers
# ============================================================================

class PassengerSerializer(serializers.ModelSerializer):
    """Serializer for Passenger model."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Passenger
        fields = [
            "id", "title", "first_name", "last_name", "full_name",
            "date_of_birth", "passenger_type", "passport_number",
            "passport_expiry", "passport_country", "nationality",
            "seat_number", "is_checked_in", "checked_in_at",
            "meal_preference", "checked_baggage"
        ]
        read_only_fields = ["id", "is_checked_in", "checked_in_at"]


class PassengerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating passengers."""

    class Meta:
        model = Passenger
        fields = [
            "title", "first_name", "last_name", "date_of_birth",
            "passenger_type", "passport_number", "passport_expiry",
            "passport_country", "nationality", "meal_preference"
        ]


class BookingListSerializer(serializers.ModelSerializer):
    """Serializer for Booking list view."""

    flight_number = serializers.CharField(source="flight.flight_number", read_only=True)
    origin = serializers.CharField(source="flight.origin.code", read_only=True)
    destination = serializers.CharField(source="flight.destination.code", read_only=True)
    departure_date = serializers.DateTimeField(source="flight.scheduled_departure", read_only=True)
    passenger_count = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            "id", "reference", "flight_number", "origin", "destination",
            "departure_date", "seat_class", "status", "passenger_count",
            "total_price", "created_at"
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    """Serializer for Booking detail view."""

    flight = FlightListSerializer(read_only=True)
    passengers = PassengerSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "reference", "user_email", "flight", "passengers",
            "status", "seat_class", "base_price", "taxes", "fees",
            "discount", "total_price", "contact_email", "contact_phone",
            "special_requests", "booked_at", "confirmed_at", "cancelled_at",
            "cancellation_reason", "created_at", "updated_at"
        ]


class BookingCreateSerializer(serializers.Serializer):
    """Serializer for creating a booking."""

    flight_id = serializers.IntegerField()
    seat_class = serializers.ChoiceField(choices=SeatClass.choices)
    passengers = PassengerCreateSerializer(many=True)
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField(max_length=20)
    special_requests = serializers.CharField(required=False, allow_blank=True)

    def validate_flight_id(self, value):
        try:
            flight = Flight.objects.get(pk=value)
            if not flight.is_bookable:
                raise serializers.ValidationError("This flight is not available for booking.")
            return value
        except Flight.DoesNotExist:
            raise serializers.ValidationError("Flight not found.")

    def validate_passengers(self, value):
        if not value:
            raise serializers.ValidationError("At least one passenger is required.")
        if len(value) > 9:
            raise serializers.ValidationError("Maximum 9 passengers per booking.")
        return value


# ============================================================================
# Payment Serializers
# ============================================================================

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""

    booking_reference = serializers.CharField(source="booking.reference", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "booking", "booking_reference", "amount", "currency",
            "status", "payment_method", "paystack_reference",
            "paid_at", "created_at"
        ]
        read_only_fields = [
            "id", "paystack_reference", "paid_at", "created_at"
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating a payment."""

    booking_reference = serializers.CharField(max_length=6)

    def validate_booking_reference(self, value):
        try:
            booking = Booking.objects.get(reference=value.upper())
            if booking.status != "PENDING":
                raise serializers.ValidationError("Booking is not pending payment.")
            return value.upper()
        except Booking.DoesNotExist:
            raise serializers.ValidationError("Booking not found.")


# ============================================================================
# Notification Serializers
# ============================================================================

class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "title", "message",
            "is_read", "action_url", "action_text",
            "created_at", "read_at"
        ]
        read_only_fields = ["id", "created_at"]


# ============================================================================
# Dashboard/Stats Serializers
# ============================================================================

class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for user dashboard statistics."""

    total_bookings = serializers.IntegerField()
    upcoming_flights = serializers.IntegerField()
    completed_flights = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=12, decimal_places=2)
    loyalty_points = serializers.IntegerField()
