import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

# UWAGA: Zamień 'twoja_aplikacja' na nazwę swojej aplikacji w Django!
from fizjoapp.models import Fizjoterapeuta, Pacjent

class Command(BaseCommand):
    help = 'Generuje fałszywych pacjentów i fizjoterapeutów.'

    def add_arguments(self, parser):
        parser.add_argument('--fizjo', type=int, default=5, help='Liczba fizjoterapeutów do wygenerowania')
        parser.add_argument('--pacjenci', type=int, default=20, help='Liczba pacjentów do wygenerowania')

    def handle(self, *args, **options):
        fake = Faker('pl_PL')
        liczba_fizjo = options['fizjo']
        liczba_pacjentow = options['pacjenci']

        specki = ['Ortopedia', 'Neurologia', 'Pediatria', 'Medycyna Sportowa', 'Geriatria']
        tytuly = ['mgr', 'dr', 'dr n. med.']
        wspolne_haslo = 'testpassword123'

        self.stdout.write(self.style.WARNING('Rozpoczynam generowanie danych...'))

        # --- GENEROWANIE FIZJOTERAPEUTÓW ---
        utworzono_fizjo = 0
        for _ in range(liczba_fizjo):
            imie = fake.first_name()
            nazwisko = fake.last_name()
            username = fake.unique.user_name()
            
            # Tworzymy konto User
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password=wspolne_haslo,
                first_name=imie,
                last_name=nazwisko
            )
            
            # Tworzymy profil Fizjoterapeuty
            Fizjoterapeuta.objects.create(
                user=user,
                imie=imie,
                nazwisko=nazwisko,
                specka=random.choice(specki),
                tytul=random.choice(tytuly)
            )
            utworzono_fizjo += 1

        self.stdout.write(self.style.SUCCESS(f'Utworzono {utworzono_fizjo} fizjoterapeutów.'))

        # --- GENEROWANIE PACJENTÓW ---
        utworzono_pacjentow = 0
        wszyscy_fizjo = list(Fizjoterapeuta.objects.all())

        for _ in range(liczba_pacjentow):
            imie = fake.first_name()
            nazwisko = fake.last_name()
            username = fake.unique.user_name()
            email = fake.unique.email()
            
            # Tworzymy konto User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=wspolne_haslo,
                first_name=imie,
                last_name=nazwisko
            )

            # Generujemy unikalny kod pacjenta
            kod = fake.unique.bothify(text='PAC-####-????').upper()

            # Przypisujemy losowego fizjoterapeutę (jeśli istnieje)
            przypisany_fizjo = random.choice(wszyscy_fizjo) if wszyscy_fizjo else None
            
            # Tworzymy profil Pacjenta
            Pacjent.objects.create(
                user=user,
                imie=imie,
                nazwisko=nazwisko,
                email=email,
                fizjo=przypisany_fizjo,
                kod_pacjenta=kod
            )
            utworzono_pacjentow += 1

        self.stdout.write(self.style.SUCCESS(f'Utworzono {utworzono_pacjentow} pacjentów.'))
        self.stdout.write(self.style.SUCCESS(f'Loginy są unikalne, hasło dla wszystkich to: {wspolne_haslo}'))