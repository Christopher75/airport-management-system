"""
Flight views for the Airport Management System.

Handles flight search, listing, detail pages, and real-time flight information.
"""

import json
from datetime import timedelta

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from .forms import FlightSearchForm
from .models import Airport, Flight, FlightStatus


class FlightSearchView(TemplateView):
    """
    Flight search page with search form and results.
    """

    template_name = "flights/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize form with GET data
        form = FlightSearchForm(self.request.GET or None)
        context["form"] = form
        context["airports"] = Airport.objects.filter(is_active=True).order_by("name")

        # If form is submitted and valid, perform search
        if self.request.GET and form.is_valid():
            flights = self.search_flights(form.cleaned_data)
            context["flights"] = flights
            context["search_performed"] = True
            context["search_params"] = form.cleaned_data
        else:
            context["flights"] = []
            context["search_performed"] = False

        return context

    def search_flights(self, data):
        """
        Search for flights based on form data.
        """
        flights = Flight.objects.select_related(
            "airline", "origin", "destination", "aircraft"
        ).filter(
            status__in=[
                FlightStatus.SCHEDULED,
                FlightStatus.CHECK_IN_OPEN,
                FlightStatus.DELAYED,
            ]
        )

        # Filter by origin
        if data.get("origin"):
            flights = flights.filter(origin__code=data["origin"])

        # Filter by destination
        if data.get("destination"):
            flights = flights.filter(destination__code=data["destination"])

        # Filter by departure date
        if data.get("departure_date"):
            departure_date = data["departure_date"]
            flights = flights.filter(
                scheduled_departure__date=departure_date
            )
        else:
            # Default to future flights
            flights = flights.filter(scheduled_departure__gte=timezone.now())

        # Filter by seat class availability
        seat_class = data.get("seat_class", "ECONOMY")
        if seat_class == "ECONOMY":
            flights = flights.filter(available_economy_seats__gt=0)
        elif seat_class == "BUSINESS":
            flights = flights.filter(available_business_seats__gt=0)
        elif seat_class == "FIRST":
            flights = flights.filter(available_first_class_seats__gt=0)

        # Filter by minimum seats needed
        passengers = data.get("passengers", 1)
        if seat_class == "ECONOMY":
            flights = flights.filter(available_economy_seats__gte=passengers)
        elif seat_class == "BUSINESS":
            flights = flights.filter(available_business_seats__gte=passengers)
        elif seat_class == "FIRST":
            flights = flights.filter(available_first_class_seats__gte=passengers)

        return flights.order_by("scheduled_departure")[:50]


class FlightListView(ListView):
    """
    List all upcoming flights with filtering options.
    """

    model = Flight
    template_name = "flights/list.html"
    context_object_name = "flights"
    paginate_by = 20

    def get_queryset(self):
        queryset = Flight.objects.select_related(
            "airline", "origin", "destination", "aircraft"
        ).filter(
            scheduled_departure__gte=timezone.now()
        ).order_by("scheduled_departure")

        # Apply filters from GET parameters
        origin = self.request.GET.get("origin")
        if origin:
            queryset = queryset.filter(origin__code=origin)

        destination = self.request.GET.get("destination")
        if destination:
            queryset = queryset.filter(destination__code=destination)

        airline = self.request.GET.get("airline")
        if airline:
            queryset = queryset.filter(airline__code=airline)

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["airports"] = Airport.objects.filter(is_active=True).order_by("name")
        context["statuses"] = FlightStatus.choices
        return context


