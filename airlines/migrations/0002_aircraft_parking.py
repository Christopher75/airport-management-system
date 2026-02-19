# Generated migration for Aircraft Parking Management models

import decimal
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airlines", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AircraftStand",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("stand_number", models.CharField(max_length=10, unique=True, verbose_name="stand number")),
                ("terminal", models.CharField(default="T1", max_length=5, verbose_name="terminal")),
                ("stand_type", models.CharField(
                    choices=[("CONTACT", "Contact Stand (Jetway)"), ("REMOTE", "Remote Stand (Bus Transfer)"), ("CARGO", "Cargo Stand"), ("MAINT", "Maintenance Bay")],
                    default="CONTACT", max_length=10, verbose_name="stand type",
                )),
                ("max_aircraft_size", models.CharField(
                    choices=[("LIGHT", "Light (< 7,000 kg MTOW)"), ("SMALL", "Small (7,000–27,000 kg MTOW)"), ("MEDIUM", "Medium (27,000–136,000 kg MTOW)"), ("LARGE", "Large (136,000–300,000 kg MTOW)"), ("HEAVY", "Heavy (> 300,000 kg MTOW)")],
                    default="MEDIUM", help_text="Maximum aircraft size this stand can accommodate", max_length=10, verbose_name="max aircraft size",
                )),
                ("has_jetway", models.BooleanField(default=False, verbose_name="has jetway")),
                ("has_gpu", models.BooleanField(default=False, help_text="Provides ground electrical power to parked aircraft", verbose_name="Ground Power Unit (GPU)")),
                ("has_pca", models.BooleanField(default=False, help_text="Provides climate-controlled air to parked aircraft", verbose_name="Pre-Conditioned Air (PCA)")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                ("notes", models.TextField(blank=True, verbose_name="notes")),
            ],
            options={"verbose_name": "aircraft stand", "verbose_name_plural": "aircraft stands", "ordering": ["terminal", "stand_number"]},
        ),
        migrations.AddIndex(
            model_name="aircraftstand",
            index=models.Index(fields=["terminal", "is_active"], name="airlines_ai_termina_idx"),
        ),
        migrations.CreateModel(
            name="AircraftParkingRate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("aircraft_size", models.CharField(
                    choices=[("LIGHT", "Light (< 7,000 kg MTOW)"), ("SMALL", "Small (7,000–27,000 kg MTOW)"), ("MEDIUM", "Medium (27,000–136,000 kg MTOW)"), ("LARGE", "Large (136,000–300,000 kg MTOW)"), ("HEAVY", "Heavy (> 300,000 kg MTOW)")],
                    max_length=10, unique=True, verbose_name="aircraft size category",
                )),
                ("landing_fee", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), help_text="One-time fee charged when aircraft lands", max_digits=12, verbose_name="landing fee (₦)")),
                ("hourly_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="hourly parking rate (₦)")),
                ("daily_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), help_text="Applied for stays exceeding 24 hours", max_digits=12, verbose_name="daily parking rate (₦)")),
                ("weekly_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), help_text="Applied for stays exceeding 7 days", max_digits=12, verbose_name="weekly parking rate (₦)")),
                ("gpu_hourly_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="GPU hourly rate (₦)")),
                ("pca_hourly_rate", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="PCA hourly rate (₦)")),
                ("effective_from", models.DateField(default=django.utils.timezone.now, verbose_name="effective from")),
                ("effective_until", models.DateField(blank=True, null=True, verbose_name="effective until")),
            ],
            options={"verbose_name": "aircraft parking rate", "verbose_name_plural": "aircraft parking rates"},
        ),
        migrations.CreateModel(
            name="AircraftParkingRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("record_number", models.CharField(editable=False, max_length=20, unique=True, verbose_name="record number")),
                ("aircraft_size", models.CharField(
                    choices=[("LIGHT", "Light (< 7,000 kg MTOW)"), ("SMALL", "Small (7,000–27,000 kg MTOW)"), ("MEDIUM", "Medium (27,000–136,000 kg MTOW)"), ("LARGE", "Large (136,000–300,000 kg MTOW)"), ("HEAVY", "Heavy (> 300,000 kg MTOW)")],
                    max_length=10, verbose_name="aircraft size",
                )),
                ("scheduled_arrival", models.DateTimeField(verbose_name="scheduled arrival")),
                ("scheduled_departure", models.DateTimeField(verbose_name="scheduled departure")),
                ("actual_arrival_time", models.DateTimeField(blank=True, null=True, verbose_name="actual arrival")),
                ("actual_departure_time", models.DateTimeField(blank=True, null=True, verbose_name="actual departure")),
                ("gpu_requested", models.BooleanField(default=False, verbose_name="GPU requested")),
                ("pca_requested", models.BooleanField(default=False, verbose_name="PCA requested")),
                ("landing_fee", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="landing fee (₦)")),
                ("parking_fee", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="parking fee (₦)")),
                ("service_fee", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="ground services fee (₦)")),
                ("total_due", models.DecimalField(decimal_places=2, default=decimal.Decimal("0"), max_digits=12, verbose_name="total due (₦)")),
                ("is_paid", models.BooleanField(default=False, verbose_name="paid")),
                ("payment_date", models.DateTimeField(blank=True, null=True, verbose_name="payment date")),
                ("payment_reference", models.CharField(blank=True, max_length=100, verbose_name="payment reference")),
                ("invoice_number", models.CharField(blank=True, max_length=30, verbose_name="invoice number")),
                ("status", models.CharField(
                    choices=[("SCHEDULED", "Scheduled"), ("ACTIVE", "Active (On Stand)"), ("COMPLETED", "Completed"), ("OVERDUE", "Overdue – Unpaid"), ("CANCELLED", "Cancelled")],
                    default="SCHEDULED", max_length=15, verbose_name="status",
                )),
                ("notes", models.TextField(blank=True, verbose_name="notes")),
                ("aircraft", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="parking_records", to="airlines.aircraft")),
                ("airline", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="parking_records", to="airlines.airline")),
                ("stand", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="parking_records", to="airlines.aircraftstand")),
            ],
            options={"verbose_name": "aircraft parking record", "verbose_name_plural": "aircraft parking records", "ordering": ["-scheduled_arrival"]},
        ),
        migrations.AddIndex(
            model_name="aircraftparkingrecord",
            index=models.Index(fields=["airline", "status"], name="airlines_ap_airline_idx"),
        ),
        migrations.AddIndex(
            model_name="aircraftparkingrecord",
            index=models.Index(fields=["stand", "status"], name="airlines_ap_stand_idx"),
        ),
        migrations.AddIndex(
            model_name="aircraftparkingrecord",
            index=models.Index(fields=["is_paid"], name="airlines_ap_is_paid_idx"),
        ),
    ]
