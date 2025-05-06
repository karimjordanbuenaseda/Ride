from django.core.management.base import BaseCommand
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
from core.models import User, Ride, RideEvent
import random
import datetime
import json

class Command(BaseCommand):
    help = 'Initializes application with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing data before initializing new data',
        )

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data initialization...'))
        
        # Clean existing data if needed
        if kwargs.get('clean', False):
            self.clean_data()
        
        # Create Django users and custom users
        self.create_users()
        
        # Create rides
        self.create_rides()
        
        # Create ride events
        self.create_ride_events()
        
        self.stdout.write(self.style.SUCCESS('Data initialization completed successfully!'))
    
    def clean_data(self):
        """Clean existing data"""
        self.stdout.write('Cleaning existing data...')
        RideEvent.objects.all().delete()
        Ride.objects.all().delete()
        User.objects.all().delete()
        DjangoUser.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('Existing data cleaned.'))
    
    def create_users(self):
        """Create sample users with different roles"""
        self.stdout.write('Creating users...')
        
        # Admin user
        admin_user = DjangoUser.objects.create_user(
            username='admin', 
            email='admin@example.com', 
            password='admin123',
            is_staff=True
        )
        
        admin_custom = User.objects.create(
            id_user=admin_user.id,
            role='admin',
            first_name='Admin',
            last_name='User',
            email='admin@example.com',
            phone_number='1234567890',
            created_by=admin_user,
            modified_by=admin_user
        )
        
        # Create 5 drivers
        drivers = []
        for i in range(1, 6):
            driver_user = DjangoUser.objects.create_user(
                username=f'driver{i}',
                email=f'driver{i}@example.com',
                password='driver123'
            )
            
            driver_custom = User.objects.create(
                id_user=driver_user.id,
                role='driver',
                first_name=f'Driver{i}',
                last_name='User',
                email=f'driver{i}@example.com',
                phone_number=f'2{i}34567890',
                created_by=admin_user,
                modified_by=admin_user
            )
            drivers.append(driver_custom)
        
        # Create 10 riders
        riders = []
        for i in range(1, 11):
            rider_user = DjangoUser.objects.create_user(
                username=f'rider{i}',
                email=f'rider{i}@example.com',
                password='rider123'
            )
            
            rider_custom = User.objects.create(
                id_user=rider_user.id,
                role='rider',
                first_name=f'Rider{i}',
                last_name='User',
                email=f'rider{i}@example.com',
                phone_number=f'3{i}34567890',
                created_by=admin_user,
                modified_by=admin_user
            )
            riders.append(rider_custom)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(drivers)} drivers and {len(riders)} riders.'))
    
    def create_rides(self):
        """Create sample rides with various statuses"""
        self.stdout.write('Creating rides...')
        
        # Get users by role
        admin_user = DjangoUser.objects.get(username='admin')
        drivers = User.objects.filter(role='driver')
        riders = User.objects.filter(role='rider')
        
        # Status options with weights for random selection
        statuses = ['pending', 'en-route', 'pickup', 'dropoff', 'completed', 'cancelled']
        status_weights = [0.1, 0.2, 0.1, 0.1, 0.4, 0.1]  # More completed rides
        
        # Create 30 rides with different statuses
        now = timezone.now()
        rides = []
        
        for i in range(30):
            # Random driver and rider
            driver = random.choice(drivers)
            rider = random.choice(riders)
            
            # Random status
            status = random.choices(statuses, weights=status_weights)[0]
            
            # Random pickup time within +/- 3 days from now
            pickup_time = now + datetime.timedelta(
                days=random.randint(-3, 3),
                hours=random.randint(-12, 12),
                minutes=random.randint(-30, 30)
            )
            
            # Random coordinates in a reasonable range
            # These are roughly in the US
            pickup_lat = random.uniform(37.0, 38.0)
            pickup_long = random.uniform(-122.5, -121.5)
            dropoff_lat = random.uniform(37.0, 38.0)
            dropoff_long = random.uniform(-122.5, -121.5)
            
            ride = Ride.objects.create(
                status=status,
                id_rider=rider,
                id_driver=driver,
                pickup_latitude=pickup_lat,
                pickup_longitude=pickup_long,
                dropoff_latitude=dropoff_lat,
                dropoff_longitude=dropoff_long,
                pickup_time=pickup_time,
                created_by=admin_user,
                modified_by=admin_user
            )
            rides.append(ride)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(rides)} rides.'))
    
    def create_ride_events(self):
        """Create sample ride events for the rides"""
        self.stdout.write('Creating ride events...')
        
        admin_user = DjangoUser.objects.get(username='admin')
        rides = Ride.objects.all()
        event_descriptions = [
            "Ride requested",
            "Driver assigned",
            "Driver en-route to pickup",
            "Driver arrived at pickup location",
            "Ride started",
            "Approaching destination",
            "Ride completed",
            "Payment processed",
            "Ride cancelled by rider",
            "Ride cancelled by driver",
            "Route changed",
            "Unexpected delay",
            "Traffic encountered"
        ]
        
        events = []
        # Create 2-5 events for each ride
        for ride in rides:
            num_events = random.randint(2, 5)
            
            # For completed rides, ensure they have the full flow
            if ride.status == 'completed':
                ride_events = event_descriptions[:7]  # Get the complete flow events
                random.shuffle(ride_events)  # Shuffle to get a random subset if needed
                ride_events = ride_events[:num_events]  # Take only the number we need
            else:
                ride_events = random.sample(event_descriptions, num_events)
            
            for event_desc in ride_events:
                event = RideEvent.objects.create(
                    id_ride=ride,
                    description=event_desc,
                    created_by=admin_user,
                    modified_by=admin_user
                )
                events.append(event)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(events)} ride events.'))