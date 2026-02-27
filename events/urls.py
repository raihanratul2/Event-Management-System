from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    # Participants
    path('participants/', views.participant_list, name='participant_list'),
    path('participants/add/', views.add_participant, name='add_participant'),
]