from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('panel-fizjo/', views.dashboard_fizjo, name='dodaj_fizjoterapeute'),
    path('panel-pacjent/', views.dashboard_pacjent, name='dodaj_pacjenta'),
    path('rejestracja/', views.rejestracja, name='dodaj_program'),
]