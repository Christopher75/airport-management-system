# Generated migration for Airport Taxis & Transfers app

import uuid
import decimal
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
            name="VehicleCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="vehicle name")),
                ("slug", models.SlugField(unique=True)),
                ("vehicle_type", models.CharField(
                    choices=[
                        ("SEDAN", "Economy Sedan"),
                        ("SUV", "Standard SUV"),
                        ("LUXURY", "Luxury / Executive"),
                        ("MINIVAN", "Minivan"),
                        ("BUS", "Shuttle / Minibus"),
                    ],
                    default="SEDAN", max_length=10, verbose_name="vehicle type",
                )),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("max_passengers", models.PositiveSmallIntegerField(default=4, verbose_name="max passengers")),
                ("max_luggage", models.PositiveSmallIntegerField(
                    default=3,
                    help_text="Maximum number of standard-sized bags",
                    verbose_name="max luggage bags",
                )),
                ("price_per_km", models.DecimalField(
                    decimal_places=2, max_digits=8,
                    help_text="Rate charged per kilometre of the journey",
                    verbose_name="price per km (₦)",
                )),
                ("minimum_fare", models.DecimalField(
                    decimal_places=2, max_digits=10,
                    help_text="Minimum charge regardless of distance",
                    verbose_name="minimum fare (₦)",
                )),
                ("waiting_charge_per_hour", models.DecimalField(
                    decimal_places=2, default=decimal.Decimal("2000.00"),
                    max_digits=8, verbose_name="waiting charge per hour (₦)",
                )),
                ("features", models.JSONField(
                    blank=True, default=list,
                    help_text="List of features, e.g. ['AC', 'WiFi', 'Meet & Greet']",
                    verbose_name="features",
                )),
                ("image", models.ImageField(blank=True, null=True, upload_to="taxis/vehicles/", verbose_name="vehicle image")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
            ],
            options={"verbose_name": "vehicle category", "verbose_name_plural": "vehicle categories", "ordering": ["price_per_km"]},
        ),
        migrations.CreateModel(
            name="TaxiBooking",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("reference", models.CharField(editable=False, max_length=12, unique=True, verbose_name="booking reference")),
                ("trip_type", models.CharField(
                    choices=[
                        ("ARRIVAL", "Airport Arrival (Airport → Destination)"),
                        ("DEPARTURE", "Airport Departure (Origin → Airport)"),
                        ("TRANSFER", "Point-to-Point Transfer"),
                    ],
                    default="ARRIVAL", max_length=10, verbose_name="trip type",
                )),
                ("pickup_location", models.CharField(max_length=255, verbose_name="pickup location")),
                ("dropoff_location", models.CharField(max_length=255, verbose_name="drop-off location")),
                ("pickup_datetime", models.DateTimeField(verbose_name="pickup date & time")),
                ("flight_number", models.CharField(
                    blank=True, max_length=10,
                    help_text="Optional: helps driver monitor your flight for delays",
                    verbose_name="flight number",
                )),
                ("num_passengers", models.PositiveSmallIntegerField(default=1, verbose_name="number of passengers")),
                ("num_luggage", models.PositiveSmallIntegerField(default=1, verbose_name="number of bags")),
                ("special_requests", models.TextField(blank=True, verbose_name="special requests")),
                ("estimated_distance_km", models.DecimalField(
                    decimal_places=1, default=decimal.Decimal("10.0"),
                    max_digits=6, verbose_name="estimated distance (km)",
                )),
                ("base_fare", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="base fare (₦)")),
                ("vat_amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="VAT 7.5% (₦)")),
                ("total_fare", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="total fare (₦)")),
                ("passenger_name", models.CharField(max_length=200, verbose_name="passenger name")),
                ("passenger_email", models.EmailField(verbose_name="email")),
                ("passenger_phone", models.CharField(max_length=25, verbose_name="phone")),
                ("is_paid", models.BooleanField(default=False, verbose_name="paid")),
                ("payment_reference", models.CharField(blank=True, max_length=100, verbose_name="payment reference")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="paid at")),
                ("driver_name", models.CharField(blank=True, max_length=100, verbose_name="driver name")),
                ("driver_phone", models.CharField(blank=True, max_length=25, verbose_name="driver phone")),
                ("vehicle_plate", models.CharField(blank=True, max_length=20, verbose_name="vehicle plate")),
                ("vehicle_colour", models.CharField(blank=True, max_length=30, verbose_name="vehicle colour")),
                ("status", models.CharField(
                    choices=[
                        ("PENDING", "Pending Payment"),
                        ("CONFIRMED", "Confirmed"),
                        ("ASSIGNED", "Driver Assigned"),
                        ("EN_ROUTE", "Driver En Route"),
                        ("COMPLETED", "Completed"),
                        ("CANCELLED", "Cancelled"),
                    ],
                    default="PENDING", max_length=12, verbose_name="status",
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="taxi_bookings",
                    to=settings.AUTH_USER_MODEL,
                    verbose_name="user",
                )),
                ("vehicle_category", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="bookings",
                    to="taxis.vehiclecategory",
                    verbose_name="vehicle category",
                )),
            ],
            options={"verbose_name": "taxi booking", "verbose_name_plural": "taxi bookings", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="taxibooking",
            index=models.Index(fields=["reference"], name="taxis_taxibooking_ref_idx"),
        ),
        migrations.AddIndex(
            model_name="taxibooking",
            index=models.Index(fields=["user", "status"], name="taxis_taxibooking_usr_idx"),
        ),
        migrations.AddIndex(
            model_name="taxibooking",
            index=models.Index(fields=["pickup_datetime"], name="taxis_taxibooking_dt_idx"),
        ),
    ]
