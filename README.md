# 🚗 Vehicle Recognition System

A comprehensive Django-based system for automatic vehicle number plate recognition, challan management, and payment processing with advanced deep learning capabilities.

## ✨ Features

### 🔍 Advanced Number Plate Recognition
- **Multi-Engine OCR**: Uses EasyOCR, Tesseract, and custom deep learning models
- **Advanced Image Preprocessing**: Multiple preprocessing techniques for better accuracy
- **Region Detection**: Automatic detection of number plate regions in images
- **Pattern Validation**: Validates Indian number plate patterns
- **High Accuracy**: Improved recognition with confidence scoring

### 💳 Enhanced Payment System
- **Multiple Payment Methods**: Credit Card, Debit Card, UPI, Net Banking, Digital Wallets
- **Secure Processing**: PCI DSS compliant payment gateway
- **Real-time Validation**: Client-side and server-side validation
- **Transaction Tracking**: Unique transaction IDs for all payments
- **Automatic Status Update**: Challan status automatically updated to "PAID"

### 📱 Improved SMS Notifications
- **Multiple SMS Services**: Fast2SMS, TextLocal, Twilio, MSG91 support
- **Optimized Messages**: Character-optimized messages for better delivery
- **Payment Confirmations**: Automatic SMS confirmation for successful payments
- **Error Handling**: Robust error handling and fallback mechanisms

### 📧 Email Notifications
- **HTML Email Templates**: Beautiful, responsive email templates
- **Payment Confirmations**: Detailed payment confirmation emails
- **Multiple SMTP Support**: Gmail, custom SMTP server support

### 🎯 Admin Features
- **Dashboard Analytics**: Real-time statistics and reports
- **Challan Management**: Create, view, and manage challans
- **Vehicle Database**: Comprehensive vehicle information management
- **Payment Tracking**: Monitor payment status and history

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Tesseract OCR (for enhanced recognition)
- Virtual environment

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
   cd projectvehicle
```

2. **Run the setup script**
```bash
   python setup.py
   ```

3. **Configure environment variables**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your configuration
   nano .env
   ```

4. **Start the server**
```bash
   venv\Scripts\python.exe manage.py runserver
   ```

5. **Access the application**
   - URL: http://127.0.0.1:8000
   - Admin: admin/admin123

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# SMS Configuration - Multiple Services Supported

# Fast2SMS (Primary for India)
FAST2SMS_API_KEY=your-fast2sms-api-key

# TextLocal (Alternative for India)
TEXTLOCAL_API_KEY=your-textlocal-api-key

# Twilio (International)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_FROM_NUMBER=+1234567890

# MSG91 (Another Indian SMS service)
MSG91_API_KEY=your-msg91-api-key
MSG91_FLOW_ID=your-flow-id

# SMS Sender ID (for services that support it)
SMS_SENDER_ID=TRAFFIC

# Base URL for payment links
BASE_URL=http://127.0.0.1:8000
```

### SMS Service Setup

#### Fast2SMS (Recommended for India)
1. Sign up at https://www.fast2sms.com/
2. Get your API key
3. Add to `.env`: `FAST2SMS_API_KEY=your-key`

#### TextLocal
1. Sign up at https://www.textlocal.in/
2. Get your API key
3. Add to `.env`: `TEXTLOCAL_API_KEY=your-key`

#### Twilio (International)
1. Sign up at https://www.twilio.com/
2. Get Account SID and Auth Token
3. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your-sid
   TWILIO_AUTH_TOKEN=your-token
   TWILIO_FROM_NUMBER=+1234567890
   ```

### Email Setup

#### Gmail
1. Enable 2-factor authentication
2. Generate App Password
3. Add to `.env`:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

## 🔧 System Dependencies

### Windows
- Tesseract OCR: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Visual Studio Build Tools (for TensorFlow)
- CUDA Toolkit (optional, for GPU support)

