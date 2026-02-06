"""
Core forms for the Airport Management System.

Contains forms for public-facing features like contact page.
"""

from django import forms


class ContactForm(forms.Form):
    """
    Contact form for customer inquiries.
    """

    SUBJECT_CHOICES = [
        ("", "Select a subject"),
        ("general", "General Inquiry"),
        ("booking", "Booking Assistance"),
        ("lost_found", "Lost & Found"),
        ("feedback", "Feedback & Suggestions"),
        ("complaint", "Complaint"),
        ("partnership", "Business Partnership"),
        ("other", "Other"),
    ]

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "Your full name",
            }
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "your.email@example.com",
            }
        ),
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "+234 XXX XXX XXXX",
            }
        ),
    )

    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
            }
        ),
    )

    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-naia-green focus:border-naia-green",
                "placeholder": "How can we help you?",
                "rows": 5,
            }
        ),
    )

    def clean_message(self):
        message = self.cleaned_data.get("message", "")
        if len(message) < 10:
            raise forms.ValidationError("Please provide more details in your message.")
        return message
