from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_migrate, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Event


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.name != 'events':
        return

    for role_name in ['Admin', 'Organizer', 'Participant']:
        Group.objects.get_or_create(name=role_name)


@receiver(post_save, sender=User)
def send_activation_email_on_register(sender, instance, created, **kwargs):
    if not created or instance.is_active or not instance.email:
        return

    uid = urlsafe_base64_encode(force_bytes(instance.pk))
    token = default_token_generator.make_token(instance)
    activation_path = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
    activation_url = f"{settings.ACTIVATION_BASE_URL.rstrip('/')}{activation_path}"

    send_mail(
        subject='Activate your Event Manager account',
        message=(
            f"Hi {instance.first_name or instance.username},\n\n"
            "Thanks for registering. Activate your account using this link:\n"
            f"{activation_url}\n\n"
            "If you did not register, you can ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[instance.email],
        fail_silently=True,
    )


@receiver(m2m_changed, sender=Event.rsvps.through)
def send_rsvp_email_notification(sender, instance, action, pk_set, **kwargs):
    if action != 'post_add' or not pk_set:
        return

    users = User.objects.filter(pk__in=pk_set).exclude(email='')
    for user in users:
        send_mail(
            subject=f'RSVP Confirmed: {instance.name}',
            message=(
                f"Hi {user.first_name or user.username},\n\n"
                f"Your RSVP for '{instance.name}' on {instance.date_time:%Y-%m-%d %H:%M} has been recorded.\n"
                f"Location: {instance.location or 'TBA'}\n\n"
                "Thank you."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
