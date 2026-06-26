from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
<<<<<<< Updated upstream
=======

# ==========================================
# 1. PROFILE UŻYTKOWNIKÓW I RELACJE
# ==========================================
>>>>>>> Stashed changes

class Fizjoterapeuta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    imie = models.CharField(max_length=50, verbose_name="Imię")
    nazwisko = models.CharField(max_length=100, verbose_name="Nazwisko")
    specka = models.CharField(max_length=150, verbose_name="Specjalizacja")
    tytul = models.CharField(max_length=20, verbose_name="Tytuł Naukowy")
    
    def __str__(self):
        return f"{self.tytul} {self.imie} {self.nazwisko} ({self.specka})"

class Pacjent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    imie = models.CharField(max_length=50, verbose_name="Imię pacjenta")
    nazwisko = models.CharField(max_length=100, verbose_name="Nazwisko pacjenta")
    email = models.EmailField(verbose_name="Adres e-mail")
    # Usunięto bezpośredni FK do fizjoterapeuty na rzecz modelu FizjoPacjent

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"

class FizjoPacjent(models.Model):
<<<<<<< Updated upstream
    fizjoterapeuta = models.ForeignKey(
        'Fizjoterapeuta',
        on_delete=models.CASCADE,
        related_name='relacje_z_pacjentami'
    )
    pacjent = models.ForeignKey(
        'Pacjent',
        on_delete=models.CASCADE,
        related_name='relacje_z_fizjo'
    )

    status_choices = [
        ('oczekujacy', 'Oczekujący'),
        ('zaakceptowany', 'Zaakceptowany'),
    ]
    
    status = models.CharField(max_length=20, choices=status_choices, default='zaakceptowany')
=======
    fizjoterapeuta = models.ForeignKey(Fizjoterapeuta, on_delete=models.CASCADE, related_name='relacje_z_pacjentami')
    pacjent = models.ForeignKey(Pacjent, on_delete=models.CASCADE, related_name='relacje_z_fizjo')
    
    STATUS_CHOICES = [
        ('oczekujacy', 'Oczekujący'),
        ('zaakceptowany', 'Zaakceptowany'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='zaakceptowany')
>>>>>>> Stashed changes
    data_utworzenia = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('fizjoterapeuta', 'pacjent')
        verbose_name = "Relacja fizjo-pacjent"
        verbose_name_plural = "Relacje fizjo-pacjent"

    def __str__(self):
        return f"{self.fizjoterapeuta} -> {self.pacjent} ({self.get_status_display()})"
<<<<<<< Updated upstream
    
class TreningLog(models.Model):
    pacjent = models.ForeignKey('Pacjent', on_delete=models.CASCADE, related_name='logi_treningow')
    program = models.ForeignKey('Program', on_delete=models.SET_NULL, null=True, blank=True) 
    data_wykonania = models.DateField(auto_now_add=True)

    skala_bol = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Oceń trudność treningu (odczuwany ból) w skali od 1 do 10"
    )
    pacjent_kom = models.TextField(blank=True, null=True, help_text="Opisz jak się czułeś podczas ćwiczeń.")

    class Meta:
        verbose_name = "Log Treningu"
        verbose_name_plural = "Logi Treningów"
        ordering = ['-data_wykonania']

    def __str__(self):
        return f"Trening {self.pacjent} - {self.data_wykonania}"
=======

# ==========================================
# 2. KALENDARZ I WIZYTY
# ==========================================

class Wizyta(models.Model):
    fizjoterapeuta = models.ForeignKey(Fizjoterapeuta, on_delete=models.CASCADE, related_name="wizyty")
    pacjent = models.ForeignKey(Pacjent, on_delete=models.CASCADE, related_name="wizyty")
    
    data_rozpoczecia = models.DateTimeField()
    data_zakonczenia = models.DateTimeField()
    
    STATUSY = [
        ('propozycja', 'Propozycja Pacjenta'),
        ('zatwierdzona', 'Zatwierdzona'),
        ('odrzucona', 'Odrzucona')
    ]
    status = models.CharField(max_length=20, choices=STATUSY, default='propozycja')

    def __str__(self):
        return f"{self.pacjent} u {self.fizjoterapeuta} - {self.data_rozpoczecia.strftime('%Y-%m-%d %H:%M')}"

# ==========================================
# 3. PROGRAMY I BIBLIOTEKA ĆWICZEŃ
# ==========================================
>>>>>>> Stashed changes

