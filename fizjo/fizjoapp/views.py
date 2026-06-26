<<<<<<< Updated upstream
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
=======
import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone

from .models import (
    Fizjoterapeuta, Pacjent, FizjoPacjent, 
    Program, GlobalCwiczenie, ProgramCwiczenie, 
    TreningLog, ZrobioneCwiczenia, Wizyta
)
from .forms import FizjoForm, PacjentForm, ProgramForm, RejestrForm, LoginForm, CwiczenieFormSet
>>>>>>> Stashed changes

@login_required
def dashboard(request):
    if hasattr(request.user, 'fizjoterapeuta'):
        return redirect('dashboard_fizjo')
    elif hasattr(request.user, 'pacjent'):
        return redirect('dashboard_pacjent')
    return render(request, 'dashboard.html')

@login_required
def dashboard_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    
    fizjo = request.user.fizjoterapeuta
    context = {
        'moi_pacjenci_liczba': FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='zaakceptowany').count(),
        'aktywne_programy': Program.objects.filter(fizjoterapeuta=fizjo).count(),
        'dzisiejsze_wizyty': Wizyta.objects.filter(fizjoterapeuta=fizjo, status='zatwierdzona').count(),
    }
    return render(request, 'dashboard_fizjo.html', context)

@login_required
def dashboard_pacjent(request):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    
    pacjent = request.user.pacjent
    context = {
        'programy': Program.objects.filter(pacjent=pacjent),
        'fizjoterapeuci': Fizjoterapeuta.objects.all()
    }
    return render(request, 'dashboard_pacjent.html', context)

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm

def wyloguj(request):
    logout(request)
    return redirect('login')

def rejestracja(request):
    if request.method == "POST":
        form = RejestrForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            rola = form.cleaned_data.get('rola')
            user.first_name = form.cleaned_data['imie']
            user.last_name = form.cleaned_data['nazwisko']
            user.save()
<<<<<<< Updated upstream
            if rola == 'fizjo':
                Fizjoterapeuta.objects.create(user=user, imie=user.first_name, nazwisko=user.last_name, specka="Do uzupełnienia", tytul="Do uzupełnienia")
            else:
                Pacjent.objects.create(user=user, imie=user.first_name, nazwisko=user.last_name, email=user.email)

=======
            
            if rola == 'fizjo':
                Fizjoterapeuta.objects.create(
                    user=user, imie=user.first_name, nazwisko=user.last_name, 
                    specka="Do uzupełnienia", tytul="mgr"
                )
            else:
                Pacjent.objects.create(
                    user=user, imie=user.first_name, nazwisko=user.last_name, email=user.email
                )
>>>>>>> Stashed changes
            login(request, user)
            return redirect('dashboard')
    else:
        form = RejestrForm()
    return render(request, 'registration/rejestracja.html', {'form': form})

<<<<<<< Updated upstream

def wyloguj(request):
    logout(request)
    return redirect('login')
=======
>>>>>>> Stashed changes

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm
@login_required
<<<<<<< Updated upstream
def wyszukiwarka_lekarzy(request):
    fraza = request.GET.get('szukaj', '')
    if fraza:
        lekarze = User.objects.filter(username__icontains=fraza)
    else:
        lekarze = User.objects.all()
=======
def wykonaj_dzisiejszy_trening(request, program_id):
    pacjent = get_object_or_404(Pacjent, user=request.user)
    program = get_object_or_404(Program, id=program_id, pacjent=pacjent)
    
    dzisiaj = timezone.now().date()
    
    if TreningLog.objects.filter(pacjent=pacjent, program=program, data_wykonania=dzisiaj).exists():
        return render(request, 'sukces.html', {'wiadomosc': 'Trening z dzisiaj został już zapisany!'})

    cwiczenia_w_placu = program.cwiczenia.all()

    if request.method == 'POST':
        bol = request.POST.get('skala_bol')
        komentarz = request.POST.get('pacjent_kom', '')
>>>>>>> Stashed changes
        
        nowy_log = TreningLog.objects.create(
            pacjent=pacjent,
            program=program,
            skala_bol=bol,
            pacjent_kom=komentarz
        )
        for cw in cwiczenia_w_placu:
            czy_zrobione = request.POST.get(f'cwiczenie_{cw.id}') == 'on'
            ZrobioneCwiczenia.objects.create(
                trening_log=nowy_log,
                cwiczenie_program=cw,
                wykonane=czy_zrobione
            )
        return redirect('dashboard_sukces')

    return render(request, 'wykonaj_trening.html', {
        'program': program, 
        'cwiczenia': cwiczenia_w_placu
    })


@login_required
def strona_sukces(request):
    return render(request, 'sukces.html', {'wiadomosc': 'Dobra robota! Raport ćwiczenia pomyślnie wysłany do Twojego fizjoterapeuty.'})


