from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
import os
import json
import re

from .forms import UserRegistrationForm, VehicleImageUploadForm, ChallanForm, VehicleSearchForm
from .models import Vehicle, Challan, ViolationType, Payment, UploadedImage
from .utils import NumberPlateRecognition, NotificationService, PaymentService, generate_challan_id, create_sample_data


def home(request):
    """Home page view"""
    return render(request, 'vehicle_recognition/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the Vehicle Recognition System.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'vehicle_recognition/register.html', {'form': form})


@login_required
def dashboard(request):
    """Admin dashboard view"""
    # Get statistics
    total_vehicles = Vehicle.objects.count()
    total_challans = Challan.objects.count()
    pending_challans = Challan.objects.filter(status='PENDING').count()
    paid_challans = Challan.objects.filter(status='PAID').count()
    
    # Get recent challans
    recent_challans = Challan.objects.select_related('vehicle', 'violation_type').order_by('-created_at')[:5]
    
    context = {
        'total_vehicles': total_vehicles,
        'total_challans': total_challans,
        'pending_challans': pending_challans,
        'paid_challans': paid_challans,
        'recent_challans': recent_challans,
    }
    
    return render(request, 'vehicle_recognition/dashboard.html', context)


@login_required
def upload_image(request):
    """Image upload and number plate recognition view"""
    if request.method == 'POST':
        form = VehicleImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded image
            uploaded_image = UploadedImage.objects.create(
                image=form.cleaned_data['image']
            )
            
            manual_plate = (form.cleaned_data.get('manual_number_plate') or '').strip().upper()
            manual_plate = re.sub(r'[^A-Z0-9]', '', manual_plate) if manual_plate else ''

            number_plate = None
            confidence = 0.0

            if manual_plate:
                number_plate = manual_plate
                confidence = 1.0
            else:
                recognizer = NumberPlateRecognition()
                image_path = uploaded_image.image.path
                number_plate, confidence = recognizer.detect_number_plate(image_path)

            uploaded_image.number_plate_detected = number_plate or ''
            uploaded_image.confidence_score = confidence
            uploaded_image.processed = True
            uploaded_image.save()

            if number_plate:
                # Try to find vehicle in database
                try:
                    vehicle = Vehicle.objects.get(number_plate=number_plate.upper())
                    messages.success(request, f'Number plate detected: {number_plate} (Confidence: {confidence:.2f})')
                    return redirect('create_challan', vehicle_id=vehicle.id)
                except Vehicle.DoesNotExist:
                    messages.warning(request, f'Vehicle with number plate {number_plate} not found in database. Please add the vehicle first.')
                    return redirect('add_vehicle')
            else:
                messages.error(
                    request,
                    'Could not detect number plate automatically. '
                    'Install Tesseract OCR on this machine, or enter the plate manually in the optional field and upload again.'
                )
                return redirect('upload_image')
    else:
        form = VehicleImageUploadForm()
    
    return render(request, 'vehicle_recognition/upload_image.html', {'form': form})


@login_required
def search_vehicle(request):
    """Vehicle search view"""
    if request.method == 'POST':
        form = VehicleSearchForm(request.POST)
        if form.is_valid():
            number_plate = form.cleaned_data['number_plate']
            try:
                vehicle = Vehicle.objects.get(number_plate=number_plate.upper())
                return redirect('create_challan', vehicle_id=vehicle.id)
            except Vehicle.DoesNotExist:
                messages.error(request, f'Vehicle with number plate {number_plate} not found.')
    else:
        form = VehicleSearchForm()
    
    return render(request, 'vehicle_recognition/search_vehicle.html', {'form': form})


@login_required
def create_challan(request, vehicle_id):
    """Create challan view"""
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if request.method == 'POST':
        form = ChallanForm(request.POST)
        if form.is_valid():
            challan = form.save(commit=False)
            challan.challan_id = generate_challan_id()
            challan.vehicle = vehicle
            challan.penalty_amount = challan.violation_type.penalty_amount
            challan.created_by = request.user
            challan.violation_date = timezone.now()
            challan.save()
            
            # Send notifications to vehicle owner
            NotificationService.send_email_notification(challan)
            NotificationService.send_sms_notification(challan)
            
            messages.success(request, f'Challan {challan.challan_id} created successfully! Email and SMS sent to vehicle owner.')
            return redirect('challan_detail', challan_id=challan.challan_id)
    else:
        form = ChallanForm()
    
    context = {
        'vehicle': vehicle,
        'form': form,
    }
    
    return render(request, 'vehicle_recognition/create_challan.html', context)


@login_required
def challan_list(request):
    """List all challans with pagination and search"""
    challans = Challan.objects.select_related('vehicle', 'violation_type', 'created_by').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        challans = challans.filter(
            Q(challan_id__icontains=search_query) |
            Q(vehicle__number_plate__icontains=search_query) |
            Q(vehicle__owner_name__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        challans = challans.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(challans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'vehicle_recognition/challan_list.html', context)


@login_required
def challan_detail(request, challan_id):
    """Challan detail view - Admin can only check payment status"""
    challan = get_object_or_404(Challan, challan_id=challan_id)
    
    # Get payment status for admin to check
    payment_status = PaymentService.get_payment_status(challan)
    
    context = {
        'challan': challan,
        'payment_status': payment_status,
    }
    
    return render(request, 'vehicle_recognition/challan_detail.html', context)


def pay_challan(request, challan_id):
    """Public payment page for vehicle owners to pay challan with improved error handling"""
    try:
        challan = get_object_or_404(Challan, challan_id=challan_id)
        
        # Check if challan is already paid
        if challan.status == 'PAID':
            messages.info(request, 'This challan has already been paid.')
            return redirect('payment_success', challan_id=challan.challan_id)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method')
            transaction_id = request.POST.get('transaction_id', '').strip()
            card_number = request.POST.get('card_number', '').strip()
            card_holder = request.POST.get('card_holder', '').strip()
            expiry_date = request.POST.get('expiry_date', '').strip()
            cvv = request.POST.get('cvv', '').strip()
            
            # Validate payment method
            if not payment_method:
                messages.error(request, 'Please select a payment method.')
                return render(request, 'vehicle_recognition/pay_challan.html', {'challan': challan})
            
            # Validate card details for card payments
            if payment_method in ['Credit Card', 'Debit Card']:
                if not all([card_number, card_holder, expiry_date, cvv]):
                    messages.error(request, 'Please fill in all card details.')
                    return render(request, 'vehicle_recognition/pay_challan.html', {'challan': challan})
                
                # Basic card validation
                if len(card_number.replace(' ', '')) < 13 or len(card_number.replace(' ', '')) > 19:
                    messages.error(request, 'Please enter a valid card number.')
                    return render(request, 'vehicle_recognition/pay_challan.html', {'challan': challan})
                
                if len(cvv) < 3 or len(cvv) > 4:
                    messages.error(request, 'Please enter a valid CVV.')
                    return render(request, 'vehicle_recognition/pay_challan.html', {'challan': challan})
            
            # Validate UPI ID for UPI payments
            elif payment_method == 'UPI':
                upi_id = request.POST.get('upi_id', '').strip()
                if not upi_id or '@' not in upi_id:
                    messages.error(request, 'Please enter a valid UPI ID.')
                    return render(request, 'vehicle_recognition/pay_challan.html', {'challan': challan})
            
            # Validate net banking details
            elif payment_method == 'Net Banking':
                bank_name = request.POST.get('bank_name', '').strip()
                if not bank_name:
                    messages.error(request, 'Please select your bank.')
                    return render(request, 'vehicle_recognition/pay_challan.html', {'challan': challan})
            
            # Process payment
            try:
                payment, message = PaymentService.process_payment(challan, payment_method, transaction_id)
                if payment:
                    messages.success(request, f'Payment processed successfully! Payment ID: {payment.payment_id}')
                    return redirect('payment_success', challan_id=challan.challan_id)
                else:
                    messages.error(request, f'Payment failed: {message}')
            except Exception as e:
                messages.error(request, f'Payment processing error: {str(e)}')
        
        context = {
            'challan': challan,
        }
        
        return render(request, 'vehicle_recognition/pay_challan.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading payment page: {str(e)}')
        return redirect('home')


def payment_success(request, challan_id):
    """Payment success page"""
    challan = get_object_or_404(Challan, challan_id=challan_id)
    
    context = {
        'challan': challan,
    }
    
    return render(request, 'vehicle_recognition/payment_success.html', context)


@login_required
def vehicle_list(request):
    """List all vehicles"""
    vehicles = Vehicle.objects.all().order_by('number_plate')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        vehicles = vehicles.filter(
            Q(number_plate__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(owner_email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(vehicles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'vehicle_recognition/vehicle_list.html', context)


@login_required
def add_vehicle(request):
    """Add new vehicle"""
    if request.method == 'POST':
        number_plate = request.POST.get('number_plate')
        owner_name = request.POST.get('owner_name')
        owner_email = request.POST.get('owner_email')
        owner_phone = request.POST.get('owner_phone')
        vehicle_type = request.POST.get('vehicle_type', 'Car')
        
        if number_plate and owner_name and owner_email:
            vehicle, created = Vehicle.objects.get_or_create(
                number_plate=number_plate.upper(),
                defaults={
                    'owner_name': owner_name,
                    'owner_email': owner_email,
                    'owner_phone': owner_phone,
                    'vehicle_type': vehicle_type,
                }
            )
            
            if created:
                messages.success(request, f'Vehicle {vehicle.number_plate} added successfully!')
            else:
                messages.info(request, f'Vehicle {vehicle.number_plate} already exists.')
            
            return redirect('vehicle_list')
        else:
            messages.error(request, 'Please fill all required fields.')
    
    return render(request, 'vehicle_recognition/add_vehicle.html')


@csrf_exempt
def ajax_number_plate_detection(request):
    """AJAX endpoint for number plate detection"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_path = data.get('image_path')
            
            if image_path and os.path.exists(image_path):
                recognizer = NumberPlateRecognition()
                number_plate, confidence = recognizer.detect_number_plate(image_path)
                
                return JsonResponse({
                    'success': True,
                    'number_plate': number_plate,
                    'confidence': confidence
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Image path not found'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def setup_sample_data(request):
    """Setup sample data for testing"""
    if request.user.is_superuser:
        create_sample_data()
        messages.success(request, 'Sample data created successfully!')
    else:
        messages.error(request, 'Only superusers can setup sample data.')
    
    return redirect('dashboard') 