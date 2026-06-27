from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.forms import modelformset_factory
from django.utils import timezone
from django.db.models import Q
import json
import csv
from django.http import JsonResponse

from django.contrib.auth.models import User

from .models import (
    Fizjoterapeuta, Pacjent, Program,
    Wizyta, FizjoPacjent,
    PlanTreningowy, Cwiczenie, OcenaCwiczenia,
    TreningLog,
)
from .forms import (
    FizjoForm, PacjentForm, ProgramForm,
    RejestrForm, LoginForm,
    OcenaCwiczeniaForm,
    PlanTreningowyForm, CwiczenieFormSet,
)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARDS
# ─────────────────────────────────────────────────────────────────────────────

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

    # Real stats from DB (replaces hardcoded "67 pacjentów" etc.)
    moi_pacjenci_count = FizjoPacjent.objects.filter(
        fizjoterapeuta=fizjo, status='zaakceptowany'
    ).count()
    moje_plany_count = PlanTreningowy.objects.filter(fizjoterapeuta=fizjo).count()
    nadchodzace_wizyty_count = Wizyta.objects.filter(
        lekarz=request.user,
        status='zaakceptowana',
        data_rozpoczecia__gte=timezone.now()
    ).count()
    oczekujace_count = Wizyta.objects.filter(
        lekarz=request.user,
        status='oczekujaca'
    ).count()

    context = {
        'fizjoterapeuci': Fizjoterapeuta.objects.all(),
        'pacjenci': Pacjent.objects.all(),
        'programy': Program.objects.all(),
        'moi_pacjenci_count': moi_pacjenci_count,
        'moje_plany_count': moje_plany_count,
        'nadchodzace_wizyty_count': nadchodzace_wizyty_count,
        'oczekujace_count': oczekujace_count,
    }
    return render(request, 'dashboard_fizjo.html', context)


