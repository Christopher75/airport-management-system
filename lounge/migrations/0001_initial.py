# Generated migration for Airport Lounge Booking app

import decimal
import uuid
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AirportLounge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200, verbose_name="lounge name")),
                ("slug", models.SlugField(unique=True)),
                ("lounge_type", models.CharField(
                    choices=[("AIRLINE", "Airline Lounge"), ("INDEPENDENT", "Independent / Priority Pass"), ("VIP", "VIP / Government"), ("TRANSIT", "Transit Lounge")],
                    default="INDEPENDENT", max_length=15, verbose_name="lounge type",
                )),
                ("terminal", models.CharField(default="T1", max_length=5, verbose_name="terminal")),
                ("location_description", models.CharField(
                    help_text="e.g. Level 2, after Security Gate B",
                    max_length=200, verbose_name="location",
                )),
                ("description", models.TextField(verbose_name="description")),
                ("capacity", models.PositiveSmallIntegerField(default=50, verbose_name="capacity")),
                ("day_pass_price", models.DecimalField(
                    decimal_places=2, max_digits=10,
                    help_text="Price per adult for one visit (up to 3 hours)",
                    verbose_name="day pass price (₦)",
                )),
                ("child_price", models.DecimalField(
                    decimal_places=2, default=decimal.Decimal("0"), max_digits=10,
                    help_text="Price per child under 12. Set 0 for free.",
                    verbose_name="child price (₦)",
                )),
                ("has_wifi", models.BooleanField(default=True, verbose_name="WiFi")),
                ("has_food", models.BooleanField(default=True, verbose_name="Food & Drinks")),
                ("has_shower", models.BooleanField(default=False, verbose_name="Shower Facilities")),
                ("has_spa", models.BooleanField(default=False, verbose_name="Spa / Wellness")),
                ("has_prayer_room", models.BooleanField(default=False, verbose_name="Prayer Room")),
                ("has_business_centre", models.BooleanField(default=False, verbose_name="Business Centre")),
                ("opening_time", models.TimeField(default="05:00", verbose_name="opens")),
                ("closing_time", models.TimeField(default="23:00", verbose_name="closes")),
                ("image", models.ImageField(blank=True, null=True, upload_to="lounges/", verbose_name="image")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
            ],
            options={"verbose_name": "airport lounge", "verbose_name_plural": "airport lounges", "ordering": ["terminal", "name"]},
        ),
        migrations.CreateModel(
            name="LoungeBooking",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=10, unique=True, verbose_name="reference")),
                ("visit_date", models.DateField(verbose_name="visit date")),
                ("num_adults", models.PositiveSmallIntegerField(default=1, verbose_name="adults")),
                ("num_children", models.PositiveSmallIntegerField(default=0, verbose_name="children under 12")),
                ("guest_name", models.CharField(max_length=200, verbose_name="guest name")),
                ("guest_email", models.EmailField(verbose_name="email")),
                ("guest_phone", models.CharField(blank=True, max_length=25, verbose_name="phone")),
                ("flight_number", models.CharField(blank=True, help_text="Optional: for entry verification", max_length=10, verbose_name="flight number")),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="subtotal (₦)")),
                ("vat_amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="VAT (₦)")),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="total (₦)")),
                ("is_paid", models.BooleanField(default=False, verbose_name="paid")),
                ("payment_reference", models.CharField(blank=True, max_length=100, verbose_name="payment ref")),
                ("access_code", models.CharField(blank=True, editable=False, max_length=8, verbose_name="access code")),
                ("status", models.CharField(
                    choices=[("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("USED", "Used / Entry Granted"), ("EXPIRED", "Expired"), ("CANCELLED", "Cancelled")],
                    default="PENDING", max_length=12, verbose_name="status",
                )),
                ("lounge", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="lounge.airportlounge")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lounge_bookings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "lounge booking", "verbose_name_plural": "lounge bookings", "ordering": ["-created_at"]},
        ),
    ]
