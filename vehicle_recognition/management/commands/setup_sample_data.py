from django.core.management.base import BaseCommand
from vehicle_recognition.utils import create_sample_data


class Command(BaseCommand):
    help = 'Setup sample data for the vehicle recognition system'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Setting up sample data...')
        
        try:
            create_sample_data()
            self.stdout.write(
                self.style.SUCCESS('✅ Sample data created successfully!')
            )
            self.stdout.write('📋 Created:')
            self.stdout.write('   - 10 violation types with different penalties')
            self.stdout.write('   - 3 sample vehicles with complete information')
            self.stdout.write('\n🎯 You can now test the system with sample data.')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating sample data: {e}')
            ) 