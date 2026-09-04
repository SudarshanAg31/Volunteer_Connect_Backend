from django.core.management.base import BaseCommand
from api.models import User, Opportunity, Application
from datetime import date

class Command(BaseCommand):
    help = 'Seed the database with sample data'
    
    def handle(self, *args, **kwargs):
        # Create admin user
        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'name': 'Admin User',
                'phone': '9999999999',
                'password': 'admin123',
                'role': 'admin'
            }
        )
        
        # Create volunteer users
        volunteer1, created = User.objects.get_or_create(
            email='volunteer@example.com',
            defaults={
                'name': 'John Volunteer',
                'phone': '8888888888',
                'password': 'vol123',
                'role': 'volunteer'
            }
        )
        
        volunteer2, created = User.objects.get_or_create(
            email='priya@example.com',
            defaults={
                'name': 'Priya Singh',
                'phone': '7777777777',
                'password': 'priya123',
                'role': 'volunteer'
            }
        )
        
        # Sample opportunities
        opportunities_data = [
            {
                'title': 'Tree Plantation Drive',
                'description': 'Join us in planting trees in the local community to create a greener environment.',
                'ngo_name': 'Green Earth Foundation',
                'category': 'Environment',
                'location': 'Delhi',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'date': date(2026, 9, 15),
                'time': '09:00 AM - 01:00 PM',
                'volunteers_required': 20
            },
            {
                'title': 'Teaching Support Program',
                'description': 'Help underprivileged children with their studies and provide educational support.',
                'ngo_name': 'Helping Hands',
                'category': 'Education',
                'location': 'Noida',
                'latitude': 28.5355,
                'longitude': 77.3910,
                'date': date(2026, 9, 20),
                'time': '10:00 AM - 02:00 PM',
                'volunteers_required': 15
            },
            {
                'title': 'Food Distribution Drive',
                'description': 'Distribute food and essential supplies to families in need.',
                'ngo_name': 'Care Foundation',
                'category': 'Community',
                'location': 'Gurgaon',
                'latitude': 28.4595,
                'longitude': 77.0266,
                'date': date(2026, 9, 25),
                'time': '08:00 AM - 12:00 PM',
                'volunteers_required': 25
            },
            {
                'title': 'Animal Shelter Support',
                'description': 'Help care for animals at the local shelter - feeding, cleaning, and providing love.',
                'ngo_name': 'Paws Care',
                'category': 'Animal Welfare',
                'location': 'Delhi',
                'latitude': 28.7041,
                'longitude': 77.1025,
                'date': date(2026, 10, 5),
                'time': '09:30 AM - 01:30 PM',
                'volunteers_required': 10
            }
        ]
        
        for opp_data in opportunities_data:
            opportunity, created = Opportunity.objects.get_or_create(
                title=opp_data['title'],
                defaults=opp_data
            )
            
            # Create some sample applications
            if created:
                # Volunteer 1 applies to first opportunity
                if opp_data['title'] == 'Tree Plantation Drive':
                    Application.objects.get_or_create(
                        user=volunteer1,
                        opportunity=opportunity,
                        defaults={'status': 'Applied'}
                    )
                
                # Volunteer 2 applies to second opportunity
                if opp_data['title'] == 'Teaching Support Program':
                    Application.objects.get_or_create(
                        user=volunteer2,
                        opportunity=opportunity,
                        defaults={'status': 'Approved'}
                    )
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Created admin: admin@example.com / admin123'))
        self.stdout.write(self.style.SUCCESS(f'Created volunteer: volunteer@example.com / vol123'))