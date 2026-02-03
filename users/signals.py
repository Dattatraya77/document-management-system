from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create profile automatically when a new user is created.
    Also safe for existing users.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        # Prevent crash if profile does not exist
        Profile.objects.get_or_create(user=instance)
