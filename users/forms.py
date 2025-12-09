
from django import forms
from django.contrib.auth.forms import SetPasswordForm as AuthSetPasswordForm
from django.core.exceptions import ValidationError
from .models import User
from django.db.models import Q


class SignupForm(forms.ModelForm):
    contact_info = forms.CharField(
        label="Email or Phone Number",
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your email or phone number'})
    )

    class Meta:
        model = User
        fields = ['username', 'contact_info']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username
    
    def clean_contact_info(self):
        contact_info = self.cleaned_data.get('contact_info')
        if '@' in contact_info:
            if User.objects.filter(email=contact_info).exists():
                raise ValidationError("A user with that email already exists.")
        else:
            if User.objects.filter(phone_number=contact_info).exists():
                raise ValidationError("A user with that phone number already exists.")
        return contact_info


class SetPasswordForm(AuthSetPasswordForm):
    age = forms.IntegerField(
        required=False,
        min_value=13,
        label="Your Age",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 21'})
    )

    preferred_city = forms.CharField(
        required=False,
        label="Preferred City",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Coimbatore'
        })
    )
    
    preferred_area = forms.ChoiceField(
        required=False,
        label="Preferred Area in City",
    )

    taste_tags = forms.CharField(
        required=False,
        label="Your Tastes",
        help_text="Comma-separated tags like vegetarian, spicy, cozy",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'list': 'taste-suggestions',
            'placeholder': 'e.g., vegetarian, chettinad, cozy'
        })
    )


class LoginForm(forms.Form):
    login = forms.CharField(
        label="Username, Email, or Phone",
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Enter username, email, or phone'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )


class ForgotPasswordForm(forms.Form):
    contact_info = forms.CharField(
        label="Email or Phone Number",
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your email or phone number'})
    )


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'profile_photo', 'username', 'email', 'phone_number', 
            'age', 'preferred_city', 'preferred_area', 
            'preferred_price', 'taste_tags'
        ]
        
        widgets = {
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +919876543210'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'preferred_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Coimbatore'}),
            'preferred_area': forms.Select(attrs={'class': 'form-select'}),
            'preferred_price': forms.Select(attrs={'class': 'form-select'}),
            'taste_tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., vegetarian, cozy'}),
        }
        
        labels = {
            'profile_photo': 'Change Profile Photo',
            'preferred_area': 'Preferred Area (e.g., RS Puram, Hopes)',
            'preferred_price': 'Your Preferred Price Range',
            'taste_tags': 'Your Tastes (Comma-separated)'
        }