@login_required
def dashboard_pacjent(request):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)

    pacjent_programy = Program.objects.filter(pacjent=request.user.pacjent)

    # FIX: only show physios, not all users
    lekarze = Fizjoterapeuta.objects.select_related('user').all()

    context = {
        'programy': pacjent_programy,
        'lekarze': lekarze,
    }
    return render(request, 'dashboard_pacjent.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# GENERIC ADD (physio/patient/program)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────

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
                Fizjoterapeuta.objects.create(
                    user=user,
                    imie=user.first_name,
                    nazwisko=user.last_name,
                    specka="Do uzupełnienia",
                    tytul="Do uzupełnienia"
                )
            else:
                Pacjent.objects.create(
                    user=user,
                    imie=user.first_name,
                    nazwisko=user.last_name,
                    email=user.email
                )
            login(request, user)
            return redirect('dashboard')
    else:
        form = RejestrForm()
    return render(request, 'registration/rejestracja.html', {'form': form})


def wyloguj(request):
    logout(request)
    return redirect('login')


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm


# ─────────────────────────────────────────────────────────────────────────────
# DOCTOR SEARCH  (FIX: only Fizjoterapeuta users, not all Users)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def wyszukiwarka_lekarzy(request):
    fraza = request.GET.get('szukaj', '')
    if fraza:
        lekarze = Fizjoterapeuta.objects.filter(
            Q(imie__icontains=fraza) |
            Q(nazwisko__icontains=fraza) |
            Q(specka__icontains=fraza) |
            Q(user__username__icontains=fraza)
        ).select_related('user')
    else:
        lekarze = Fizjoterapeuta.objects.select_related('user').all()

    return render(request, 'lista_lekarzy.html', {'lekarze': lekarze, 'fraza': fraza})


@login_required
def profil_lekarza(request, lekarz_id):
    lekarz = get_object_or_404(User, id=lekarz_id)
    return render(request, 'profil_lekarza.html', {'lekarz': lekarz})


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR – PATIENT-FACING APIs
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def get_wizyty_pacjent(request, lekarz_id):
    """
    Returns calendar events for a specific physio's profile page (patient view).
    - Accepted + physio-blocked slots → red (can't book)
    - Current patient's own pending request → yellow
    """
    events = []

    # Slots that are unavailable to everyone
    blokady = Wizyta.objects.filter(
        lekarz_id=lekarz_id,
        status__in=['zaakceptowana', 'zablokowana']
    )
    for w in blokady:
        events.append({
            'title': 'Termin zajęty',
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': '#dc3545',
        })

    # Show the logged-in patient's own pending request (so they know it's waiting)
    if hasattr(request.user, 'pacjent'):
        moje_oczekujace = Wizyta.objects.filter(
            lekarz_id=lekarz_id,
            status='oczekujaca',
            pacjent=request.user.pacjent
        )
        for w in moje_oczekujace:
            events.append({
                'title': '⏳ Oczekuje na potwierdzenie',
                'start': w.data_rozpoczecia.isoformat(),
                'end': w.data_zakonczenia.isoformat(),
                'color': '#ffc107',
            })

    return JsonResponse(events, safe=False)


@login_required
def formularz_rezerwacji(request, lekarz_id):
    """
    Patient submits an appointment request form.
    Creates Wizyta with status='oczekujaca' — physio must accept/reject.
    """
    lekarz = get_object_or_404(User, id=lekarz_id)

    if request.method == 'POST':
        start = request.POST.get('start', '').replace(' ', '+')
        end = request.POST.get('end', '').replace(' ', '+')
        powod = request.POST.get('powod', '')

        pacjent = getattr(request.user, 'pacjent', None)
        pelne_nazwisko = request.user.get_full_name() or request.user.username

        Wizyta.objects.create(
            lekarz=lekarz,
            pacjent=pacjent,
            pacjent_nazwa=pelne_nazwisko,
            powod=powod,
            data_rozpoczecia=start,
            data_zakonczenia=end,
            status='oczekujaca',  # ← awaiting physio approval
        )
        return redirect('profil_lekarza', lekarz_id=lekarz.id)
    else:
        start = request.GET.get('start', '').replace(' ', '+')
        end = request.GET.get('end', '').replace(' ', '+')
        return render(request, 'formularz_rezerwacji.html', {
            'lekarz': lekarz,
            'start': start,
            'end': end,
        })


@login_required
def get_moje_wizyty(request):
    """
    Patient's own appointments for their dashboard calendar.
    FIX: uses real FK instead of fragile string contains search.
    """
    if not hasattr(request.user, 'pacjent'):
        return JsonResponse([], safe=False)

    wizyty = Wizyta.objects.filter(
        pacjent=request.user.pacjent
    ).exclude(status='odrzucona').select_related('lekarz')

    events = []
    for w in wizyty:
        lekarz_name = w.lekarz.get_full_name() or w.lekarz.username
        if w.status == 'zaakceptowana':
            color = '#198754'
            title = f'✅ Wizyta u dr {lekarz_name}'
        else:  # oczekujaca
            color = '#ffc107'
            title = f'⏳ Oczekuje u dr {lekarz_name}'

        events.append({
            'title': title,
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': color,
        })
    return JsonResponse(events, safe=False)


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR – PHYSIO-FACING APIs
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def get_wizyty(request):
    """
    Returns all appointments for the logged-in physio.
    Colour-coded: yellow=pending, green=accepted, grey=rejected, red=blocked-by-physio.
    """
    wizyty = Wizyta.objects.filter(lekarz_id=request.user.id).select_related('pacjent')
    events = []
    for w in wizyty:
        if w.status == 'oczekujaca':
            color = '#ffc107'
            title = f'⏳ {w.pacjent_nazwa}'
        elif w.status == 'zaakceptowana':
            color = '#198754'
            title = f'✅ {w.pacjent_nazwa}'
        elif w.status == 'odrzucona':
            color = '#6c757d'
            title = f'❌ {w.pacjent_nazwa}'
        else:  # zablokowana
            color = '#dc3545'
            title = 'Zablokowane'

        events.append({
            'id': w.id,
            'title': title,
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': color,
            'status': w.status,
            'powod': w.powod or '',
            'pacjent_nazwa': w.pacjent_nazwa,
        })
    return JsonResponse(events, safe=False)


@csrf_exempt
@login_required
def dodaj_wizyte(request):
    """Physio blocks their own calendar slot."""
    if request.method == 'POST':
        data = json.loads(request.body)
        Wizyta.objects.create(
            lekarz_id=request.user.id,
            pacjent_nazwa="Zablokowane przez fizjoterapeutę",
            data_rozpoczecia=data['start'],
            data_zakonczenia=data['end'],
            status='zablokowana',
        )
        return JsonResponse({'status': 'Zapisano pomyślnie'})


@login_required
def zatwierdz_wizyte(request, wizyta_id):
    """Physio accepts a pending patient appointment request."""
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    wizyta = get_object_or_404(Wizyta, id=wizyta_id, lekarz=request.user)
    wizyta.status = 'zaakceptowana'
    wizyta.save()
    return JsonResponse({'status': 'zaakceptowana'})


@login_required
def odrzuc_wizyte(request, wizyta_id):
    """Physio rejects a pending patient appointment request."""
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    wizyta = get_object_or_404(Wizyta, id=wizyta_id, lekarz=request.user)
    wizyta.status = 'odrzucona'
    wizyta.save()
    return JsonResponse({'status': 'odrzucona'})


# ─────────────────────────────────────────────────────────────────────────────
# PHYSIO PANEL PAGES
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def kalendarz_fizjo(request):
    return render(request, 'kalendarz_fizjo.html')


@login_required
def pacjenci_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    relacje = FizjoPacjent.objects.filter(
        fizjoterapeuta=fizjo, status='zaakceptowany'
    ).select_related('pacjent')
    moi_pacjenci = [r.pacjent for r in relacje]
    return render(request, 'pacjenci_fizjo.html', {'pacjenci': moi_pacjenci})


@login_required
def edit_fizjo(request):
    return render(request, 'edit_fizjo.html')


@login_required
def log_fizjo(request):
    """
    Activity log: all exercise feedback submitted by this physio's patients.
    Ordered newest-first.
    """
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)

    fizjo = request.user.fizjoterapeuta

    # All exercise ratings for plans created by this physio
    oceny = (
        OcenaCwiczenia.objects
        .filter(cwiczenie__plan__fizjoterapeuta=fizjo)
        .select_related(
            'cwiczenie',
            'cwiczenie__plan',
            'cwiczenie__plan__pacjent',
            'pacjent',
        )
        .order_by('-data_oceny')
    )

    return render(request, 'log_fizjo.html', {'oceny': oceny})


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING PLANS – PHYSIO
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def programy_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    plany = PlanTreningowy.objects.filter(
        fizjoterapeuta=fizjo
    ).order_by('-data_utworzenia')
    return render(request, 'programy_fizjo.html', {'plany': plany})


