from django import forms
from django.contrib.auth.models import User
from .models import Booking, Review, Profile # <--- Add Profile


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['customer_name', 'phone_number', 'location', 'service']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }

# --- NEW REVIEW FORM ---
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['customer_name', 'rating', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'rating': forms.Select(choices=[(5, '⭐⭐⭐⭐⭐ (Excellent)'), (4, '⭐⭐⭐⭐ (Good)'), (3, '⭐⭐⭐ (Average)'), (2, '⭐⭐ (Poor)'), (1, '⭐ (Bad)')], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience...'}),
        }

# --- PROFILE UPDATE FORMS ---
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile_number']
        widgets = {
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91...'}),
        }