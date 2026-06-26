from django import forms
<<<<<<< Updated upstream
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Fizjoterapeuta, Pacjent, Program
from .models import PlanTreningowy, Cwiczenie
from django.forms import inlineformset_factory

class RejestrForm(UserCreationForm):
    username = forms.CharField(
        max_length=50, 
        label="Nazwa Użytkownika",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    imie = forms.CharField(
        max_length=50, 
        label="Imię",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nazwisko = forms.CharField(
        max_length=100, 
        label="Nazwisko",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True, 
        label="Adres e-mail",
=======
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

# NASZE NOWE MODELE:
from .models import (
    Fizjoterapeuta, Pacjent, Program, 
    GlobalCwiczenie, ProgramCwiczenie, TreningLog
)

# ==========================================
# 1. FORMULARZE AUTORYZACJI
# ==========================================

class RejestrForm(UserCreationForm):
    username = forms.CharField(
        max_length=50, label="Nazwa Użytkownika",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    imie = forms.CharField(
        max_length=50, label="Imię",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nazwisko = forms.CharField(
        max_length=100, label="Nazwisko",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True, label="Adres e-mail",
>>>>>>> Stashed changes
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    role_wybor = [
        ('pacjent', 'Jestem Pacjentem'),
        ('fizjo', 'Jestem Fizjoterapeutą'),
    ]
    
    # Dla przycisków Radio używamy innej klasy Bootstrapa: 'form-check-input'
    rola = forms.ChoiceField(
        choices=role_wybor,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Typ konta"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'Hasło'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].label = 'Potwierdź hasło'

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nazwa użytkownika"
        self.fields['password'].label = "Hasło"
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Wpisz login...'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Wpisz hasło...'})


# ==========================================
# 2. PROSTE FORMULARZE PROFILOWE
# ==========================================

class FizjoForm(forms.ModelForm):
    class Meta:
        model = Fizjoterapeuta
        exclude = ['user']

class PacjentForm(forms.ModelForm):
    class Meta:
        model = Pacjent
        exclude = ['user']


# ==========================================
# 3. FORMULARZE PROGRAMU I ĆWICZEŃ (SERCE SYSTEMU)
# ==========================================

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
<<<<<<< Updated upstream
        fields = '__all__'

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Nazwa użytkownika"
        self.fields['password'].label = "Hasło"
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Wpisz swój login...'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Wpisz hasło...'})

from .models import OcenaCwiczenia

class OcenaCwiczeniaForm(forms.ModelForm):
    class Meta:
        model = OcenaCwiczenia
        fields = ['skala_bolu', 'uwagi']
        widgets = {
            # Zmieniamy zwykłe pole tekstowe na suwak od 0 do 10
            'skala_bolu': forms.NumberInput(attrs={
                'type': 'range', 'min': '0', 'max': '10', 'class': 'form-range'
            }),
            'uwagi': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Np. kłucie w kolanie przy 3 serii...'}),
        }

class PlanTreningowyForm(forms.ModelForm):
    class Meta:
        model = PlanTreningowy
        fields = ['pacjent', 'nazwa'] # Fizjoterapeutę dodamy automatycznie w widoku
        widgets = {
            'pacjent': forms.Select(attrs={'class': 'form-select'}),
            'nazwa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Powrót po kontuzji ACL'}),
        }

# Tworzymy powiązane formularze dla ćwiczeń (extra=3 oznacza, że domyślnie pojawią się 3 puste wiersze na ćwiczenia)
CwiczenieFormSet = inlineformset_factory(
    PlanTreningowy, 
    Cwiczenie, 
    fields=['nazwa_cwiczenia', 'serie', 'powtórzenia'],
    extra=3, 
    can_delete=False,
    widgets={
        'nazwa_cwiczenia': forms.TextInput(attrs={'class': 'form-control'}),
        'serie': forms.NumberInput(attrs={'class': 'form-control'}),
        'powtórzenia': forms.TextInput(attrs={'class': 'form-control'}),
    }
)
=======
        # Fizjoterapeutę przypisujemy automatycznie w widoku z request.user!
        fields = ['pacjent', 'nazwa', 'opis', 'data_startu', 'data_konca', 'czestotliwosc_tygodniowa']
        widgets = {
            'pacjent': forms.Select(attrs={'class': 'form-select'}),
            'nazwa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Rehabilitacja barku po zwichnięciu'}),
            'opis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Zalecenia ogólne dla pacjenta...'}),
            'data_startu': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_konca': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'czestotliwosc_tygodniowa': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 7}),
        }

# FORMSET: Łączy Program z 3 wierszami ćwiczeń do wyboru
CwiczenieFormSet = inlineformset_factory(
    Program, 
    ProgramCwiczenie, 
    fields=['cwiczenie_bazowe', 'serie', 'powtorzenia'],
    extra=3, 
    can_delete=True,
    widgets={
        'cwiczenie_bazowe': forms.Select(attrs={'class': 'form-select'}), # <--- TO JEST TWÓJ DROPDOWN Z BAZY!
        'serie': forms.NumberInput(attrs={'class': 'form-control'}),
        'powtorzenia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. 12-15 lub 45s'}),
    }
)


# ==========================================
# 4. FORMULARZ DZIENNICZKA DLA PACJENTA
# ==========================================

class TreningLogForm(forms.ModelForm):
    class Meta:
        model = TreningLog
        fields = ['skala_bol', 'pacjent_kom']
        widgets = {
            'skala_bol': forms.NumberInput(attrs={
                'type': 'range', 'min': '1', 'max': '10', 'class': 'form-range'
            }),
            'pacjent_kom': forms.Textarea(attrs={
                'rows': 3, 'class': 'form-control', 'placeholder': 'Opisz jak się dzisiaj czułeś...'
            }),
        }
>>>>>>> Stashed changes
