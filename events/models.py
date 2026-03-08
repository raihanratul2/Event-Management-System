from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/default-avatar.svg')
    phone_number = models.CharField(
        max_length=16,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{7,15}$',
                message='Enter a valid phone number with 7 to 15 digits, optionally starting with +.',
            )
        ],
    )

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
     
    def __str__(self):
        return self.name



class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='events',null=True, blank=True)
    image = models.ImageField(upload_to='events/', default='events/default_event.svg')
    rsvps = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rsvp_events', blank=True)

    def __str__(self):
        return self.name + " - " + self.date_time.strftime("%Y-%m-%d %H:%M")
