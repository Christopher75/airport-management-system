"""
Flight forms for the Airport Management System.

Contains forms for flight search and filtering.
"""

from django import forms
from django.utils import timezone

from .models import Airport


class FlightSearchForm(forms.Form):
    """
    Flight search form with origin, destination, date, passengers, and class.
    """

    TRIP_TYPE_CHOICES = [
        ("one_way", "One Way"),
        ("round_trip", "Round Trip"),
    ]

    SEAT_CLASS_CHOICES = [
        ("ECONOMY", "Economy"),
        ("BUSINESS", "Business"),
        ("FIRST", "First Class"),
    ]

    PASSENGER_CHOICES = [(i, f"{i} Passenger{'s' if i > 1 else ''}") for i in range(1, 10)]

    trip_type = forms.ChoiceField(
        choices=TRIP_TYPE_CHOICES,
        initial="one_way",
        required=False,
        widget=forms.RadioSelect(
            attrs={"class": "form-radio text-naia-green"}
        ),
    )

    origin = forms.CharField(
        max_length=3,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green appearance-none bg-white",
            }
        ),
    )

    destination = forms.CharField(
        max_length=3,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green appearance-none bg-white",
            }
        ),
    )

    departure_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green departure-date",
            }
        ),
    )

    return_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green return-date",
            }
        ),
    )

    passengers = forms.TypedChoiceField(
        choices=PASSENGER_CHOICES,
        coerce=int,
        initial=1,
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green appearance-none bg-white",
            }
        ),
    )

    seat_class = forms.ChoiceField(
        choices=SEAT_CLASS_CHOICES,
        initial="ECONOMY",
        required=False,
        widget=forms.Select(
            attrs={
                "class": "w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green appearance-none bg-white",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        origin = cleaned_data.get("origin")
        destination = cleaned_data.get("destination")
        departure_date = cleaned_data.get("departure_date")
        return_date = cleaned_data.get("return_date")
        trip_type = cleaned_data.get("trip_type")

        # Check origin and destination are different
        if origin and destination and origin == destination:
            raise forms.ValidationError(
                "Origin and destination cannot be the same airport."
            )

        # Check departure date is not in the past
        if departure_date and departure_date < timezone.now().date():
            raise forms.ValidationError(
                "Departure date cannot be in the past."
            )

        # Check return date is after departure date for round trips
        if trip_type == "round_trip":
            if not return_date:
                raise forms.ValidationError(
                    "Return date is required for round trip flights."
                )
            if return_date and departure_date and return_date < departure_date:
                raise forms.ValidationError(
                    "Return date must be after departure date."
                )

        return cleaned_data
