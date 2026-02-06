"""
Management command to seed parking data for the NAIA Airport Management System.
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from parking.models import (
    ParkingZone, ParkingSpot, ParkingPricing, ParkingService,
    ParkingZoneType, VehicleType
)


class Command(BaseCommand):
    help = 'Seeds the database with parking zones, pricing, and services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing parking data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing parking data...')
            ParkingService.objects.all().delete()
            ParkingPricing.objects.all().delete()
            ParkingSpot.objects.all().delete()
            ParkingZone.objects.all().delete()

        self.create_parking_zones()
        self.create_parking_pricing()
        self.create_parking_services()
        self.create_sample_spots()

        self.stdout.write(self.style.SUCCESS('Successfully seeded parking data!'))

    def create_parking_zones(self):
        """Create parking zones."""
        self.stdout.write('Creating parking zones...')

        zones_data = [
            # Short-term parking
            {
                'name': 'Terminal A Short-Term',
                'code': 'STA',
                'zone_type': ParkingZoneType.SHORT_TERM,
                'description': 'Convenient short-term parking directly in front of Terminal A. Ideal for quick pickups and drop-offs.',
                'total_spots': 200,
                'available_spots': 185,
                'terminal': 'Domestic Terminal',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 50,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': False,
                'has_ev_charging': True,
            },
            {
                'name': 'Terminal B Short-Term',
                'code': 'STB',
                'zone_type': ParkingZoneType.SHORT_TERM,
                'description': 'Quick access parking for International Terminal B. Perfect for quick trips.',
                'total_spots': 150,
                'available_spots': 120,
                'terminal': 'International Terminal',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 75,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': False,
                'has_ev_charging': True,
            },
            # Long-term parking
            {
                'name': 'Economy Lot A',
                'code': 'ELA',
                'zone_type': ParkingZoneType.LONG_TERM,
                'description': 'Affordable long-term parking with free shuttle service to all terminals. Best rates for extended stays.',
                'total_spots': 500,
                'available_spots': 423,
                'terminal': 'All Terminals',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 500,
                'is_covered': False,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': True,
            },
            {
                'name': 'Economy Lot B',
                'code': 'ELB',
                'zone_type': ParkingZoneType.LONG_TERM,
                'description': 'Extended long-term parking with excellent security and regular shuttle service.',
                'total_spots': 400,
                'available_spots': 356,
                'terminal': 'All Terminals',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 600,
                'is_covered': False,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': True,
            },
            # Premium parking
            {
                'name': 'VIP Executive Parking',
                'code': 'VIP',
                'zone_type': ParkingZoneType.PREMIUM,
                'description': 'Premium covered parking with valet service, closest to VIP lounge. Reserved for executive travelers.',
                'total_spots': 50,
                'available_spots': 38,
                'terminal': 'VIP Terminal',
                'floor_level': 'Level 1',
                'distance_to_terminal': 20,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': False,
                'has_ev_charging': True,
                'has_car_wash': True,
                'has_valet': True,
            },
            {
                'name': 'Premium Covered Parking',
                'code': 'PCP',
                'zone_type': ParkingZoneType.PREMIUM,
                'description': 'Premium multi-level covered parking structure with direct terminal access.',
                'total_spots': 300,
                'available_spots': 245,
                'terminal': 'All Terminals',
                'floor_level': 'Multi-Level',
                'distance_to_terminal': 100,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': False,
                'has_ev_charging': True,
                'has_car_wash': True,
            },
            # Valet parking
            {
                'name': 'Valet Service',
                'code': 'VAL',
                'zone_type': ParkingZoneType.VALET,
                'description': 'Full valet service - drop your car at the terminal entrance and we take care of the rest.',
                'total_spots': 75,
                'available_spots': 52,
                'terminal': 'All Terminals',
                'floor_level': 'N/A',
                'distance_to_terminal': 0,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
                'has_valet': True,
                'has_car_wash': True,
            },
            # Economy parking
            {
                'name': 'Budget Parking',
                'code': 'BUD',
                'zone_type': ParkingZoneType.ECONOMY,
                'description': 'Our most affordable parking option with regular shuttle service. Great value for travelers on a budget.',
                'total_spots': 600,
                'available_spots': 512,
                'terminal': 'All Terminals',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 800,
                'is_covered': False,
                'has_cctv': True,
                'has_security': True,
                'has_shuttle': True,
            },
            # EV Parking
            {
                'name': 'Electric Vehicle Parking',
                'code': 'EVP',
                'zone_type': ParkingZoneType.ELECTRIC,
                'description': 'Dedicated parking for electric vehicles with complimentary charging stations.',
                'total_spots': 40,
                'available_spots': 28,
                'terminal': 'Domestic Terminal',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 150,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
                'has_ev_charging': True,
            },
            # Motorcycle parking
            {
                'name': 'Motorcycle Parking',
                'code': 'MCP',
                'zone_type': ParkingZoneType.MOTORCYCLE,
                'description': 'Secure covered parking for motorcycles near terminal entrance.',
                'total_spots': 30,
                'available_spots': 22,
                'terminal': 'Domestic Terminal',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 80,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
            },
            # Accessible parking
            {
                'name': 'Accessible Parking',
                'code': 'ACP',
                'zone_type': ParkingZoneType.DISABLED,
                'description': 'Accessible parking spaces closest to terminal entrances for passengers with disabilities.',
                'total_spots': 50,
                'available_spots': 45,
                'terminal': 'All Terminals',
                'floor_level': 'Ground Level',
                'distance_to_terminal': 30,
                'is_covered': True,
                'has_cctv': True,
                'has_security': True,
            },
        ]

        for zone_data in zones_data:
            ParkingZone.objects.update_or_create(
                code=zone_data['code'],
                defaults=zone_data
            )
            self.stdout.write(f"  Created/Updated zone: {zone_data['name']}")

    def create_parking_pricing(self):
        """Create pricing for parking zones."""
        self.stdout.write('Creating parking pricing...')

        # Pricing structure (in Naira)
        pricing_config = {
            # Short-term (expensive hourly, same daily)
            'STA': {'hourly': 500, 'daily': 5000, 'weekly': 25000},
            'STB': {'hourly': 600, 'daily': 6000, 'weekly': 30000},
            # Long-term (cheaper daily/weekly)
            'ELA': {'hourly': 200, 'daily': 1500, 'weekly': 8000, 'monthly': 25000},
            'ELB': {'hourly': 200, 'daily': 1500, 'weekly': 8000, 'monthly': 25000},
            # Premium (higher rates)
            'VIP': {'hourly': 1500, 'daily': 15000, 'weekly': 80000},
            'PCP': {'hourly': 800, 'daily': 8000, 'weekly': 45000},
            # Valet (highest rates)
            'VAL': {'hourly': 2000, 'daily': 20000, 'weekly': 100000},
            # Economy (lowest rates)
            'BUD': {'hourly': 150, 'daily': 1000, 'weekly': 5000, 'monthly': 15000},
            # EV (moderate + free charging benefit)
            'EVP': {'hourly': 400, 'daily': 3500, 'weekly': 18000},
            # Motorcycle (low rates)
            'MCP': {'hourly': 100, 'daily': 500, 'weekly': 2500, 'monthly': 8000},
            # Accessible (same as short-term, often free in reality)
            'ACP': {'hourly': 300, 'daily': 3000, 'weekly': 15000},
        }

        # Vehicle type multipliers
        vehicle_multipliers = {
            VehicleType.CAR: Decimal('1.0'),
            VehicleType.SUV: Decimal('1.2'),
            VehicleType.VAN: Decimal('1.3'),
            VehicleType.TRUCK: Decimal('1.5'),
            VehicleType.MOTORCYCLE: Decimal('0.5'),
            VehicleType.ELECTRIC: Decimal('1.0'),
        }

        zones = ParkingZone.objects.all()

        for zone in zones:
            if zone.code not in pricing_config:
                continue

            config = pricing_config[zone.code]

            # Create pricing for each vehicle type
            for vehicle_type, multiplier in vehicle_multipliers.items():
                # Skip motorcycle multiplier for motorcycle-only zones
                if zone.zone_type == ParkingZoneType.MOTORCYCLE and vehicle_type != VehicleType.MOTORCYCLE:
                    continue
                # Skip motorcycle type for non-motorcycle zones (except for general zones)
                if zone.zone_type != ParkingZoneType.MOTORCYCLE and vehicle_type == VehicleType.MOTORCYCLE:
                    continue

                pricing_data = {
                    'zone': zone,
                    'vehicle_type': vehicle_type,
                    'hourly_rate': Decimal(str(config['hourly'])) * multiplier,
                    'daily_rate': Decimal(str(config['daily'])) * multiplier,
                    'weekly_rate': Decimal(str(config.get('weekly', 0))) * multiplier if config.get('weekly') else None,
                    'monthly_rate': Decimal(str(config.get('monthly', 0))) * multiplier if config.get('monthly') else None,
                    'grace_period_minutes': 15,
                    'online_booking_discount': Decimal('10.00'),
                    'loyalty_discount': Decimal('5.00'),
                }

                ParkingPricing.objects.update_or_create(
                    zone=zone,
                    vehicle_type=vehicle_type,
                    defaults=pricing_data
                )

        self.stdout.write(f"  Created pricing for {zones.count()} zones")

    def create_parking_services(self):
        """Create additional parking services."""
        self.stdout.write('Creating parking services...')

        services_data = [
            {
                'name': 'Basic Car Wash',
                'code': 'WASH_BASIC',
                'description': 'Exterior wash including windows, wheels, and body.',
                'price': Decimal('3000.00'),
                'duration_minutes': 30,
            },
            {
                'name': 'Premium Car Wash',
                'code': 'WASH_PREMIUM',
                'description': 'Full car wash including exterior wash, interior vacuum, and dashboard wipe.',
                'price': Decimal('5000.00'),
                'duration_minutes': 45,
            },
            {
                'name': 'Deluxe Car Detailing',
                'code': 'DETAIL_DELUXE',
                'description': 'Complete interior and exterior detailing with wax, polish, and tire shine.',
                'price': Decimal('15000.00'),
                'duration_minutes': 120,
            },
            {
                'name': 'Interior Cleaning Only',
                'code': 'CLEAN_INTERIOR',
                'description': 'Thorough interior vacuum and wipe down of all surfaces.',
                'price': Decimal('2500.00'),
                'duration_minutes': 30,
            },
            {
                'name': 'EV Charging (Fast)',
                'code': 'EV_FAST',
                'description': 'Fast DC charging for electric vehicles up to 80% in 30 minutes.',
                'price': Decimal('2000.00'),
                'duration_minutes': 30,
            },
            {
                'name': 'EV Charging (Standard)',
                'code': 'EV_STANDARD',
                'description': 'Standard AC charging for electric vehicles (free with EV parking zone).',
                'price': Decimal('0.00'),
                'duration_minutes': 0,
            },
            {
                'name': 'Valet Service',
                'code': 'VALET',
                'description': 'Personal valet to park and retrieve your vehicle.',
                'price': Decimal('5000.00'),
                'duration_minutes': 0,
            },
            {
                'name': 'Jump Start Service',
                'code': 'JUMP_START',
                'description': 'Battery jump start service if your car won\'t start.',
                'price': Decimal('1500.00'),
                'duration_minutes': 15,
            },
            {
                'name': 'Tire Pressure Check',
                'code': 'TIRE_CHECK',
                'description': 'Check and adjust tire pressure to manufacturer specifications.',
                'price': Decimal('500.00'),
                'duration_minutes': 10,
            },
            {
                'name': 'Luggage Assistance',
                'code': 'LUGGAGE',
                'description': 'Porter service to help with luggage from car to terminal.',
                'price': Decimal('1000.00'),
                'duration_minutes': 15,
            },
        ]

        premium_zones = ParkingZone.objects.filter(zone_type__in=[
            ParkingZoneType.PREMIUM, ParkingZoneType.VALET
        ])
        ev_zones = ParkingZone.objects.filter(zone_type=ParkingZoneType.ELECTRIC)
        all_zones = ParkingZone.objects.all()

        for service_data in services_data:
            service, created = ParkingService.objects.update_or_create(
                code=service_data['code'],
                defaults=service_data
            )

            # Assign services to appropriate zones
            if 'WASH' in service_data['code'] or 'DETAIL' in service_data['code'] or 'CLEAN' in service_data['code']:
                service.available_zones.set(premium_zones)
            elif 'EV' in service_data['code']:
                service.available_zones.set(ev_zones)
            elif service_data['code'] == 'VALET':
                service.available_zones.set(ParkingZone.objects.filter(zone_type=ParkingZoneType.VALET))
            else:
                service.available_zones.set(all_zones)

            self.stdout.write(f"  Created/Updated service: {service_data['name']}")

    def create_sample_spots(self):
        """Create sample parking spots for a few zones."""
        self.stdout.write('Creating sample parking spots...')

        # Only create spots for premium zones to demonstrate the feature
        premium_zones = ParkingZone.objects.filter(zone_type__in=[
            ParkingZoneType.PREMIUM, ParkingZoneType.VALET
        ])[:2]

        for zone in premium_zones:
            # Skip if spots already exist
            if zone.spots.exists():
                continue

            # Create sample spots
            for i in range(1, min(zone.total_spots, 21)):  # Up to 20 spots per zone
                spot_number = f"{zone.code}-{i:03d}"
                ParkingSpot.objects.create(
                    zone=zone,
                    spot_number=spot_number,
                    is_covered=zone.is_covered,
                    is_accessible=(i <= 2),  # First 2 spots are accessible
                    is_ev_charging=(i % 5 == 0),  # Every 5th spot has EV charging
                    vehicle_type=VehicleType.CAR,
                    is_occupied=(i % 4 == 0),  # Every 4th spot is occupied
                )

            self.stdout.write(f"  Created spots for zone: {zone.name}")
