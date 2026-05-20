#!/usr/bin/env python
"""
Simple test script to verify notification system
Run this to test if emails and SMS are being sent properly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
django.setup()

from django.contrib.auth.models import User
from vehicle_recognition.models import Vehicle, ViolationType, Challan
from vehicle_recognition.utils import NotificationService
from django.utils import timezone

def test_notification_system():
    """Test the notification system with sample data"""
    
    print("🚗 Testing Vehicle Recognition System - Notifications")
    print("=" * 60)
    
    # Get test credentials from user
    test_email = input("Enter your email address for testing: ").strip()
    test_phone = input("Enter your phone number (+1234567890): ").strip()
    
    if not test_email or not test_phone:
        print("❌ Email and phone number are required for testing")
        return
    
    print(f"\n📧 Test Email: {test_email}")
    print(f"📱 Test Phone: {test_phone}")
    
    try:
        # Create test user
        user, _ = User.objects.get_or_create(
            username='test_admin',
            defaults={'email': 'admin@test.com', 'is_staff': True}
        )
        
        # Create test vehicle
        vehicle, created = Vehicle.objects.get_or_create(
            number_plate='TEST001',
            defaults={
                'owner_name': 'Test Owner',
                'owner_email': test_email,
                'owner_phone': test_phone,
                'vehicle_type': 'Car'
            }
        )
        
        if created:
            print(f"✅ Created test vehicle: {vehicle.number_plate}")
        else:
            print(f"ℹ️ Using existing vehicle: {vehicle.number_plate}")
        
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
            challan_id='TEST001',
            vehicle=vehicle,
            violation_type=violation_type,
            penalty_amount=1000.00,
            created_by=user,
            violation_date=timezone.now(),
            location='Test Location',
            description='This is a test challan for notification testing'
        )
        
        print(f"\n✅ Created test challan: {challan.challan_id}")
        print(f"Vehicle: {vehicle.number_plate}")
        print(f"Owner: {vehicle.owner_name}")
        print(f"Violation: {violation_type.name}")
        print(f"Penalty: ₹{challan.penalty_amount}")
        
        # Test email notification
        print(f"\n📧 Testing email notification...")
        email_result = NotificationService.send_email_notification(challan)
        
        if email_result:
            print("✅ Email notification sent successfully!")
        else:
            print("❌ Email notification failed!")
            print("   Check your .env file configuration")
        
        # Test SMS notification
        print(f"\n📱 Testing SMS notification...")
        sms_result = NotificationService.send_sms_notification(challan)
        
        if sms_result:
            print("✅ SMS notification sent successfully!")
        else:
            print("⚠️ SMS notification failed (check console for details)")
            print("   Configure SMS service in .env file for actual SMS")
        
        # Clean up test data
        challan.delete()
        
        print(f"\n📊 Test Results Summary:")
        print(f"Email: {'✅ Success' if email_result else '❌ Failed'}")
        print(f"SMS: {'✅ Success' if sms_result else '❌ Failed'}")
        
        if email_result and sms_result:
            print(f"\n🎉 All notifications working properly!")
        else:
            print(f"\n⚠️ Some notifications failed. Check configuration.")
        
        print(f"\n📋 Next Steps:")
        print(f"1. Check your email inbox: {test_email}")
        print(f"2. Check your phone for SMS: {test_phone}")
        print(f"3. If not received, check .env file configuration")
        print(f"4. Run 'python manage.py test_notifications' for detailed testing")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notification_system() 