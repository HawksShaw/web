from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Fizjoterapeuta, Pacjent, Program
from .forms import FizjoForm, PacjentForm, ProgramForm, RejestrForm

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

def rejestracja(request):
    if request.method == "POST":
        form = RejestrForm(request.POST)
        if form.is_valid():
            user = form.save()
            rola = form.cleaned_data.get('rola')
            if rola == 'fizjo':
                Fizjoterapeuta.objects.create(user=user, imie=user.username, nazwisko="", specka="Do uzupełnienia", tytul="Do uzupełnienia")
            else:
                Pacjent.objects.create(user=user, imie=user.username, nazwisko="", email=user.email)

            login(request, user)
            return redirect('dashboard')
        else:
            form = RejestrForm()
        return render(request, 'registration/rejestracja.html', {'form':form})