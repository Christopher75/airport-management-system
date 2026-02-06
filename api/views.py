"""
API Views for the Airport Management System.

RESTful API endpoints for flights, bookings, users, and more.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from airlines.models import Airline
from bookings.models import Booking, BookingStatus, Passenger, SeatClass
from flights.models import Airport, Flight, FlightStatus
from notifications.models import Notification
from payments.models import Payment, PaymentStatus

from .serializers import (
    AirlineSerializer,
    AirportSerializer,
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingListSerializer,
    DashboardStatsSerializer,
    FlightDetailSerializer,
    FlightListSerializer,
    FlightSearchSerializer,
    NotificationSerializer,
    PassengerSerializer,
    PaymentInitiateSerializer,
    PaymentSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


# ============================================================================
# Authentication Views
# ============================================================================

class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.

    POST /api/v1/auth/register/
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Registration successful.",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the current user's profile.

    GET /api/v1/auth/profile/
    PUT/PATCH /api/v1/auth/profile/
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserSerializer


# ============================================================================
# Airport Views
# ============================================================================

class AirportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for airports.

    GET /api/v1/airports/ - List all active airports
    GET /api/v1/airports/{id}/ - Get airport details
    GET /api/v1/airports/search/?q=lagos - Search airports
    """

    queryset = Airport.objects.filter(is_active=True).order_by("name")
    serializer_class = AirportSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=["get"])
    def search(self, request):
        """Search airports by name, city, or code."""
        query = request.query_params.get("q", "")
        if len(query) < 2:
            return Response([])

        airports = self.queryset.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(code__icontains=query)
        )[:10]

        serializer = self.get_serializer(airports, many=True)
        return Response(serializer.data)


# ============================================================================
# Airline Views
# ============================================================================

class AirlineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for airlines.

    GET /api/v1/airlines/ - List all active airlines
    GET /api/v1/airlines/{id}/ - Get airline details
    """

    queryset = Airline.objects.filter(is_active=True).order_by("name")
    serializer_class = AirlineSerializer
    permission_classes = [permissions.AllowAny]


# ============================================================================
# Flight Views
# ============================================================================

class FlightViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for flights.

    GET /api/v1/flights/ - List upcoming flights
    GET /api/v1/flights/{id}/ - Get flight details
    GET /api/v1/flights/search/ - Search flights
    GET /api/v1/flights/status-board/ - Get status board data
    """

    queryset = Flight.objects.select_related(
        "airline", "origin", "destination", "aircraft"
    ).order_by("scheduled_departure")
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Default to future flights
        if self.action == "list":
            queryset = queryset.filter(
                scheduled_departure__gte=timezone.now()
            )

        return queryset

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Search for available flights.

        Query params:
        - origin: Airport code (e.g., ABV)
        - destination: Airport code (e.g., LOS)
        - departure_date: Date (YYYY-MM-DD)
        - passengers: Number of passengers (1-9)
        - seat_class: ECONOMY, BUSINESS, or FIRST
        """
        serializer = FlightSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        queryset = self.get_queryset().filter(
            status__in=[FlightStatus.SCHEDULED, FlightStatus.CHECK_IN_OPEN, FlightStatus.DELAYED]
        )

        if data.get("origin"):
            queryset = queryset.filter(origin__code=data["origin"].upper())

        if data.get("destination"):
            queryset = queryset.filter(destination__code=data["destination"].upper())

        if data.get("departure_date"):
            queryset = queryset.filter(scheduled_departure__date=data["departure_date"])

        # Filter by seat availability
        seat_class = data.get("seat_class", "ECONOMY")
        passengers = data.get("passengers", 1)

        if seat_class == "ECONOMY":
            queryset = queryset.filter(available_economy_seats__gte=passengers)
        elif seat_class == "BUSINESS":
            queryset = queryset.filter(available_business_seats__gte=passengers)
        elif seat_class == "FIRST":
            queryset = queryset.filter(available_first_class_seats__gte=passengers)

        flights = queryset[:50]
        serializer = FlightListSerializer(flights, many=True, context={"request": request})

        return Response({
            "count": len(flights),
            "results": serializer.data
        })

    @action(detail=False, methods=["get"])
    def status_board(self, request):
        """
        Get flight status board data.

        Query params:
        - airport: Airport code (default: ABV)
        - type: departures or arrivals (default: departures)
        """
        airport_code = request.query_params.get("airport", "ABV")
        board_type = request.query_params.get("type", "departures")
        now = timezone.now()

        try:
            airport = Airport.objects.get(code=airport_code.upper())
        except Airport.DoesNotExist:
            return Response(
                {"error": "Airport not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        time_start = now - timedelta(hours=1)
        time_end = now + timedelta(hours=12)

        if board_type == "arrivals":
            flights = Flight.objects.select_related(
                "airline", "origin", "destination"
            ).filter(
                destination=airport,
                scheduled_arrival__range=(time_start, time_end)
            ).order_by("scheduled_arrival")[:20]
        else:
            flights = Flight.objects.select_related(
                "airline", "origin", "destination"
            ).filter(
                origin=airport,
                scheduled_departure__range=(time_start, time_end)
            ).order_by("scheduled_departure")[:20]

        serializer = FlightListSerializer(flights, many=True, context={"request": request})

        return Response({
            "airport": AirportSerializer(airport).data,
            "type": board_type,
            "timestamp": now.isoformat(),
            "flights": serializer.data
        })

    @action(detail=True, methods=["get"])
    def track(self, request, pk=None):
        """Get real-time tracking data for a flight."""
        flight = self.get_object()
        now = timezone.now()

        # Calculate progress
        if flight.scheduled_departure and flight.scheduled_arrival:
            total_duration = (flight.scheduled_arrival - flight.scheduled_departure).total_seconds()
            elapsed = (now - flight.scheduled_departure).total_seconds()

            if elapsed < 0:
                progress = 0
            elif elapsed >= total_duration:
                progress = 100
            else:
                progress = int((elapsed / total_duration) * 100)
        else:
            progress = 0

        serializer = FlightDetailSerializer(flight, context={"request": request})

        return Response({
            "flight": serializer.data,
            "progress": progress,
            "timestamp": now.isoformat()
        })


# ============================================================================
# Booking Views
# ============================================================================

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for bookings.

    GET /api/v1/bookings/ - List user's bookings
    POST /api/v1/bookings/ - Create a new booking
    GET /api/v1/bookings/{reference}/ - Get booking details
    DELETE /api/v1/bookings/{reference}/ - Cancel booking
    """

    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        return Booking.objects.select_related(
            "flight", "flight__airline", "flight__origin", "flight__destination"
        ).prefetch_related("passengers").filter(
            user=self.request.user
        ).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        if self.action in ["retrieve", "list"]:
            if self.action == "retrieve":
                return BookingDetailSerializer
            return BookingListSerializer
        return BookingListSerializer

    def create(self, request, *args, **kwargs):
        """Create a new booking."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        flight = Flight.objects.get(pk=data["flight_id"])
        seat_class = data["seat_class"]
        passengers_data = data["passengers"]
        passenger_count = len(passengers_data)

        # Check availability
        if seat_class == "ECONOMY" and flight.available_economy_seats < passenger_count:
            return Response(
                {"error": "Not enough economy seats available."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif seat_class == "BUSINESS" and flight.available_business_seats < passenger_count:
            return Response(
                {"error": "Not enough business seats available."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif seat_class == "FIRST" and flight.available_first_class_seats < passenger_count:
            return Response(
                {"error": "Not enough first class seats available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate price
        if seat_class == "BUSINESS":
            unit_price = flight.business_price
        elif seat_class == "FIRST":
            unit_price = flight.first_class_price
        else:
            unit_price = flight.economy_price

        base_price = unit_price * passenger_count
        taxes = base_price * Decimal("0.10")
        fees = Decimal("2000.00")
        total = base_price + taxes + fees

        # Create booking
        booking = Booking.objects.create(
            user=request.user,
            flight=flight,
            seat_class=seat_class,
            base_price=base_price,
            taxes=taxes,
            fees=fees,
            total_price=total,
            contact_email=data["contact_email"],
            contact_phone=data["contact_phone"],
            special_requests=data.get("special_requests", ""),
            status=BookingStatus.PENDING,
        )

        # Create passengers
        for pax_data in passengers_data:
            Passenger.objects.create(booking=booking, **pax_data)

        return Response(
            BookingDetailSerializer(booking, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """Cancel a booking."""
        booking = self.get_object()

        if not booking.is_cancellable:
            return Response(
                {"error": "This booking cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()
        booking.save()

        return Response({"message": "Booking cancelled successfully."})

    @action(detail=True, methods=["get"])
    def passengers(self, request, reference=None):
        """Get passengers for a booking."""
        booking = self.get_object()
        passengers = booking.passengers.all()
        serializer = PassengerSerializer(passengers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def eticket(self, request, reference=None):
        """Get e-ticket download URL."""
        booking = self.get_object()

        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]:
            return Response(
                {"error": "E-ticket is only available for confirmed bookings."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "download_url": request.build_absolute_uri(
                f"/bookings/eticket/{booking.reference}/"
            )
        })


# ============================================================================
# Payment Views
# ============================================================================

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for payments.

    GET /api/v1/payments/ - List user's payments
    GET /api/v1/payments/{id}/ - Get payment details
    POST /api/v1/payments/initiate/ - Initiate a payment
    """

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.select_related("booking").filter(
            user=self.request.user
        ).order_by("-created_at")

    @action(detail=False, methods=["post"])
    def initiate(self, request):
        """Initiate a payment for a booking."""
        serializer = PaymentInitiateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = Booking.objects.get(reference=serializer.validated_data["booking_reference"])

        if booking.user != request.user:
            return Response(
                {"error": "You don't have permission to pay for this booking."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check for existing pending payment
        existing_payment = Payment.objects.filter(
            booking=booking,
            status=PaymentStatus.PENDING
        ).first()

        if existing_payment:
            return Response({
                "message": "Payment already initiated.",
                "payment": PaymentSerializer(existing_payment).data,
                "payment_url": request.build_absolute_uri(
                    f"/payments/initiate/{booking.reference}/"
                )
            })

        return Response({
            "booking": BookingListSerializer(booking).data,
            "payment_url": request.build_absolute_uri(
                f"/payments/initiate/{booking.reference}/"
            )
        })


# ============================================================================
# Notification Views
# ============================================================================

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for notifications.

    GET /api/v1/notifications/ - List user's notifications
    GET /api/v1/notifications/unread-count/ - Get unread count
    POST /api/v1/notifications/{id}/mark-read/ - Mark as read
    POST /api/v1/notifications/mark-all-read/ - Mark all as read
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({"message": "Notification marked as read."})

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({"message": "All notifications marked as read."})


# ============================================================================
# Dashboard Views
# ============================================================================

class DashboardStatsView(APIView):
    """
    Get dashboard statistics for the current user.

    GET /api/v1/dashboard/stats/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()

        # Get booking stats
        bookings = Booking.objects.filter(user=user)
        total_bookings = bookings.count()

        upcoming_flights = bookings.filter(
            status=BookingStatus.CONFIRMED,
            flight__scheduled_departure__gt=now
        ).count()

        completed_flights = bookings.filter(
            status=BookingStatus.COMPLETED
        ).count()

        # Total spent
        total_spent = Payment.objects.filter(
            user=user,
            status=PaymentStatus.COMPLETED
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        # Loyalty points (placeholder - implement actual logic)
        loyalty_points = int(total_spent / 1000)  # 1 point per 1000 NGN

        data = {
            "total_bookings": total_bookings,
            "upcoming_flights": upcoming_flights,
            "completed_flights": completed_flights,
            "total_spent": total_spent,
            "loyalty_points": loyalty_points
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)


class UpcomingFlightsView(APIView):
    """
    Get upcoming flights for the current user.

    GET /api/v1/dashboard/upcoming-flights/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.select_related(
            "flight", "flight__airline", "flight__origin", "flight__destination"
        ).filter(
            user=request.user,
            status=BookingStatus.CONFIRMED,
            flight__scheduled_departure__gt=timezone.now()
        ).order_by("flight__scheduled_departure")[:5]

        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)
