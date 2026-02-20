from django.urls import path

from . import views

app_name = "taxis"

urlpatterns = [
    path("", views.taxi_list, name="taxi_list"),
    path("book/<slug:slug>/", views.book_taxi, name="book_taxi"),
    path("confirmation/<str:reference>/", views.booking_confirmation, name="booking_confirmation"),
    path("my-bookings/", views.my_taxi_bookings, name="my_bookings"),
    path("cancel/<str:reference>/", views.cancel_taxi_booking, name="cancel_booking"),
]
