from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vehicle, Challan, ViolationType


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class VehicleImageUploadForm(forms.Form):
    """Form for uploading vehicle images"""
    image = forms.ImageField(
        label='Upload Vehicle Image',
        help_text='Upload a clear image of the vehicle showing the number plate'
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Location where violation occurred'})
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional description of the violation'})
    )


class ChallanForm(forms.ModelForm):
    """Form for creating challans"""
    violation_type = forms.ModelChoiceField(
        queryset=ViolationType.objects.all(),
        empty_label="Select violation type"
    )
    
    class Meta:
        model = Challan
        fields = ['violation_type', 'location', 'description']
        widgets = {
            'location': forms.TextInput(attrs={'placeholder': 'Location of violation'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description of the violation'}),
        }


class VehicleSearchForm(forms.Form):
    """Form for searching vehicles by number plate"""
    number_plate = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Enter vehicle number plate'})
    ) 