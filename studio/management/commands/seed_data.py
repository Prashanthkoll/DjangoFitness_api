from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from studio.models import FitnessClass

class Command(BaseCommand):
    help = 'Seed database with sample fitness classes'
    
    def handle(self, *args, **options):
        # Clear existing classes
        FitnessClass.objects.all().delete()
        
        # Create sample classes
        base_time = timezone.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        classes_data = [
            {
                'name': 'YOGA',
                'instructor': 'Priya Sharma',
                'datetime': base_time + timedelta(days=1),
                'total_slots': 15,
                'available_slots': 15
            },
            {
                'name': 'ZUMBA',
                'instructor': 'Rahul Gupta',
                'datetime': base_time + timedelta(days=1, hours=2),
                'total_slots': 20,
                'available_slots': 20
            },
            {
                'name': 'HIIT',
                'instructor': 'Anjali Verma',
                'datetime': base_time + timedelta(days=2),
                'total_slots': 12,
                'available_slots': 12
            },
            {
                'name': 'YOGA',
                'instructor': 'Suresh Kumar',
                'datetime': base_time + timedelta(days=3),
                'total_slots': 18,
                'available_slots': 18
            },
            {
                'name': 'ZUMBA',
                'instructor': 'Meera Patel',
                'datetime': base_time + timedelta(days=4),
                'total_slots': 25,
                'available_slots': 25
            },
            {
                'name': 'HIIT',
                'instructor': 'Karan Singh',
                'datetime': base_time + timedelta(days=5),
                'total_slots': 15,
                'available_slots': 15
            }
        ]
        
        for class_data in classes_data:
            FitnessClass.objects.create(**class_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(classes_data)} fitness classes')
        )