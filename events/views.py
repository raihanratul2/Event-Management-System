from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import CategoryForm, EventForm, GroupCreateForm, LoginForm, ProfileUpdateForm, RoleUpdateForm, SignUpForm
from .models import Category, Event

User = get_user_model()


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


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_groups = []

    def test_func(self):
        return in_group(self.request.user, self.allowed_groups)

    def handle_no_permission(self):
        return redirect('login')


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_groups = ['Admin']


class OrganizerRequiredMixin(RoleRequiredMixin):
    allowed_groups = ['Admin', 'Organizer']


class ParticipantRequiredMixin(RoleRequiredMixin):
    allowed_groups = ['Participant']


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
class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    ordering = ['-date_time']

    def get_queryset(self):
        return Event.objects.select_related('category').order_by('-date_time')


class AddEventView(OrganizerRequiredMixin, CreateView):
    form_class = EventForm
    template_name = 'add_event.html'
    success_url = reverse_lazy('event_list')


class EditEventView(OrganizerRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/edit_event.html'
    success_url = reverse_lazy('event_list')
    context_object_name = 'event'


class DeleteEventView(OrganizerRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        event.delete()
        return redirect('event_list')

    def get(self, request, pk):
        return redirect('event_list')


@participant_required
def rsvp_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.rsvps.add(request.user)
        messages.success(request, f'RSVP confirmed for {event.name}.')
    return redirect('event_list')


# ─── Categories ───────────────────────────────────────────────────────────────
class CategoryListView(OrganizerRequiredMixin, ListView):
    model = Category
    template_name = 'events/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.all()


class AddCategoryView(OrganizerRequiredMixin, CreateView):
    form_class = CategoryForm
    template_name = 'events/add_category.html'
    success_url = reverse_lazy('category_list')


class EditCategoryView(OrganizerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'events/edit_category.html'
    success_url = reverse_lazy('category_list')
    context_object_name = 'category'


class DeleteCategoryView(OrganizerRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return redirect('category_list')

    def get(self, request, pk):
        return redirect('category_list')


# ─── Participants ─────────────────────────────────────────────────────────────
class ParticipantListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'events/participant_list.html'
    context_object_name = 'participants'

    def get_queryset(self):
        return User.objects.filter(groups__name='Participant').distinct().order_by('username')


class DeleteParticipantView(AdminRequiredMixin, View):
    def post(self, request, user_id):
        participant = get_object_or_404(User, pk=user_id, groups__name='Participant')
        participant.delete()
        return redirect('participant_list')

    def get(self, request, user_id):
        return redirect('participant_list')


class ManageGroupsView(AdminRequiredMixin, View):
    template_name = 'events/group_management.html'

    def get(self, request):
        form = GroupCreateForm()
        groups = Group.objects.all().order_by('name')
        return render(request, self.template_name, {'form': form, 'groups': groups})

    def post(self, request):
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            Group.objects.create(name=form.cleaned_data['name'])
            messages.success(request, 'Group created successfully.')
            return redirect('manage_groups')
        groups = Group.objects.all().order_by('name')
        return render(request, self.template_name, {'form': form, 'groups': groups})


class DeleteGroupView(AdminRequiredMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, pk=group_id)
        protected_groups = {'Admin', 'Organizer', 'Participant'}
        if group.name in protected_groups:
            messages.error(request, 'Default role groups cannot be deleted.')
        else:
            group.delete()
            messages.success(request, 'Group deleted successfully.')
        return redirect('manage_groups')

    def get(self, request, group_id):
        return redirect('manage_groups')


class ChangeUserRoleView(AdminRequiredMixin, View):
    template_name = 'events/change_role.html'

    def get(self, request):
        form = RoleUpdateForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RoleUpdateForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            group = form.cleaned_data['group']
            user.groups.clear()
            user.groups.add(group)
            messages.success(request, f'Role updated for {user.username}.')
            return redirect('change_user_role')
        return render(request, self.template_name, {'form': form})


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/profile_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.request.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = 'profile/profile_edit.html'
    success_url = reverse_lazy('profile_detail')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'profile/change_password.html'
    success_url = reverse_lazy('profile_detail')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully.')
        return super().form_valid(form)