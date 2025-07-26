from django import forms
from .models import User, Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'avatar', 'bio', 'country', 'city']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['website', 'linkedin', 'github', 'preferred_language', 'newsletter_subscription', 'email_notifications']
