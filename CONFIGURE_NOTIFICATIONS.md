# Configure Email and SMS Notifications - Step by Step Guide

This guide will help you configure the notification system so that emails and SMS are actually sent to vehicle owners when violations occur.

## 🚨 Problem: Notifications Not Being Sent

If you're not receiving emails and SMS, it's likely because:
1. Email settings are not configured in `.env` file
2. SMS service credentials are not set up
3. The system is using default placeholder values

## 📧 Step 1: Configure Email (Gmail)

### 1.1 Enable 2-Factor Authentication on Gmail
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security"
3. Enable "2-Step Verification"

### 1.2 Generate App Password
1. In Security settings, click "App passwords"
2. Select "Mail" as the app
3. Click "Generate"
4. Copy the 16-character password

### 1.3 Update .env File
Edit your `.env` file and replace the email settings:

```env
# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-actual-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-digit-app-password
```

**Important:** Replace `your-actual-email@gmail.com` with your real Gmail address and `your-16-digit-app-password` with the app password you generated.

## 📱 Step 2: Configure SMS (Optional)

### Option A: Twilio (International)
1. Sign up at [Twilio.com](https://www.twilio.com)
2. Get your Account SID and Auth Token from the dashboard
3. Get a Twilio phone number
4. Update `.env` file:

```env
# SMS Configuration (Twilio)
SMS_API_KEY=your-actual-twilio-account-sid
SMS_API_SECRET=your-actual-twilio-auth-token
SMS_FROM_NUMBER=+1234567890
```

### Option B: Fast2SMS (India)
1. Sign up at [Fast2SMS.com](https://www.fast2sms.com)
2. Get your API key from the dashboard
3. Update `.env` file:

```env
# SMS Configuration (Fast2SMS)
FAST2SMS_API_KEY=your-actual-fast2sms-api-key
FAST2SMS_SENDER_ID=YOURID
```

## 🧪 Step 3: Test the Configuration

### 3.1 Quick Test
Run the simple test script:
```bash
python test_notification_system.py
```

### 3.2 Detailed Test
Run the Django management command:
```bash
python manage.py test_notifications
```

### 3.3 Manual Test
1. Start the server: `python manage.py runserver`
2. Go to http://localhost:8000
3. Login and create a challan
4. Check if notifications are sent

## 🔍 Step 4: Verify Configuration

### Check .env File
Make sure your `.env` file has real values, not placeholder text:

```env
# ✅ CORRECT - Real values
EMAIL_HOST_USER=john.doe@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop

# ❌ WRONG - Placeholder values
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Check Console Output
When you create a challan, you should see:
```
✅ Email sent successfully to john.doe@gmail.com
✅ SMS sent via Twilio to +1234567890
```

If you see:
```
❌ Email not configured. Would send to john.doe@gmail.com
📱 SMS would be sent to +1234567890
```
Then your configuration is not set up properly.

## 🛠️ Step 5: Troubleshooting

### Email Issues
- **"Authentication failed"**: Check your Gmail app password
- **"Connection refused"**: Check firewall settings
- **"No emails received"**: Check spam folder

### SMS Issues
- **"Invalid phone number"**: Use format +[country code][number]
- **"API errors"**: Check your API credentials
- **"No SMS received"**: Check phone number format

### General Issues
- **Import errors**: Run `pip install -r requirements.txt`
- **Configuration errors**: Check `.env` file format
- **Permission errors**: Ensure proper file permissions

## 📋 Step 6: Admin Panel Features

After configuration, you'll see in the admin panel:

### Vehicle List
- Total challans per vehicle
- Payment percentage (green/orange/red)
- Owner contact information

### Challan List
- Payment status with badges
- Payment method and date
- Direct links to payment pages
- Detailed payment information

### Payment List
- Complete payment history
- Transaction details
- Challan information
- Owner details

## 🎯 What You'll Receive

### Email Notifications
- **Professional HTML emails** with styling
- **Complete challan details**
- **Payment link** with multiple payment options
- **Mobile-responsive design**

### SMS Notifications
- **Concise violation alerts**
- **Payment link** with payment methods
- **Immediate delivery**

### Admin Panel
- **Real-time payment tracking**
- **Payment status indicators**
- **Detailed payment information**
- **Owner contact details**

## 🔒 Security Notes

1. **Never commit** your `.env` file to version control
2. **Use strong passwords** for email and SMS services
3. **Enable 2FA** on all service accounts
4. **Regularly rotate** API keys and passwords

## 📞 Support

If you still have issues:
1. Check the console output for specific error messages
2. Verify your `.env` file has real values
3. Test with a simple email/SMS first
4. Check service provider documentation

## ✅ Success Indicators

You'll know it's working when:
- ✅ You receive emails in your inbox
- ✅ You receive SMS on your phone
- ✅ Admin panel shows payment status
- ✅ Console shows success messages
- ✅ No more "not configured" messages

---

**Remember:** The system will only send actual emails and SMS when you configure real credentials in the `.env` file. Default placeholder values will only show console output for testing purposes. 