@login_required
def dodaj_plan_treningowy(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)

    fizjo = request.user.fizjoterapeuta

    if request.method == 'POST':
        form = PlanTreningowyForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.fizjoterapeuta = fizjo
            formset = CwiczenieFormSet(request.POST, instance=plan)
            if formset.is_valid():
                plan.save()
                formset.save()
                return redirect('dashboard_fizjo')
    else:
        form = PlanTreningowyForm()
        formset = CwiczenieFormSet()

    return render(request, 'dodaj_plan_treningowy.html', {
        'form': form,
        'formset': formset,
    })


@login_required
def szczegoly_planu_fizjo(request, plan_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=fizjo)
    cwiczenia = plan.cwiczenia.prefetch_related('oceny__pacjent').all()
    return render(request, 'szczegoly_planu_fizjo.html', {
        'plan': plan,
        'cwiczenia': cwiczenia,
    })


def eksportuj_plan_csv(request, plan_id):
    plan = get_object_or_404(PlanTreningowy, id=plan_id)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="plan_{plan.id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nazwa cwiczenia', 'Serie', 'Powtorzenia'])
    for cwiczenie in plan.cwiczenia.all():
        writer.writerow([cwiczenie.nazwa_cwiczenia, cwiczenie.serie, cwiczenie.powtórzenia])
    return response


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING PLANS – PATIENT
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def plany_treningowe(request):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    plany = PlanTreningowy.objects.filter(
        pacjent=request.user.pacjent
    ).order_by('-data_utworzenia')
    return render(request, 'plany_treningowe.html', {'plany': plany})


