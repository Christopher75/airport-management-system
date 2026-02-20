"""
Management command to assign real images to Hotels, Lounges, and Taxi vehicles.

Copies images from static/images/ into the correct media/ subdirectories
and updates each model instance's image field so they appear on the site.

Usage:
    python manage.py assign_images
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Assign real images from static/images/ to Hotels, Lounges, and Taxi vehicles"

    # ---------- mapping: model slug -> image filename in static/images/ ----------

    HOTEL_IMAGES = {
        "sheraton-abuja":              "SheratonAbujaHotel.jpg",
        "transcorp-hilton-abuja":      "TranscorpHiltonAbuja.jpg",
        "naia-airport-transit-hotel":  "AirportTransitHotel.jpg",
        "radisson-blu-anchorage-abuja":"RadissonBluAnchorageHotel.jpg",
    }

    LOUNGE_IMAGES = {
        "naia-executive-lounge":          "ExecutiveLounge.jpg",
        "air-peace-premier-lounge":       "AirPeacePremierLounge.jpg",
        "state-house-vip-lounge":         "StateHouseVIPLounge.jpg",
        "nnamdi-transit-hub-lounge":      "TransitHubLounge.jpg",
        "green-sapphire-business-lounge": "GreenSapphireBusinessLounge.jpg",
    }

    TAXI_IMAGES = {
        "economy-saloon":      "EconomySaloonTaxi.jpg",
        "standard-suv":        "StandardSUV.jpg",
        "luxury-executive":    "LuxuryExecutiveTaxi.jpg",
        "family-minivan":      "FamilyMinivan.jpg",
        "corporate-shuttle-bus": "CorporateShuttleBus.jpg",
    }

    def handle(self, *args, **options):
        # Root paths
        static_img = Path(settings.BASE_DIR) / "static" / "images"
        media_root = Path(settings.MEDIA_ROOT)

        self._assign_hotels(static_img, media_root)
        self._assign_lounges(static_img, media_root)
        self._assign_taxis(static_img, media_root)

        self.stdout.write(self.style.SUCCESS("All images assigned successfully!"))

    # ------------------------------------------------------------------
    def _copy(self, src_dir, dest_dir, filename):
        """Copy image file and return the relative media path, or None on error."""
        src = src_dir / filename
        if not src.exists():
            self.stdout.write(self.style.WARNING(f"  [SKIP] not found: {src}"))
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / filename
        shutil.copy2(src, dest)
        # Return the path relative to MEDIA_ROOT (what Django stores in ImageField)
        return str(dest.relative_to(Path(settings.MEDIA_ROOT)))

    # ------------------------------------------------------------------
    def _assign_hotels(self, static_img, media_root):
        from hotels.models import Hotel
        dest_dir = media_root / "hotels"
        count = 0
        for slug, filename in self.HOTEL_IMAGES.items():
            try:
                hotel = Hotel.objects.get(slug=slug)
            except Hotel.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  [SKIP] Hotel not found: {slug}"))
                continue
            rel_path = self._copy(static_img, dest_dir, filename)
            if rel_path:
                hotel.image = rel_path
                hotel.save(update_fields=["image"])
                self.stdout.write(f"  Hotel: {hotel.name}")
                count += 1
        self.stdout.write(self.style.SUCCESS(f"  OK: {count} hotel images assigned"))

    # ------------------------------------------------------------------
    def _assign_lounges(self, static_img, media_root):
        from lounge.models import AirportLounge
        dest_dir = media_root / "lounges"
        count = 0
        for slug, filename in self.LOUNGE_IMAGES.items():
            try:
                lounge = AirportLounge.objects.get(slug=slug)
            except AirportLounge.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  [SKIP] Lounge not found: {slug}"))
                continue
            rel_path = self._copy(static_img, dest_dir, filename)
            if rel_path:
                lounge.image = rel_path
                lounge.save(update_fields=["image"])
                self.stdout.write(f"  Lounge: {lounge.name}")
                count += 1
        self.stdout.write(self.style.SUCCESS(f"  OK: {count} lounge images assigned"))

    # ------------------------------------------------------------------
    def _assign_taxis(self, static_img, media_root):
        from taxis.models import VehicleCategory
        dest_dir = media_root / "taxis" / "vehicles"
        count = 0
        for slug, filename in self.TAXI_IMAGES.items():
            try:
                vehicle = VehicleCategory.objects.get(slug=slug)
            except VehicleCategory.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  [SKIP] Vehicle not found: {slug}"))
                continue
            rel_path = self._copy(static_img, dest_dir, filename)
            if rel_path:
                vehicle.image = rel_path
                vehicle.save(update_fields=["image"])
                self.stdout.write(f"  Taxi: {vehicle.name}")
                count += 1
        self.stdout.write(self.style.SUCCESS(f"  OK: {count} taxi vehicle images assigned"))
