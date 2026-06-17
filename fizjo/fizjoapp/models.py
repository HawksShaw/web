from django.db import models
from django.contrib.auth.models import User

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