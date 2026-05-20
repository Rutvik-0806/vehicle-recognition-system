#!/usr/bin/env python
"""
Simple script to configure .env file with your credentials
"""

import os

def configure_env():
    """Configure .env file with your credentials"""
    
    print("🚗 Quick .env Configuration")
    print("=" * 40)
    
    # Your credentials from the setup
    email_user = "pqrx0339@gmail.com"
    email_password = "lirg ifkx zfib nlpn"
    
    # Create .env content with simpler SMS configuration
    env_content = f"""# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER={email_user}
EMAIL_HOST_PASSWORD={email_password}

# SMS Configuration (TextLocal - Simple)
SMS_API_KEY=your-textlocal-api-key
SMS_API_SECRET=your-textlocal-secret

# Fast2SMS Configuration (Alternative)
FAST2SMS_API_KEY=3ygeCFwvd4GaW8NfZbcmPJEDnI2zH9oLulj1QxXUOBRs0AYqMVi5BeV02molnT83aPHZjcKhqLO9fEMW

# Twilio Configuration (Optional)
SMS_FROM_NUMBER=+1234567890
"""
    
    # Write to .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file configured with your credentials!")
    print(f"📧 Email: {email_user}")
    print(f"📱 SMS: Multiple services configured")
    
    print("\n🧪 Testing configuration...")
    print("Run: python test_notification_system.py")
    
    return True

if __name__ == "__main__":
    configure_env() 