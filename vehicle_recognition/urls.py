from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='vehicle_recognition/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Image upload and recognition
    path('upload/', views.upload_image, name='upload_image'),
    path('search-vehicle/', views.search_vehicle, name='search_vehicle'),
    
    # Challan management
    path('create-challan/<int:vehicle_id>/', views.create_challan, name='create_challan'),
    path('challans/', views.challan_list, name='challan_list'),
    path('challan/<str:challan_id>/', views.challan_detail, name='challan_detail'),
    
    # Payment routes (for vehicle owners)
    path('pay-challan/<str:challan_id>/', views.pay_challan, name='pay_challan'),
    path('payment-success/<str:challan_id>/', views.payment_success, name='payment_success'),
    
    # Vehicle management
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    
    # AJAX endpoints
    path('ajax/detect-number-plate/', views.ajax_number_plate_detection, name='ajax_number_plate_detection'),
    
    # Setup
    path('setup-sample-data/', views.setup_sample_data, name='setup_sample_data'),
] 