class FlightDetailView(DetailView):
    """
    Detail view for a specific flight.
    """

    model = Flight
    template_name = "flights/detail.html"
    context_object_name = "flight"

    def get_queryset(self):
        return Flight.objects.select_related(
            "airline", "origin", "destination", "aircraft", "departure_gate"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        flight = self.object

        # Check seat availability
        context["economy_available"] = flight.available_economy_seats > 0
        context["business_available"] = flight.available_business_seats > 0
        context["first_available"] = flight.available_first_class_seats > 0

        # Check if flight is bookable
        context["is_bookable"] = flight.is_bookable

        return context


def airport_autocomplete(request):
    """
    AJAX endpoint for airport autocomplete.
    Returns JSON list of airports matching the search term.
    """
    from django.http import JsonResponse

    term = request.GET.get("term", "")
    if len(term) < 2:
        return JsonResponse([], safe=False)

    airports = Airport.objects.filter(
        Q(name__icontains=term) |
        Q(city__icontains=term) |
        Q(code__icontains=term)
    ).filter(is_active=True)[:10]

    results = [
        {
            "id": airport.code,
            "text": f"{airport.city} ({airport.code}) - {airport.name}",
            "code": airport.code,
            "city": airport.city,
            "country": airport.country,
        }
        for airport in airports
    ]

    return JsonResponse(results, safe=False)


# ============================================================================
# Real-Time Flight Information Views
# ============================================================================

class FlightStatusBoardView(TemplateView):
    """
    Real-time flight status board showing departures and arrivals.
    Similar to airport display boards.
    """

    template_name = "flights/status_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Get the airport (default to ABV - Nnamdi Azikiwe)
        airport_code = self.request.GET.get("airport", "ABV")
        try:
            airport = Airport.objects.get(code=airport_code)
        except Airport.DoesNotExist:
            airport = Airport.objects.filter(is_active=True).first()

        context["airport"] = airport
        context["airports"] = Airport.objects.filter(is_active=True).order_by("name")

        # Time window: 2 hours before to 12 hours after now
        time_start = now - timedelta(hours=2)
        time_end = now + timedelta(hours=12)

        # Departures from this airport
        departures = Flight.objects.select_related(
            "airline", "origin", "destination", "departure_gate"
        ).filter(
            origin=airport,
            scheduled_departure__range=(time_start, time_end)
        ).order_by("scheduled_departure")[:20]

        # Arrivals to this airport
        arrivals = Flight.objects.select_related(
            "airline", "origin", "destination", "arrival_gate"
        ).filter(
            destination=airport,
            scheduled_arrival__range=(time_start, time_end)
        ).order_by("scheduled_arrival")[:20]

        context["departures"] = departures
        context["arrivals"] = arrivals
        context["current_time"] = now
        context["board_type"] = self.request.GET.get("type", "departures")

        return context


class DeparturesBoardView(TemplateView):
    """Departures-only board view."""

    template_name = "flights/departures_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        airport_code = self.request.GET.get("airport", "ABV")
        try:
            airport = Airport.objects.get(code=airport_code)
        except Airport.DoesNotExist:
            airport = Airport.objects.filter(is_active=True).first()

        context["airport"] = airport
        context["airports"] = Airport.objects.filter(is_active=True).order_by("name")

        # Time window
        time_start = now - timedelta(hours=1)
        time_end = now + timedelta(hours=24)

        departures = Flight.objects.select_related(
            "airline", "origin", "destination", "departure_gate"
        ).filter(
            origin=airport,
            scheduled_departure__range=(time_start, time_end)
        ).order_by("scheduled_departure")[:30]

        context["flights"] = departures
        context["current_time"] = now

        return context


class ArrivalsBoardView(TemplateView):
    """Arrivals-only board view."""

    template_name = "flights/arrivals_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        airport_code = self.request.GET.get("airport", "ABV")
        try:
            airport = Airport.objects.get(code=airport_code)
        except Airport.DoesNotExist:
            airport = Airport.objects.filter(is_active=True).first()

        context["airport"] = airport
        context["airports"] = Airport.objects.filter(is_active=True).order_by("name")

        # Time window
        time_start = now - timedelta(hours=1)
        time_end = now + timedelta(hours=24)

        arrivals = Flight.objects.select_related(
            "airline", "origin", "destination", "arrival_gate"
        ).filter(
            destination=airport,
            scheduled_arrival__range=(time_start, time_end)
        ).order_by("scheduled_arrival")[:30]

        context["flights"] = arrivals
        context["current_time"] = now

        return context


class FlightTrackingView(DetailView):
    """
    Real-time flight tracking view with map and status updates.
    """

    model = Flight
    template_name = "flights/tracking.html"
    context_object_name = "flight"

    def get_queryset(self):
        return Flight.objects.select_related(
            "airline", "origin", "destination", "aircraft",
            "departure_gate", "arrival_gate"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        flight = self.object
        now = timezone.now()

        # Calculate flight progress percentage
        if flight.scheduled_departure and flight.scheduled_arrival:
            total_duration = (flight.scheduled_arrival - flight.scheduled_departure).total_seconds()
            elapsed = (now - flight.scheduled_departure).total_seconds()

            if elapsed < 0:
                progress = 0  # Not departed yet
            elif elapsed >= total_duration:
                progress = 100  # Arrived
            else:
                progress = int((elapsed / total_duration) * 100)

            context["flight_progress"] = progress
        else:
            context["flight_progress"] = 0

        # Flight status timeline
        context["status_timeline"] = self._get_status_timeline(flight)

        # Estimated time remaining
        if flight.status in [FlightStatus.IN_FLIGHT, FlightStatus.DEPARTED]:
            remaining = flight.scheduled_arrival - now
            if remaining.total_seconds() > 0:
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes = remainder // 60
                context["time_remaining"] = f"{hours}h {minutes}m"
            else:
                context["time_remaining"] = "Arriving soon"
        else:
            context["time_remaining"] = None

        return context

    def _get_status_timeline(self, flight):
        """Generate timeline events for the flight."""
        timeline = []
        now = timezone.now()

        # Scheduled
        timeline.append({
            "status": "Scheduled",
            "time": flight.scheduled_departure,
            "completed": True,
            "icon": "fa-calendar-check",
        })

        # Check-in Open (2 hours before departure)
        checkin_time = flight.scheduled_departure - timedelta(hours=2)
        timeline.append({
            "status": "Check-in Open",
            "time": checkin_time,
            "completed": now >= checkin_time or flight.status not in [FlightStatus.SCHEDULED],
            "icon": "fa-clipboard-check",
        })

        # Boarding (45 min before)
        boarding_time = flight.scheduled_departure - timedelta(minutes=45)
        timeline.append({
            "status": "Boarding",
            "time": boarding_time,
            "completed": flight.status in [
                FlightStatus.BOARDING, FlightStatus.GATE_CLOSED,
                FlightStatus.DEPARTED, FlightStatus.IN_FLIGHT,
                FlightStatus.LANDED, FlightStatus.ARRIVED
            ],
            "icon": "fa-door-open",
        })

        # Departed
        departure_time = flight.actual_departure or flight.scheduled_departure
        timeline.append({
            "status": "Departed",
            "time": departure_time,
            "completed": flight.status in [
                FlightStatus.DEPARTED, FlightStatus.IN_FLIGHT,
                FlightStatus.LANDED, FlightStatus.ARRIVED
            ],
            "icon": "fa-plane-departure",
        })

        # In Flight
        timeline.append({
            "status": "In Flight",
            "time": None,
            "completed": flight.status in [
                FlightStatus.IN_FLIGHT, FlightStatus.LANDED, FlightStatus.ARRIVED
            ],
            "icon": "fa-plane",
        })

        # Arrived
        arrival_time = flight.actual_arrival or flight.scheduled_arrival
        timeline.append({
            "status": "Arrived",
            "time": arrival_time,
            "completed": flight.status in [FlightStatus.LANDED, FlightStatus.ARRIVED],
            "icon": "fa-plane-arrival",
        })

        return timeline


class FlightStatusAPIView(View):
    """
    API endpoint for real-time flight status updates.
    Used for AJAX polling or WebSocket updates.
    """

    def get(self, request, pk=None):
        """Get flight status for one or multiple flights."""
        if pk:
            # Single flight
            try:
                flight = Flight.objects.select_related(
                    "airline", "origin", "destination", "departure_gate"
                ).get(pk=pk)
                return JsonResponse(self._serialize_flight(flight))
            except Flight.DoesNotExist:
                return JsonResponse({"error": "Flight not found"}, status=404)
        else:
            # Multiple flights (for board updates)
            airport_code = request.GET.get("airport", "ABV")
            board_type = request.GET.get("type", "departures")
            now = timezone.now()

            try:
                airport = Airport.objects.get(code=airport_code)
            except Airport.DoesNotExist:
                return JsonResponse({"error": "Airport not found"}, status=404)

            time_start = now - timedelta(hours=1)
            time_end = now + timedelta(hours=12)

            if board_type == "arrivals":
                flights = Flight.objects.select_related(
                    "airline", "origin", "destination", "arrival_gate"
                ).filter(
                    destination=airport,
                    scheduled_arrival__range=(time_start, time_end)
                ).order_by("scheduled_arrival")[:20]
            else:
                flights = Flight.objects.select_related(
                    "airline", "origin", "destination", "departure_gate"
                ).filter(
                    origin=airport,
                    scheduled_departure__range=(time_start, time_end)
                ).order_by("scheduled_departure")[:20]

            return JsonResponse({
                "airport": airport.code,
                "type": board_type,
                "timestamp": now.isoformat(),
                "flights": [self._serialize_flight(f, board_type) for f in flights]
            })

    def _serialize_flight(self, flight, board_type="departures"):
        """Convert flight to JSON-serializable dict."""
        data = {
            "id": flight.id,
            "flight_number": flight.flight_number,
            "airline": {
                "name": flight.airline.name,
                "code": flight.airline.code,
                "logo": flight.airline.logo.url if flight.airline.logo else None,
            },
            "origin": {
                "code": flight.origin.code,
                "city": flight.origin.city,
                "name": flight.origin.name,
            },
            "destination": {
                "code": flight.destination.code,
                "city": flight.destination.city,
                "name": flight.destination.name,
            },
            "scheduled_departure": flight.scheduled_departure.isoformat(),
            "scheduled_arrival": flight.scheduled_arrival.isoformat(),
            "actual_departure": flight.actual_departure.isoformat() if flight.actual_departure else None,
            "actual_arrival": flight.actual_arrival.isoformat() if flight.actual_arrival else None,
            "status": flight.status,
            "status_display": flight.get_status_display(),
            "delay_reason": flight.delay_reason,
            "duration": flight.duration,
        }

        # Add gate info based on board type
        if board_type == "arrivals" and flight.arrival_gate:
            data["gate"] = f"{flight.arrival_gate.terminal}{flight.arrival_gate.gate_number}"
        elif flight.departure_gate:
            data["gate"] = f"{flight.departure_gate.terminal}{flight.departure_gate.gate_number}"
        else:
            data["gate"] = None

        return data
