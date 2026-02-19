# Generated migration for Hotel Booking app

import decimal
import random
import uuid
import django.core.validators
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
            name="Hotel",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200, verbose_name="hotel name")),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField(verbose_name="description")),
                ("star_rating", models.PositiveSmallIntegerField(
                    default=3,
                    validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)],
                    verbose_name="star rating",
                )),
                ("address", models.TextField(verbose_name="address")),
                ("distance_from_airport", models.DecimalField(
                    decimal_places=1, max_digits=5,
                    help_text="Walking/driving distance from the airport terminal",
                    verbose_name="distance from airport (km)",
                )),
                ("phone", models.CharField(max_length=25, verbose_name="phone")),
                ("email", models.EmailField(blank=True, verbose_name="email")),
                ("website", models.URLField(blank=True, verbose_name="website")),
                ("amenities", models.JSONField(blank=True, default=list, verbose_name="amenities")),
                ("has_airport_shuttle", models.BooleanField(
                    default=False,
                    help_text="Free shuttle service between hotel and airport",
                    verbose_name="airport shuttle",
                )),
                ("check_in_time", models.TimeField(default="14:00", verbose_name="check-in time")),
                ("check_out_time", models.TimeField(default="12:00", verbose_name="check-out time")),
                ("image", models.ImageField(blank=True, null=True, upload_to="hotels/", verbose_name="main image")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
            ],
            options={"verbose_name": "hotel", "verbose_name_plural": "hotels", "ordering": ["-star_rating", "name"]},
        ),
        migrations.AddIndex(
            model_name="hotel",
            index=models.Index(fields=["is_active", "star_rating"], name="hotels_hote_is_acti_idx"),
        ),
        migrations.CreateModel(
            name="RoomType",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, verbose_name="room name")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                ("bed_type", models.CharField(
                    choices=[("Single", "Single Bed"), ("Double", "Double Bed"), ("Twin", "Twin Beds"), ("King", "King Size"), ("Queen", "Queen Size")],
                    default="Double", max_length=50, verbose_name="bed type",
                )),
                ("max_occupancy", models.PositiveSmallIntegerField(default=2, verbose_name="max occupancy")),
                ("base_price_per_night", models.DecimalField(
                    decimal_places=2,
                    help_text="Price before taxes and fees",
                    max_digits=10,
                    verbose_name="base price per night (₦)",
                )),
                ("total_rooms", models.PositiveSmallIntegerField(default=10, verbose_name="total rooms")),
                ("amenities", models.JSONField(blank=True, default=list, verbose_name="room amenities")),
                ("image", models.ImageField(blank=True, null=True, upload_to="hotels/rooms/", verbose_name="room image")),
                ("is_active", models.BooleanField(default=True, verbose_name="available")),
                ("hotel", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="room_types",
                    to="hotels.hotel",
                )),
            ],
            options={"verbose_name": "room type", "verbose_name_plural": "room types", "ordering": ["hotel", "base_price_per_night"]},
        ),
        migrations.CreateModel(
            name="HotelBooking",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reference", models.CharField(editable=False, max_length=10, unique=True, verbose_name="booking reference")),
                ("check_in_date", models.DateField(verbose_name="check-in date")),
                ("check_out_date", models.DateField(verbose_name="check-out date")),
                ("num_rooms", models.PositiveSmallIntegerField(default=1, verbose_name="number of rooms")),
                ("num_adults", models.PositiveSmallIntegerField(default=1, verbose_name="adults")),
                ("num_children", models.PositiveSmallIntegerField(default=0, verbose_name="children")),
                ("guest_first_name", models.CharField(max_length=100, verbose_name="first name")),
                ("guest_last_name", models.CharField(max_length=100, verbose_name="last name")),
                ("guest_email", models.EmailField(verbose_name="email")),
                ("guest_phone", models.CharField(max_length=25, verbose_name="phone")),
                ("special_requests", models.TextField(blank=True, verbose_name="special requests")),
                ("room_rate", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="room rate per night (₦)")),
                ("num_nights", models.PositiveSmallIntegerField(default=1, verbose_name="number of nights")),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="subtotal (₦)")),
                ("vat_amount", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="VAT 7.5% (₦)")),
                ("service_fee", models.DecimalField(decimal_places=2, max_digits=10, verbose_name="service fee 5% (₦)")),
                ("total_price", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="total price (₦)")),
                ("is_paid", models.BooleanField(default=False, verbose_name="paid")),
                ("payment_reference", models.CharField(blank=True, max_length=100, verbose_name="payment reference")),
                ("paid_at", models.DateTimeField(blank=True, null=True, verbose_name="paid at")),
                ("status", models.CharField(
                    choices=[("PENDING", "Pending Payment"), ("CONFIRMED", "Confirmed"), ("CHECKED_IN", "Checked In"), ("COMPLETED", "Completed"), ("CANCELLED", "Cancelled"), ("NO_SHOW", "No Show")],
                    default="PENDING", max_length=15, verbose_name="status",
                )),
                ("related_flight_ref", models.CharField(
                    blank=True, max_length=10,
                    help_text="Optional: link to a flight booking (for transit guests)",
                    verbose_name="related flight booking ref",
                )),
                ("hotel", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="hotels.hotel")),
                ("room_type", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="hotels.roomtype")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="hotel_bookings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "hotel booking", "verbose_name_plural": "hotel bookings", "ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="hotelbooking",
            index=models.Index(fields=["reference"], name="hotels_hote_referen_idx"),
        ),
        migrations.AddIndex(
            model_name="hotelbooking",
            index=models.Index(fields=["user", "status"], name="hotels_hote_user_id_idx"),
        ),
    ]