@login_required
def szczegoly_planu(request, plan_id):
    """
    Patient views a training plan and submits pain ratings.

    FIX: OcenaCwiczenia is now a ForeignKey (not OneToOne) so a patient
    can submit feedback multiple times — each submission creates a new row.
    We iterate formset.forms by index to correctly match each form to its
    exercise, regardless of which forms were left empty.
    """
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)

    pacjent = request.user.pacjent
    plan = get_object_or_404(PlanTreningowy, id=plan_id, pacjent=pacjent)
    cwiczenia = list(plan.cwiczenia.all())

    OcenaFormSet = modelformset_factory(
        OcenaCwiczenia,
        form=OcenaCwiczeniaForm,
        extra=len(cwiczenia)
    )

    if request.method == 'POST':
        formset = OcenaFormSet(request.POST, queryset=OcenaCwiczenia.objects.none())
        if formset.is_valid():
            for i, form in enumerate(formset.forms):
                # Only save forms the patient actually filled in
                if form.has_changed() and i < len(cwiczenia):
                    ocena = form.save(commit=False)
                    ocena.cwiczenie = cwiczenia[i]
                    ocena.pacjent = pacjent
                    ocena.save()
            return redirect('dashboard_sukces')
    else:
        formset = OcenaFormSet(queryset=OcenaCwiczenia.objects.none())

    # Get latest existing rating per exercise so the patient can see their history
    ostatnie_oceny = {}
    for c in cwiczenia:
        ostatnia = c.oceny.filter(pacjent=pacjent).first()  # ordered by -data_oceny
        if ostatnia:
            ostatnie_oceny[c.id] = ostatnia

    zestaw = list(zip(cwiczenia, formset.forms))

    return render(request, 'szczegoly_planu.html', {
        'plan': plan,
        'zestaw': zestaw,
        'formset': formset,
        'ostatnie_oceny': ostatnie_oceny,
    })


@login_required
def strona_sukcesu(request):
    return render(request, 'sukces.html')

# views.py
from django.http import JsonResponse
from .models import Pacjent, Cwiczenie, OcenaCwiczenia

