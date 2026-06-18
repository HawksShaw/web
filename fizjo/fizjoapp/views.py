from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from .models import Fizjoterapeuta, Pacjent, Program
from .forms import FizjoForm, PacjentForm, ProgramForm, RejestrForm, LoginForm

# Create your views here.
@login_required
def dashboard(request):
    if hasattr(request.user, 'fizjoterapeuta'):
        return redirect('dashboard_fizjo')
    elif hasattr(request.user, 'pacjent'):
        return redirect('dashboard_pacjent')
    else:
        return render(request, 'dashboard.html')

@login_required
def dashboard_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    
    context = {
        'fizjoterapeuci' : Fizjoterapeuta.objects.all(),
        'pacjenci' : Pacjent.objects.all(),
        'programy' : Program.objects.all(),
    }
    return render(request, 'dashboard_fizjo.html', context)

@login_required
def dashboard_pacjent(request):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    
    pacjent_programy = Program.objects.filter(pacjent=request.user.pacjent)

    context = {
        'programy' : pacjent_programy,
    }

    return render(request, 'dashboard_pacjent.html', context)

def dodaj_element(request, form_class, szablon_tytul):
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')
    
    return render(request, 'formularz.html', {'form': form, 'tytul': szablon_tytul})

@login_required
def dodaj_fizjoterapeute(request):
    return dodaj_element(request, FizjoForm, "Dodaj Fizjoterapeutę")

@login_required
def dodaj_pacjenta(request):
    return dodaj_element(request, PacjentForm, "Dodaj Pacjenta")

@login_required
def dodaj_program(request):
    return dodaj_element(request, ProgramForm, "Przypisz Program Ćwiczeniowy")


def rejestracja(request):
    if request.method == "POST":
        form = RejestrForm(request.POST)
        if form.is_valid():
            user = form.save()
            rola = form.cleaned_data.get('rola')
            if rola == 'fizjo':
                Fizjoterapeuta.objects.create(user=user, imie=user.imie, nazwisko=user.nazwisko, specka="Do uzupełnienia", tytul="Do uzupełnienia")
            else:
                Pacjent.objects.create(user=user, imie=user.imie, nazwisko=user.nazwisko, email=user.email)

            login(request, user)
            return redirect('dashboard')
    else:
        form = RejestrForm()
    return render(request, 'registration/rejestracja.html', {'form':form})


def wyloguj(request):
    logout(request)
    return redirect('login')

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = LoginForm