from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Vehicle(models.Model):
    """Model for storing vehicle information"""
    number_plate = models.CharField(max_length=20, unique=True)
    owner_name = models.CharField(max_length=100)
    owner_email = models.EmailField()
    owner_phone = models.CharField(max_length=15)
    vehicle_type = models.CharField(max_length=50, default='Car')
    registration_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.number_plate} - {self.owner_name}"


class ViolationType(models.Model):
    """Model for different types of traffic violations"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} - ${self.penalty_amount}"


class Challan(models.Model):
    """Model for storing challan information"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    challan_id = models.CharField(max_length=20, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    violation_type = models.ForeignKey(ViolationType, on_delete=models.CASCADE)
    violation_date = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    penalty_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Challan {self.challan_id} - {self.vehicle.number_plate}"


class Payment(models.Model):
    """Model for storing payment information"""
    challan = models.OneToOneField(Challan, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.challan.challan_id}"


class UploadedImage(models.Model):
    """Model for storing uploaded vehicle images"""
    image = models.ImageField(upload_to='vehicle_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    number_plate_detected = models.CharField(max_length=20, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"Image {self.id} - {self.uploaded_at}" 