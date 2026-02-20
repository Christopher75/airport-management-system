from decimal import Decimal

from django import forms
from django.utils import timezone

from .models import TaxiBooking, VehicleCategory


class TaxiSearchForm(forms.Form):
    trip_type = forms.ChoiceField(
        choices=TaxiBooking.TripType.choices,
        initial=TaxiBooking.TripType.ARRIVAL,
        widget=forms.Select(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green"}),
    )
    num_passengers = forms.IntegerField(
        min_value=1, max_value=14, initial=1,
        widget=forms.NumberInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green"}),
    )


class TaxiBookingForm(forms.ModelForm):
    class Meta:
        model = TaxiBooking
        fields = [
            "trip_type", "pickup_location", "dropoff_location",
            "pickup_datetime", "flight_number",
            "num_passengers", "num_luggage",
            "passenger_name", "passenger_email", "passenger_phone",
            "special_requests", "estimated_distance_km",
        ]
        widgets = {
            "trip_type": forms.Select(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green"}),
            "pickup_location": forms.TextInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "placeholder": "e.g. NAIA Terminal 1 Arrivals"}),
            "dropoff_location": forms.TextInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "placeholder": "e.g. Wuse Zone 5, Abuja"}),
            "pickup_datetime": forms.DateTimeInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "type": "datetime-local"}),
            "flight_number": forms.TextInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "placeholder": "e.g. P47123 (optional)"}),
            "num_passengers": forms.NumberInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "min": 1, "max": 14}),
            "num_luggage": forms.NumberInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "min": 0, "max": 20}),
            "passenger_name": forms.TextInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "placeholder": "Full name as on ID"}),
            "passenger_email": forms.EmailInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green"}),
            "passenger_phone": forms.TextInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "placeholder": "+234 800 000 0000"}),
            "special_requests": forms.Textarea(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "rows": 3, "placeholder": "e.g. child seat required, meet & greet service..."}),
            "estimated_distance_km": forms.NumberInput(attrs={"class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green", "step": "0.5", "min": "1"}),
        }

    def clean_pickup_datetime(self):
        dt = self.cleaned_data.get("pickup_datetime")
        if dt and dt < timezone.now():
            raise forms.ValidationError("Pickup time must be in the future.")
        return dt

    def clean_num_passengers(self):
        n = self.cleaned_data.get("num_passengers")
        vehicle = self.initial.get("vehicle_category")
        if vehicle and n and n > vehicle.max_passengers:
            raise forms.ValidationError(
                f"This vehicle fits a maximum of {vehicle.max_passengers} passengers."
            )
        return n