class Program(models.Model):
    pacjent = models.ForeignKey(Pacjent, on_delete=models.CASCADE, related_name="programy")
    fizjoterapeuta = models.ForeignKey(Fizjoterapeuta, on_delete=models.CASCADE, related_name="programy")
    
    nazwa = models.CharField(max_length=100, verbose_name="Nazwa programu")
    opis = models.TextField(verbose_name="Zalecenia ogólne", blank=True, null=True)
    
    data_startu = models.DateField(verbose_name="Data rozpoczęcia")
    data_konca = models.DateField(verbose_name="Data zakończenia")
    
    czestotliwosc_tygodniowa = models.PositiveSmallIntegerField(
        default=3, 
        help_text="Ile sesji w tygodniu pacjent ma do wyrobienia"
    )

    def __str__(self):
        return f"{self.nazwa} ({self.pacjent})"

class GlobalCwiczenie(models.Model):
    # Biblioteka bazowa ćwiczeń do wyboru z listy
    nazwa = models.CharField(max_length=255)
    opis_techniki = models.TextField(blank=True, null=True)
    wideo_url = models.URLField(blank=True, null=True)

    def __str__(self):
<<<<<<< Updated upstream
        return f"{self.pacjent_nazwa} - {self.data_rozpoczecia}"
    
class PlanTreningowy(models.Model):
    fizjoterapeuta = models.ForeignKey('Fizjoterapeuta', on_delete=models.CASCADE, related_name='plany')
    pacjent = models.ForeignKey('Pacjent', on_delete=models.CASCADE, related_name='plany')
    nazwa = models.CharField(max_length=200)
    data_utworzenia = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nazwa} - {self.pacjent}"

class Cwiczenie(models.Model):
    plan = models.ForeignKey(PlanTreningowy, on_delete=models.CASCADE, related_name='cwiczenia')
    nazwa_cwiczenia = models.CharField(max_length=255)
    serie = models.IntegerField(default=3)
    powtórzenia = models.CharField(max_length=50) # "10", "12-15", "30s"

    def __str__(self):
        return self.nazwa_cwiczenia

class OcenaCwiczenia(models.Model):
    cwiczenie = models.OneToOneField(Cwiczenie, on_delete=models.CASCADE, related_name='ocena')
    skala_bolu = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    uwagi = models.TextField(blank=True, null=True)
    data_oceny = models.DateTimeField(auto_now_add=True)
=======
        return self.nazwa

class ProgramCwiczenie(models.Model):
    # Przypisanie ćwiczenia do konkretnego programu z seriami
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='cwiczenia')
    cwiczenie_bazowe = models.ForeignKey(GlobalCwiczenie, on_delete=models.PROTECT)
    
    serie = models.IntegerField(default=3)
    powtorzenia = models.CharField(max_length=50) # "10", "12-15", "30s"

    def __str__(self):
        return f"{self.cwiczenie_bazowe.nazwa} ({self.program.nazwa})"

# ==========================================
# 4. LOGI I DZIENNICZEK PACJENTA
# ==========================================

class TreningLog(models.Model):
    pacjent = models.ForeignKey(Pacjent, on_delete=models.CASCADE, related_name='logi_treningow')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='logi') 
    data_wykonania = models.DateField(auto_now_add=True)

    skala_bol = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Oceń odczuwany ból w skali od 1 do 10"
    )
    pacjent_kom = models.TextField(blank=True, null=True, help_text="Opisz jak się czułeś podczas ćwiczeń.")

    class Meta:
        verbose_name = "Log Treningu"
        verbose_name_plural = "Logi Treningów"
        ordering = ['-data_wykonania']
        # BRAMKARZ: Blokuje podwójny wpis z tego samego dnia!
        unique_together = ('pacjent', 'program', 'data_wykonania') 

    def __str__(self):
        return f"Trening {self.pacjent} - {self.data_wykonania}"

class ZrobioneCwiczenia(models.Model):
    # Konkretne odhaczenie checkboxa w aplikacji z danego dnia
    trening_log = models.ForeignKey(TreningLog, on_delete=models.CASCADE, related_name='wykonane_cwiczenia')
    cwiczenie_program = models.ForeignKey(ProgramCwiczenie, on_delete=models.CASCADE)
    wykonane = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cwiczenie_z_programu.cwiczenie_bazowe.nazwa} - {'Zrobione' if self.wykonane else 'Pominięte'}"
>>>>>>> Stashed changes