@login_required
<<<<<<< Updated upstream
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
=======
def log_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    
    fizjo = request.user.fizjoterapeuta
    
    wpisy = TreningLog.objects.filter(
        program__fizjoterapeuta=fizjo
    ).select_related('pacjent', 'program').prefetch_related('wykonane_cwiczenia__cwiczenie_program__cwiczenie_bazowe')

    return render(request, 'log_fizjo.html', {'wpisy': wpisy})

@login_required
def wyszukiwarka_fizjo(request):
    fraza = request.GET.get('szukaj', '')
    fizjo_lista = Fizjoterapeuta.objects.filter(nazwisko__icontains=fraza) if fraza else Fizjoterapeuta.objects.all()
    return render(request, 'lista_fizjo.html', {'fizjoterapeuci': fizjo_lista, 'fraza': fraza})

@login_required
def profil_fizjo(request, fizjo_id):
    fizjo = get_object_or_404(Fizjoterapeuta, id=fizjo_id)
    return render(request, 'profil_lekarza.html', {'lekarz': fizjo}) # DO ZMIANY 'lekarz' NA 'fizjo', ZOSTAWIONE NA RAZIE ŻEBY DZIAŁAŁO

@login_required
def get_wizyty_pacjent(request, fizjo_id):
    wizyty = Wizyta.objects.filter(fizjoterapeuta_id=fizjo_id, status='zatwierdzona')
    events = [{'title': 'Zajęte', 'start': w.data_rozpoczecia.isoformat(), 'end': w.data_zakonczenia.isoformat(), 'color': '#dc3545'} for w in wizyty]
>>>>>>> Stashed changes
    return JsonResponse(events, safe=False)

@csrf_exempt
@login_required
def dodaj_wizyte_pacjent(request, fizjo_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        pacjent = get_object_or_404(Pacjent, user=request.user)
        
        Wizyta.objects.create(
            fizjoterapeuta_id=fizjo_id,
            pacjent=pacjent,
            data_rozpoczecia=data['start'],
            data_zakonczenia=data['end'],
            status='propozycja'
        )
        return JsonResponse({'status': 'Wysłano propozycję wizyty!'})

@login_required
def get_wizyty(request):
    fizjo = request.user.fizjoterapeuta
    wizyty = Wizyta.objects.filter(fizjoterapeuta=fizjo)
    
    # Kolorowanie kalendarza u fizjo: żółty = propozycja, zielony = pewniak
    events = []
    for w in wizyty:
        kolor = '#ffc107' if w.status == 'propozycja' else '#198754'
        events.append({
            'id': w.id,
            'title': f"{w.pacjent} ({w.get_status_display()})",
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': kolor
        })
    return JsonResponse(events, safe=False)

@csrf_exempt
@login_required
def dodaj_wizyte(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Szybka blokada własnego kalendarza przez fizjo
        Wizyta.objects.create(
            fizjoterapeuta=request.user.fizjoterapeuta,
            pacjent=Pacjent.objects.first(), # Tymczasowe przypisanie techniczne
            data_rozpoczecia=data['start'],
            data_zakonczenia=data['end'],
            status='zatwierdzona'
        )
<<<<<<< Updated upstream
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
=======
        return JsonResponse({'status': 'Zablokowano termin'})
>>>>>>> Stashed changes

@login_required
def pacjenci_fizjo(request):
    fizjo = request.user.fizjoterapeuta
    relacje = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='zaakceptowany')
<<<<<<< Updated upstream
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
=======
    return render(request, 'pacjenci_fizjo.html', {'pacjenci': [r.pacjent for r in relacje]})

@login_required
def programy_fizjo(request):
    fizjo = request.user.fizjoterapeuta
    return render(request, 'programy_fizjo.html', {'programy': Program.objects.filter(fizjoterapeuta=fizjo)})

@login_required
def kalendarz_fizjo(request): return render(request, 'kalendarz_fizjo.html')

@login_required
def edit_fizjo(request): return render(request, 'edit_fizjo.html')

def eksportuj_plan_csv(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="program_{program.nazwa}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Ćwiczenie', 'Serie', 'Powtórzenia'])
    for cw in program.cwiczenia.all():
        writer.writerow([cw.cwiczenie_bazowe.nazwa, cw.serie, cw.powtorzenia])
    return response


@login_required
def dodaj_program(request):
>>>>>>> Stashed changes
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)

    fizjo = request.user.fizjoterapeuta

    if request.method == 'POST':
<<<<<<< Updated upstream
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

=======
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save(commit=False)
            program.fizjoterapeuta = fizjo # Przypisuje zalogowanego fizjo
            
            formset = CwiczenieFormSet(request.POST, instance=program)
            if formset.is_valid():
                program.save()
                formset.save()
                return redirect('dashboard_fizjo')
    else:
        form = ProgramForm()
>>>>>>> Stashed changes
        formset = CwiczenieFormSet()

    return render(request, 'dodaj_plan_treningowy.html', {
        'form': form,
        'formset': formset
    })
<<<<<<< Updated upstream

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
=======
>>>>>>> Stashed changes