@login_required
def profil_pacjenta(request, pacjent_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    
    # Upewniamy się, że pacjent istnieje
    pacjent = get_object_or_404(Pacjent, id=pacjent_id)
    
    # Pobieramy wszystkie ćwiczenia powiązane z planami tego pacjenta
    # Wyciągamy tylko te, które faktycznie otrzymały jakieś oceny
    cwiczenia = Cwiczenie.objects.filter(
        plan__pacjent=pacjent, 
        oceny__isnull=False
    ).distinct()

    return render(request, 'profil_pacjenta.html', {
        'pacjent': pacjent,
        'cwiczenia': cwiczenia
    })

# views.py

@login_required
def profil_pacjenta(request, pacjent_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    
    pacjent = get_object_or_404(Pacjent, id=pacjent_id)
    
    # ZMIANA: Pobieramy tylko unikalne NAZWY ćwiczeń, które ten pacjent kiedykolwiek ocenił
    cwiczenia_nazwy = Cwiczenie.objects.filter(
        plan__pacjent=pacjent, 
        oceny__isnull=False
    ).values_list('nazwa_cwiczenia', flat=True).distinct()

    return render(request, 'profil_pacjenta.html', {
        'pacjent': pacjent,
        'cwiczenia_nazwy': cwiczenia_nazwy  # Przekazujemy listę nazw (stringów)
    })


@login_required
def api_wykres_bolu(request, pacjent_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
        
    # Pobieramy nazwę ćwiczenia z parametru URL (?nazwa=...)
    nazwa_cwiczenia = request.GET.get('nazwa', '')
    
    if not nazwa_cwiczenia:
        return JsonResponse({'error': 'Nie podano nazwy ćwiczenia'}, status=400)
        
    # ZMIANA: Szukamy wszystkich ocen tego PACJENTA, gdzie ćwiczenie nazywa się tak samo
    # Używamy __iexact, żeby ignorować wielkość liter (np. rdl i RDL połączy w jedno)
    oceny = OcenaCwiczenia.objects.filter(
        pacjent_id=pacjent_id,
        cwiczenie__nazwa_cwiczenia__iexact=nazwa_cwiczenia
    ).order_by('data_oceny')
    
    labels = [ocena.data_oceny.strftime('%d.%m.%Y') for ocena in oceny]
    data = [ocena.skala_bolu for ocena in oceny]
    
    # Dodatkowo w dymku (tooltipie) możemy pokazać, z jakiego planu pochodziło dane ćwiczenie
    uwagi = []
    for ocena in oceny:
        plan_nazwa = ocena.cwiczenie.plan.nazwa
        tekst_uwagi = f"[{plan_nazwa}]"
        if ocena.uwagi:
            tekst_uwagi += f" - {ocena.uwagi}"
        uwagi.append(tekst_uwagi)
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'uwagi': uwagi
    })

@login_required
def edit_fizjo(request):
    """Widok panelu edycji/zarządzania planami."""
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
        
    fizjo = request.user.fizjoterapeuta
    # Pobieramy wszystkie plany tego fizjoterapeuty, sortując od najnowszego
    plany = PlanTreningowy.objects.filter(fizjoterapeuta=fizjo).order_by('-data_utworzenia')
    
    return render(request, 'edit_fizjo.html', {'plany': plany})

@login_required
def usun_plan(request, plan_id):
    """Widok odpowiadający za usunięcie planu."""
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
        
    fizjo = request.user.fizjoterapeuta
    # Pobieramy plan, upewniając się, że należy do zalogowanego fizjoterapeuty
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=fizjo)
    
    # Dla bezpieczeństwa usuwamy tylko przy żądaniu POST
    if request.method == 'POST':
        plan.delete()
        # Po udanym usunięciu wracamy do panelu edycji
        return redirect('edit_fizjo')
        
    return redirect('edit_fizjo')

@login_required
def edytuj_plan_treningowy(request, plan_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)

    fizjo = request.user.fizjoterapeuta
    # Pobieramy konkretny plan, sprawdzając czy należy do tego fizjoterapeuty
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=fizjo)

    if request.method == 'POST':
        # KLUCZOWE: przekazujemy instance=plan, aby Django wiedziało, że edytujemy istniejący rekord
        form = PlanTreningowyForm(request.POST, instance=plan)
        formset = CwiczenieFormSet(request.POST, instance=plan)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('edit_fizjo') # Wracamy do panelu zarządzania
    else:
        # Wypełniamy formularze dotychczasowymi danymi z bazy
        form = PlanTreningowyForm(instance=plan)
        formset = CwiczenieFormSet(instance=plan)

    return render(request, 'edytuj_plan_treningowy.html', {
        'form': form,
        'formset': formset,
        'plan': plan,
    })