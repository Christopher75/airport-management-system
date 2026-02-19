"""
Airport Taxes Views.

Provides a public tax lookup, invoice detail, and staff management views.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import PayTaxInvoiceForm, TaxLookupForm
from .models import TaxInvoice, TaxType


def tax_home(request):
    """
    Public landing page for the Airport Taxes module.
    Shows active tax rates and a lookup form.
    """
    active_taxes = TaxType.objects.filter(is_active=True).order_by("category", "name")
    form = TaxLookupForm(request.GET or None)
    invoices = None

    if form.is_valid():
        ref = form.cleaned_data["booking_reference"].strip().upper()
        invoices = TaxInvoice.objects.filter(booking_reference__iexact=ref).prefetch_related("items__tax_type")
        if not invoices.exists():
            messages.info(request, f"No tax invoice found for reference '{ref}'.")

    return render(request, "taxes/tax_home.html", {
        "active_taxes": active_taxes,
        "form": form,
        "invoices": invoices,
    })


def tax_invoice_detail(request, invoice_number):
    """
    Detailed view of a single tax invoice with all line items.
    Accessible publicly via direct URL (invoice number acts as a token).
    """
    invoice = get_object_or_404(
        TaxInvoice.objects.prefetch_related("items__tax_type"),
        invoice_number=invoice_number,
    )
    return render(request, "taxes/invoice_detail.html", {"invoice": invoice})


@login_required
def my_tax_invoices(request):
    """
    Show all tax invoices linked to the current user's bookings.
    Matches by email address stored in passenger_email.
    """
    invoices = TaxInvoice.objects.filter(
        passenger_email__iexact=request.user.email
    ).prefetch_related("items__tax_type").order_by("-created_at")

    return render(request, "taxes/my_invoices.html", {"invoices": invoices})


@login_required
def mark_invoice_paid(request, invoice_number):
    """
    Staff-only: mark a tax invoice as paid.
    """
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to perform this action.")
        return redirect("taxes:home")

    invoice = get_object_or_404(TaxInvoice, invoice_number=invoice_number)

    if request.method == "POST":
        form = PayTaxInvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.is_paid = True
            inv.status = TaxInvoice.InvoiceStatus.PAID
            inv.paid_at = timezone.now()
            inv.save()
            messages.success(request, f"Invoice {invoice_number} marked as paid.")
            return redirect("taxes:invoice_detail", invoice_number=invoice_number)
    else:
        form = PayTaxInvoiceForm(instance=invoice)

    return render(request, "taxes/mark_paid.html", {"invoice": invoice, "form": form})


def tax_rates_public(request):
    """
    Public page showing all current airport tax rates — for transparency.
    """
    taxes = TaxType.objects.filter(is_active=True).order_by("category", "name")
    return render(request, "taxes/rates.html", {"taxes": taxes})
