from django.shortcuts import render, redirect
from .models import Fizjoterapeuta, Pacjent, Program
from .forms import FizjoForm, PacjentForm, ProgramForm

# Create your views here.
def dashboard(request):
    fizjoterapeuci = Fizjoterapeuta.objects.all()
    pacjenci = Pacjent.objects.all()
    programy = Program.objects.all()

    context = {
        'fizjoterapeuci' : fizjoterapeuci,
        'pacjenci' : pacjenci,
        'programy' : programy
    }
    return render(request, 'dashboard.html', context)

def add_element(request, form_class, template_label):
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'formularz.html', {'form':form, 'tytul':template_label})


def add_fizjo(request):
    return add_element(request, FizjoForm, "Dodaj Fizjoterapeutę")

def add_pacjent(request):
    return add_element(request, PacjentForm, "Dodaj Pacjenta")

def add_program(request):
    return add_element(request, ProgramForm, "Dodaj Program Ćwiczeniowy")
