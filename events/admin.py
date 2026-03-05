from .models import Category, Event

from django.contrib import admin

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_time', 'location', 'category')
	search_fields = ('name', 'location')


admin.site.register(Category)
