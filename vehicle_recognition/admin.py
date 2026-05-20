from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Vehicle, ViolationType, Challan, Payment, UploadedImage


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('number_plate', 'owner_name', 'owner_email', 'owner_phone', 'vehicle_type', 'registration_date', 'total_challans', 'total_paid')
    list_filter = ('vehicle_type', 'registration_date')
    search_fields = ('number_plate', 'owner_name', 'owner_email')
    ordering = ('number_plate',)
    
    def total_challans(self, obj):
        return obj.challan_set.count()
    total_challans.short_description = 'Total Challans'
    
    def total_paid(self, obj):
        paid_count = obj.challan_set.filter(status='PAID').count()
        total_count = obj.challan_set.count()
        if total_count > 0:
            percentage = (paid_count / total_count) * 100
            return format_html('<span style="color: {};">{}/{} ({:.1f}%)</span>', 
                             'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red',
                             paid_count, total_count, percentage)
        return '0/0 (0%)'
    total_paid.short_description = 'Paid/Total'


@admin.register(ViolationType)
class ViolationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'penalty_amount', 'description', 'total_violations')
    list_filter = ('penalty_amount',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    def total_violations(self, obj):
        return obj.challan_set.count()
    total_violations.short_description = 'Total Violations'


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ('challan_id', 'vehicle_info', 'violation_type', 'penalty_amount', 'status_badge', 'payment_info', 'created_at', 'created_by')
    list_filter = ('status', 'violation_type', 'created_at', 'paid_at')
    search_fields = ('challan_id', 'vehicle__number_plate', 'vehicle__owner_name', 'vehicle__owner_email')
    ordering = ('-created_at',)
    readonly_fields = ('challan_id', 'created_at', 'paid_at', 'payment_status_info')
    
    fieldsets = (
        ('Challan Information', {
            'fields': ('challan_id', 'vehicle', 'violation_type', 'penalty_amount', 'status')
        }),
        ('Violation Details', {
            'fields': ('violation_date', 'location', 'description')
        }),
        ('Payment Information', {
            'fields': ('payment_status_info', 'paid_at'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def vehicle_info(self, obj):
        return format_html(
            '<div><strong>{}</strong><br/>'
            '<small>Owner: {}<br/>'
            'Email: {}<br/>'
            'Phone: {}</small></div>',
            obj.vehicle.number_plate,
            obj.vehicle.owner_name,
            obj.vehicle.owner_email,
            obj.vehicle.owner_phone
        )
    vehicle_info.short_description = 'Vehicle & Owner Info'
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'PAID': 'green',
            'CANCELLED': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status
        )
    status_badge.short_description = 'Status'
    
    def payment_info(self, obj):
        if obj.status == 'PAID' and hasattr(obj, 'payment_set') and obj.payment_set.exists():
            payment = obj.payment_set.first()
            return format_html(
                '<div><strong>✅ Paid</strong><br/>'
                '<small>Method: {}<br/>'
                'Date: {}<br/>'
                'ID: {}</small></div>',
                payment.payment_method,
                payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                payment.payment_id
            )
        elif obj.status == 'PENDING':
            return format_html(
                '<span style="color: orange;">⏳ Pending Payment</span><br/>'
                '<small><a href="{}" target="_blank">View Payment Page</a></small>',
                reverse('pay_challan', args=[obj.challan_id])
            )
        else:
            return format_html('<span style="color: red;">❌ No Payment</span>')
    payment_info.short_description = 'Payment Status'
    
    def payment_status_info(self, obj):
        if obj.status == 'PAID' and hasattr(obj, 'payment_set') and obj.payment_set.exists():
            payment = obj.payment_set.first()
            return format_html(
                '<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">'
                '<h4>Payment Details:</h4>'
                '<p><strong>Payment ID:</strong> {}</p>'
                '<p><strong>Amount:</strong> ₹{}</p>'
                '<p><strong>Method:</strong> {}</p>'
                '<p><strong>Date:</strong> {}</p>'
                '<p><strong>Transaction ID:</strong> {}</p>'
                '</div>',
                payment.payment_id,
                payment.amount,
                payment.payment_method,
                payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                payment.transaction_id or 'N/A'
            )
        else:
            return format_html(
                '<div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7;">'
                '<h4>Payment Pending</h4>'
                '<p>This challan has not been paid yet.</p>'
                '<p><a href="{}" target="_blank" class="button">View Payment Page</a></p>'
                '</div>',
                reverse('pay_challan', args=[obj.challan_id])
            )
    payment_status_info.short_description = 'Payment Information'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'challan_info', 'amount', 'payment_method', 'payment_date', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('payment_id', 'challan__challan_id', 'challan__vehicle__number_plate', 'challan__vehicle__owner_name')
    ordering = ('-payment_date',)
    readonly_fields = ('payment_id', 'payment_date', 'challan_info_detailed')
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'challan', 'amount', 'payment_method', 'transaction_id')
        }),
        ('Challan Details', {
            'fields': ('challan_info_detailed',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('payment_date',),
            'classes': ('collapse',)
        }),
    )
    
    def challan_info(self, obj):
        challan = obj.challan
        return format_html(
            '<div><strong>Challan: {}</strong><br/>'
            '<small>Vehicle: {}<br/>'
            'Owner: {}<br/>'
            'Violation: {}</small></div>',
            challan.challan_id,
            challan.vehicle.number_plate,
            challan.vehicle.owner_name,
            challan.violation_type.name
        )
    challan_info.short_description = 'Challan Information'
    
    def challan_info_detailed(self, obj):
        challan = obj.challan
        return format_html(
            '<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">'
            '<h4>Challan Details:</h4>'
            '<p><strong>Challan ID:</strong> {}</p>'
            '<p><strong>Vehicle Number:</strong> {}</p>'
            '<p><strong>Owner Name:</strong> {}</p>'
            '<p><strong>Owner Email:</strong> {}</p>'
            '<p><strong>Owner Phone:</strong> {}</p>'
            '<p><strong>Violation Type:</strong> {}</p>'
            '<p><strong>Penalty Amount:</strong> ₹{}</p>'
            '<p><strong>Violation Date:</strong> {}</p>'
            '<p><strong>Location:</strong> {}</p>'
            '<p><strong>Description:</strong> {}</p>'
            '</div>',
            challan.challan_id,
            challan.vehicle.number_plate,
            challan.vehicle.owner_name,
            challan.vehicle.owner_email,
            challan.vehicle.owner_phone,
            challan.violation_type.name,
            challan.penalty_amount,
            challan.violation_date.strftime('%Y-%m-%d %H:%M'),
            challan.location or 'Not specified',
            challan.description or 'No additional details'
        )
    challan_info_detailed.short_description = 'Detailed Challan Information'


@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'uploaded_at', 'processed', 'number_plate_detected', 'confidence_score')
    list_filter = ('processed', 'uploaded_at')
    search_fields = ('number_plate_detected',)
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at', 'image_preview_large')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 60px; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Image Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px; border-radius: 8px; border: 2px solid #ddd;" />',
                obj.image.url
            )
        return "No Image"
    image_preview_large.short_description = 'Image Preview (Large)' 