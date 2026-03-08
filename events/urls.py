from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('login/', views.RoleAwareLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/organizer/', views.organizer_dashboard, name='organizer_dashboard'),
    path('dashboard/participant/', views.participant_dashboard, name='participant_dashboard'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),
    # Events
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/add/', views.AddEventView.as_view(), name='add_event'),
    path('events/<int:pk>/edit/', views.EditEventView.as_view(), name='edit_event'),
    path('events/<int:pk>/delete/', views.DeleteEventView.as_view(), name='delete_event'),
    path('events/<int:pk>/rsvp/', views.rsvp_event, name='rsvp_event'),
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.AddCategoryView.as_view(), name='add_category'),
    path('categories/<int:pk>/edit/', views.EditCategoryView.as_view(), name='edit_category'),
    path('categories/<int:pk>/delete/', views.DeleteCategoryView.as_view(), name='delete_category'),
    # Participants
    path('participants/', views.ParticipantListView.as_view(), name='participant_list'),
    path('participants/<int:user_id>/delete/', views.DeleteParticipantView.as_view(), name='delete_participant'),
    # Groups / Roles
    path('groups/', views.ManageGroupsView.as_view(), name='manage_groups'),
    path('groups/<int:group_id>/delete/', views.DeleteGroupView.as_view(), name='delete_group'),
    path('roles/change/', views.ChangeUserRoleView.as_view(), name='change_user_role'),
]