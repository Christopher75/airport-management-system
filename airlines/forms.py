"""
Forms for the Aircraft Parking Management module.
"""

from django import forms
from django.utils import timezone

from .models import Aircraft, AircraftParkingRecord, AircraftStand


class AircraftParkingRecordForm(forms.ModelForm):
    """Form for airline staff to register an aircraft for stand parking."""

    class Meta:
        model = AircraftParkingRecord
        fields = [
            "aircraft",
            "stand",
            "aircraft_size",
            "scheduled_arrival",
            "scheduled_departure",
            "gpu_requested",
            "pca_requested",
            "notes",
        ]
        widgets = {
            "scheduled_arrival": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "scheduled_departure": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "aircraft": forms.Select(attrs={"class": "form-select"}),
            "stand": forms.Select(attrs={"class": "form-select"}),
            "aircraft_size": forms.Select(attrs={"class": "form-select"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, airline=None, **kwargs):
        super().__init__(*args, **kwargs)
        if airline:
            self.fields["aircraft"].queryset = Aircraft.objects.filter(
                airline=airline, is_active=True
            )
        self.fields["stand"].queryset = AircraftStand.objects.filter(is_active=True)
        # Make datetime-local work with Django
        for fname in ["scheduled_arrival", "scheduled_departure"]:
            self.fields[fname].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned = super().clean()
        arrival = cleaned.get("scheduled_arrival")
        departure = cleaned.get("scheduled_departure")
        if arrival and departure:
            if departure <= arrival:
                raise forms.ValidationError(
                    "Scheduled departure must be after scheduled arrival."
                )
        return cleaned


class MarkPaidForm(forms.Form):
    """Simple form for marking a parking record as paid."""

    payment_reference = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Transaction reference"}),
        label="Payment / Transaction Reference",
    )
