from django import forms
from .models import Event, Category, Participant

BASE_CLASSES = (
    "w-full rounded-xl bg-slate-900/60 border border-white/10 "
    "focus:border-brandGlow focus:ring-2 focus:ring-brandGlow/30 "
    "px-4 py-3 text-slate-50 placeholder:text-slate-500 transition"
)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'date_time', 'category']
        labels = {
            'name': 'Event Name',
            'description': 'Event Description',
            'location': 'Event Location',
            'date_time': 'Event Date and Time',
            'category': 'Event Category',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': BASE_CLASSES,
                'placeholder': 'Enter event name',
            }),
            'description': forms.Textarea(attrs={
                'class': BASE_CLASSES,
                'rows': 4,
                'placeholder': 'Describe the event',
            }),
            'location': forms.TextInput(attrs={
                'class': BASE_CLASSES,
                'placeholder': 'Venue or meeting link',
            }),
            'date_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': BASE_CLASSES,
            }),
            'category': forms.Select(attrs={
                'class': BASE_CLASSES,
            }),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Category Name',
            'description': 'Category Description',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': BASE_CLASSES,
                'placeholder': 'Enter category name',
            }),
            'description': forms.Textarea(attrs={
                'class': BASE_CLASSES,
                'rows': 3,
                'placeholder': 'Describe this category',
            }),
        }


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email', 'event']
        labels = {
            'name': 'Participant Name',
            'email': 'Email Address',
            'event': 'Events',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': BASE_CLASSES,
                'placeholder': 'Full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': BASE_CLASSES,
                'placeholder': 'email@example.com',
            }),
            'event': forms.SelectMultiple(attrs={
                'class': BASE_CLASSES,
            }),
        }