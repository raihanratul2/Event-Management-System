from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from .forms import CategoryForm, EventForm, GroupCreateForm, LoginForm, RoleUpdateForm, SignUpForm
from .models import Category, Event


def in_group(user, groups):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=groups).exists())


def is_admin(user):
    return in_group(user, ['Admin'])


def is_organizer(user):
    return in_group(user, ['Admin', 'Organizer'])


def is_participant(user):
    return in_group(user, ['Participant'])


admin_required = user_passes_test(is_admin, login_url='login')
organizer_required = user_passes_test(is_organizer, login_url='login')
participant_required = user_passes_test(is_participant, login_url='login')


def redirect_dashboard_for_user(user):
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return 'admin_dashboard'
    if user.groups.filter(name='Organizer').exists():
        return 'organizer_dashboard'
    return 'participant_dashboard'

def home(request):
    if request.user.is_authenticated:
        return redirect(redirect_dashboard_for_user(request.user))
    return render(request, 'home.html')


class RoleAwareLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse(redirect_dashboard_for_user(self.request.user))


def signup(request):
    if request.user.is_authenticated:
        return redirect(redirect_dashboard_for_user(request.user))

    form = SignUpForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        participant_group, _ = Group.objects.get_or_create(name='Participant')
        user.groups.add(participant_group)
        messages.success(request, 'Account created. Check your email to activate your account.')
        return redirect('login')
    return render(request, 'signup.html', {'form': form})


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        messages.success(request, 'Your account has been activated. Please login.')
        return redirect('login')

    messages.error(request, 'Activation link is invalid or expired.')
    return redirect('home')


@login_required
def dashboard_redirect(request):
    return redirect(redirect_dashboard_for_user(request.user))


@admin_required
def admin_dashboard(request):
    context = {
        'events_count': Event.objects.count(),
        'categories_count': Category.objects.count(),
        'participants_count': User.objects.filter(groups__name='Participant').distinct().count(),
        'events': Event.objects.order_by('-date_time')[:5],
    }
    return render(request, 'dashboards/admin_dashboard.html', context)


@organizer_required
def organizer_dashboard(request):
    context = {
        'events_count': Event.objects.count(),
        'categories_count': Category.objects.count(),
        'events': Event.objects.order_by('-date_time')[:5],
    }
    return render(request, 'dashboards/organizer_dashboard.html', context)


@participant_required
def participant_dashboard(request):
    my_events = request.user.rsvp_events.select_related('category').order_by('-date_time')
    return render(request, 'dashboards/participant_dashboard.html', {'events': my_events})


# ─── Events ───────────────────────────────────────────────────────────────────
@login_required
def event_list(request):
    events = Event.objects.select_related('category').order_by('-date_time')
    return render(request, 'events/event_list.html', {'events': events})

@organizer_required
def add_event(request):
    form = EventForm()
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    return render(request, 'add_event.html', {'form': form})


@organizer_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, request.FILES or None, instance=event)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('event_list')
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})


@organizer_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
    return redirect('event_list')


@participant_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.rsvps.add(request.user)
        messages.success(request, f'RSVP confirmed for {event.name}.')
    return redirect('event_list')


# ─── Categories ───────────────────────────────────────────────────────────────
@organizer_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'events/category_list.html', {'categories': categories})

@organizer_required
def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    return render(request, 'events/add_category.html', {'form': form})


@organizer_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'events/edit_category.html', {'form': form, 'category': category})


@organizer_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
    return redirect('category_list')


# ─── Participants ─────────────────────────────────────────────────────────────
@admin_required
def participant_list(request):
    participants = User.objects.filter(groups__name='Participant').distinct().order_by('username')
    return render(request, 'events/participant_list.html', {'participants': participants})

@admin_required
def delete_participant(request, user_id):
    participant = get_object_or_404(User, pk=user_id, groups__name='Participant')
    if request.method == 'POST':
        participant.delete()
    return redirect('participant_list')


@admin_required
def manage_groups(request):
    form = GroupCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Group.objects.create(name=form.cleaned_data['name'])
        messages.success(request, 'Group created successfully.')
        return redirect('manage_groups')
    groups = Group.objects.all().order_by('name')
    return render(request, 'events/group_management.html', {'form': form, 'groups': groups})


@admin_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    protected_groups = {'Admin', 'Organizer', 'Participant'}
    if request.method == 'POST':
        if group.name in protected_groups:
            messages.error(request, 'Default role groups cannot be deleted.')
        else:
            group.delete()
            messages.success(request, 'Group deleted successfully.')
    return redirect('manage_groups')


@admin_required
def change_user_role(request):
    form = RoleUpdateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        group = form.cleaned_data['group']
        user.groups.clear()
        user.groups.add(group)
        messages.success(request, f'Role updated for {user.username}.')
        return redirect('change_user_role')
    return render(request, 'events/change_role.html', {'form': form})