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
        return f"{self.tytul} {self.imie} {self.nazwisko} ({self.specka})"
    

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
#Kalendarz  
class Wizyta(models.Model):
    lekarz = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    pacjent_nazwa = models.CharField(max_length=100, default="Pacjent")
    data_rozpoczecia = models.DateTimeField()
    data_zakonczenia = models.DateTimeField()

    def __str__(self):
        return f"{self.pacjent_nazwa} - {self.data_rozpoczecia}"