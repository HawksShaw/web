from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from .models import Fizjoterapeuta, Pacjent, Program, Wizyta, FizjoPacjent
from .forms import FizjoForm, PacjentForm, ProgramForm, RejestrForm, LoginForm
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
from .models import PlanTreningowy
import csv
from django.http import HttpResponse
from django.forms import modelformset_factory
from .models import PlanTreningowy, OcenaCwiczenia, Cwiczenie
from .forms import OcenaCwiczeniaForm
from .forms import PlanTreningowyForm, CwiczenieFormSet

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
            user = form.save(commit=False)
            rola = form.cleaned_data.get('rola')
            user.first_name = form.cleaned_data['imie']
            user.last_name = form.cleaned_data['nazwisko']
            user.save()
            if rola == 'fizjo':
                Fizjoterapeuta.objects.create(user=user, imie=user.first_name, nazwisko=user.last_name, specka="Do uzupełnienia", tytul="Do uzupełnienia")
            else:
                Pacjent.objects.create(user=user, imie=user.first_name, nazwisko=user.last_name, email=user.email)

            login(request, user)
            return redirect('dashboard')
    else:
        form = RejestrForm()
    return render(request, 'registration/rejestracja.html', {'form':form})


def wyloguj(request):
    logout(request)
    return redirect('login')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
