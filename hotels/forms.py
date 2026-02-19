"""
Forms for Hotel Booking.
"""

from django import forms
from django.utils import timezone

from .models import HotelBooking, RoomType


class HotelSearchForm(forms.Form):
    """Search form on the hotel listing page."""

    check_in = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Check-in Date",
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Check-out Date",
    )
    num_rooms = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Rooms",
    )
    num_adults = forms.IntegerField(
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Adults",
    )

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        today = timezone.now().date()

        if check_in and check_in < today:
            raise forms.ValidationError("Check-in date cannot be in the past.")
        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out date must be after check-in date.")
        return cleaned


class HotelBookingForm(forms.ModelForm):
    """Main booking form — guest details & special requests."""

    class Meta:
        model = HotelBooking
        fields = [
            "guest_first_name",
            "guest_last_name",
            "guest_email",
            "guest_phone",
            "num_adults",
            "num_children",
            "special_requests",
            "related_flight_ref",
        ]
        widgets = {
            "guest_first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "guest_last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "guest_email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "guest_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+234…"}),
            "num_adults": forms.NumberInput(attrs={"class": "form-control", "min": 1, "max": 10}),
            "num_children": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 10}),
            "special_requests": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Any special requests (e.g. high floor, extra pillows, early check-in)"}
            ),
            "related_flight_ref": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "e.g. ABC123 (optional)"}
            ),
        }
