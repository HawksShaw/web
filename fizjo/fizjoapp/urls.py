from django.urls import path
from . import views

urlpatterns = [
    # Główne widoki
    path('', views.dashboard, name='dashboard'),
    path('panel-fizjo/', views.dashboard_fizjo, name='dashboard_fizjo'),
    path('panel-pacjent/', views.dashboard_pacjent, name='dashboard_pacjent'),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('wyloguj/', views.wyloguj, name='wyloguj'),
    
    # Widoki formularzy (wymagane przez przyciski w dashboard.html)
    path('dodaj-fizjoterapeute/', views.dodaj_fizjoterapeute, name='dodaj_fizjoterapeute'),
    path('dodaj-pacjenta/', views.dodaj_pacjenta, name='dodaj_pacjenta'),
    path('dodaj-program/', views.dodaj_program, name='dodaj_program'),
]