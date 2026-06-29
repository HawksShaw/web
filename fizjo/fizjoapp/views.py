from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.forms import modelformset_factory
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
import json
import csv
import random
import string
import datetime

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


def generuj_kod_pacjenta():
    """Generate a unique patient identifier like P-A3F92K1B."""
    chars = string.ascii_uppercase + string.digits
    while True:
        kod = 'P-' + ''.join(random.choices(chars, k=8))
        if not Pacjent.objects.filter(kod_pacjenta=kod).exists():
            return kod


def sesje_w_biezacym_tygodniu(plan, pacjent=None):
    """Count distinct days a patient submitted exercise feedback for a plan this week."""
    today = timezone.localdate()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=7)
    qs = OcenaCwiczenia.objects.filter(
        cwiczenie__plan=plan,
        data_oceny__date__gte=start_of_week,
        data_oceny__date__lt=end_of_week,
    )
    if pacjent:
        qs = qs.filter(pacjent=pacjent)
    return qs.dates('data_oceny', 'day').count()


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
    moi_pacjenci_count = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='zaakceptowany').count()
    moje_plany_count = PlanTreningowy.objects.filter(fizjoterapeuta=fizjo).count()
    nadchodzace_wizyty_count = Wizyta.objects.filter(
        lekarz=request.user, status='zaakceptowana', data_rozpoczecia__gte=timezone.now()
    ).count()
    oczekujace_count = Wizyta.objects.filter(lekarz=request.user, status='oczekujaca').count()

    context = {
        'fizjoterapeuci': Fizjoterapeuta.objects.all(),
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

    pacjent = request.user.pacjent

    if not pacjent.kod_pacjenta:
        pacjent.kod_pacjenta = generuj_kod_pacjenta()
        pacjent.save()

    pacjent_programy = Program.objects.filter(pacjent=pacjent)
    lekarze = Fizjoterapeuta.objects.select_related('user').all()
    zaproszenia = FizjoPacjent.objects.filter(
        pacjent=pacjent, status='oczekujacy'
    ).select_related('fizjoterapeuta')
    moi_lekarze = Fizjoterapeuta.objects.filter(
        relacje_z_pacjentami__pacjent=pacjent,
        relacje_z_pacjentami__status='zaakceptowany'
    ).select_related('user')
    nadchodzace_wizyty = Wizyta.objects.filter(
        pacjent=pacjent, status='zaakceptowana', data_rozpoczecia__gte=timezone.now()
    ).count()
    plany_count = PlanTreningowy.objects.filter(pacjent=pacjent).count()

    context = {
        'programy': pacjent_programy,
        'lekarze': lekarze,
        'zaproszenia': zaproszenia,
        'moi_lekarze': moi_lekarze,
        'nadchodzace_wizyty': nadchodzace_wizyty,
        'plany_count': plany_count,
    }
    return render(request, 'dashboard_pacjent.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# GENERIC ADD
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
                    email=user.email,
                    kod_pacjenta=generuj_kod_pacjenta(),
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
# DOCTOR SEARCH
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def wyszukiwarka_lekarzy(request):
    fraza = request.GET.get('szukaj', '')
    if fraza:
        lekarze = Fizjoterapeuta.objects.filter(
            Q(imie__icontains=fraza) |
            Q(nazwisko__icontains=fraza) |
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
# CALENDAR – PATIENT APIS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def get_wizyty_pacjent(request, lekarz_id):
    """
    Physio-profile calendar view for patients.
    - Accepted + physio-blocked → red (unavailable)
    - Patient's own pending → yellow (waiting)
    - Patient's own REJECTED → grey (blocked so they can't re-book the same slot)
    """
    events = []

    # Slots unavailable to everyone
    for w in Wizyta.objects.filter(lekarz_id=lekarz_id, status__in=['zaakceptowana', 'zablokowana']):
        events.append({
            'title': 'Termin zajęty',
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': '#dc3545',
        })

    if hasattr(request.user, 'pacjent'):
        # Patient's own pending
        for w in Wizyta.objects.filter(lekarz_id=lekarz_id, status='oczekujaca', pacjent=request.user.pacjent):
            events.append({
                'title': '⏳ Oczekuje na potwierdzenie',
                'start': w.data_rozpoczecia.isoformat(),
                'end': w.data_zakonczenia.isoformat(),
                'color': '#ffc107',
            })
        # Patient's own rejected — show as grey/blocked so they can't re-book
        for w in Wizyta.objects.filter(lekarz_id=lekarz_id, status='odrzucona', pacjent=request.user.pacjent):
            events.append({
                'title': '❌ Twoja propozycja odrzucona',
                'start': w.data_rozpoczecia.isoformat(),
                'end': w.data_zakonczenia.isoformat(),
                'color': '#6c757d',
            })

    return JsonResponse(events, safe=False)


@login_required
def formularz_rezerwacji(request, lekarz_id):
    lekarz = get_object_or_404(User, id=lekarz_id)
    if request.method == 'POST':
        start = request.POST.get('start', '').replace(' ', '+')
        end = request.POST.get('end', '').replace(' ', '+')
        powod = request.POST.get('powod', '')
        pacjent = getattr(request.user, 'pacjent', None)
        pelne_nazwisko = request.user.get_full_name() or request.user.username
        Wizyta.objects.create(
            lekarz=lekarz, pacjent=pacjent, pacjent_nazwa=pelne_nazwisko,
            powod=powod, data_rozpoczecia=start, data_zakonczenia=end, status='oczekujaca',
        )
        return redirect('profil_lekarza', lekarz_id=lekarz.id)
    else:
        start = request.GET.get('start', '').replace(' ', '+')
        end = request.GET.get('end', '').replace(' ', '+')
        return render(request, 'formularz_rezerwacji.html', {'lekarz': lekarz, 'start': start, 'end': end})


@login_required
def get_moje_wizyty(request):
    """
    Patient's own appointments for their dashboard calendar.
    Includes rejected (grey) so patients can see the slot is blocked.
    """
    if not hasattr(request.user, 'pacjent'):
        return JsonResponse([], safe=False)

    wizyty = Wizyta.objects.filter(
        pacjent=request.user.pacjent
    ).select_related('lekarz')

    lekarz_id = request.GET.get('lekarz_id')
    if lekarz_id:
        wizyty = wizyty.filter(lekarz_id=lekarz_id)

    events = []
    for w in wizyty:
        lekarz_name = w.lekarz.get_full_name() or w.lekarz.username
        if w.status == 'zaakceptowana':
            color, title = '#198754', f'✅ Wizyta u {lekarz_name}'
        elif w.status == 'odrzucona':
            color, title = '#6c757d', f'❌ Odrzucona – {lekarz_name}'
        else:  # oczekujaca
            color, title = '#ffc107', f'⏳ Oczekuje u {lekarz_name}'
        events.append({
            'title': title,
            'start': w.data_rozpoczecia.isoformat(),
            'end': w.data_zakonczenia.isoformat(),
            'color': color,
        })
    return JsonResponse(events, safe=False)


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR – PHYSIO APIS
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def get_wizyty(request):
    wizyty = Wizyta.objects.filter(lekarz_id=request.user.id).select_related('pacjent')
    events = []
    for w in wizyty:
        if w.status == 'oczekujaca':
            color, title = '#ffc107', f'⏳ {w.pacjent_nazwa}'
        elif w.status == 'zaakceptowana':
            color, title = '#198754', f'✅ {w.pacjent_nazwa}'
        elif w.status == 'odrzucona':
            color, title = '#6c757d', f'❌ {w.pacjent_nazwa}'
        else:  # zablokowana
            color, title = '#dc3545', 'Zablokowane'
        events.append({
            'id': w.id, 'title': title,
            'start': w.data_rozpoczecia.isoformat(), 'end': w.data_zakonczenia.isoformat(),
            'color': color, 'status': w.status, 'powod': w.powod or '', 'pacjent_nazwa': w.pacjent_nazwa,
        })
    return JsonResponse(events, safe=False)


@csrf_exempt
@login_required
def dodaj_wizyte(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Wizyta.objects.create(
            lekarz_id=request.user.id,
            pacjent_nazwa="Zablokowane przez fizjoterapeutę",
            data_rozpoczecia=data['start'], data_zakonczenia=data['end'],
            status='zablokowana',
        )
        return JsonResponse({'status': 'Zapisano pomyślnie'})


@login_required
def zatwierdz_wizyte(request, wizyta_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    wizyta = get_object_or_404(Wizyta, id=wizyta_id, lekarz=request.user)
    wizyta.status = 'zaakceptowana'
    wizyta.save()
    return JsonResponse({'status': 'zaakceptowana'})


@login_required
def odrzuc_wizyte(request, wizyta_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    wizyta = get_object_or_404(Wizyta, id=wizyta_id, lekarz=request.user)
    wizyta.status = 'odrzucona'
    wizyta.save()
    return JsonResponse({'status': 'odrzucona'})


@login_required
def usun_wizyte(request, wizyta_id):
    """Physio deletes a rejected appointment, freeing the slot entirely."""
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    wizyta = get_object_or_404(Wizyta, id=wizyta_id, lekarz=request.user, status='odrzucona')
    wizyta.delete()
    return JsonResponse({'status': 'usunieto'})


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
    zaakceptowani = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='zaakceptowany').select_related('pacjent')
    oczekujace = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='oczekujacy').select_related('pacjent')
    return render(request, 'pacjenci_fizjo.html', {
        'pacjenci': [r.pacjent for r in zaakceptowani],
        'oczekujace': oczekujace,
    })


@login_required
def edit_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    plany = PlanTreningowy.objects.filter(fizjoterapeuta=fizjo).order_by('-data_utworzenia')
    return render(request, 'edit_fizjo.html', {'plany': plany})


@login_required
def log_fizjo(request):
    """
    Activity log: all exercise feedback by this physio's patients.
    Supports search, sort, and pagination via GET params.
    FIX: view now passes page_obj that the template expects.
    """
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)

    fizjo = request.user.fizjoterapeuta
    search = request.GET.get('search', '').strip()
    sort = request.GET.get('sort', 'data_desc')
    try:
        per_page = int(request.GET.get('per_page', 10))
    except ValueError:
        per_page = 10

    oceny = (
        OcenaCwiczenia.objects
        .filter(cwiczenie__plan__fizjoterapeuta=fizjo)
        .select_related('cwiczenie', 'cwiczenie__plan', 'cwiczenie__plan__pacjent', 'pacjent')
    )

    if search:
        oceny = oceny.filter(
            Q(pacjent__imie__icontains=search) |
            Q(pacjent__nazwisko__icontains=search) |
            Q(cwiczenie__nazwa_cwiczenia__icontains=search) |
            Q(uwagi__icontains=search)
        )

    sort_map = {
        'data_desc': '-data_oceny',
        'bol_desc': '-skala_bolu',
        'bol_asc': 'skala_bolu',
        'pacjent_asc': 'pacjent__nazwisko',
        'pacjent_desc': '-pacjent__nazwisko',
    }
    oceny = oceny.order_by(sort_map.get(sort, '-data_oceny'))

    paginator = Paginator(oceny, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'log_fizjo.html', {
        'page_obj': page_obj,
        'current_sort': sort,
        'current_per_page': str(per_page),
        'current_search': search,
    })


# ─────────────────────────────────────────────────────────────────────────────
# PATIENT CODE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def dodaj_pacjenta_po_kodzie(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    if request.method != 'POST':
        return redirect('pacjenci_fizjo')

    fizjo = request.user.fizjoterapeuta
    kod = request.POST.get('kod', '').strip().upper()

    def render_z_bledem(blad):
        zaakceptowani = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='zaakceptowany').select_related('pacjent')
        oczekujace = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, status='oczekujacy').select_related('pacjent')
        return render(request, 'pacjenci_fizjo.html', {
            'pacjenci': [r.pacjent for r in zaakceptowani],
            'oczekujace': oczekujace, 'blad': blad, 'wpisany_kod': kod,
        })

    if not kod:
        return render_z_bledem('Wpisz kod pacjenta.')
    try:
        pacjent = Pacjent.objects.get(kod_pacjenta=kod)
    except Pacjent.DoesNotExist:
        return render_z_bledem(f'Nie znaleziono pacjenta o kodzie „{kod}". Sprawdź pisownię.')

    existing = FizjoPacjent.objects.filter(fizjoterapeuta=fizjo, pacjent=pacjent).first()
    if existing:
        if existing.status == 'zaakceptowany':
            return render_z_bledem('Ten pacjent jest już przypisany do Twojego gabinetu.')
        elif existing.status == 'oczekujacy':
            return render_z_bledem('Zaproszenie do tego pacjenta zostało już wysłane — czeka na odpowiedź.')

    FizjoPacjent.objects.create(fizjoterapeuta=fizjo, pacjent=pacjent, status='oczekujacy')
    return redirect('pacjenci_fizjo')


@login_required
def zaakceptuj_zaproszenie(request, relacja_id):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    relacja = get_object_or_404(FizjoPacjent, id=relacja_id, pacjent=request.user.pacjent, status='oczekujacy')
    relacja.status = 'zaakceptowany'
    relacja.save()
    return redirect('dashboard_pacjent')


@login_required
def odrzuc_zaproszenie(request, relacja_id):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    relacja = get_object_or_404(FizjoPacjent, id=relacja_id, pacjent=request.user.pacjent, status='oczekujacy')
    relacja.delete()
    return redirect('dashboard_pacjent')


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING PLANS – PHYSIO
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def programy_fizjo(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    plany = PlanTreningowy.objects.filter(fizjoterapeuta=fizjo).order_by('-data_utworzenia')
    return render(request, 'programy_fizjo.html', {'plany': plany})


@login_required
def dodaj_plan_treningowy(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    if request.method == 'POST':
        form = PlanTreningowyForm(request.POST, fizjo=fizjo)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.fizjoterapeuta = fizjo
            formset = CwiczenieFormSet(request.POST, instance=plan)
            if formset.is_valid():
                plan.save()
                formset.save()
                return redirect('dashboard_fizjo')
    else:
        form = PlanTreningowyForm(fizjo=fizjo)
        formset = CwiczenieFormSet()
    return render(request, 'dodaj_plan_treningowy.html', {'form': form, 'formset': formset})


@login_required
def szczegoly_planu_fizjo(request, plan_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=fizjo)
    cwiczenia = plan.cwiczenia.prefetch_related('oceny__pacjent').all()
    sesje_w_tygodniu = sesje_w_biezacym_tygodniu(plan)
    return render(request, 'szczegoly_planu_fizjo.html', {
        'plan': plan,
        'cwiczenia': cwiczenia,
        'sesje_w_tygodniu': sesje_w_tygodniu,
    })


def eksportuj_plan_csv(request, plan_id):
    plan = get_object_or_404(PlanTreningowy, id=plan_id)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="plan_{plan.id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nazwa cwiczenia', 'Serie', 'Powtorzenia'])
    for c in plan.cwiczenia.all():
        writer.writerow([c.nazwa_cwiczenia, c.serie, c.powtórzenia])
    return response


@login_required
def usun_plan(request, plan_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=request.user.fizjoterapeuta)
    if request.method == 'POST':
        plan.delete()
        return redirect('edit_fizjo')
    return redirect('edit_fizjo')


@login_required
def edytuj_plan_treningowy(request, plan_id):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    plan = get_object_or_404(PlanTreningowy, id=plan_id, fizjoterapeuta=fizjo)
    if request.method == 'POST':
        form = PlanTreningowyForm(request.POST, instance=plan, fizjo=fizjo)
        formset = CwiczenieFormSet(request.POST, instance=plan)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('edit_fizjo')
    else:
        form = PlanTreningowyForm(instance=plan, fizjo=fizjo)
        formset = CwiczenieFormSet(instance=plan)
    return render(request, 'edytuj_plan_treningowy.html', {'form': form, 'formset': formset, 'plan': plan})


@login_required
def importuj_plan_csv(request):
    if not hasattr(request.user, 'fizjoterapeuta'):
        return render(request, '403.html', status=403)
    fizjo = request.user.fizjoterapeuta
    if request.method == 'POST':
        nazwa_planu = request.POST.get('nazwa')
        pacjent_id = request.POST.get('pacjent')
        plik = request.FILES.get('plik_csv')
        if not (nazwa_planu and pacjent_id and plik):
            return HttpResponse("Wszystkie pola są wymagane.", status=400)
        if not plik.name.endswith('.csv'):
            return HttpResponse("Plik musi mieć rozszerzenie .csv", status=400)
        pacjent = get_object_or_404(Pacjent, id=pacjent_id)
        try:
            decoded_file = plik.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(decoded_file)
            next(reader, None)
            plan = PlanTreningowy.objects.create(fizjoterapeuta=fizjo, pacjent=pacjent, nazwa=nazwa_planu)
            for row in reader:
                if len(row) >= 3:
                    Cwiczenie.objects.create(
                        plan=plan, nazwa_cwiczenia=row[0].strip(),
                        serie=row[1].strip(), powtórzenia=row[2].strip()
                    )
            return redirect('programy_fizjo')
        except Exception as e:
            return HttpResponse(f"Błąd przetwarzania pliku CSV: {e}", status=400)

    pacjenci = Pacjent.objects.filter(
        relacje_z_fizjo__fizjoterapeuta=fizjo, relacje_z_fizjo__status='zaakceptowany'
    )
    return render(request, 'importuj_plan_csv.html', {'pacjenci': pacjenci})


# ─────────────────────────────────────────────────────────────────────────────
# TRAINING PLANS – PATIENT
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def plany_treningowe(request):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    pacjent = request.user.pacjent
    plany = PlanTreningowy.objects.filter(pacjent=pacjent).order_by('-data_utworzenia')
    # Attach this week's session count to each plan
    plany_z_sesjami = [(p, sesje_w_biezacym_tygodniu(p, pacjent)) for p in plany]
    return render(request, 'plany_treningowe.html', {'plany_z_sesjami': plany_z_sesjami})


@login_required
def szczegoly_planu(request, plan_id):
    if not hasattr(request.user, 'pacjent'):
        return render(request, '403.html', status=403)
    pacjent = request.user.pacjent
    plan = get_object_or_404(PlanTreningowy, id=plan_id, pacjent=pacjent)
    cwiczenia = list(plan.cwiczenia.all())

    OcenaFormSet = modelformset_factory(OcenaCwiczenia, form=OcenaCwiczeniaForm, extra=len(cwiczenia))

    if request.method == 'POST':
        formset = OcenaFormSet(request.POST, queryset=OcenaCwiczenia.objects.none())
        if formset.is_valid():
            for i, form in enumerate(formset.forms):
                if form.has_changed() and i < len(cwiczenia):
                    ocena = form.save(commit=False)
                    ocena.cwiczenie = cwiczenia[i]
                    ocena.pacjent = pacjent
                    ocena.save()
            return redirect('dashboard_sukces')
    else:
        formset = OcenaFormSet(queryset=OcenaCwiczenia.objects.none())

    ostatnie_oceny = {}
    for c in cwiczenia:
        ostatnia = c.oceny.filter(pacjent=pacjent).first()
        if ostatnia:
            ostatnie_oceny[c.id] = ostatnia

    zestaw = [(c, formset.forms[i], ostatnie_oceny.get(c.id)) for i, c in enumerate(cwiczenia)]
    sesje_w_tygodniu = sesje_w_biezacym_tygodniu(plan, pacjent)

    return render(request, 'szczegoly_planu.html', {
        'plan': plan,
        'zestaw': zestaw,
        'formset': formset,
        'sesje_w_tygodniu': sesje_w_tygodniu,
    })


@login_required
def strona_sukcesu(request):
    return render(request, 'sukces.html')