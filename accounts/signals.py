"""
Signals for the accounts app.

Auto-creates a Profile when a new user is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser, Profile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a Profile instance when a new CustomUser is created.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the Profile instance when the CustomUser is saved.
    """
    # Check if profile exists before saving (handles existing users without profiles)
    if hasattr(instance, "profile"):
        instance.profile.save()
