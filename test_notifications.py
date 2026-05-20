#!/usr/bin/env python
"""
Test script for email and SMS notifications
Run this script to test if your email and SMS configurations are working properly.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehicle_system.settings')
django.setup()

from django.conf import settings
from vehicle_recognition.models import Vehicle, ViolationType, Challan
from vehicle_recognition.utils import NotificationService
from django.contrib.auth.models import User
from django.utils import timezone

def test_email_configuration():
    """Test email configuration"""
    print("📧 Testing Email Configuration...")
    
    try:
        # Test basic email settings
        print(f"Email Host: {settings.EMAIL_HOST}")
        print(f"Email Port: {settings.EMAIL_PORT}")
        print(f"Email User: {settings.EMAIL_HOST_USER}")
        print(f"TLS Enabled: {settings.EMAIL_USE_TLS}")
        
        # Test sending a simple email
        from django.core.mail import send_mail
        
        test_email = "test@example.com"  # Replace with your test email
        subject = "Test Email from Vehicle Recognition System"
        message = "This is a test email to verify your email configuration is working properly."
        
        print(f"\nSending test email to: {test_email}")
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [test_email],
            fail_silently=False,
        )
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_sms_configuration():
    """Test SMS configuration"""
    print("\n📱 Testing SMS Configuration...")
    
    try:
        # Check SMS settings
        print(f"SMS API Key configured: {'Yes' if hasattr(settings, 'SMS_API_KEY') and settings.SMS_API_KEY != 'your-twilio-account-sid' else 'No'}")
        print(f"Fast2SMS API Key configured: {'Yes' if hasattr(settings, 'FAST2SMS_API_KEY') and settings.FAST2SMS_API_KEY != 'your-fast2sms-api-key' else 'No'}")
        
        # Test phone number
        test_phone = "+1234567890"  # Replace with your test phone number
        test_message = "Test SMS from Vehicle Recognition System"
        
        print(f"\nSending test SMS to: {test_phone}")
        
        # Create a dummy challan for testing
        user, _ = User.objects.get_or_create(username='test_user', defaults={'email': 'test@example.com'})
        vehicle, _ = Vehicle.objects.get_or_create(
            number_plate='TEST123',
            defaults={
                'owner_name': 'Test User',
                'owner_email': 'test@example.com',
                'owner_phone': test_phone,
                'vehicle_type': 'Car'
            }
        )
        violation_type, _ = ViolationType.objects.get_or_create(
            name='Test Violation',
            defaults={
                'description': 'Test violation for SMS testing',
                'penalty_amount': 100.00
            }
        )
        
        challan = Challan.objects.create(
            challan_id='TEST001',
            vehicle=vehicle,
            violation_type=violation_type,
            penalty_amount=100.00,
            created_by=user,
            violation_date=timezone.now()
        )
        
        # Test SMS sending
        result = NotificationService.send_sms_notification(challan)
        
        if result:
            print("✅ SMS test completed (check console for details)")
        else:
            print("❌ SMS test failed")
        
        # Clean up test data
        challan.delete()
        
        return result
        
    except Exception as e:
        print(f"❌ SMS test failed: {e}")
        return False

def test_notification_integration():
    """Test full notification integration"""
    print("\n🔧 Testing Full Notification Integration...")
    
    try:
        # Create test data
        user, _ = User.objects.get_or_create(username='test_user', defaults={'email': 'test@example.com'})
        
        # Create test vehicle with your email and phone
        test_email = input("Enter your email for testing: ").strip()
        test_phone = input("Enter your phone number for testing (+1234567890): ").strip()
        
        vehicle, _ = Vehicle.objects.get_or_create(
            number_plate='TEST456',
            defaults={
                'owner_name': 'Test Owner',
                'owner_email': test_email,
                'owner_phone': test_phone,
                'vehicle_type': 'Car'
            }
        )
        
        violation_type, _ = ViolationType.objects.get_or_create(
            name='Test Violation',
            defaults={
                'description': 'Test violation for notification testing',
                'penalty_amount': 500.00
            }
        )
        
        # Create test challan
        challan = Challan.objects.create(
            challan_id='TEST002',
            vehicle=vehicle,
            violation_type=violation_type,
            penalty_amount=500.00,
            created_by=user,
            violation_date=timezone.now(),
            location='Test Location',
            description='This is a test challan for notification testing'
        )
        
        print(f"\nCreated test challan: {challan.challan_id}")
        print(f"Vehicle: {vehicle.number_plate}")
        print(f"Owner: {vehicle.owner_name}")
        print(f"Email: {vehicle.owner_email}")
        print(f"Phone: {vehicle.owner_phone}")
        
        # Test email notification
        print("\n📧 Sending email notification...")
        email_result = NotificationService.send_email_notification(challan)
        
        # Test SMS notification
        print("\n📱 Sending SMS notification...")
        sms_result = NotificationService.send_sms_notification(challan)
        
        print(f"\n📊 Test Results:")
        print(f"Email: {'✅ Success' if email_result else '❌ Failed'}")
        print(f"SMS: {'✅ Success' if sms_result else '❌ Failed'}")
        
        # Clean up
        challan.delete()
        
        return email_result and sms_result
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚗 Vehicle Recognition System - Notification Test")
    print("=" * 50)
    
    # Test 1: Email Configuration
    email_ok = test_email_configuration()
    
    # Test 2: SMS Configuration
    sms_ok = test_sms_configuration()
    
    # Test 3: Full Integration (optional)
    if email_ok and sms_ok:
        print("\n" + "=" * 50)
        print("🎯 All basic tests passed! Testing full integration...")
        integration_ok = test_notification_integration()
        
        if integration_ok:
            print("\n🎉 All tests passed! Your notification system is working properly.")
        else:
            print("\n⚠️ Integration test failed. Check your configuration.")
    else:
        print("\n❌ Basic tests failed. Please fix configuration issues first.")
    
    print("\n📋 Next Steps:")
    print("1. Check your email inbox for test emails")
    print("2. Check your phone for test SMS messages")
    print("3. If tests failed, review the EMAIL_SMS_SETUP.md guide")
    print("4. Update your .env file with correct credentials")

if __name__ == "__main__":
    main() 