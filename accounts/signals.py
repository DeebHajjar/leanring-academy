from django.db.models.signals import pre_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount
from .models import User

@receiver(pre_save, sender=SocialAccount)
def save_google_profile_info(sender, instance, **kwargs):
    """Save additional Google profile information"""
    if instance.provider == 'google':
        user = instance.user
        extra_data = instance.extra_data
        
        # Save Google ID
        if 'id' in extra_data:
            user.google_id = extra_data['id']
        
        # Save profile picture URL
        if 'picture' in extra_data:
            user.profile_picture_url = extra_data['picture']
        
        # Save first name if not already set
        if not user.first_name and 'given_name' in extra_data:
            user.first_name = extra_data['given_name']
        
        if not user.last_name and 'family_name' in extra_data:
            user.last_name = extra_data['family_name']
        
        user.save()
