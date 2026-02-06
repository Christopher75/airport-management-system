"""
Management command to seed the database with test data.

Creates airports, airlines, aircraft, and sample flights for testing.
Usage: python manage.py seed_data
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from airlines.models import Aircraft, Airline
from flights.models import Airport, Flight, Gate


class Command(BaseCommand):
    """Seed the database with test data for development and testing."""

    help = "Seed the database with airports, airlines, aircraft, and flights"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )
        parser.add_argument(
            "--flights-only",
            action="store_true",
            help="Only seed flights (assumes airports and airlines exist)",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to generate flights for (default: 30)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Flight.objects.all().delete()
            Gate.objects.all().delete()
            Aircraft.objects.all().delete()
            Airline.objects.all().delete()
            Airport.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Data cleared."))

        if not options["flights_only"]:
            self.create_airports()
            self.create_airlines()
            self.create_aircraft()
            self.create_gates()

        self.create_flights(days=options["days"])

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

    def create_airports(self):
        """Create Nigerian and international airports."""
        self.stdout.write("Creating airports...")

        # Nigerian Airports
        nigerian_airports = [
            {
                "name": "Nnamdi Azikiwe International Airport",
                "code": "ABV",
                "icao_code": "DNAA",
                "city": "Abuja",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("9.006792"),
                "longitude": Decimal("7.263172"),
                "is_international": True,
                "phone": "+234 9 5238301",
            },
            {
                "name": "Murtala Muhammed International Airport",
                "code": "LOS",
                "icao_code": "DNMM",
                "city": "Lagos",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("6.577370"),
                "longitude": Decimal("3.321156"),
                "is_international": True,
                "phone": "+234 1 2700701",
            },
            {
                "name": "Port Harcourt International Airport",
                "code": "PHC",
                "icao_code": "DNPO",
                "city": "Port Harcourt",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("5.015494"),
                "longitude": Decimal("6.949594"),
                "is_international": True,
            },
            {
                "name": "Mallam Aminu Kano International Airport",
                "code": "KAN",
                "icao_code": "DNKN",
                "city": "Kano",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("12.047560"),
                "longitude": Decimal("8.524620"),
                "is_international": True,
            },
            {
                "name": "Akanu Ibiam International Airport",
                "code": "ENU",
                "icao_code": "DNEN",
                "city": "Enugu",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("6.474272"),
                "longitude": Decimal("7.561960"),
                "is_international": True,
            },
            {
                "name": "Margaret Ekpo International Airport",
                "code": "CBQ",
                "icao_code": "DNCA",
                "city": "Calabar",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("4.976019"),
                "longitude": Decimal("8.347200"),
                "is_international": False,
            },
            {
                "name": "Sam Mbakwe International Cargo Airport",
                "code": "QOW",
                "icao_code": "DNIM",
                "city": "Owerri",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("5.427060"),
                "longitude": Decimal("7.206030"),
                "is_international": False,
            },
            {
                "name": "Yakubu Gowon Airport",
                "code": "JOS",
                "icao_code": "DNJO",
                "city": "Jos",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("9.639830"),
                "longitude": Decimal("8.869050"),
                "is_international": False,
            },
            {
                "name": "Sadiq Abubakar III International Airport",
                "code": "SKO",
                "icao_code": "DNSO",
                "city": "Sokoto",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("12.916300"),
                "longitude": Decimal("5.207190"),
                "is_international": False,
            },
            {
                "name": "Benin Airport",
                "code": "BNI",
                "icao_code": "DNBE",
                "city": "Benin City",
                "country": "Nigeria",
                "timezone": "Africa/Lagos",
                "latitude": Decimal("6.316979"),
                "longitude": Decimal("5.599503"),
                "is_international": False,
            },
        ]

        # International Airports
        international_airports = [
            {
                "name": "London Heathrow Airport",
                "code": "LHR",
                "icao_code": "EGLL",
                "city": "London",
                "country": "United Kingdom",
                "timezone": "Europe/London",
                "latitude": Decimal("51.470020"),
                "longitude": Decimal("-0.454295"),
                "is_international": True,
            },
            {
                "name": "Dubai International Airport",
                "code": "DXB",
                "icao_code": "OMDB",
                "city": "Dubai",
                "country": "United Arab Emirates",
                "timezone": "Asia/Dubai",
                "latitude": Decimal("25.252778"),
                "longitude": Decimal("55.364444"),
                "is_international": True,
            },
            {
                "name": "John F. Kennedy International Airport",
                "code": "JFK",
                "icao_code": "KJFK",
                "city": "New York",
                "country": "United States",
                "timezone": "America/New_York",
                "latitude": Decimal("40.639722"),
                "longitude": Decimal("-73.778889"),
                "is_international": True,
            },
            {
                "name": "Bole International Airport",
                "code": "ADD",
                "icao_code": "HAAB",
                "city": "Addis Ababa",
                "country": "Ethiopia",
                "timezone": "Africa/Addis_Ababa",
                "latitude": Decimal("8.977778"),
                "longitude": Decimal("38.799167"),
                "is_international": True,
            },
            {
                "name": "Jomo Kenyatta International Airport",
                "code": "NBO",
                "icao_code": "HKJK",
                "city": "Nairobi",
                "country": "Kenya",
                "timezone": "Africa/Nairobi",
                "latitude": Decimal("-1.319167"),
                "longitude": Decimal("36.927778"),
                "is_international": True,
            },
            {
                "name": "Kotoka International Airport",
                "code": "ACC",
                "icao_code": "DGAA",
                "city": "Accra",
                "country": "Ghana",
                "timezone": "Africa/Accra",
                "latitude": Decimal("5.605186"),
                "longitude": Decimal("-0.166786"),
                "is_international": True,
            },
            {
                "name": "O.R. Tambo International Airport",
                "code": "JNB",
                "icao_code": "FAOR",
                "city": "Johannesburg",
                "country": "South Africa",
                "timezone": "Africa/Johannesburg",
                "latitude": Decimal("-26.133694"),
                "longitude": Decimal("28.242317"),
                "is_international": True,
            },
            {
                "name": "Charles de Gaulle Airport",
                "code": "CDG",
                "icao_code": "LFPG",
                "city": "Paris",
                "country": "France",
                "timezone": "Europe/Paris",
                "latitude": Decimal("49.009722"),
                "longitude": Decimal("2.547778"),
                "is_international": True,
            },
            {
                "name": "Hamad International Airport",
                "code": "DOH",
                "icao_code": "OTHH",
                "city": "Doha",
                "country": "Qatar",
                "timezone": "Asia/Qatar",
                "latitude": Decimal("25.273056"),
                "longitude": Decimal("51.608056"),
                "is_international": True,
            },
            {
                "name": "Cairo International Airport",
                "code": "CAI",
                "icao_code": "HECA",
                "city": "Cairo",
                "country": "Egypt",
                "timezone": "Africa/Cairo",
                "latitude": Decimal("30.121944"),
                "longitude": Decimal("31.405556"),
                "is_international": True,
            },
        ]

        all_airports = nigerian_airports + international_airports
        created_count = 0

        for airport_data in all_airports:
            airport, created = Airport.objects.get_or_create(
                code=airport_data["code"],
                defaults=airport_data,
            )
            if created:
                created_count += 1

        self.stdout.write(f"  Created {created_count} airports")

    def create_airlines(self):
        """Create Nigerian and international airlines."""
        self.stdout.write("Creating airlines...")

        airlines_data = [
            # Nigerian Airlines
            {
                "name": "Air Peace",
                "code": "P4",
                "icao_code": "APK",
                "country": "Nigeria",
                "headquarters": "Lagos",
                "website": "https://flyairpeace.com",
                "description": "Nigeria's largest carrier offering domestic and international flights.",
                "is_active": True,
            },
            {
                "name": "Arik Air",
                "code": "W3",
                "icao_code": "ARA",
                "country": "Nigeria",
                "headquarters": "Lagos",
                "website": "https://arikair.com",
                "description": "West Africa's leading airline with extensive domestic network.",
                "is_active": True,
            },
            {
                "name": "Ibom Air",
                "code": "I5",
                "icao_code": "IBA",
                "country": "Nigeria",
                "headquarters": "Uyo",
                "website": "https://ibomair.com",
                "description": "Premium regional airline known for punctuality and service.",
                "is_active": True,
            },
            {
                "name": "Green Africa Airways",
                "code": "Q9",
                "icao_code": "GNA",
                "country": "Nigeria",
                "headquarters": "Lagos",
                "website": "https://greenafrica.com",
                "description": "Value carrier making air travel accessible to all.",
                "is_active": True,
            },
            {
                "name": "Overland Airways",
                "code": "OJ",
                "icao_code": "OVL",
                "country": "Nigeria",
                "headquarters": "Lagos",
                "website": "https://overlandairways.com",
                "description": "Regional airline connecting Nigerian cities.",
                "is_active": True,
            },
            # International Airlines
            {
                "name": "Emirates",
                "code": "EK",
                "icao_code": "UAE",
                "country": "United Arab Emirates",
                "headquarters": "Dubai",
                "website": "https://emirates.com",
                "description": "Award-winning airline offering world-class service.",
                "is_active": True,
                "alliance": "NONE",
            },
            {
                "name": "British Airways",
                "code": "BA",
                "icao_code": "BAW",
                "country": "United Kingdom",
                "headquarters": "London",
                "website": "https://britishairways.com",
                "description": "The UK's flag carrier with global reach.",
                "is_active": True,
                "alliance": "ONEWORLD",
            },
            {
                "name": "Ethiopian Airlines",
                "code": "ET",
                "icao_code": "ETH",
                "country": "Ethiopia",
                "headquarters": "Addis Ababa",
                "website": "https://ethiopianairlines.com",
                "description": "Africa's largest airline group with extensive network.",
                "is_active": True,
                "alliance": "STAR_ALLIANCE",
            },
            {
                "name": "Qatar Airways",
                "code": "QR",
                "icao_code": "QTR",
                "country": "Qatar",
                "headquarters": "Doha",
                "website": "https://qatarairways.com",
                "description": "World's best airline with award-winning service.",
                "is_active": True,
                "alliance": "ONEWORLD",
            },
            {
                "name": "Kenya Airways",
                "code": "KQ",
                "icao_code": "KQA",
                "country": "Kenya",
                "headquarters": "Nairobi",
                "website": "https://kenya-airways.com",
                "description": "The Pride of Africa connecting the continent.",
                "is_active": True,
                "alliance": "SKYTEAM",
            },
            {
                "name": "South African Airways",
                "code": "SA",
                "icao_code": "SAA",
                "country": "South Africa",
                "headquarters": "Johannesburg",
                "website": "https://flysaa.com",
                "description": "South Africa's national carrier.",
                "is_active": True,
                "alliance": "STAR_ALLIANCE",
            },
            {
                "name": "Air France",
                "code": "AF",
                "icao_code": "AFR",
                "country": "France",
                "headquarters": "Paris",
                "website": "https://airfrance.com",
                "description": "France's flag carrier with premium service.",
                "is_active": True,
                "alliance": "SKYTEAM",
            },
        ]

        created_count = 0
        for airline_data in airlines_data:
            airline, created = Airline.objects.get_or_create(
                code=airline_data["code"],
                defaults=airline_data,
            )
            if created:
                created_count += 1

        self.stdout.write(f"  Created {created_count} airlines")

    def create_aircraft(self):
        """Create aircraft for each airline."""
        self.stdout.write("Creating aircraft...")

        aircraft_configs = {
            # Nigerian Airlines - Domestic focus
            "P4": [  # Air Peace
                ("5N-BQO", "B738", 162, 0, 16, 146),
                ("5N-BQP", "B738", 162, 0, 16, 146),
                ("5N-BWM", "E195", 124, 0, 12, 112),
                ("5N-BWN", "E195", 124, 0, 12, 112),
            ],
            "W3": [  # Arik Air
                ("5N-MJP", "B738", 160, 0, 16, 144),
                ("5N-MJQ", "B738", 160, 0, 16, 144),
                ("5N-MJR", "A320", 156, 0, 12, 144),
            ],
            "I5": [  # Ibom Air
                ("5N-BMS", "A20N", 158, 0, 16, 142),
                ("5N-BMT", "A20N", 158, 0, 16, 142),
                ("5N-BMU", "A20N", 158, 0, 16, 142),
            ],
            "Q9": [  # Green Africa
                ("5N-GAA", "AT72", 70, 0, 0, 70),
                ("5N-GAB", "AT72", 70, 0, 0, 70),
            ],
            "OJ": [  # Overland
                ("5N-OLA", "AT72", 68, 0, 0, 68),
            ],
            # International Airlines
            "EK": [  # Emirates
                ("A6-ENB", "B77W", 354, 8, 42, 304),
                ("A6-ENC", "A388", 489, 14, 76, 399),
            ],
            "BA": [  # British Airways
                ("G-ZBKA", "B789", 214, 8, 42, 164),
                ("G-ZBKB", "B77W", 275, 14, 48, 213),
            ],
            "ET": [  # Ethiopian
                ("ET-AUQ", "B789", 262, 0, 30, 232),
                ("ET-AUR", "B788", 246, 0, 24, 222),
            ],
            "QR": [  # Qatar
                ("A7-BEA", "B77W", 358, 8, 42, 308),
            ],
            "KQ": [  # Kenya Airways
                ("5Y-KQS", "B788", 234, 0, 30, 204),
            ],
            "SA": [  # South African Airways
                ("ZS-SXB", "A333", 239, 0, 36, 203),
            ],
            "AF": [  # Air France
                ("F-HRBA", "B789", 276, 0, 36, 240),
            ],
        }

        created_count = 0
        for airline_code, aircraft_list in aircraft_configs.items():
            try:
                airline = Airline.objects.get(code=airline_code)
                for reg, ac_type, total, first, business, economy in aircraft_list:
                    aircraft, created = Aircraft.objects.get_or_create(
                        registration=reg,
                        defaults={
                            "airline": airline,
                            "aircraft_type": ac_type,
                            "total_seats": total,
                            "first_class_seats": first,
                            "business_class_seats": business,
                            "economy_class_seats": economy,
                            "year_manufactured": random.randint(2015, 2023),
                            "is_active": True,
                            "status": "ACTIVE",
                        },
                    )
                    if created:
                        created_count += 1
            except Airline.DoesNotExist:
                pass

        self.stdout.write(f"  Created {created_count} aircraft")

    def create_gates(self):
        """Create gates for Nigerian airports."""
        self.stdout.write("Creating gates...")

        # Only create gates for major Nigerian airports
        gate_configs = {
            "ABV": [
                ("D", ["D1", "D2", "D3", "D4", "D5", "D6"], True),
                ("I", ["I1", "I2", "I3", "I4"], True),
            ],
            "LOS": [
                ("D", ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"], True),
                ("I", ["I1", "I2", "I3", "I4", "I5", "I6"], True),
            ],
            "PHC": [
                ("T1", ["A1", "A2", "A3", "A4"], True),
            ],
            "KAN": [
                ("T1", ["G1", "G2", "G3", "G4"], True),
            ],
        }

        created_count = 0
        for airport_code, terminals in gate_configs.items():
            try:
                airport = Airport.objects.get(code=airport_code)
                for terminal, gates, is_international in terminals:
                    for gate_number in gates:
                        gate, created = Gate.objects.get_or_create(
                            airport=airport,
                            terminal=terminal,
                            gate_number=gate_number,
                            defaults={
                                "is_international": is_international,
                                "status": "AVAILABLE",
                            },
                        )
                        if created:
                            created_count += 1
            except Airport.DoesNotExist:
                pass

        self.stdout.write(f"  Created {created_count} gates")

    def create_flights(self, days=30):
        """Create sample flights for the specified number of days."""
        self.stdout.write(f"Creating flights for the next {days} days...")

        # Define routes
        domestic_routes = [
            # From Abuja
            ("ABV", "LOS", "P4", 55, Decimal("45000"), Decimal("120000"), Decimal("0")),
            ("ABV", "LOS", "W3", 55, Decimal("42000"), Decimal("115000"), Decimal("0")),
            ("ABV", "LOS", "I5", 55, Decimal("55000"), Decimal("140000"), Decimal("0")),
            ("ABV", "PHC", "P4", 50, Decimal("38000"), Decimal("100000"), Decimal("0")),
            ("ABV", "KAN", "W3", 45, Decimal("35000"), Decimal("90000"), Decimal("0")),
            ("ABV", "ENU", "P4", 40, Decimal("32000"), Decimal("85000"), Decimal("0")),
            ("ABV", "CBQ", "Q9", 55, Decimal("28000"), Decimal("0"), Decimal("0")),
            # From Lagos
            ("LOS", "ABV", "P4", 55, Decimal("45000"), Decimal("120000"), Decimal("0")),
            ("LOS", "ABV", "W3", 55, Decimal("42000"), Decimal("115000"), Decimal("0")),
            ("LOS", "ABV", "I5", 55, Decimal("55000"), Decimal("140000"), Decimal("0")),
            ("LOS", "PHC", "P4", 50, Decimal("40000"), Decimal("105000"), Decimal("0")),
            ("LOS", "KAN", "W3", 90, Decimal("48000"), Decimal("125000"), Decimal("0")),
            ("LOS", "ENU", "Q9", 55, Decimal("32000"), Decimal("0"), Decimal("0")),
            # From Port Harcourt
            ("PHC", "ABV", "P4", 50, Decimal("38000"), Decimal("100000"), Decimal("0")),
            ("PHC", "LOS", "P4", 50, Decimal("40000"), Decimal("105000"), Decimal("0")),
        ]

        international_routes = [
            # From Abuja
            ("ABV", "LHR", "BA", 390, Decimal("850000"), Decimal("2500000"), Decimal("4500000")),
            ("ABV", "DXB", "EK", 420, Decimal("650000"), Decimal("1800000"), Decimal("3200000")),
            ("ABV", "ADD", "ET", 240, Decimal("380000"), Decimal("1100000"), Decimal("0")),
            ("ABV", "ACC", "P4", 75, Decimal("180000"), Decimal("450000"), Decimal("0")),
            # From Lagos
            ("LOS", "LHR", "BA", 390, Decimal("820000"), Decimal("2400000"), Decimal("4300000")),
            ("LOS", "DXB", "EK", 420, Decimal("620000"), Decimal("1750000"), Decimal("3100000")),
            ("LOS", "JFK", "EK", 780, Decimal("1200000"), Decimal("3500000"), Decimal("6500000")),
            ("LOS", "JNB", "SA", 420, Decimal("480000"), Decimal("1400000"), Decimal("0")),
            ("LOS", "NBO", "KQ", 240, Decimal("350000"), Decimal("950000"), Decimal("0")),
            ("LOS", "CDG", "AF", 390, Decimal("750000"), Decimal("2200000"), Decimal("0")),
            ("LOS", "DOH", "QR", 420, Decimal("580000"), Decimal("1600000"), Decimal("2900000")),
            ("LOS", "ACC", "P4", 60, Decimal("160000"), Decimal("420000"), Decimal("0")),
            # Return flights
            ("LHR", "ABV", "BA", 390, Decimal("850000"), Decimal("2500000"), Decimal("4500000")),
            ("LHR", "LOS", "BA", 390, Decimal("820000"), Decimal("2400000"), Decimal("4300000")),
            ("DXB", "ABV", "EK", 420, Decimal("650000"), Decimal("1800000"), Decimal("3200000")),
            ("DXB", "LOS", "EK", 420, Decimal("620000"), Decimal("1750000"), Decimal("3100000")),
            ("ADD", "ABV", "ET", 240, Decimal("380000"), Decimal("1100000"), Decimal("0")),
        ]

        # Flight schedules (hour of day)
        domestic_schedules = [6, 7, 8, 9, 10, 12, 14, 16, 18, 20]
        international_schedules = [1, 7, 10, 14, 22, 23]

        now = timezone.now()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        created_count = 0
        flight_counter = {}  # Track flight numbers per airline

        for day in range(days):
            current_date = start_date + timedelta(days=day)

            # Create domestic flights
            for route in domestic_routes:
                origin_code, dest_code, airline_code, duration, economy, business, first = route

                try:
                    origin = Airport.objects.get(code=origin_code)
                    destination = Airport.objects.get(code=dest_code)
                    airline = Airline.objects.get(code=airline_code)
                    aircraft = Aircraft.objects.filter(airline=airline, is_active=True).first()

                    if not aircraft:
                        continue

                    # Create 2-3 flights per route per day
                    num_flights = random.randint(2, 3)
                    selected_times = random.sample(domestic_schedules, min(num_flights, len(domestic_schedules)))

                    for hour in selected_times:
                        # Generate flight number
                        if airline_code not in flight_counter:
                            flight_counter[airline_code] = 100
                        flight_counter[airline_code] += 1
                        flight_number = f"{airline_code}{flight_counter[airline_code]}"

                        departure_time = current_date.replace(hour=hour, minute=random.choice([0, 15, 30, 45]))
                        arrival_time = departure_time + timedelta(minutes=duration)

                        flight, created = Flight.objects.get_or_create(
                            flight_number=flight_number,
                            scheduled_departure=departure_time,
                            defaults={
                                "airline": airline,
                                "aircraft": aircraft,
                                "origin": origin,
                                "destination": destination,
                                "scheduled_arrival": arrival_time,
                                "economy_price": economy,
                                "business_price": business if business > 0 else economy * 3,
                                "first_class_price": first if first > 0 else economy * 6,
                                "available_economy_seats": aircraft.economy_class_seats,
                                "available_business_seats": aircraft.business_class_seats,
                                "available_first_class_seats": aircraft.first_class_seats,
                                "is_international": False,
                                "meal_service": duration > 60,
                                "wifi_available": random.choice([True, False]),
                            },
                        )
                        if created:
                            created_count += 1

                except (Airport.DoesNotExist, Airline.DoesNotExist):
                    continue

            # Create international flights (fewer per day)
            if day % 2 == 0:  # Every other day for international
                for route in international_routes:
                    origin_code, dest_code, airline_code, duration, economy, business, first = route

                    try:
                        origin = Airport.objects.get(code=origin_code)
                        destination = Airport.objects.get(code=dest_code)
                        airline = Airline.objects.get(code=airline_code)
                        aircraft = Aircraft.objects.filter(airline=airline, is_active=True).first()

                        if not aircraft:
                            continue

                        # 1-2 flights per international route
                        num_flights = random.randint(1, 2)
                        selected_times = random.sample(international_schedules, min(num_flights, len(international_schedules)))

                        for hour in selected_times:
                            if airline_code not in flight_counter:
                                flight_counter[airline_code] = 100
                            flight_counter[airline_code] += 1
                            flight_number = f"{airline_code}{flight_counter[airline_code]}"

                            departure_time = current_date.replace(hour=hour, minute=random.choice([0, 30]))
                            arrival_time = departure_time + timedelta(minutes=duration)

                            flight, created = Flight.objects.get_or_create(
                                flight_number=flight_number,
                                scheduled_departure=departure_time,
                                defaults={
                                    "airline": airline,
                                    "aircraft": aircraft,
                                    "origin": origin,
                                    "destination": destination,
                                    "scheduled_arrival": arrival_time,
                                    "economy_price": economy,
                                    "business_price": business,
                                    "first_class_price": first if first > 0 else business * 2,
                                    "available_economy_seats": aircraft.economy_class_seats,
                                    "available_business_seats": aircraft.business_class_seats,
                                    "available_first_class_seats": aircraft.first_class_seats,
                                    "is_international": True,
                                    "meal_service": True,
                                    "wifi_available": True,
                                },
                            )
                            if created:
                                created_count += 1

                    except (Airport.DoesNotExist, Airline.DoesNotExist):
                        continue

        self.stdout.write(f"  Created {created_count} flights")
