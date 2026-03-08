from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import Group
from .models import Event, Category

User = get_user_model()

BASE_CLASSES = (
    "w-full rounded-xl bg-slate-900/60 border border-white/10 "
    "focus:border-brandGlow focus:ring-2 focus:ring-brandGlow/30 "
    "px-4 py-3 text-slate-50 placeholder:text-slate-500 transition"
)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'location', 'date_time', 'category', 'image']
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
            'image': forms.ClearableFileInput(attrs={
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


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': BASE_CLASSES, 'placeholder': 'email@example.com'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': 'First name'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': 'Last name'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'profile_picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': BASE_CLASSES, 'placeholder': 'email@example.com'}),
            'phone_number': forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': '+1234567890'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': BASE_CLASSES}),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class GroupCreateForm(forms.Form):
    name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': BASE_CLASSES, 'placeholder': 'Group name'}))

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Group.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError('Group already exists.')
        return name


class RoleUpdateForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={'class': BASE_CLASSES}))
    group = forms.ModelChoiceField(queryset=Group.objects.all(), widget=forms.Select(attrs={'class': BASE_CLASSES}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.order_by('username')
        self.fields['group'].queryset = Group.objects.order_by('name')