import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Fizjoterapeuta(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    imie = models.CharField(max_length=50, verbose_name="Imię")
    nazwisko = models.CharField(max_length=100, verbose_name="Nazwisko")
    specka = models.CharField(max_length=150, verbose_name="Specjalizacja")
    tytul = models.CharField(max_length=20, verbose_name="Tytuł Naukowy")

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"

class Pacjent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    imie = models.CharField(max_length=50, verbose_name="Imię pacjenta")
    nazwisko = models.CharField(max_length=100, verbose_name="Nazwisko pacjenta")
    email = models.EmailField(verbose_name="Adres e-mail")
    fizjo = models.ForeignKey(
        Fizjoterapeuta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pacjenci",
        verbose_name="Fizjoterapeuta odpowiedzialny za pacjenta"
    )

    kod_pacjenta = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Kod pacjenta"
    )

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"

class FizjoPacjent(models.Model):
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
        ('odrzucony', 'Odrzucony'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='zaakceptowany')
    data_utworzenia = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('fizjoterapeuta', 'pacjent')
        verbose_name = "Relacja fizjo-pacjent"
        verbose_name_plural = "Relacje fizjo-pacjent"

    def __str__(self):
        return f"{self.fizjoterapeuta} -> {self.pacjent} ({self.get_status_display()})"


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

class Program(models.Model):
    nazwa = models.CharField(max_length=200, verbose_name="Nazwa programu")
    opis = models.TextField(verbose_name="Opis")
    data = models.DateField(auto_now_add=True)
    pacjent = models.ForeignKey(
        Pacjent,
        on_delete=models.CASCADE,
        related_name="programy",
        verbose_name="Pacjent"
    )

    def __str__(self):
        return f"{self.nazwa} - {self.pacjent}"
     
class Wizyta(models.Model):
    STATUS_CHOICES = [
        ('oczekujaca', 'Oczekująca'),
        ('zaakceptowana', 'Zaakceptowana'),
        ('odrzucona', 'Odrzucona'),
        ('zablokowana', 'Zablokowana'),
    ]

    lekarz = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1,
        related_name='wizyty_jako_lekarz'
    )
    pacjent = models.ForeignKey(
        Pacjent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wizyty'
    )
    pacjent_nazwa = models.CharField(max_length=200, default="Pacjent", blank=True)
    powod = models.TextField(blank=True, null=True, verbose_name="Powód wizyty")
    data_rozpoczecia = models.DateTimeField()
    data_zakonczenia = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='oczekujaca')

    def __str__(self):
        return f"{self.pacjent_nazwa} - {self.data_rozpoczecia} [{self.get_status_display()}]"

    
class PlanTreningowy(models.Model):
    fizjoterapeuta = models.ForeignKey('Fizjoterapeuta', on_delete=models.CASCADE, related_name='plany')
    pacjent = models.ForeignKey('Pacjent', on_delete=models.CASCADE, related_name='plany')
    nazwa = models.CharField(max_length=200)
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    sesje_tygodniowo = models.IntegerField(default=3, verbose_name="Sesji w tygodniu")
    czas_trwania_tygodnie = models.IntegerField(default=4, verbose_name="Czas trwania (tygodnie)")

    def __str__(self):
        return f"{self.nazwa} - {self.pacjent}"

class Cwiczenie(models.Model):
    plan = models.ForeignKey(PlanTreningowy, on_delete=models.CASCADE, related_name='cwiczenia')
    nazwa_cwiczenia = models.CharField(max_length=255)
    serie = models.IntegerField(default=3)
    powtórzenia = models.CharField(max_length=50)

    def __str__(self):
        return self.nazwa_cwiczenia

class OcenaCwiczenia(models.Model):
    cwiczenie = models.ForeignKey(
        Cwiczenie,
        on_delete=models.CASCADE,
        related_name='oceny'
    )
    pacjent = models.ForeignKey(
        Pacjent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oceny'
    )
    skala_bolu = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    uwagi = models.TextField(blank=True, null=True)
    data_oceny = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_oceny']
        verbose_name = "Ocena ćwiczenia"
        verbose_name_plural = "Oceny ćwiczeń"

    def __str__(self):
        return f"Ocena: {self.cwiczenie} przez {self.pacjent} ({self.data_oceny.date() if self.data_oceny else '?'})"