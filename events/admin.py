from django.contrib.auth.admin import UserAdmin

from .models import Category, Event, User

from django.contrib import admin

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ('name', 'date_time', 'location', 'category')
	search_fields = ('name', 'location')


admin.site.register(Category)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	fieldsets = UserAdmin.fieldsets + (
		('Profile', {'fields': ('profile_picture', 'phone_number')}),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		('Profile', {'fields': ('profile_picture', 'phone_number')}),
	)
