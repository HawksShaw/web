from django.urls import path
from . import views
from .forms import LoginForm

urlpatterns = [
    # Główne widoki
    path('', views.dashboard, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('panel-fizjo/', views.dashboard_fizjo, name='dashboard_fizjo'),
    path('panel-pacjent/', views.dashboard_pacjent, name='dashboard_pacjent'),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('wyloguj/', views.wyloguj, name='wyloguj'),
    
    # Widoki formularzy (wymagane przez przyciski w dashboard.html)
    path('dodaj-fizjoterapeute/', views.dodaj_fizjoterapeute, name='dodaj_fizjoterapeute'),
    path('dodaj-pacjenta/', views.dodaj_pacjenta, name='dodaj_pacjenta'),
    path('dodaj-program/', views.dodaj_program, name='dodaj_program'),

    #Kalendarz
    path('lekarze/', views.wyszukiwarka_lekarzy, name='wyszukiwarka_lekarzy'),
    path('lekarz/<int:lekarz_id>/', views.profil_lekarza, name='profil_lekarza'),
    path('api/get-appointments/<int:lekarz_id>/', views.get_wizyty_pacjent, name='get_wizyty_pacjent'),
    path('api/add-appointment/<int:lekarz_id>/', views.dodaj_wizyte_pacjent, name='dodaj_wizyte_pacjent'),
    path('api/get-appointments/', views.get_wizyty, name='get_wizyty'),
    path('api/add-appointment/', views.dodaj_wizyte, name='dodaj_wizyte'),
]