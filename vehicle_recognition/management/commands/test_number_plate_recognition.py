from django.core.management.base import BaseCommand
from django.conf import settings
import os
from vehicle_recognition.utils import NumberPlateRecognition
import time

class Command(BaseCommand):
    help = 'Test the improved number plate recognition system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image-path',
            type=str,
            help='Path to test image (optional)',
        )
        parser.add_argument(
            '--test-all',
            action='store_true',
            help='Test all images in media/vehicle_images/',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚗 Testing Improved Number Plate Recognition System')
        )
        self.stdout.write('=' * 60)
        
        recognizer = NumberPlateRecognition()
        
        # Test with specific image
        if options['image_path']:
            self.test_single_image(recognizer, options['image_path'])
        
        # Test with all images in media folder
        elif options['test_all']:
            self.test_all_images(recognizer)
        
        # Default test with sample patterns
        else:
            self.test_sample_patterns(recognizer)
    
    def test_single_image(self, recognizer, image_path):
        """Test recognition with a specific image"""
        self.stdout.write(f'\n📸 Testing image: {image_path}')
        
        if not os.path.exists(image_path):
            self.stdout.write(
                self.style.ERROR(f'❌ Image not found: {image_path}')
            )
            return
        
        start_time = time.time()
        number_plate, confidence = recognizer.detect_number_plate(image_path)
        end_time = time.time()
        
        self.stdout.write(f'⏱️  Processing time: {end_time - start_time:.2f} seconds')
        
        if number_plate:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Detected: {number_plate} (Confidence: {confidence:.2f})')
            )
        else:
            self.stdout.write(
                self.style.WARNING('❌ No number plate detected')
            )
    
    def test_all_images(self, recognizer):
        """Test recognition with all images in media folder"""
        media_path = os.path.join(settings.MEDIA_ROOT, 'vehicle_images')
        
        if not os.path.exists(media_path):
            self.stdout.write(
                self.style.ERROR(f'❌ Media folder not found: {media_path}')
            )
            return
        
        image_files = [f for f in os.listdir(media_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        if not image_files:
            self.stdout.write(
                self.style.WARNING('⚠️  No image files found in media folder')
            )
            return
        
        self.stdout.write(f'\n📸 Testing {len(image_files)} images from media folder')
        self.stdout.write('=' * 60)
        
        total_time = 0
        successful_detections = 0
        
        for image_file in image_files:
            image_path = os.path.join(media_path, image_file)
            self.stdout.write(f'\n🔍 Testing: {image_file}')
            
            start_time = time.time()
            number_plate, confidence = recognizer.detect_number_plate(image_path)
            end_time = time.time()
            
            processing_time = end_time - start_time
            total_time += processing_time
            
            if number_plate:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {number_plate} (Confidence: {confidence:.2f}, Time: {processing_time:.2f}s)')
                )
                successful_detections += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'❌ No detection (Time: {processing_time:.2f}s)')
                )
        
        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(
            self.style.SUCCESS(f'📊 Summary:')
        )
        self.stdout.write(f'   Total images: {len(image_files)}')
        self.stdout.write(f'   Successful detections: {successful_detections}')
        self.stdout.write(f'   Success rate: {(successful_detections/len(image_files)*100):.1f}%')
        self.stdout.write(f'   Average processing time: {total_time/len(image_files):.2f}s')
    
    def test_sample_patterns(self, recognizer):
        """Test with sample number plate patterns"""
        self.stdout.write('\n🧪 Testing with sample patterns')
        self.stdout.write('=' * 60)
        
        # Sample Indian number plate patterns
        sample_patterns = [
            "KA01AB1234",  # Karnataka format
            "DL12CD5678",  # Delhi format
            "MH34EF9012",  # Maharashtra format
            "TN56GH3456",  # Tamil Nadu format
            "AP78IJ7890",  # Andhra Pradesh format
            "KL90KL1234",  # Kerala format
            "HR12MN5678",  # Haryana format
            "GJ34OP9012",  # Gujarat format
            "UP56QR3456",  # Uttar Pradesh format
            "MP78ST7890",  # Madhya Pradesh format
        ]
        
        self.stdout.write('📋 Sample patterns to test:')
        for pattern in sample_patterns:
            self.stdout.write(f'   {pattern}')
        
        self.stdout.write('\n💡 To test with actual images:')
        self.stdout.write('   python manage.py test_number_plate_recognition --test-all')
        self.stdout.write('   python manage.py test_number_plate_recognition --image-path path/to/image.jpg')
        
        # Test pattern validation
        self.stdout.write('\n🔍 Testing pattern validation:')
        for pattern in sample_patterns:
            is_valid, confidence = recognizer.validate_number_plate(pattern)
            if is_valid:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {pattern} (Confidence: {confidence:.2f})')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {pattern} (Invalid)')
                )
        
        # Test invalid patterns
        invalid_patterns = [
            "ABC",           # Too short
            "ABCDEFGHIJKLMNOP",  # Too long
            "123456",        # Numbers only
            "ABCDEF",        # Letters only
            "AB@123",        # Invalid characters
        ]
        
        self.stdout.write('\n❌ Testing invalid patterns:')
        for pattern in invalid_patterns:
            is_valid, confidence = recognizer.validate_number_plate(pattern)
            if not is_valid:
                self.stdout.write(
                    self.style.WARNING(f'✅ {pattern} correctly rejected')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {pattern} incorrectly accepted')
                )
    
    def test_ocr_engines(self, recognizer):
        """Test different OCR engines"""
        self.stdout.write('\n🔧 Testing OCR engines availability:')
        
        # Check EasyOCR
        if hasattr(recognizer, 'easyocr_reader') and recognizer.easyocr_reader:
            self.stdout.write(
                self.style.SUCCESS('✅ EasyOCR available')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  EasyOCR not available')
            )
        
        # Check Tesseract
        try:
            import pytesseract
            self.stdout.write(
                self.style.SUCCESS('✅ PyTesseract available')
            )
        except ImportError:
            self.stdout.write(
                self.style.WARNING('⚠️  PyTesseract not available')
            )
        
        # Check TensorFlow
        try:
            import tensorflow as tf
            self.stdout.write(
                self.style.SUCCESS('✅ TensorFlow available')
            )
        except ImportError:
            self.stdout.write(
                self.style.WARNING('⚠️  TensorFlow not available')
            ) 