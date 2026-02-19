"""
URL configuration for the Airlines app — Aircraft Parking Management.
"""

from django.urls import path

from . import views

app_name = "airlines"

urlpatterns = [
    path("parking/", views.aircraft_parking_dashboard, name="parking_dashboard"),
    path("parking/register/", views.register_aircraft_parking, name="register_parking"),
    path("parking/<int:pk>/", views.aircraft_parking_detail, name="parking_detail"),
    path("parking/rates/", views.parking_rates, name="parking_rates"),
]
