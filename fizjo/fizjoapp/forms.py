from django import forms
from .models import Fizjoterapeuta, Pacjent, Program

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