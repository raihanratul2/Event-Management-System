from .models import Category, Event, Participant

from django.contrib import admin

admin.site.register(Event)
admin.site.register(Category)
admin.site.register(Participant)
