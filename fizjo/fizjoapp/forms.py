from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Fizjoterapeuta, Pacjent, Program

class RejestrForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adres e-mail")

    role_wybor = [
        ('pacjent', 'Jestem Pacjentem'),
        ('fizjo', 'Jestem Fizjoterapeutą'),
    ]
    rola = forms.ChoiceField(
        choices=role_wybor,
        widget=forms.RadioSelect,
        label="Typ konta"
    )

class Meta(UserCreationForm):
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