from django.urls import path
from . import views

app_name = "lounge"

urlpatterns = [
    path("", views.lounge_list, name="lounge_list"),
    path("<int:pk>/book/", views.book_lounge, name="book_lounge"),
    path("booking/<str:reference>/confirmed/", views.booking_confirmation, name="booking_confirmation"),
    path("my-passes/", views.my_lounge_bookings, name="my_bookings"),
]
