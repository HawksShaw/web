from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dodaj-fizjo/', views.add_fizjo, name='dodaj_fizjoterapeute'),
    path('dodaj-pacjenta/', views.add_pacjent, name='dodaj pacjenta'),
    path('dodaj-program/', views.add_program, name='dodaj_program'),
]