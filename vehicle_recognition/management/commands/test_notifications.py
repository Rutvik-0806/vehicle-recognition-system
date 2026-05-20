from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from vehicle_recognition.models import Vehicle, ViolationType, Challan
from vehicle_recognition.utils import NotificationService


class Command(BaseCommand):
    help = 'Test email and SMS notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Test email address',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Test phone number',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚗 Testing Vehicle Recognition System Notifications')
        )
        
        # Get test credentials
        test_email = options['email'] or input("Enter test email address: ").strip()
        test_phone = options['phone'] or input("Enter test phone number (+1234567890): ").strip()
        
        if not test_email or not test_phone:
            self.stdout.write(
                self.style.ERROR('❌ Email and phone number are required for testing')
            )
            return
        
        try:
            # Create test user
            user, _ = User.objects.get_or_create(
                username='test_user',
                defaults={'email': 'test@example.com'}
            )
            
            # Create test vehicle
            vehicle, _ = Vehicle.objects.get_or_create(
                number_plate='TEST789',
                defaults={
                    'owner_name': 'Test Owner',
                    'owner_email': test_email,
                    'owner_phone': test_phone,
                    'vehicle_type': 'Car'
                }
            )
            
            # Create test violation type
            violation_type, _ = ViolationType.objects.get_or_create(
                name='Test Violation',
                defaults={
                    'description': 'Test violation for notification testing',
                    'penalty_amount': 1000.00
                }
            )
            
            # Create test challan
            challan = Challan.objects.create(
                challan_id='TEST789',
                vehicle=vehicle,
                violation_type=violation_type,
                penalty_amount=1000.00,
                created_by=user,
                violation_date=timezone.now(),
                location='Test Location',
                description='This is a test challan for notification testing'
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Created test challan: {challan.challan_id}')
            )
            self.stdout.write(f'Vehicle: {vehicle.number_plate}')
            self.stdout.write(f'Owner: {vehicle.owner_name}')
            self.stdout.write(f'Email: {vehicle.owner_email}')
            self.stdout.write(f'Phone: {vehicle.owner_phone}')
            
            # Test email notification
            self.stdout.write('\n📧 Testing email notification...')
            email_result = NotificationService.send_email_notification(challan)
            
            if email_result:
                self.stdout.write(
                    self.style.SUCCESS('✅ Email notification sent successfully!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Email notification failed!')
                )
            
            # Test SMS notification
            self.stdout.write('\n📱 Testing SMS notification...')
            sms_result = NotificationService.send_sms_notification(challan)
            
            if sms_result:
                self.stdout.write(
                    self.style.SUCCESS('✅ SMS notification sent successfully!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ SMS notification failed (check console for details)')
                )
            
            # Clean up test data
            challan.delete()
            
            self.stdout.write('\n📋 Test Results Summary:')
            self.stdout.write(f'Email: {"✅ Success" if email_result else "❌ Failed"}')
            self.stdout.write(f'SMS: {"✅ Success" if sms_result else "❌ Failed"}')
            
            if email_result and sms_result:
                self.stdout.write(
                    self.style.SUCCESS('\n🎉 All notifications working properly!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('\n⚠️ Some notifications failed. Check EMAIL_SMS_SETUP.md for configuration help.')
                )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test failed with error: {e}')
            ) 