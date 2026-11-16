from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.services import create_notification


@receiver(signal=post_save, sender=User, dispatch_uid="post-save-uid123")
def on_user_creation(sender, instance, created, **kwargs):

    if created and isinstance(instance, User):
        create_notification(instance, f"Welcome to your account, {instance.username}!")
