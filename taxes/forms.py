from django import forms

from .models import TaxInvoice


class TaxLookupForm(forms.Form):
    """Look up the tax invoice for any booking by reference."""
    booking_reference = forms.CharField(
        max_length=20,
        label="Booking Reference",
        widget=forms.TextInput(attrs={
            "placeholder": "e.g. R6Y6BU or HTL-123456",
            "class": "w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-naia-green focus:border-transparent",
        }),
    )


class PayTaxInvoiceForm(forms.ModelForm):
    """Mark a tax invoice as paid (admin/staff use)."""

    class Meta:
        model = TaxInvoice
        fields = ["payment_reference", "notes"]
        widgets = {
            "payment_reference": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-4 py-2 text-sm",
                "placeholder": "Paystack/bank reference",
            }),
            "notes": forms.Textarea(attrs={
                "class": "w-full border border-gray-300 rounded-lg px-4 py-2 text-sm",
                "rows": 2,
            }),
        }
