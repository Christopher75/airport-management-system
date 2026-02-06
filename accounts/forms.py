"""
Account forms for the Airport Management System.

Profile and user update forms.
"""

from django import forms

from .models import CustomUser, Profile


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating basic user information.
    """

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
        }


class ProfileForm(forms.ModelForm):
    """
    Form for updating user profile details.
    """

    class Meta:
        model = Profile
        fields = [
            "title",
            "gender",
            "date_of_birth",
            "phone_number",
            "nationality",
            "passport_number",
            "passport_expiry",
            "passport_country",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "preferred_seat",
            "meal_preference",
            "special_assistance",
            "avatar",
        ]
        widgets = {
            "title": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "gender": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "+234 XXX XXX XXXX",
                }
            ),
            "nationality": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "passport_number": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "A12345678",
                }
            ),
            "passport_expiry": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "passport_country": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "address_line1": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "Street address",
                }
            ),
            "address_line2": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "Apartment, suite, etc. (optional)",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "emergency_contact_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "Full name",
                }
            ),
            "emergency_contact_phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "+234 XXX XXX XXXX",
                }
            ),
            "emergency_contact_relationship": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "placeholder": "e.g., Spouse, Parent, Sibling",
                }
            ),
            "preferred_seat": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "meal_preference": forms.Select(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
            "special_assistance": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                    "rows": 3,
                    "placeholder": "Please describe any special assistance requirements",
                }
            ),
            "avatar": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                }
            ),
        }
