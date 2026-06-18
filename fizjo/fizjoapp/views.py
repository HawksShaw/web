from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from .models import Fizjoterapeuta, Pacjent, Program, Wizyta
from .forms import FizjoForm, PacjentForm, ProgramForm, RejestrForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User

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
    # 1. Zabezpieczenie - tylko pacjent ma tu dostęp
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    
    # 2. Pobieramy programy dla pacjenta
    pacjent_programy = Program.objects.filter(pacjent=request.user.pacjent)

    # 3. Pobieramy listę lekarzy 
    # (Jeśli masz model profilu Lekarz, lepiej użyć: User.objects.filter(lekarz__isnull=False) żeby nie pokazywać na liście innych pacjentów)
    lekarze = User.objects.all() 

    # 4. Pakujemy WSZYSTKO do kontekstu
    context = {
        'programy': pacjent_programy,
        'lekarze': lekarze,  # <--- Dodałem tę linijkę!
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
@login_required
def wyszukiwarka_lekarzy(request):
    # Pobieramy wszystkich użytkowników (później odfiltrujemy tylko lekarzy)
    fraza = request.GET.get('szukaj', '')
    if fraza:
        lekarze = User.objects.filter(username__icontains=fraza)
    else:
        lekarze = User.objects.all()
        
    return render(request, 'lista_lekarzy.html', {'lekarze': lekarze, 'fraza': fraza})

# 2. Profil konkretnego lekarza z kalendarzem
@login_required
def profil_lekarza(request, lekarz_id):
    lekarz = get_object_or_404(User, id=lekarz_id)
    return render(request, 'profil_lekarza.html', {'lekarz': lekarz})


# --- ZMIANY W API KALENDARZA ---

# Zmieniamy API, żeby pobierało wizyty po ID lekarza z URL
@login_required
def get_wizyty_pacjent(request, lekarz_id):
    wizyty = Wizyta.objects.filter(lekarz_id=lekarz_id)
    events = []
    for w in wizyty:
        events.append({
            'title': 'Termin zajęty', # Pacjent nie powinien widzieć nazwisk innych pacjentów!
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': '#ff0000',
            'display': 'background' # Fajny trik: robi całe tło na czerwono, uniemożliwiając kliknięcie
        })
    return JsonResponse(events, safe=False)

@csrf_exempt
@login_required
def dodaj_wizyte_pacjent(request, lekarz_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        Wizyta.objects.create(
            lekarz_id=lekarz_id,
            pacjent_nazwa=request.user.username, # Zapisujemy, który pacjent to kliknął!
            data_rozpoczecia=data['start'],
            data_zakonczenia=data['end']
        )
        return JsonResponse({'status': 'Zapisano pomyślnie'})
    
# --- API DLA PANELU FIZJOTERAPEUTY (Bez ID w adresie) ---

@login_required
def get_wizyty(request):
    # Pobiera wizyty, gdzie lekarzem jest aktualnie zalogowany fizjoterapeuta
    wizyty = Wizyta.objects.filter(lekarz_id=request.user.id)
    events = []
    for w in wizyty:
        events.append({
            'title': w.pacjent_nazwa, # Fizjo widzi imię pacjenta
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': '#ff0000'
        })
    return JsonResponse(events, safe=False)

@csrf_exempt
@login_required
def dodaj_wizyte(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        Wizyta.objects.create(
            lekarz_id=request.user.id, # Przypisuje zalogowanego fizjo
            pacjent_nazwa="Zablokowane przez fizjoterapeutę", # Jeśli fizjo sam wyklika termin
            data_rozpoczecia=data['start'],
            data_zakonczenia=data['end']
        )
        return JsonResponse({'status': 'Zapisano pomyślnie'})
