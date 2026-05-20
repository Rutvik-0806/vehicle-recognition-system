#!/usr/bin/env python
"""
Setup script for email and SMS notifications
This script will help you configure your .env file properly
"""

import os
import re

def setup_email_config():
    """Setup email configuration"""
    print("📧 Email Configuration Setup")
    print("=" * 40)
    
    print("\n1. Gmail Setup Instructions:")
    print("   - Go to https://myaccount.google.com/")
    print("   - Click on 'Security'")
    print("   - Enable '2-Step Verification'")
    print("   - Go to 'App passwords'")
    print("   - Select 'Mail' and generate password")
    print("   - Copy the 16-character password")
    
    print("\n2. Enter your Gmail details:")
    email = input("   Gmail address: ").strip()
    password = input("   App password (16 characters): ").strip()
    
    if email and password:
        # Update .env file
        update_env_file('EMAIL_HOST_USER', email)
        update_env_file('EMAIL_HOST_PASSWORD', password)
        print(f"✅ Email configured: {email}")
        return True
    else:
        print("❌ Email configuration incomplete")
        return False

def setup_sms_config():
    """Setup SMS configuration"""
    print("\n📱 SMS Configuration Setup")
    print("=" * 40)
    
    print("\nChoose SMS service:")
    print("1. Twilio (International)")
    print("2. Fast2SMS (India)")
    print("3. Skip SMS setup")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        return setup_twilio()
    elif choice == '2':
        return setup_fast2sms()
    else:
        print("⏭️ Skipping SMS setup")
        return False

def setup_twilio():
    """Setup Twilio SMS"""
    print("\nTwilio Setup Instructions:")
    print("1. Go to https://www.twilio.com/")
    print("2. Sign up for free account")
    print("3. Get Account SID and Auth Token from dashboard")
    print("4. Get a Twilio phone number")
    
    print("\nEnter Twilio details:")
    account_sid = input("   Account SID: ").strip()
    auth_token = input("   Auth Token: ").strip()
    phone_number = input("   Twilio phone number (+1234567890): ").strip()
    
    if account_sid and auth_token and phone_number:
        update_env_file('SMS_API_KEY', account_sid)
        update_env_file('SMS_API_SECRET', auth_token)
        update_env_file('SMS_FROM_NUMBER', phone_number)
        print(f"✅ Twilio configured: {phone_number}")
        return True
    else:
        print("❌ Twilio configuration incomplete")
        return False

def setup_fast2sms():
    """Setup Fast2SMS"""
    print("\nFast2SMS Setup Instructions:")
    print("1. Go to https://www.fast2sms.com/")
    print("2. Sign up for account")
    print("3. Get API key from dashboard")
    
    print("\nEnter Fast2SMS details:")
    api_key = input("   API Key: ").strip()
    
    if api_key:
        update_env_file('FAST2SMS_API_KEY', api_key)
        print(f"✅ Fast2SMS configured with API key")
        return True
    else:
        print("❌ Fast2SMS configuration incomplete")
        return False

def update_env_file(key, value):
    """Update .env file with new values"""
    env_file = '.env'
    
    # Read existing .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Find and update the key
    key_found = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            key_found = True
            break
    
    # Add key if not found
    if not key_found:
        lines.append(f'{key}={value}\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(lines)

def test_configuration():
    """Test the configuration"""
    print("\n🧪 Testing Configuration")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    # Read .env file
    with open('.env', 'r') as f:
        content = f.read()
    
    # Check email configuration
    email_user = re.search(r'EMAIL_HOST_USER=(.+)', content)
    email_pass = re.search(r'EMAIL_HOST_PASSWORD=(.+)', content)
    
    if email_user and email_pass:
        email = email_user.group(1).strip()
        if email not in ['your-email@gmail.com', 'your-actual-email@gmail.com']:
            print(f"✅ Email configured: {email}")
        else:
            print("❌ Email not configured properly")
    else:
        print("❌ Email configuration missing")
    
    # Check SMS configuration
    sms_key = re.search(r'SMS_API_KEY=(.+)', content)
    fast2sms_key = re.search(r'FAST2SMS_API_KEY=(.+)', content)
    
    if sms_key and sms_key.group(1).strip() not in ['your-twilio-account-sid', 'your-sms-api-key']:
        print("✅ Twilio SMS configured")
    elif fast2sms_key and fast2sms_key.group(1).strip() not in ['your-fast2sms-api-key', 'your-sms-api-key']:
        print("✅ Fast2SMS configured")
    else:
        print("❌ SMS not configured")
    
    return True

def main():
    """Main setup function"""
    print("🚗 Vehicle Recognition System - Notification Setup")
    print("=" * 60)
    
    print("\nThis script will help you configure email and SMS notifications.")
    print("Follow the instructions to set up your credentials.")
    
    # Setup email
    email_configured = setup_email_config()
    
    # Setup SMS
    sms_configured = setup_sms_config()
    
    # Test configuration
    test_configuration()
    
    print("\n📋 Next Steps:")
    if email_configured:
        print("1. ✅ Email configured - test with: python test_notification_system.py")
    else:
        print("1. ❌ Email not configured - run this script again")
    
    if sms_configured:
        print("2. ✅ SMS configured - test with: python test_notification_system.py")
    else:
        print("2. ❌ SMS not configured - run this script again")
    
    print("3. Start server: python manage.py runserver")
    print("4. Create a challan to test notifications")
    
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    main() 