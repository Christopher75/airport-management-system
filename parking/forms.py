"""
Forms for the Parking app.
"""

from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import (
    ParkingZone, ParkingReservation, ParkingService,
    VehicleType, ParkingZoneType
)


class ParkingSearchForm(forms.Form):
    """Form for searching available parking."""
    check_in_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }
        ),
        label='Check-in Date & Time'
    )
    check_out_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }
        ),
        label='Check-out Date & Time'
    )
    vehicle_type = forms.ChoiceField(
        choices=[('', 'All Vehicle Types')] + list(VehicleType.choices),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }
        ),
        label='Vehicle Type'
    )
    zone_type = forms.ChoiceField(
        choices=[('', 'All Parking Types')] + list(ParkingZoneType.choices),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }
        ),
        label='Parking Type'
    )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')

        if check_in and check_out:
            # Check-in must be in the future
            if check_in < timezone.now():
                raise forms.ValidationError('Check-in date must be in the future.')

            # Check-out must be after check-in
            if check_out <= check_in:
                raise forms.ValidationError('Check-out date must be after check-in date.')

            # Maximum parking duration is 30 days
            if (check_out - check_in) > timedelta(days=30):
                raise forms.ValidationError('Maximum parking duration is 30 days.')

        return cleaned_data


class ParkingReservationForm(forms.ModelForm):
    """Form for creating a parking reservation."""

    services = forms.ModelMultipleChoiceField(
        queryset=ParkingService.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'}
        ),
        label='Additional Services'
    )

    class Meta:
        model = ParkingReservation
        fields = [
            'zone', 'vehicle_type', 'vehicle_registration',
            'vehicle_make', 'vehicle_model', 'vehicle_color',
            'check_in_date', 'check_out_date', 'flight_number',
            'contact_phone', 'contact_email', 'special_requests'
        ]
        widgets = {
            'zone': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
                }
            ),
            'vehicle_type': forms.Select(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
                }
            ),
            'vehicle_registration': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': 'e.g., ABC-123-XY'
                }
            ),
            'vehicle_make': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': 'e.g., Toyota'
                }
            ),
            'vehicle_model': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': 'e.g., Camry'
                }
            ),
            'vehicle_color': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': 'e.g., Silver'
                }
            ),
            'check_in_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
                }
            ),
            'check_out_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
                }
            ),
            'flight_number': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': 'e.g., P4101 (optional)'
                }
            ),
            'contact_phone': forms.TextInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': '+234...'
                }
            ),
            'contact_email': forms.EmailInput(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'placeholder': 'email@example.com'
                }
            ),
            'special_requests': forms.Textarea(
                attrs={
                    'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                    'rows': 3,
                    'placeholder': 'Any special requests or notes...'
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active zones with available spots
        self.fields['zone'].queryset = ParkingZone.objects.filter(
            is_active=True,
            available_spots__gt=0
        )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        zone = cleaned_data.get('zone')

        if check_in and check_out:
            if check_in < timezone.now():
                raise forms.ValidationError('Check-in date must be in the future.')

            if check_out <= check_in:
                raise forms.ValidationError('Check-out date must be after check-in date.')

            if (check_out - check_in) > timedelta(days=30):
                raise forms.ValidationError('Maximum parking duration is 30 days.')

        if zone and zone.available_spots <= 0:
            raise forms.ValidationError('Selected parking zone is full.')

        return cleaned_data


class QuickParkingForm(forms.Form):
    """Quick booking form for home page."""
    check_in_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }
        ),
        label='Check-in'
    )
    check_out_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }
        ),
        label='Check-out'
    )


class CancelReservationForm(forms.Form):
    """Form for cancelling a reservation."""
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'rows': 3,
                'placeholder': 'Reason for cancellation (optional)'
            }
        ),
        label='Cancellation Reason'
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'}
        ),
        label='I confirm I want to cancel this reservation'
    )
