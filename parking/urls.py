"""
URL configuration for the Parking app.
"""

from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    # Main parking page
    path('', views.ParkingHomeView.as_view(), name='home'),

    # Search
    path('search/', views.ParkingSearchView.as_view(), name='search'),

    # Pricing
    path('pricing/', views.PricingView.as_view(), name='pricing'),

    # Zone detail
    path('zone/<int:pk>/', views.ParkingZoneDetailView.as_view(), name='zone_detail'),

    # Reservations
    path('reserve/', views.CreateReservationView.as_view(), name='create_reservation'),
    path('my-reservations/', views.MyReservationsView.as_view(), name='my_reservations'),
    path('reservation/<int:pk>/', views.ReservationDetailView.as_view(), name='reservation_detail'),
    path('reservation/<int:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/<int:pk>/pay/', views.PayReservationView.as_view(), name='pay_reservation'),
    path('reservation/<int:pk>/verify/<str:payment_ref>/', views.verify_parking_payment, name='verify_payment'),

    # AJAX endpoints
    path('api/price-estimate/', views.get_price_estimate, name='price_estimate'),
]
