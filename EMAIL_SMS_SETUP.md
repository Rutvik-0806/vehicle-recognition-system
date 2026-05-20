# Email and SMS Notification Setup Guide

This guide will help you configure email and SMS notifications for the Vehicle Recognition System.

## 📧 Email Configuration

### Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
3. **Update .env file**:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-digit-app-password
   ```

### Other Email Providers

- **Outlook/Hotmail**: Use `smtp-mail.outlook.com` with port 587
- **Yahoo**: Use `smtp.mail.yahoo.com` with port 587
- **Custom SMTP**: Use your provider's SMTP settings

## 📱 SMS Configuration

### Option 1: Twilio (International)

1. **Sign up** at [Twilio.com](https://www.twilio.com)
2. **Get your credentials**:
   - Account SID
   - Auth Token
   - Twilio phone number
3. **Update .env file**:
   ```
   SMS_API_KEY=your-twilio-account-sid
   SMS_API_SECRET=your-twilio-auth-token
   SMS_FROM_NUMBER=+1234567890
   ```

### Option 2: Fast2SMS (India)

1. **Sign up** at [Fast2SMS.com](https://www.fast2sms.com)
2. **Get your API key** from the dashboard
3. **Update .env file**:
   ```
   FAST2SMS_API_KEY=your-fast2sms-api-key
   FAST2SMS_SENDER_ID=YOURID
   ```

### Option 3: Other SMS Services

You can integrate other SMS services by modifying the `send_sms_notification` method in `vehicle_recognition/utils.py`.

## 🚀 Installation Steps

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   - Copy `env_example.txt` to `.env`
   - Update the values as per your configuration

3. **Test the configuration**:
   ```bash
   python manage.py runserver
   ```

4. **Create a test challan** to verify notifications

## 🔧 Testing Notifications

### Test Email
1. Create a vehicle with a valid email address
2. Create a challan for that vehicle
3. Check the console for email sending status
4. Check the recipient's email inbox

### Test SMS
1. Create a vehicle with a valid phone number
2. Create a challan for that vehicle
3. Check the console for SMS sending status
4. Check the recipient's phone for SMS

## 📋 Troubleshooting

### Email Issues
- **Authentication failed**: Check your email and app password
- **Connection refused**: Check firewall settings
- **No emails received**: Check spam folder

### SMS Issues
- **Invalid phone number**: Ensure format is +[country code][number]
- **API errors**: Check your API credentials
- **No SMS received**: Check phone number format and carrier

### General Issues
- **Import errors**: Run `pip install -r requirements.txt`
- **Configuration errors**: Check `.env` file format
- **Permission errors**: Ensure proper file permissions

## 🔒 Security Notes

1. **Never commit** your `.env` file to version control
2. **Use strong passwords** for email and SMS services
3. **Enable 2FA** on all service accounts
4. **Regularly rotate** API keys and passwords

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify your configuration settings
3. Test with a simple email/SMS first
4. Check service provider documentation

## 🎯 Features

### Email Notifications
- ✅ HTML formatted emails
- ✅ Plain text fallback
- ✅ Challan creation notifications
- ✅ Payment confirmation emails
- ✅ Professional styling

### SMS Notifications
- ✅ Multiple service support
- ✅ Fallback mechanisms
- ✅ Concise messaging
- ✅ Payment links included
- ✅ Error handling

### Both Services
- ✅ Automatic sending on challan creation
- ✅ Payment confirmation
- ✅ Error logging
- ✅ Console output for debugging 