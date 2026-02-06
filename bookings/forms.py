"""
Booking forms for the Airport Management System.

Contains forms for passenger details and seat selection.
"""

from django import forms
from django.forms import formset_factory

from .models import Passenger


class PassengerForm(forms.Form):
    """
    Form for collecting passenger information.
    """

    TITLE_CHOICES = [
        ("MR", "Mr."),
        ("MRS", "Mrs."),
        ("MS", "Ms."),
        ("DR", "Dr."),
        ("MSTR", "Master"),
        ("MISS", "Miss"),
    ]

    PASSENGER_TYPE_CHOICES = [
        ("ADULT", "Adult"),
        ("CHILD", "Child (2-11)"),
        ("INFANT", "Infant (0-2)"),
    ]

    title = forms.ChoiceField(
        choices=TITLE_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
            }
        ),
    )

    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "First name (as on travel document)",
            }
        ),
    )

    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "Last name (as on travel document)",
            }
        ),
    )

    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
            }
        ),
    )

    passenger_type = forms.ChoiceField(
        choices=PASSENGER_TYPE_CHOICES,
        initial="ADULT",
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
            }
        ),
    )

    # Travel Documents (required for international flights)
    passport_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "Passport number",
            }
        ),
    )

    passport_expiry = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
            }
        ),
    )

    passport_country = forms.CharField(
        max_length=100,
        required=False,
        initial="Nigeria",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "Passport issuing country",
            }
        ),
    )

    nationality = forms.CharField(
        max_length=100,
        required=False,
        initial="Nigerian",
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "Nationality",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        # Validate age based on passenger type
        date_of_birth = cleaned_data.get("date_of_birth")
        passenger_type = cleaned_data.get("passenger_type")

        if date_of_birth and passenger_type:
            from datetime import date
            today = date.today()
            age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )

            if passenger_type == "ADULT" and age < 12:
                raise forms.ValidationError(
                    "Adult passengers must be 12 years or older."
                )
            elif passenger_type == "CHILD" and (age < 2 or age > 11):
                raise forms.ValidationError(
                    "Child passengers must be between 2 and 11 years old."
                )
            elif passenger_type == "INFANT" and age >= 2:
                raise forms.ValidationError(
                    "Infant passengers must be under 2 years old."
                )

        return cleaned_data


# Create formset for multiple passengers
PassengerFormSet = formset_factory(
    PassengerForm,
    extra=9,  # Max passengers
    max_num=9,
)


class SeatSelectionForm(forms.Form):
    """
    Form for seat selection.
    """

    selected_seats = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    def __init__(self, *args, max_seats=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_seats = max_seats

    def clean_selected_seats(self):
        seats = self.cleaned_data.get("selected_seats", "")
        if seats:
            seat_list = [s.strip() for s in seats.split(",") if s.strip()]
            if len(seat_list) > self.max_seats:
                raise forms.ValidationError(
                    f"You can only select up to {self.max_seats} seats."
                )
            return seat_list
        return []
