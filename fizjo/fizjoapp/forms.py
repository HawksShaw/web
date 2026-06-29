from django import forms
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

class FizjoForm(forms.ModelForm):
    class Meta:
        model = Fizjoterapeuta
        fields = '__all__'

class PacjentForm(forms.ModelForm):
    class Meta:
        model = Pacjent
        exclude = ['kod_pacjenta']  # auto-generated on registration, never user-editable

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
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
        fields = ['pacjent', 'nazwa', 'sesje_tygodniowo', 'czas_trwania_tygodnie']
        widgets = {
            'pacjent': forms.Select(attrs={'class': 'form-select'}),
            'nazwa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Powrót po kontuzji ACL'}),
            'sesje_tygodniowo': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '7'}),
            'czas_trwania_tygodnie': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'sesje_tygodniowo': 'Sesji w tygodniu',
            'czas_trwania_tygodnie': 'Czas trwania (tygodnie)',
        }

    def __init__(self, *args, **kwargs):
        # Wyciągamy przekazanego fizjoterapeutę (jeśli istnieje)
        fizjo = kwargs.pop('fizjo', None)
        super().__init__(*args, **kwargs)
        
        if fizjo:
            # Filtrujemy queryset pacjentów korzystając z relacji (related_name='relacje_z_fizjo')
            self.fields['pacjent'].queryset = Pacjent.objects.filter(
                relacje_z_fizjo__fizjoterapeuta=fizjo,
                relacje_z_fizjo__status='zaakceptowany'
            )

# Tworzymy powiązane formularze dla ćwiczeń (extra=3 oznacza, że domyślnie pojawią się 3 puste wiersze na ćwiczenia)
CwiczenieFormSet = inlineformset_factory(
    PlanTreningowy, 
    Cwiczenie, 
    fields=['nazwa_cwiczenia', 'serie', 'powtórzenia'],
    extra=3, 
    can_delete=True,
    widgets={
        'nazwa_cwiczenia': forms.TextInput(attrs={'class': 'form-control'}),
        'serie': forms.NumberInput(attrs={'class': 'form-control'}),
        'powtórzenia': forms.TextInput(attrs={'class': 'form-control'}),
    }
)