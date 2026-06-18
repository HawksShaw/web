from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Fizjoterapeuta, Pacjent, Program

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
        fields = '__all__'

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