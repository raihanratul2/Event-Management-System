from django.db import models
from django.contrib.auth.models import User

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
    rsvps = models.ManyToManyField(User, related_name='rsvp_events', blank=True)

    def __str__(self):
        return self.name + " - " + self.date_time.strftime("%Y-%m-%d %H:%M")