@login_required
def wyszukiwarka_lekarzy(request):
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
    # Pobieramy wizyty konkretnego lekarza
    wizyty = Wizyta.objects.filter(lekarz_id=lekarz_id)
    events = []
    for w in wizyty:
        events.append({
            'title': 'Termin zajęty', # Wymuszamy domyślny tytuł bez zdradzania danych pacjenta
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': '#ff0000'
            # Upewniamy się, że nie ma tu parametru 'display': 'background'
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
    
@login_required
def formularz_rezerwacji(request, lekarz_id):
    lekarz = get_object_or_404(User, id=lekarz_id)
    
    if request.method == 'POST':
        # ZABEZPIECZENIE: .replace(' ', '+') naprawia ucięty plus ze strefy czasowej
        start = request.POST.get('start', '').replace(' ', '+')
        end = request.POST.get('end', '').replace(' ', '+')
        powod = request.POST.get('powod', '')
        
        Wizyta.objects.create(
            lekarz=lekarz,
            pacjent_nazwa=f"{request.user.username} - {powod}",
            data_rozpoczecia=start,
            data_zakonczenia=end
        )
        return redirect('profil_lekarza', lekarz_id=lekarz.id)
        
    else:
        # To samo robimy przy pobieraniu danych z linku
        start = request.GET.get('start', '').replace(' ', '+')
        end = request.GET.get('end', '').replace(' ', '+')
        
        return render(request, 'formularz_rezerwacji.html', {
            'lekarz': lekarz,
            'start': start,
            'end': end
        })
    
@login_required
def get_moje_wizyty(request):
    # Szukamy wizyt, gdzie nazwa pacjenta zawiera username aktualnie zalogowanego użytkownika
    wizyty = Wizyta.objects.filter(pacjent_nazwa__icontains=request.user.username)
    
    events = []
    for w in wizyty:
        events.append({
            'title': f'Wizyta u dr {w.lekarz.username}', # Pacjent widzi do kogo idzie
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': '#0d6efd' # Niebieski kolor dla odróżnienia na panelu pacjenta
        })
    return JsonResponse(events, safe=False)

@login_required
def kalendarz_fizjo(request):
    return render(request, 'kalendarz_fizjo.html')

@login_required
def programy_fizjo(request):
    return render(request, 'programy_fizjo.html')

@login_required
def pacjenci_fizjo(request):
    fizjo = request.user.fizjoterapeuta
    relacje = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='zaakceptowany')
    moi_pacjenci = [relacja.pacjent for relacja in relacje]
    context = {
        'pacjenci' : moi_pacjenci
    }
    return render(request, 'pacjenci_fizjo.html', context)

@login_required
def edit_fizjo(request):
    return render(request, 'edit_fizjo.html')

@login_required
def log_fizjo(request):
    return render(request, 'log_fizjo.html')
def eksportuj_plan_csv(request, plan_id):
    plan = get_object_or_404(PlanTreningowy, id=plan_id)
    
    # Tworzymy obiekt HttpResponse z odpowiednim nagłówkiem CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="plan_{plan.id}.csv"'

    writer = csv.writer(response)
    # Nagłówki kolumn w pliku CSV
    writer.writerow(['Nazwa ćwiczenia', 'Serie', 'Powtórzenia'])

    # Zapisujemy każde ćwiczenie do wiersza
    for cwiczenie in plan.cwiczenia.all():
        writer.writerow([cwiczenie.nazwa_cwiczenia, cwiczenie.serie, cwiczenie.powtórzenia])

    return response

@login_required
def szczegoly_planu(request, plan_id):
    # ZMIANA: Tutaj też dodajemy .pacjent na końcu request.user
    plan = get_object_or_404(PlanTreningowy, id=plan_id, pacjent=request.user.pacjent)
    cwiczenia = plan.cwiczenia.all()
    
    # FormSet o wielkości równej liczbie ćwiczeń
    OcenaFormSet = modelformset_factory(OcenaCwiczenia, form=OcenaCwiczeniaForm, extra=len(cwiczenia))

    if request.method == 'POST':
        formset = OcenaFormSet(request.POST)
        if formset.is_valid():
            instancje = formset.save(commit=False)
            for i, form in enumerate(instancje):
                form.cwiczenie = cwiczenia[i]
                form.save()
            return redirect('dashboard_sukces')
    else:
        formset = OcenaFormSet(queryset=OcenaCwiczenia.objects.none())

    # Łączymy ćwiczenia z formularzami w pary przy pomocy zip()
    zestaw = zip(cwiczenia, formset)

    return render(request, 'szczegoly_planu.html', {
        'plan': plan,
        'zestaw': zestaw,  # Przekazujemy pod krótką nazwą
        'formset': formset
    })

@login_required
def plany_treningowe(request):
    # ZMIANA: Dodajemy .pacjent na końcu request.user
    plany = PlanTreningowy.objects.filter(pacjent=request.user.pacjent).order_by('-data_utworzenia')
    
    return render(request, 'plany_treningowe.html', {'plany': plany})

@login_required
def strona_sukcesu(request):
    # Prosta strona wyświetlana po udanym zapisie bólu i uwag
    return render(request, 'sukces.html')

@login_required
def dodaj_plan_treningowy(request):
    # Ochrona: sprawdzamy, czy użytkownik to na pewno fizjoterapeuta
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)

    fizjo = request.user.fizjoterapeuta

    if request.method == 'POST':
        form = PlanTreningowyForm(request.POST)
        
        if form.is_valid():
            # Zapisujemy plan, ale jeszcze nie pchamy do bazy (commit=False)
            plan = form.save(commit=False)
            plan.fizjoterapeuta = fizjo # Automatycznie przypisujemy zalogowanego fizjo
            
            # Wrzucamy dane z metody POST do FormSetu ćwiczeń przypisanych do tego planu
            formset = CwiczenieFormSet(request.POST, instance=plan)
            
            if formset.is_valid():
                plan.save()     # Zapisujemy plan w bazie
                formset.save()  # Zapisujemy wszystkie powiązane ćwiczenia
                
                # Przekierowujemy fizjo z powrotem na dashboard po sukcesie
                return redirect('dashboard_fizjo') 
    else:
        # Puste formularze do wyświetlenia na stronie
        form = PlanTreningowyForm()
        
        # Opcjonalnie: ograniczenie listy pacjentów tylko do tych przypisanych do danego fizjo. 
        # (Zależy od Twojego modelu FizjoPacjent, jeśli chcesz zostawić wszystkich - pomiń tę linię)
        # form.fields['pacjent'].queryset = Pacjent.objects.filter(fizjopacjent__fizjoterapeuta=fizjo)

        formset = CwiczenieFormSet()

    return render(request, 'dodaj_plan_treningowy.html', {
        'form': form,
        'formset': formset
    })

@login_required
def programy_fizjo(request):
    # Sprawdzamy czy to fizjoterapeuta
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
        
    fizjo = request.user.fizjoterapeuta
    # Pobieramy plany stworzone przez tego konkretnego fizjoterapeutę
    plany = PlanTreningowy.objects.filter(fizjoterapeuta=fizjo).order_by('-data_utworzenia')
    
    return render(request, 'programy_fizjo.html', {'plany': plany})

@login_required
def szczegoly_planu_fizjo(request, plan_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
        
    fizjo = request.user.fizjoterapeuta
    # Upewniamy się, że fizjo może oglądać tylko SWOJE plany
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=fizjo)
    cwiczenia = plan.cwiczenia.all()
    
    return render(request, 'szczegoly_planu_fizjo.html', {
        'plan': plan,
        'cwiczenia': cwiczenia
    })