### Linux
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
sudo apt-get install -y libsm6 libxext6 libxrender-dev
sudo apt-get install -y libgomp1 libgcc-s1
```

### macOS
```bash
brew install tesseract
brew install tesseract-lang
```

## 📚 Usage

### Admin Panel
1. Login with admin credentials
2. Upload vehicle images for number plate recognition
3. Create challans for detected violations
4. Monitor payment status and generate reports

### Payment Process
1. Vehicle owner receives email/SMS notification
2. Clicks "Pay Now" button in email
3. Selects payment method (Card/UPI/Net Banking)
4. Completes payment with secure validation
5. Receives confirmation email/SMS
6. Challan status automatically updated to "PAID"

### Number Plate Recognition
1. Upload vehicle image
2. System processes image with multiple OCR engines
3. Detects number plate regions
4. Validates against Indian number plate patterns
5. Returns recognized number plate with confidence score

## 🛠️ Technical Details

### Number Plate Recognition Engine
- **EasyOCR**: Primary OCR engine with high accuracy
- **Tesseract**: Secondary OCR engine for fallback
- **Image Preprocessing**: Multiple techniques including:
  - Gaussian blur and thresholding
  - Adaptive thresholding
  - Morphological operations
  - Edge detection
  - Contrast enhancement
- **Region Detection**: Contour analysis for number plate localization
- **Pattern Validation**: Regex-based validation for Indian number plates

### Payment Processing
- **Client-side Validation**: JavaScript validation for form fields
- **Server-side Validation**: Django form validation
- **Transaction Tracking**: Unique transaction IDs
- **Status Management**: Automatic challan status updates
- **Confirmation Notifications**: Email and SMS confirmations

### SMS Integration
- **Multiple Providers**: Support for 4 different SMS services
- **Fallback Mechanism**: Automatic fallback if primary service fails
- **Message Optimization**: Character-limited messages for better delivery
- **Error Handling**: Comprehensive error logging and handling

## 📊 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /pay-challan/<challan_id>/` - Payment page
- `GET /payment-success/<challan_id>/` - Payment success page

### Admin Endpoints (Login Required)
- `GET /dashboard/` - Admin dashboard
- `GET /upload-image/` - Image upload
- `GET /search-vehicle/` - Vehicle search
- `GET /create-challan/<vehicle_id>/` - Create challan
- `GET /challan-list/` - List all challans
- `GET /vehicle-list/` - List all vehicles
- `GET /add-vehicle/` - Add new vehicle

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **Input Validation**: Comprehensive input validation
- **Secure Payment**: PCI DSS compliant payment processing
- **Authentication**: Django's built-in authentication system
- **File Upload Security**: Secure file upload handling

## 🐛 Troubleshooting

### Common Issues

1. **Number Plate Not Detected**
   - Ensure image is clear and well-lit
   - Check if Tesseract is properly installed
   - Verify image format (JPEG, PNG supported)

2. **SMS Not Sending**
   - Check API key configuration
   - Verify phone number format (10 digits for India)
   - Check SMS service account balance

3. **Email Not Sending**
   - Verify SMTP settings
   - Check Gmail App Password
   - Ensure email address is valid

4. **Payment Errors**
   - Check form validation
   - Verify payment method selection
   - Ensure all required fields are filled

### Debug Mode
Enable debug mode in `.env`:
```env
DEBUG=True
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

## 🔄 Updates

### Latest Improvements
- ✅ Enhanced number plate recognition with multiple OCR engines
- ✅ Improved payment system with multiple payment methods
- ✅ Better SMS integration with multiple providers
- ✅ Advanced image preprocessing for better accuracy
- ✅ Comprehensive error handling and validation
- ✅ Beautiful UI/UX with responsive design
- ✅ Automatic payment confirmation notifications
- ✅ Real-time admin dashboard with analytics

---

**Note**: This system is designed for educational and demonstration purposes. For production use, ensure proper security measures and compliance with local regulations. 