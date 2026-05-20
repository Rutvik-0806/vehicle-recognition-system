import cv2
import numpy as np
import pytesseract
import re
import os
import requests
from django.utils import timezone
from django.conf import settings
import uuid
from PIL import Image, ImageEnhance

class NumberPlateRecognition:
    """Improved number plate recognition with better preprocessing and fallback methods"""
    
    def __init__(self):
        # Initialize YOLO model
        self._setup_yolo_model()
        # Setup Tesseract
        self._setup_tesseract()
        
    def _setup_yolo_model(self):
        """Setup YOLO model with proper error handling"""
        try:
            import torch
        except ImportError:
            print("PyTorch not installed; YOLO detection disabled (OCR still available).")
            self.model = None
            return

        try:
            model_path = 'best.pt'
            if os.path.exists(model_path):
                print("Loading custom YOLO model...")
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
            else:
                print("Custom model not found. Using YOLOv5s...")
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            
            # Adjust confidence threshold
            self.model.conf = 0.25  # Lower threshold to catch more detections
            self.model.iou = 0.45   # Non-maximum suppression threshold
            print("YOLO model loaded successfully")
            
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None
    
    def _setup_tesseract(self):
        """Setup Tesseract OCR"""
        try:
            # Try to find Tesseract automatically
            import shutil
            tesseract_path = shutil.which('tesseract')
            if tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                print(f"Tesseract found at: {tesseract_path}")
            else:
                # Common Windows path
                windows_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                if os.path.exists(windows_path):
                    pytesseract.pytesseract.tesseract_cmd = windows_path
                    print(f"Tesseract found at: {windows_path}")
                else:
                    print("Warning: Tesseract not found in standard locations")
        except Exception as e:
            print(f"Error setting up Tesseract: {e}")
    
    def preprocess_image(self, image):
        """Enhanced image preprocessing for better OCR"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply different preprocessing techniques
        processed_images = []
        
        # 1. Original grayscale
        processed_images.append(("original", gray))
        
        # 2. Gaussian blur + threshold
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh1 = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(("otsu_thresh", thresh1))
        
        # 3. Adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed_images.append(("adaptive_thresh", adaptive_thresh))
        
        # 4. Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
        processed_images.append(("morphological", morph))
        
        # 5. Contrast enhancement
        enhanced = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
        processed_images.append(("enhanced", enhanced))
        
        return processed_images
    
    def extract_text_with_multiple_configs(self, image):
        """Try multiple Tesseract configurations"""
        configs = [
            '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--oem 3 --psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            '--oem 1 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        ]
        
        best_text = ""
        best_confidence = 0
        
        for config in configs:
            try:
                # Get text and confidence
                text = pytesseract.image_to_string(image, config=config).strip()
                
                # Try to get confidence data
                try:
                    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = np.mean(confidences) if confidences else 0
                except:
                    avg_confidence = 50  # Default confidence
                
                cleaned_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                
                if len(cleaned_text) >= 4 and avg_confidence > best_confidence:
                    best_text = cleaned_text
                    best_confidence = avg_confidence
                    
            except Exception as e:
                print(f"OCR config failed: {e}")
                continue
        
        return best_text, best_confidence
    
    def validate_number_plate(self, text):
        """Validate if the extracted text looks like a number plate"""
        if not text or len(text) < 4:
            return False
        
        # Common number plate patterns (adjust for your region)
        patterns = [
            r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$',  # Indian format: XX00XX0000
            r'^[A-Z]{3}[0-9]{3,4}$',                 # Simple format: XXX000
            r'^[A-Z]{1,3}[0-9]{1,4}[A-Z]{0,3}$',    # Mixed format
            r'^[0-9]{1,3}[A-Z]{1,3}[0-9]{1,4}$',    # Number-Letter-Number
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        
        # Basic validation: must contain both letters and numbers
        has_letter = bool(re.search(r'[A-Z]', text))
        has_number = bool(re.search(r'[0-9]', text))
        
        return has_letter and has_number and 4 <= len(text) <= 12
    
    def detect_with_contours(self, image):
        """Fallback method using contour detection for number plates"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Find edges
            edges = cv2.Canny(filtered, 30, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
            
            best_text = ""
            best_conf = 0
            
            for contour in contours:
                # Approximate contour
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Look for rectangular shapes (potential number plates)
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by aspect ratio (typical number plate ratios)
                    aspect_ratio = w / h
                    if 2.0 <= aspect_ratio <= 5.0 and w > 100 and h > 30:
                        # Extract the region
                        plate_img = gray[y:y+h, x:x+w]
                        
                        # Preprocess and extract text
                        processed_images = self.preprocess_image(plate_img)
                        
                        for name, proc_img in processed_images:
                            text, conf = self.extract_text_with_multiple_configs(proc_img)
                            if text and self.validate_number_plate(text) and conf > best_conf:
                                best_text = text
                                best_conf = conf
            
            return best_text, best_conf / 100.0
            
        except Exception as e:
            print(f"Contour detection failed: {e}")
            return "", 0.0
    
    def detect_number_plate(self, image_path):
        """Main detection method with multiple fallback approaches"""
        try:
            # Load image
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    print(f"ERROR: Could not load image from {image_path}")
                    return None, 0.0
            else:
                image = image_path  # Assume it's already a numpy array
            
            print(f"Image loaded successfully. Shape: {image.shape}")
            
            best_plate = ""
            best_confidence = 0.0
            
            # Method 1: YOLO Detection (if model is available)
            if self.model is not None:
                try:
                    print("Running YOLO detection...")
                    results = self.model(image)
                    detections = results.xyxy[0].cpu().numpy()
                    print(f"YOLO found {len(detections)} detections")
                    
                    for i, det in enumerate(detections):
                        x1, y1, x2, y2, conf, cls = det
                        print(f"Detection {i+1}: conf={conf:.3f}, class={int(cls)}")
                        
                        if conf > 0.2:  # Lower threshold
                            # Extract with padding
                            pad = 10
                            x1, y1, x2, y2 = map(int, [max(0, x1-pad), max(0, y1-pad), 
                                                       min(image.shape[1], x2+pad), 
                                                       min(image.shape[0], y2+pad)])
                            
                            plate_img = image[y1:y2, x1:x2]
                            
                            if plate_img.size > 0:
                                # Try multiple preprocessing methods
                                processed_images = self.preprocess_image(plate_img)
                                
                                for name, proc_img in processed_images:
                                    text, ocr_conf = self.extract_text_with_multiple_configs(proc_img)
                                    
                                    if text and self.validate_number_plate(text):
                                        combined_conf = (float(conf) + ocr_conf/100) / 2
                                        if combined_conf > best_confidence:
                                            best_plate = text
                                            best_confidence = combined_conf
                                            print(f"Found plate with {name} preprocessing: {text} (conf: {combined_conf:.3f})")
                                
                except Exception as e:
                    print(f"YOLO detection failed: {e}")
            
            # Method 2: Contour-based detection (fallback)
            if not best_plate or best_confidence < 0.5:
                print("Trying contour-based detection...")
                contour_text, contour_conf = self.detect_with_contours(image)
                if contour_text and contour_conf > best_confidence:
                    best_plate = contour_text
                    best_confidence = contour_conf
                    print(f"Contour method found: {contour_text}")
            
            # Method 3: Full image OCR (last resort)
            if not best_plate or best_confidence < 0.3:
                print("Trying full image OCR...")
                processed_images = self.preprocess_image(image)
                
                for name, proc_img in processed_images:
                    text, conf = self.extract_text_with_multiple_configs(proc_img)
                    if text and self.validate_number_plate(text) and conf/100 > best_confidence:
                        best_plate = text
                        best_confidence = conf / 100
                        print(f"Full image OCR with {name}: {text}")
            
            if best_plate:
                print(f"Final result: {best_plate} (confidence: {best_confidence:.3f})")
                return best_plate, best_confidence
            else:
                print("No number plate detected")
                return None, 0.0
                
        except Exception as e:
            print(f"Error in number plate detection: {e}")
            import traceback
            traceback.print_exc()
            return None, 0.0


class NotificationService:
    """Class for sending email and SMS notifications"""
    
    @staticmethod
    def send_email_notification(challan):
        """Send email notification for challan to vehicle owner"""
        try:
            # Validate email address
            if not challan.vehicle.owner_email or '@' not in challan.vehicle.owner_email:
                print(f"❌ Invalid email address: {challan.vehicle.owner_email}")
                return False
            
            subject = f'🚨 Traffic Violation Challan - {challan.challan_id}'
            
            # Create HTML email content
            html_message = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .amount {{ color: #dc3545; font-weight: bold; font-size: 18px; }}
                    .button {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
                    .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚨 Traffic Violation Notice</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{challan.vehicle.owner_name}</strong>,</p>
                    
                    <p>You have been issued a traffic violation challan for your vehicle.</p>
                    
                    <div class="details">
                        <h3>Challan Details:</h3>
                        <p><strong>Challan ID:</strong> {challan.challan_id}</p>
                        <p><strong>Vehicle Number:</strong> {challan.vehicle.number_plate}</p>
                        <p><strong>Owner Name:</strong> {challan.vehicle.owner_name}</p>
                        <p><strong>Violation Type:</strong> {challan.violation_type.name}</p>
                        <p><strong>Penalty Amount:</strong> <span class="amount">₹{challan.penalty_amount}</span></p>
                        <p><strong>Date:</strong> {challan.violation_date.strftime('%Y-%m-%d %H:%M')}</p>
                        <p><strong>Location:</strong> {challan.location or 'Not specified'}</p>
                        <p><strong>Description:</strong> {challan.description or 'No additional details'}</p>
                    </div>
                    
                    <p><strong>⚠️ Important:</strong> Please pay the penalty within 30 days to avoid additional charges and legal action.</p>
                    
                    <a href="{getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')}/pay-challan/{challan.challan_id}/" class="button">Pay Now</a>
                    
                    <p><strong>Payment Methods Available:</strong></p>
                    <ul>
                        <li>Credit/Debit Card</li>
                        <li>Net Banking</li>
                        <li>UPI</li>
                        <li>Digital Wallets</li>
                    </ul>
                    
                    <p>If you have any questions, please contact our support team.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from Traffic Management System</p>
                    <p>Please do not reply to this email</p>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_message = f"""
Dear {challan.vehicle.owner_name},

You have been issued a traffic violation challan.

Challan Details:
- Challan ID: {challan.challan_id}
- Vehicle Number: {challan.vehicle.number_plate}
- Owner Name: {challan.vehicle.owner_name}
- Violation: {challan.violation_type.name}
- Penalty Amount: ₹{challan.penalty_amount}
- Date: {challan.violation_date.strftime('%Y-%m-%d %H:%M')}
- Location: {challan.location or 'Not specified'}

Please pay the penalty within 30 days to avoid additional charges.

Payment Link: {getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')}/pay-challan/{challan.challan_id}/

Payment Methods: Credit/Debit Card, Net Banking, UPI, Digital Wallets

Best regards,
Traffic Management System
            """
            
            # Try to send email with current settings
            try:
                from django.core.mail import send_mail, EmailMultiAlternatives
                
                from_email = getattr(settings, 'EMAIL_HOST_USER', 'noreply@trafficmanagement.com')
                
                # Send email with both HTML and plain text
                email = EmailMultiAlternatives(
                    subject,
                    plain_message,
                    from_email,
                    [challan.vehicle.owner_email]
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
                
                print(f"✅ Email sent successfully to {challan.vehicle.owner_email}")
                return True
                
            except Exception as email_error:
                print(f"❌ Email sending failed: {email_error}")
                print(f"📧 Email would be sent to {challan.vehicle.owner_email}:")
                print(f"   Subject: {subject}")
                print(f"   Message: {plain_message[:200]}...")
                print(f"   Configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env file")
                return False
            
        except Exception as e:
            print(f"❌ Error in email notification: {e}")
            return False
    
    @staticmethod
    def send_sms_notification(challan):
        """Send SMS notification for challan with improved logic"""
        try:
            # Validate phone number
            if not challan.vehicle.owner_phone:
                print(f"❌ No phone number provided for vehicle {challan.vehicle.number_plate}")
                return False
            
            # Clean phone number
            phone = challan.vehicle.owner_phone.strip()
            if phone.startswith('+91'):
                phone = phone[3:]  # Remove +91 prefix
            elif phone.startswith('+'):
                phone = phone[1:]  # Remove + prefix
            
            # Validate phone number format (Indian mobile numbers)
            if not re.match(r'^[6-9]\d{9}$', phone):
                print(f"❌ Invalid phone number format: {challan.vehicle.owner_phone}")
                return False
            
            # Create optimized SMS message (within 160 characters)
            base_url = getattr(settings, 'BASE_URL', 'http://127.0.0.1:8000')
            payment_url = f"{base_url}/pay-challan/{challan.challan_id}/"
            
            # Shortened message to fit SMS limits
            message = f"Traffic challan {challan.challan_id} for {challan.vehicle.number_plate}. Violation: {challan.violation_type.name}. Amount: ₹{challan.penalty_amount}. Pay at: {payment_url}"
            
            # If message is too long, create shorter version
            if len(message) > 140:
                message = f"Challan {challan.challan_id} for {challan.vehicle.number_plate}. Amount: ₹{challan.penalty_amount}. Pay: {payment_url}"
            
            sms_sent = False
            
            # Method 1: Try Fast2SMS (Primary for India)
            if hasattr(settings, 'FAST2SMS_API_KEY') and settings.FAST2SMS_API_KEY not in ['your-fast2sms-api-key', 'your-sms-api-key', '']:
                try:
                    url = "https://www.fast2sms.com/dev/bulkV2"
                    payload = {
                        "authorization": settings.FAST2SMS_API_KEY,
                        "message": message,
                        "language": "english",
                        "route": "q",
                        "numbers": phone
                    }
                    headers = {
                        'Content-Type': "application/x-www-form-urlencoded",
                        'Cache-Control': "no-cache",
                    }
                    response = requests.post(url, data=payload, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('status') == 'OK':
                            print(f"✅ SMS sent via Fast2SMS to {challan.vehicle.owner_phone}")
                            sms_sent = True
                        else:
                            print(f"❌ Fast2SMS API error: {result}")
                    else:
                        print(f"❌ Fast2SMS HTTP error: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Fast2SMS SMS failed: {e}")
            
            # Method 2: Try TextLocal (Alternative for India)
            if not sms_sent and hasattr(settings, 'TEXTLOCAL_API_KEY') and settings.TEXTLOCAL_API_KEY not in ['your-textlocal-api-key', 'your-sms-api-key', '']:
                try:
                    url = "https://api.textlocal.in/send/"
                    payload = {
                        "apikey": settings.TEXTLOCAL_API_KEY,
                        "message": message,
                        "numbers": phone,
                        "sender": getattr(settings, 'SMS_SENDER_ID', 'TXTLCL')
                    }
                    response = requests.post(url, data=payload, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('status') == 'success':
                            print(f"✅ SMS sent via TextLocal to {challan.vehicle.owner_phone}")
                            sms_sent = True
                        else:
                            print(f"❌ TextLocal API error: {result}")
                    else:
                        print(f"❌ TextLocal HTTP error: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ TextLocal SMS failed: {e}")
            
            # Method 3: Try Twilio (International)
            if not sms_sent and hasattr(settings, 'TWILIO_ACCOUNT_SID') and hasattr(settings, 'TWILIO_AUTH_TOKEN'):
                if settings.TWILIO_ACCOUNT_SID not in ['your-twilio-account-sid', 'your-sms-api-key', '']:
                    try:
                        from twilio.rest import Client
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        message_obj = client.messages.create(
                            body=message,
                            from_=getattr(settings, 'TWILIO_FROM_NUMBER', '+1234567890'),
                            to=f"+91{phone}"  # Add country code for Twilio
                        )
                        print(f"✅ SMS sent via Twilio to {challan.vehicle.owner_phone}")
                        sms_sent = True
                    except Exception as e:
                        print(f"❌ Twilio SMS failed: {e}")
            
            # Method 4: Try MSG91 (Another Indian SMS service)
            if not sms_sent and hasattr(settings, 'MSG91_API_KEY') and settings.MSG91_API_KEY not in ['your-msg91-api-key', 'your-sms-api-key', '']:
                try:
                    url = "https://api.msg91.com/api/v5/flow/"
                    payload = {
                        "flow_id": getattr(settings, 'MSG91_FLOW_ID', 'your-flow-id'),
                        "sender": getattr(settings, 'SMS_SENDER_ID', 'TRAFFIC'),
                        "mobiles": phone,
                        "VAR1": challan.challan_id,
                        "VAR2": challan.vehicle.number_plate,
                        "VAR3": f"₹{challan.penalty_amount}",
                        "VAR4": payment_url
                    }
                    headers = {
                        'Content-Type': 'application/json',
                        'Authkey': settings.MSG91_API_KEY
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('type') == 'success':
                            print(f"✅ SMS sent via MSG91 to {challan.vehicle.owner_phone}")
                            sms_sent = True
                        else:
                            print(f"❌ MSG91 API error: {result}")
                    else:
                        print(f"❌ MSG91 HTTP error: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ MSG91 SMS failed: {e}")
            
            # Method 5: Console output (for testing when no service is configured)
            if not sms_sent:
                print(f"📱 SMS would be sent to {challan.vehicle.owner_phone}:")
                print(f"   Message: {message}")
                print(f"   Message length: {len(message)} characters")
                print(f"   Note: Configure SMS service in .env file to send actual SMS")
                print(f"   Available services:")
                print(f"   - Fast2SMS: Set FAST2SMS_API_KEY")
                print(f"   - TextLocal: Set TEXTLOCAL_API_KEY")
                print(f"   - Twilio: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER")
                print(f"   - MSG91: Set MSG91_API_KEY, MSG91_FLOW_ID")
                # Simulate successful SMS for testing
                sms_sent = True
            
            return sms_sent
            
        except Exception as e:
            print(f"❌ Error in SMS notification: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation_email(challan, payment):
        """Send payment confirmation email"""
        try:
            # Validate email address
            if not challan.vehicle.owner_email or '@' not in challan.vehicle.owner_email:
                print(f"❌ Invalid email address: {challan.vehicle.owner_email}")
                return False
            
            subject = f'✅ Payment Confirmation - Challan {challan.challan_id}'
            
            html_message = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                    .amount {{ color: #28a745; font-weight: bold; font-size: 18px; }}
                    .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>✅ Payment Confirmation</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{challan.vehicle.owner_name}</strong>,</p>
                    
                    <p>Thank you for paying your traffic violation challan. Your payment has been processed successfully.</p>
                    
                    <div class="details">
                        <h3>Payment Details:</h3>
                        <p><strong>Challan ID:</strong> {challan.challan_id}</p>
                        <p><strong>Payment ID:</strong> {payment.payment_id}</p>
                        <p><strong>Vehicle Number:</strong> {challan.vehicle.number_plate}</p>
                        <p><strong>Amount Paid:</strong> <span class="amount">₹{payment.amount}</span></p>
                        <p><strong>Payment Method:</strong> {payment.payment_method}</p>
                        <p><strong>Payment Date:</strong> {payment.payment_date.strftime('%Y-%m-%d %H:%M')}</p>
                        <p><strong>Transaction ID:</strong> {payment.transaction_id or 'N/A'}</p>
                    </div>
                    
                    <p>Your challan has been marked as paid. Thank you for your cooperation.</p>
                </div>
                <div class="footer">
                    <p>This is an automated message from Traffic Management System</p>
                </div>
            </body>
            </html>
            """
            
            plain_message = f"""
Dear {challan.vehicle.owner_name},

Thank you for paying your traffic violation challan. Your payment has been processed successfully.

Payment Details:
- Challan ID: {challan.challan_id}
- Payment ID: {payment.payment_id}
- Vehicle Number: {challan.vehicle.number_plate}
- Amount Paid: ₹{payment.amount}
- Payment Method: {payment.payment_method}
- Payment Date: {payment.payment_date.strftime('%Y-%m-%d %H:%M')}

Your challan has been marked as paid. Thank you for your cooperation.

Best regards,
Traffic Management System
            """
            
            # Check if email settings are configured
            if not hasattr(settings, 'EMAIL_HOST_USER') or settings.EMAIL_HOST_USER in ['your-email@gmail.com', 'your-actual-email@gmail.com']:
                print(f"❌ Email not configured. Would send payment confirmation to {challan.vehicle.owner_email}")
                return False
            
            from django.core.mail import EmailMultiAlternatives
            email = EmailMultiAlternatives(
                subject,
                plain_message,
                settings.EMAIL_HOST_USER,
                [challan.vehicle.owner_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            print(f"✅ Payment confirmation email sent to {challan.vehicle.owner_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending payment confirmation email: {e}")
            return False
    
    @staticmethod
    def send_payment_confirmation_sms(challan, payment):
        """Send payment confirmation SMS"""
        try:
            # Validate phone number
            if not challan.vehicle.owner_phone:
                print(f"❌ No phone number provided for payment confirmation")
                return False
            
            # Clean phone number
            phone = challan.vehicle.owner_phone.strip()
            if phone.startswith('+91'):
                phone = phone[3:]
            elif phone.startswith('+'):
                phone = phone[1:]
            
            # Validate phone number format
            if not re.match(r'^[6-9]\d{9}$',phone):
                print(f"❌ Invalid phone number format for payment confirmation: {challan.vehicle.owner_phone}")
                return False
            
            # Create payment confirmation message
            message = f"Payment successful! Challan {challan.challan_id} paid. Amount: ₹{payment.amount}. Payment ID: {payment.payment_id}. Thank you!"
            
            # If message is too long, create shorter version
            if len(message) > 140:
                message = f"Payment successful! Challan {challan.challan_id} paid. Amount: ₹{payment.amount}. Thank you!"
            
            sms_sent = False
            
            # Try Fast2SMS
            if hasattr(settings, 'FAST2SMS_API_KEY') and settings.FAST2SMS_API_KEY not in ['your-fast2sms-api-key', 'your-sms-api-key', '']:
                try:
                    url = "https://www.fast2sms.com/dev/bulkV2"
                    payload = {
                        "authorization": settings.FAST2SMS_API_KEY,
                        "message": message,
                        "language": "english",
                        "route": "q",
                        "numbers": phone
                    }
                    headers = {
                        'Content-Type': "application/x-www-form-urlencoded",
                        "Cache-Control": "no-cache",
                    }
                    response = requests.post(url, data=payload, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('status') == 'OK':
                            print(f"✅ Payment confirmation SMS sent via Fast2SMS to {challan.vehicle.owner_phone}")
                            sms_sent = True
                except Exception as e:
                    print(f"❌ Fast2SMS payment confirmation failed: {e}")
            
            # Try TextLocal
            if not sms_sent and hasattr(settings, 'TEXTLOCAL_API_KEY') and settings.TEXTLOCAL_API_KEY not in ['your-textlocal-api-key', 'your-sms-api-key', '']:
                try:
                    url = "https://api.textlocal.in/send/"
                    payload = {
                        "apikey": settings.TEXTLOCAL_API_KEY,
                        "message": message,
                        "numbers": phone,
                        "sender": getattr(settings, 'SMS_SENDER_ID', 'TXTLCL')
                    }
                    response = requests.post(url, data=payload, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('status') == 'success':
                            print(f"✅ Payment confirmation SMS sent via TextLocal to {challan.vehicle.owner_phone}")
                            sms_sent = True
                except Exception as e:
                    print(f"❌ TextLocal payment confirmation failed: {e}")
            
            # Console output for testing
            if not sms_sent:
                print(f"📱 Payment confirmation SMS would be sent to {challan.vehicle.owner_phone}:")
                print(f"   Message: {message}")
                print(f"   Note: Configure SMS service in .env file to send actual SMS")
                sms_sent = True
            
            return sms_sent
            
        except Exception as e:
            print(f"❌ Error in payment confirmation SMS: {e}")
            return False


class PaymentService:
    """Class for handling payment processing - Only vehicle owners can pay"""
    
    @staticmethod
    def generate_payment_id():
        """Generate unique payment ID"""
        return f"PAY{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def process_payment(challan, payment_method, transaction_id=None):
        """Process payment for challan with improved validation and error handling"""
        from .models import Payment
        
        try:
            # Check if challan is already paid
            if challan.status == 'PAID':
                return None, "Challan is already paid"
            
            # Validate payment method
            valid_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Digital Wallet']
            if payment_method not in valid_methods:
                return None, f"Invalid payment method. Please select from: {', '.join(valid_methods)}"
            
            # Generate transaction ID if not provided
            if not transaction_id:
                transaction_id = f"TXN{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"
            
            # Create payment record
            payment = Payment.objects.create(
                challan=challan,
                payment_id=PaymentService.generate_payment_id(),
                amount=challan.penalty_amount,
                payment_method=payment_method,
                transaction_id=transaction_id
            )
            
            # Update challan status
            challan.status = 'PAID'
            challan.paid_at = timezone.now()
            challan.save()
            
            # Send payment confirmation email
            try:
                NotificationService.send_payment_confirmation_email(challan, payment)
            except Exception as email_error:
                print(f"Warning: Payment confirmation email failed: {email_error}")
            
            # Send payment confirmation SMS
            try:
                NotificationService.send_payment_confirmation_sms(challan, payment)
            except Exception as sms_error:
                print(f"Warning: Payment confirmation SMS failed: {sms_error}")
            
            print(f"✅ Payment processed successfully: {payment.payment_id}")
            return payment, "Payment processed successfully"
            
        except Exception as e:
            print(f"❌ Error processing payment: {e}")
            return None, f"Payment processing failed: {str(e)}"
    
    @staticmethod
    def get_payment_status(challan):
        """Get payment status for admin to check"""
        try:
            if hasattr(challan, 'payment_set') and challan.payment_set.exists():
                payment = challan.payment_set.first()
                return {
                    'status': 'PAID',
                    'payment_id': payment.payment_id,
                    'amount': payment.amount,
                    'payment_method': payment.payment_method,
                    'payment_date': payment.payment_date,
                    'transaction_id': payment.transaction_id
                }
            else:
                return {
                    'status': 'PENDING',
                    'message': 'No payment received yet'
                }
        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f'Error checking payment: {e}'
            }


def generate_challan_id():
    """Generate unique challan ID"""
    return f"CHL{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"


def create_sample_data():
    """Create sample data for testing"""
    from .models import ViolationType, Vehicle
    
    # Create sample violation types with Indian Rupees
    violation_types = [
        {'name': 'Overspeeding', 'description': 'Driving above speed limit', 'penalty_amount': 1000.00},
        {'name': 'Red Light Violation', 'description': 'Running red traffic signal', 'penalty_amount': 1500.00},
        {'name': 'Illegal Parking', 'description': 'Parking in restricted area', 'penalty_amount': 750.00},
        {'name': 'No Helmet', 'description': 'Riding motorcycle without helmet', 'penalty_amount': 500.00},
        {'name': 'Drunk Driving', 'description': 'Driving under influence of alcohol', 'penalty_amount': 5000.00},
        {'name': 'Overloading', 'description': 'Carrying passengers beyond capacity', 'penalty_amount': 2000.00},
        {'name': 'No Seat Belt', 'description': 'Driving without seat belt', 'penalty_amount': 250.00},
        {'name': 'Illegal U-turn', 'description': 'Making unauthorized U-turn', 'penalty_amount': 1000.00},
        {'name': 'Wrong Lane Driving', 'description': 'Driving in wrong lane', 'penalty_amount': 1250.00},
        {'name': 'No Insurance', 'description': 'Driving without valid insurance', 'penalty_amount': 3000.00},
    ]
    
    for violation_data in violation_types:
        ViolationType.objects.get_or_create(
            name=violation_data['name'],
            defaults=violation_data
        )
    
    # Create sample vehicles
    sample_vehicles = [
        {'number_plate': 'ABC123', 'owner_name': 'John Doe', 'owner_email': 'john@example.com', 'owner_phone': '+1234567890'},
        {'number_plate': 'XYZ789', 'owner_name': 'Jane Smith', 'owner_email': 'jane@example.com', 'owner_phone': '+1234567891'},
        {'number_plate': 'DEF456', 'owner_name': 'Bob Johnson', 'owner_email': 'bob@example.com', 'owner_phone': '+1234567892'},
    ]
    
    for vehicle_data in sample_vehicles:
        Vehicle.objects.get_or_create(
            number_plate=vehicle_data['number_plate'],
            defaults=vehicle_data
        )