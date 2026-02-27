from django.shortcuts import render, redirect
from .forms import EventForm, CategoryForm, ParticipantForm
from .models import Event, Category, Participant


def home(request):
    return render(request, 'home.html')


# ─── Events ───────────────────────────────────────────────────────────────────
def event_list(request):
    events = Event.objects.select_related('category').order_by('-date_time')
    return render(request, 'events/event_list.html', {'events': events})


def add_event(request):
    form = EventForm()
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    return render(request, 'add_event.html', {'form': form})


# ─── Categories ───────────────────────────────────────────────────────────────
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'events/category_list.html', {'categories': categories})


def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    return render(request, 'events/add_category.html', {'form': form})


# ─── Participants ─────────────────────────────────────────────────────────────
def participant_list(request):
    participants = Participant.objects.prefetch_related('event').all()
    return render(request, 'events/participant_list.html', {'participants': participants})


def add_participant(request):
    form = ParticipantForm()
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('participant_list')
    return render(request, 'events/add_participant.html', {'form': form})