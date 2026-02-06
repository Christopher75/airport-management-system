"""
URL configuration for flights app.

Flight search, listing, detail pages, and real-time flight information.
"""

from django.urls import path

from . import views

app_name = "flights"

urlpatterns = [
    # Flight search and listing
    path("", views.FlightSearchView.as_view(), name="search"),
    path("list/", views.FlightListView.as_view(), name="list"),
    path("<int:pk>/", views.FlightDetailView.as_view(), name="detail"),

    # Real-time flight information
    path("status-board/", views.FlightStatusBoardView.as_view(), name="status_board"),
    path("departures/", views.DeparturesBoardView.as_view(), name="departures"),
    path("arrivals/", views.ArrivalsBoardView.as_view(), name="arrivals"),
    path("track/<int:pk>/", views.FlightTrackingView.as_view(), name="tracking"),

    # API endpoints
    path("api/airports/", views.airport_autocomplete, name="airport_autocomplete"),
    path("api/status/", views.FlightStatusAPIView.as_view(), name="status_api"),
    path("api/status/<int:pk>/", views.FlightStatusAPIView.as_view(), name="status_api_detail"),
]
