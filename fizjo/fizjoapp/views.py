from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Fizjoterapeuta, Pacjent, Program
from .forms import FizjoForm, PacjentForm, ProgramForm

# Create your views here.
@login_required
def dashboard(request):
    fizjoterapeuci = Fizjoterapeuta.objects.all()
    pacjenci = Pacjent.objects.all()
    programy = Program.objects.all()

    context = {
        'fizjoterapeuci' : fizjoterapeuci,
        'pacjenci' : pacjenci,
        'programy' : programy
    }
    return render(request, 'dashboard.html', context)

def add_element(request, form_class, template_label):
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'formularz.html', {'form':form, 'tytul':template_label})

@login_required
def add_fizjo(request):
    return add_element(request, FizjoForm, "Dodaj Fizjoterapeutę")

@login_required
def add_pacjent(request):
    return add_element(request, PacjentForm, "Dodaj Pacjenta")

@login_required
def add_program(request):
    return add_element(request, ProgramForm, "Dodaj Program Ćwiczeniowy")

def rejestracja(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'registration/rejestracja.html', {'form':form})