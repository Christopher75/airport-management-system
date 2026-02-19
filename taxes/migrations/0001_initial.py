# Generated migration for Airport Taxes app

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TaxType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150, verbose_name="tax name")),
                ("code", models.CharField(help_text="Short identifier, e.g. ADL, PSC, VAT", max_length=10, unique=True, verbose_name="code")),
                ("category", models.CharField(
                    choices=[
                        ("PSC", "Passenger Service Charge (PSC)"),
                        ("ADL", "Airport Development Levy (ADL)"),
                        ("SEC", "Security & Safety Fee"),
                        ("DEP", "Departure Tax"),
                        ("VAT", "Value Added Tax (VAT 7.5%)"),
                        ("FUEL", "Fuel Surcharge"),
                        ("TRANSIT", "Transit Passenger Tax"),
                        ("INTL", "International Route Surcharge"),
                        ("CSD", "Customs & Stamp Duty"),
                    ],
                    default="PSC", max_length=10, verbose_name="category",
                )),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("rate_type", models.CharField(
                    choices=[("FIXED", "Fixed Amount (₦ per passenger)"), ("PERCENT", "Percentage of base fare (%)")],
                    default="FIXED", max_length=10, verbose_name="rate type",
                )),
                ("rate", models.DecimalField(
                    decimal_places=2, max_digits=10,
                    help_text="Enter a ₦ amount for FIXED, or percentage (e.g. 7.5) for PERCENTAGE",
                    verbose_name="rate / amount",
                )),
                ("applicability", models.CharField(
                    choices=[("DOMESTIC", "Domestic Flights Only"), ("INTERNATIONAL", "International Flights Only"), ("ALL", "All Flights")],
                    default="ALL", max_length=15, verbose_name="applicability",
                )),
                ("is_mandatory", models.BooleanField(
                    default=True,
                    help_text="Mandatory taxes are automatically added to all applicable bookings",
                    verbose_name="mandatory",
                )),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                ("effective_from", models.DateField(verbose_name="effective from")),
                ("effective_until", models.DateField(blank=True, null=True, verbose_name="effective until")),
            ],
            options={"verbose_name": "tax type", "verbose_name_plural": "tax types", "ordering": ["category", "name"]},
        ),
        migrations.CreateModel(
            name="TaxInvoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_number", models.CharField(editable=False, max_length=20, unique=True, verbose_name="invoice number")),
                ("service_type", models.CharField(
                    choices=[
                        ("FLIGHT", "Flight Booking"),
                        ("HOTEL", "Hotel Booking"),
                        ("LOUNGE", "Lounge Access"),
                        ("PARKING", "Vehicle Parking"),
                        ("AIRCRAFT", "Aircraft Parking"),
                    ],
                    default="FLIGHT", max_length=15, verbose_name="service type",
                )),
                ("booking_reference", models.CharField(
                    help_text="Reference number from the related booking (flight, hotel, etc.)",
                    max_length=20, verbose_name="booking reference",
                )),
                ("passenger_name", models.CharField(max_length=200, verbose_name="passenger / guest name")),
                ("passenger_email", models.EmailField(verbose_name="email")),
                ("flight_route", models.CharField(
                    blank=True, max_length=100,
                    help_text="e.g. ABV → LOS or Hotel: Sheraton Abuja",
                    verbose_name="route / service description",
                )),
                ("base_amount", models.DecimalField(
                    decimal_places=2, max_digits=12,
                    help_text="The base fare/price before taxes",
                    verbose_name="base amount (₦)",
                )),
                ("total_tax_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="total tax (₦)")),
                ("is_paid", models.BooleanField(default=False, verbose_name="paid")),
                ("payment_reference", models.CharField(blank=True, max_length=100, verbose_name="payment reference")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="paid at")),
                ("status", models.CharField(
                    choices=[
                        ("DRAFT", "Draft"),
                        ("ISSUED", "Issued"),
                        ("PAID", "Paid"),
                        ("OVERDUE", "Overdue"),
                        ("CANCELLED", "Cancelled"),
                    ],
                    default="ISSUED", max_length=12, verbose_name="status",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("notes", models.TextField(blank=True, verbose_name="notes")),
                ("created_by", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="tax_invoices_created",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="created by",
                )),
            ],
            options={"verbose_name": "tax invoice", "verbose_name_plural": "tax invoices", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="taxinvoice",
            index=models.Index(fields=["booking_reference"], name="taxes_taxinvoice_ref_idx"),
        ),
        migrations.AddIndex(
            model_name="taxinvoice",
            index=models.Index(fields=["status"], name="taxes_taxinvoice_status_idx"),
        ),
        migrations.AddIndex(
            model_name="taxinvoice",
            index=models.Index(fields=["service_type", "is_paid"], name="taxes_taxinvoice_svc_paid_idx"),
        ),
        migrations.CreateModel(
            name="TaxInvoiceItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(max_length=200, verbose_name="description")),
                ("quantity", models.PositiveSmallIntegerField(default=1, verbose_name="quantity / passengers")),
                ("unit_amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="unit amount (₦)")),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="total (₦)")),
                ("invoice", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="items",
                    to="taxes.taxinvoice",
                    verbose_name="invoice",
                )),
                ("tax_type", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="invoice_items",
                    to="taxes.taxtype",
                    verbose_name="tax type",
                )),
            ],
            options={"verbose_name": "tax invoice item", "verbose_name_plural": "tax invoice items"},
        ),
    ]
