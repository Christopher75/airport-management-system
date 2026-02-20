"""
URL configuration for the Hotel Booking app.
"""

from django.urls import path

from . import views

app_name = "hotels"

urlpatterns = [
    path("", views.hotel_list, name="hotel_list"),
    # Fixed paths must come before the <slug> wildcard
    path("my-bookings/", views.my_hotel_bookings, name="my_bookings"),
    path("book/room/<int:room_type_id>/", views.book_room, name="book_room"),
    path("booking/<str:reference>/review/", views.booking_review, name="booking_review"),
    path("booking/<str:reference>/confirmed/", views.booking_confirmation, name="booking_confirmation"),
    path("booking/<str:reference>/cancel/", views.cancel_hotel_booking, name="cancel_booking"),
    # Slug pattern last so it doesn't swallow the fixed URLs above
    path("<slug:slug>/", views.hotel_detail, name="hotel_detail"),
]
