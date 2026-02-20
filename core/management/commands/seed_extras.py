"""
Management command to seed all extra feature data:
  - Hotels & Room Types
  - Airport Lounges
  - Aircraft Stands & Parking Rates
  - Airport Tax Types
  - Vehicle Categories (Taxis)

Usage:
    python manage.py seed_extras
    python manage.py seed_extras --clear
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Seed hotels, lounges, aircraft parking, tax types, and taxi vehicles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seeded data before re-seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        self._seed_hotels()
        self._seed_lounges()
        self._seed_aircraft_stands_and_rates()
        self._seed_tax_types()
        self._seed_taxi_vehicles()

        self.stdout.write(self.style.SUCCESS("\nAll extra seed data loaded successfully!\n"))

    # ------------------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------------------
    def _clear_data(self):
        from hotels.models import Hotel, RoomType, HotelBooking
        from lounge.models import AirportLounge
        from airlines.models import AircraftStand, AircraftParkingRate, AircraftParkingRecord
        from taxes.models import TaxType, TaxInvoice
        from taxis.models import VehicleCategory, TaxiBooking

        self.stdout.write("  Clearing extra data...")
        TaxiBooking.objects.all().delete()
        VehicleCategory.objects.all().delete()
        TaxInvoice.objects.all().delete()
        TaxType.objects.all().delete()
        AircraftParkingRecord.objects.all().delete()
        AircraftParkingRate.objects.all().delete()
        AircraftStand.objects.all().delete()
        HotelBooking.objects.all().delete()
        RoomType.objects.all().delete()
        Hotel.objects.all().delete()
        AirportLounge.objects.all().delete()
        self.stdout.write(self.style.WARNING("  Data cleared."))

    # ------------------------------------------------------------------
    # HOTELS
    # ------------------------------------------------------------------
    def _seed_hotels(self):
        from hotels.models import Hotel, RoomType

        hotels_data = [
            {
                "name": "Sheraton Abuja Hotel",
                "slug": "sheraton-abuja",
                "description": (
                    "The iconic Sheraton Abuja Hotel is a 5-star property located just 500 metres "
                    "from NAIA Terminal 1. With its stunning views of Abuja's skyline, world-class "
                    "restaurant, infinity pool, and complimentary airport shuttle, it is the first "
                    "choice for business travellers and dignitaries arriving in the capital."
                ),
                "star_rating": 5,
                "address": "Ladi Kwali Way, Central Business District, Abuja, FCT",
                "distance_from_airport": Decimal("0.5"),
                "phone": "+234 9 461 0000",
                "email": "reservations@sheraton-abuja.com",
                "website": "https://www.marriott.com",
                "amenities": ["Infinity Pool", "Spa & Wellness Centre", "24-hr Room Service",
                               "Business Centre", "Multiple Restaurants", "Fitness Club",
                               "Concierge Service", "Valet Parking"],
                "has_airport_shuttle": True,
                "check_in_time": "14:00",
                "check_out_time": "12:00",
                "rooms": [
                    {
                        "name": "Deluxe King Room",
                        "description": "Spacious 42m² room with king bed, city view, marble bathroom, and high-speed Wi-Fi.",
                        "bed_type": "King",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("75000.00"),
                        "total_rooms": 80,
                        "amenities": ["King Bed", "City View", "Marble Bathroom", "Minibar",
                                       "Flat-screen TV", "Free Wi-Fi", "Bathrobe & Slippers"],
                    },
                    {
                        "name": "Executive Suite",
                        "description": "Luxurious 90m² suite with separate living area, panoramic city views, and personalised butler service.",
                        "bed_type": "King",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("150000.00"),
                        "total_rooms": 20,
                        "amenities": ["Separate Living Area", "Butler Service", "Panoramic View",
                                       "Jacuzzi", "Nespresso Machine", "Complimentary Breakfast"],
                    },
                    {
                        "name": "Deluxe Twin Room",
                        "description": "Well-appointed room with two twin beds, ideal for colleagues or family members travelling together.",
                        "bed_type": "Twin",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("72000.00"),
                        "total_rooms": 40,
                        "amenities": ["Twin Beds", "Work Desk", "Free Wi-Fi", "Air Conditioning", "LCD TV"],
                    },
                ],
            },
            {
                "name": "Transcorp Hilton Abuja",
                "slug": "transcorp-hilton-abuja",
                "description": (
                    "Transcorp Hilton Abuja is a landmark 5-star hotel in the heart of Nigeria's "
                    "capital, celebrated for its world-class conference facilities, multiple dining "
                    "options, and impeccable service. Located 2 km from the airport, it is the "
                    "preferred venue for government delegations and international conferences."
                ),
                "star_rating": 5,
                "address": "1 Aguiyi Ironsi Street, Maitama, Abuja, FCT",
                "distance_from_airport": Decimal("2.0"),
                "phone": "+234 9 461 1500",
                "email": "info@transcorphilton.com",
                "website": "https://www.hilton.com",
                "amenities": ["Olympic Swimming Pool", "Tennis Courts", "Shopping Mall",
                               "6 Restaurants & Bars", "Full-service Spa", "Helipad",
                               "Conference Facilities (5,000 pax)", "24-hr Gym"],
                "has_airport_shuttle": False,
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "rooms": [
                    {
                        "name": "Standard Queen Room",
                        "description": "Comfortable 35m² room with queen bed, work desk, and garden view.",
                        "bed_type": "Queen",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("65000.00"),
                        "total_rooms": 120,
                        "amenities": ["Queen Bed", "Work Desk", "Garden View", "Free Wi-Fi", "Mini Fridge"],
                    },
                    {
                        "name": "Executive King Room",
                        "description": "Premium room with executive lounge access, complimentary breakfast, and evening cocktails.",
                        "bed_type": "King",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("90000.00"),
                        "total_rooms": 60,
                        "amenities": ["Executive Lounge Access", "Complimentary Breakfast",
                                       "Evening Cocktails", "Pillow Menu", "King Bed"],
                    },
                    {
                        "name": "Presidential Suite",
                        "description": "The ultimate in luxury — a 250m² suite with private dining room, study, and two bedrooms.",
                        "bed_type": "King",
                        "max_occupancy": 4,
                        "base_price_per_night": Decimal("350000.00"),
                        "total_rooms": 4,
                        "amenities": ["250m² Floor Area", "Private Dining Room", "Study",
                                       "Two Bedrooms", "Butler Service", "Grand Piano"],
                    },
                ],
            },
            {
                "name": "NAIA Airport Transit Hotel",
                "slug": "naia-airport-transit-hotel",
                "description": (
                    "Conveniently located within the NAIA complex (just 100 metres from Terminal 1), "
                    "the NAIA Airport Transit Hotel is purpose-built for passengers with layovers, "
                    "early morning departures, or late-night arrivals. No shuttle needed — simply "
                    "walk from arrivals to your room within minutes."
                ),
                "star_rating": 3,
                "address": "NAIA Airport Road, Garki, Abuja, FCT (Airside — Terminal 1 Landside)",
                "distance_from_airport": Decimal("0.1"),
                "phone": "+234 9 870 2000",
                "email": "transit@naiahotel.ng",
                "website": "",
                "amenities": ["24-hr Check-in", "Restaurant & Bar", "Free Parking",
                               "Luggage Storage", "Laundry Service", "Free Wi-Fi", "Business Corner"],
                "has_airport_shuttle": True,
                "check_in_time": "00:00",
                "check_out_time": "23:59",
                "rooms": [
                    {
                        "name": "Transit Standard Room",
                        "description": "Comfortable room designed for short stays. Includes blackout curtains, shower, and all essentials.",
                        "bed_type": "Double",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("35000.00"),
                        "total_rooms": 60,
                        "amenities": ["Blackout Curtains", "Shower", "Free Wi-Fi",
                                       "Alarm Clock", "TV", "Desk"],
                    },
                    {
                        "name": "Family Room",
                        "description": "Spacious room with two double beds, perfect for families in transit.",
                        "bed_type": "Double",
                        "max_occupancy": 4,
                        "base_price_per_night": Decimal("55000.00"),
                        "total_rooms": 20,
                        "amenities": ["Two Double Beds", "Children's Amenities", "Free Wi-Fi",
                                       "Large Bathroom", "Kitchenette"],
                    },
                ],
            },
            {
                "name": "Radisson Blu Anchorage Hotel",
                "slug": "radisson-blu-anchorage-abuja",
                "description": (
                    "A contemporary 4-star business hotel 3 km from NAIA, known for its "
                    "signature restaurant, rooftop bar, and seamless connectivity. A top pick "
                    "for corporate travellers seeking modern amenities at competitive rates."
                ),
                "star_rating": 4,
                "address": "Plot 5/6 Agadez Street, Wuse Zone 5, Abuja, FCT",
                "distance_from_airport": Decimal("3.0"),
                "phone": "+234 9 290 5555",
                "email": "reservations@radissonbluabuja.com",
                "website": "https://www.radissonhotels.com",
                "amenities": ["Rooftop Bar", "Signature Restaurant", "Gym & Spa",
                               "High-speed Fibre Internet", "Airport Shuttle", "Conference Rooms"],
                "has_airport_shuttle": True,
                "check_in_time": "14:00",
                "check_out_time": "12:00",
                "rooms": [
                    {
                        "name": "Superior King Room",
                        "description": "Modern 32m² room with king bed, rain shower, and contemporary Nigerian art.",
                        "bed_type": "King",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("48000.00"),
                        "total_rooms": 90,
                        "amenities": ["King Bed", "Rain Shower", "Nigerian Art Décor",
                                       "Free Wi-Fi", "Smart TV", "Nespresso"],
                    },
                    {
                        "name": "Business Class Room",
                        "description": "Enhanced room with dedicated work zone, fast fibre internet, and complimentary minibar.",
                        "bed_type": "King",
                        "max_occupancy": 2,
                        "base_price_per_night": Decimal("62000.00"),
                        "total_rooms": 40,
                        "amenities": ["Dedicated Work Zone", "Fibre Internet", "Complimentary Minibar",
                                       "Ergonomic Chair", "Printer Access"],
                    },
                ],
            },
        ]

        count = 0
        for h in hotels_data:
            rooms = h.pop("rooms")
            hotel, created = Hotel.objects.get_or_create(
                slug=h["slug"],
                defaults=h,
            )
            if created:
                count += 1
                self.stdout.write(f"  Hotel: {hotel.name}")

            for r in rooms:
                RoomType.objects.get_or_create(
                    hotel=hotel,
                    name=r["name"],
                    defaults=r,
                )

        self.stdout.write(self.style.SUCCESS(f"  OK:{count} hotels seeded (+ room types)"))

    # ------------------------------------------------------------------
    # LOUNGES
    # ------------------------------------------------------------------
    def _seed_lounges(self):
        from lounge.models import AirportLounge

        lounges_data = [
            {
                "name": "NAIA Executive Lounge",
                "slug": "naia-executive-lounge",
                "lounge_type": "INDEPENDENT",
                "terminal": "T1",
                "location_description": "Level 2, International Departures — past Security Checkpoint B",
                "description": (
                    "The flagship NAIA Executive Lounge offers a tranquil retreat from the terminal "
                    "bustle. Enjoy unlimited food and beverages, high-speed Wi-Fi, business facilities, "
                    "and dedicated shower suites. Open to all travellers — simply purchase a day pass."
                ),
                "capacity": 80,
                "day_pass_price": Decimal("15000.00"),
                "child_price": Decimal("7500.00"),
                "has_wifi": True,
                "has_food": True,
                "has_shower": True,
                "has_spa": False,
                "has_prayer_room": True,
                "has_business_centre": True,
                "opening_time": "04:00",
                "closing_time": "23:59",
                "is_active": True,
            },
            {
                "name": "Air Peace Premier Lounge",
                "slug": "air-peace-premier-lounge",
                "lounge_type": "AIRLINE",
                "terminal": "T1",
                "location_description": "Level 1, Domestic Departures — Gate D3 Area",
                "description": (
                    "The Air Peace Premier Lounge is dedicated to Air Peace Business Class passengers "
                    "and Priority Pass members. Enjoy Nigerian and continental cuisine, premium drinks, "
                    "and a quiet work area while awaiting your flight."
                ),
                "capacity": 50,
                "day_pass_price": Decimal("12000.00"),
                "child_price": Decimal("0.00"),
                "has_wifi": True,
                "has_food": True,
                "has_shower": True,
                "has_spa": False,
                "has_prayer_room": True,
                "has_business_centre": True,
                "opening_time": "05:00",
                "closing_time": "22:00",
                "is_active": True,
            },
            {
                "name": "State House VIP Lounge",
                "slug": "state-house-vip-lounge",
                "lounge_type": "VIP",
                "terminal": "T1",
                "location_description": "Level 3, VIP Wing — separate entrance via State Protocol Gate",
                "description": (
                    "Reserved for government officials, diplomatic personnel, and corporate VIPs. "
                    "The State House VIP Lounge provides an exclusive environment with personalised "
                    "service, private meeting rooms, secure communications facilities, and luxury amenities."
                ),
                "capacity": 30,
                "day_pass_price": Decimal("35000.00"),
                "child_price": Decimal("0.00"),
                "has_wifi": True,
                "has_food": True,
                "has_shower": True,
                "has_spa": True,
                "has_prayer_room": True,
                "has_business_centre": True,
                "opening_time": "00:00",
                "closing_time": "23:59",
                "is_active": True,
            },
            {
                "name": "Nnamdi Transit Hub Lounge",
                "slug": "nnamdi-transit-hub-lounge",
                "lounge_type": "TRANSIT",
                "terminal": "T2",
                "location_description": "Ground Floor, Terminal 2 Arrivals — between Gate A1 and A5",
                "description": (
                    "Designed for passengers in transit between international flights, the Nnamdi "
                    "Transit Hub Lounge provides comfortable seating, complimentary snacks, showers, "
                    "and sleeping pods. Ideal for layovers of 2–8 hours."
                ),
                "capacity": 60,
                "day_pass_price": Decimal("8000.00"),
                "child_price": Decimal("4000.00"),
                "has_wifi": True,
                "has_food": True,
                "has_shower": True,
                "has_spa": False,
                "has_prayer_room": True,
                "has_business_centre": False,
                "opening_time": "00:00",
                "closing_time": "23:59",
                "is_active": True,
            },
            {
                "name": "Green Sapphire Business Lounge",
                "slug": "green-sapphire-business-lounge",
                "lounge_type": "INDEPENDENT",
                "terminal": "T1",
                "location_description": "Level 2, Domestic Terminal — opposite Gate B7",
                "description": (
                    "A modern independent lounge for domestic travellers. Features power outlets at "
                    "every seat, high-speed fibre Wi-Fi, a buffet of Nigerian dishes, and a well-stocked bar."
                ),
                "capacity": 45,
                "day_pass_price": Decimal("8500.00"),
                "child_price": Decimal("4000.00"),
                "has_wifi": True,
                "has_food": True,
                "has_shower": False,
                "has_spa": False,
                "has_prayer_room": False,
                "has_business_centre": True,
                "opening_time": "06:00",
                "closing_time": "21:00",
                "is_active": True,
            },
        ]

        count = 0
        for data in lounges_data:
            _, created = AirportLounge.objects.get_or_create(
                slug=data["slug"], defaults=data
            )
            if created:
                count += 1
                self.stdout.write(f"  Lounge: {data['name']}")
        self.stdout.write(self.style.SUCCESS(f"  OK:{count} lounges seeded"))

    # ------------------------------------------------------------------
    # AIRCRAFT STANDS & PARKING RATES
    # ------------------------------------------------------------------
    def _seed_aircraft_stands_and_rates(self):
        from airlines.models import AircraftStand, AircraftParkingRate, AircraftSizeCategory

        stands_data = [
            {"stand_number": "A1", "terminal": "T1", "stand_type": "CONTACT", "max_aircraft_size": "HEAVY", "has_jetway": True, "has_gpu": True, "has_pca": True, "notes": "Primary widebody stand, serves long-haul international routes."},
            {"stand_number": "A2", "terminal": "T1", "stand_type": "CONTACT", "max_aircraft_size": "HEAVY", "has_jetway": True, "has_gpu": True, "has_pca": True, "notes": "Secondary widebody stand with full ground support services."},
            {"stand_number": "B1", "terminal": "T1", "stand_type": "CONTACT", "max_aircraft_size": "LARGE", "has_jetway": True, "has_gpu": True, "has_pca": False, "notes": "Handles narrow-body aircraft on regional and domestic routes."},
            {"stand_number": "B2", "terminal": "T1", "stand_type": "CONTACT", "max_aircraft_size": "LARGE", "has_jetway": True, "has_gpu": True, "has_pca": False, "notes": "Busy domestic stand — Air Peace, Ibom Air, United Nigeria."},
            {"stand_number": "B3", "terminal": "T1", "stand_type": "CONTACT", "max_aircraft_size": "MEDIUM", "has_jetway": False, "has_gpu": True, "has_pca": False, "notes": "Medium aircraft with air-bridge access via walkway."},
            {"stand_number": "C1", "terminal": "T2", "stand_type": "REMOTE", "max_aircraft_size": "MEDIUM", "has_jetway": False, "has_gpu": True, "has_pca": False, "notes": "Remote stand; passengers bussed to terminal. Charter flights."},
            {"stand_number": "C2", "terminal": "T2", "stand_type": "REMOTE", "max_aircraft_size": "SMALL", "has_jetway": False, "has_gpu": False, "has_pca": False, "notes": "Light/small aircraft — private aviation and feeder flights."},
            {"stand_number": "CG1", "terminal": "T2", "stand_type": "CARGO", "max_aircraft_size": "LARGE", "has_jetway": False, "has_gpu": True, "has_pca": False, "notes": "Dedicated cargo stand — FedEx, DHL, Ethiopian Cargo."},
            {"stand_number": "M1", "terminal": "T1", "stand_type": "MAINT", "max_aircraft_size": "HEAVY", "has_jetway": False, "has_gpu": True, "has_pca": True, "notes": "Maintenance bay for scheduled checks and AOG repairs."},
        ]

        count = 0
        for s in stands_data:
            _, created = AircraftStand.objects.get_or_create(
                stand_number=s["stand_number"], defaults=s
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"  OK:{count} aircraft stands seeded"))

        rates_data = [
            {
                "aircraft_size": "LIGHT",
                "landing_fee": Decimal("50000.00"),
                "hourly_rate": Decimal("5000.00"),
                "daily_rate": Decimal("80000.00"),
                "weekly_rate": Decimal("400000.00"),
                "gpu_hourly_rate": Decimal("1500.00"),
                "pca_hourly_rate": Decimal("0.00"),
                "effective_from": date(2024, 1, 1),
            },
            {
                "aircraft_size": "SMALL",
                "landing_fee": Decimal("150000.00"),
                "hourly_rate": Decimal("15000.00"),
                "daily_rate": Decimal("200000.00"),
                "weekly_rate": Decimal("1000000.00"),
                "gpu_hourly_rate": Decimal("3000.00"),
                "pca_hourly_rate": Decimal("2000.00"),
                "effective_from": date(2024, 1, 1),
            },
            {
                "aircraft_size": "MEDIUM",
                "landing_fee": Decimal("400000.00"),
                "hourly_rate": Decimal("40000.00"),
                "daily_rate": Decimal("500000.00"),
                "weekly_rate": Decimal("2500000.00"),
                "gpu_hourly_rate": Decimal("6000.00"),
                "pca_hourly_rate": Decimal("5000.00"),
                "effective_from": date(2024, 1, 1),
            },
            {
                "aircraft_size": "LARGE",
                "landing_fee": Decimal("800000.00"),
                "hourly_rate": Decimal("80000.00"),
                "daily_rate": Decimal("1000000.00"),
                "weekly_rate": Decimal("5000000.00"),
                "gpu_hourly_rate": Decimal("10000.00"),
                "pca_hourly_rate": Decimal("8000.00"),
                "effective_from": date(2024, 1, 1),
            },
            {
                "aircraft_size": "HEAVY",
                "landing_fee": Decimal("1500000.00"),
                "hourly_rate": Decimal("150000.00"),
                "daily_rate": Decimal("2000000.00"),
                "weekly_rate": Decimal("10000000.00"),
                "gpu_hourly_rate": Decimal("18000.00"),
                "pca_hourly_rate": Decimal("15000.00"),
                "effective_from": date(2024, 1, 1),
            },
        ]

        rate_count = 0
        for r in rates_data:
            _, created = AircraftParkingRate.objects.get_or_create(
                aircraft_size=r["aircraft_size"], defaults=r
            )
            if created:
                rate_count += 1
        self.stdout.write(self.style.SUCCESS(f"  OK:{rate_count} aircraft parking rates seeded"))

    # ------------------------------------------------------------------
    # TAX TYPES
    # ------------------------------------------------------------------
    def _seed_tax_types(self):
        from taxes.models import TaxType

        tax_data = [
            {
                "name": "Passenger Service Charge",
                "code": "PSC",
                "category": "PSC",
                "description": "Charged per departing passenger. Retained by NAIA for terminal operations, passenger amenities, and infrastructure maintenance.",
                "rate_type": "FIXED",
                "rate": Decimal("2500.00"),
                "applicability": "ALL",
                "is_mandatory": True,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "Airport Development Levy",
                "code": "ADL",
                "category": "ADL",
                "description": "Levied by the Federal Airports Authority of Nigeria (FAAN) on all domestic and international tickets to fund airport infrastructure development across Nigeria.",
                "rate_type": "PERCENT",
                "rate": Decimal("5.00"),
                "applicability": "ALL",
                "is_mandatory": True,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "Security & Safety Fee",
                "code": "SEC",
                "category": "SEC",
                "description": "Covers passenger and baggage screening, security personnel costs, and safety equipment. Mandated by the Nigerian Civil Aviation Authority (NCAA).",
                "rate_type": "FIXED",
                "rate": Decimal("1500.00"),
                "applicability": "ALL",
                "is_mandatory": True,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "Departure Tax",
                "code": "DEP",
                "category": "DEP",
                "description": "Federal government departure tax collected from all passengers departing Nigeria. Remitted to the Consolidated Revenue Fund.",
                "rate_type": "FIXED",
                "rate": Decimal("3000.00"),
                "applicability": "ALL",
                "is_mandatory": True,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "Value Added Tax",
                "code": "VAT",
                "category": "VAT",
                "description": "7.5% VAT applied on applicable airport services as mandated by the Value Added Tax Act (as amended). Remitted to the Federal Inland Revenue Service (FIRS).",
                "rate_type": "PERCENT",
                "rate": Decimal("7.50"),
                "applicability": "ALL",
                "is_mandatory": True,
                "effective_from": date(2020, 2, 1),
            },
            {
                "name": "Fuel Surcharge",
                "code": "FUEL",
                "category": "FUEL",
                "description": "Variable surcharge reflecting the cost of aviation fuel. Applied per passenger to offset airline fuel costs passed through to the airport system.",
                "rate_type": "FIXED",
                "rate": Decimal("3000.00"),
                "applicability": "ALL",
                "is_mandatory": False,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "Transit Passenger Tax",
                "code": "TRANSIT",
                "category": "TRANSIT",
                "description": "Applied to transit passengers connecting to onward flights through NAIA. Covers transit facilitation services.",
                "rate_type": "FIXED",
                "rate": Decimal("1000.00"),
                "applicability": "INTERNATIONAL",
                "is_mandatory": False,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "International Route Surcharge",
                "code": "INTL",
                "category": "INTL",
                "description": "3% surcharge on base fares for international routes. Covers additional customs, immigration, and border security services.",
                "rate_type": "PERCENT",
                "rate": Decimal("3.00"),
                "applicability": "INTERNATIONAL",
                "is_mandatory": True,
                "effective_from": date(2024, 1, 1),
            },
            {
                "name": "Customs & Stamp Duty",
                "code": "CSD",
                "category": "CSD",
                "description": "Applicable to international passengers only. Covers customs documentation, stamp duty on tickets, and regulatory compliance costs.",
                "rate_type": "FIXED",
                "rate": Decimal("500.00"),
                "applicability": "INTERNATIONAL",
                "is_mandatory": True,
                "effective_from": date(2024, 1, 1),
            },
        ]

        count = 0
        for t in tax_data:
            _, created = TaxType.objects.get_or_create(code=t["code"], defaults=t)
            if created:
                count += 1
                self.stdout.write(f"  Tax: {t['code']} — {t['name']}")
        self.stdout.write(self.style.SUCCESS(f"  OK:{count} tax types seeded"))

    # ------------------------------------------------------------------
    # TAXI VEHICLE CATEGORIES
    # ------------------------------------------------------------------
    def _seed_taxi_vehicles(self):
        from taxis.models import VehicleCategory

        vehicles_data = [
            {
                "name": "Economy Saloon",
                "slug": "economy-saloon",
                "vehicle_type": "SEDAN",
                "description": (
                    "Our most affordable option. Clean, air-conditioned saloon cars driven by "
                    "professional, licensed NAIA-approved drivers. Perfect for solo travellers "
                    "or couples heading into the city."
                ),
                "max_passengers": 4,
                "max_luggage": 2,
                "price_per_km": Decimal("150.00"),
                "minimum_fare": Decimal("3000.00"),
                "waiting_charge_per_hour": Decimal("1500.00"),
                "features": ["Air Conditioning", "Licensed Driver", "Fixed Price", "Receipt Provided"],
            },
            {
                "name": "Standard SUV",
                "slug": "standard-suv",
                "vehicle_type": "SUV",
                "description": (
                    "Comfortable SUV with ample boot space for luggage. Ideal for small families "
                    "or business travellers with multiple bags. All vehicles are less than 3 years old."
                ),
                "max_passengers": 6,
                "max_luggage": 4,
                "price_per_km": Decimal("220.00"),
                "minimum_fare": Decimal("4500.00"),
                "waiting_charge_per_hour": Decimal("2000.00"),
                "features": ["Air Conditioning", "Extra Boot Space", "Licensed Driver", "USB Charging"],
            },
            {
                "name": "Luxury Executive",
                "slug": "luxury-executive",
                "vehicle_type": "LUXURY",
                "description": (
                    "Arrive in style with our premium executive vehicles — Mercedes E-Class, "
                    "Toyota Land Cruiser V8, or equivalent. Includes meet & greet service at "
                    "arrivals, complimentary water, and Wi-Fi hotspot. Ideal for VIPs and "
                    "corporate clients."
                ),
                "max_passengers": 4,
                "max_luggage": 3,
                "price_per_km": Decimal("400.00"),
                "minimum_fare": Decimal("10000.00"),
                "waiting_charge_per_hour": Decimal("5000.00"),
                "features": ["Meet & Greet", "Complimentary Water", "Wi-Fi Hotspot",
                               "Premium Vehicle", "Suit & Tie Driver", "Flight Monitoring"],
            },
            {
                "name": "Family Minivan",
                "slug": "family-minivan",
                "vehicle_type": "MINIVAN",
                "description": (
                    "Spacious minivan seating up to 8 passengers with room for large families "
                    "and their luggage. Air-conditioned and equipped with entertainment screens "
                    "for the little ones."
                ),
                "max_passengers": 8,
                "max_luggage": 6,
                "price_per_km": Decimal("280.00"),
                "minimum_fare": Decimal("6000.00"),
                "waiting_charge_per_hour": Decimal("2500.00"),
                "features": ["Seats up to 8", "Entertainment Screen", "Air Conditioning",
                               "Large Boot", "Child Seat Available on Request"],
            },
            {
                "name": "Corporate Shuttle Bus",
                "slug": "corporate-shuttle-bus",
                "vehicle_type": "BUS",
                "description": (
                    "14-seater shuttle bus for large groups, corporate delegations, or conference "
                    "attendees. Includes a professional driver and assistant. Ideal for hotel–airport "
                    "transfers for groups."
                ),
                "max_passengers": 14,
                "max_luggage": 14,
                "price_per_km": Decimal("350.00"),
                "minimum_fare": Decimal("15000.00"),
                "waiting_charge_per_hour": Decimal("4000.00"),
                "features": ["14 Seats", "Driver + Assistant", "Luggage Trailer Available",
                               "Air Conditioning", "PA System", "Group Discount"],
            },
        ]

        count = 0
        for v in vehicles_data:
            _, created = VehicleCategory.objects.get_or_create(
                slug=v["slug"], defaults=v
            )
            if created:
                count += 1
                self.stdout.write(f"  Vehicle: {v['name']}")
        self.stdout.write(self.style.SUCCESS(f"  OK:{count} vehicle categories seeded"))
