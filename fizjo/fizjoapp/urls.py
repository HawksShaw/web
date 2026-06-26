from django.urls import path
from . import views
from .forms import LoginForm

urlpatterns = [
    # Główne wejścia
    path('', views.dashboard, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
<<<<<<< Updated upstream
    path('panel-fizjo/', views.dashboard_fizjo, name='dashboard_fizjo'),
    path('panel-pacjent/', views.dashboard_pacjent, name='dashboard_pacjent'),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('wyloguj/', views.wyloguj, name='wyloguj'),
    
    # Widoki bloków dashboardów
    path('dodaj-fizjoterapeute/', views.dodaj_fizjoterapeute, name='dodaj_fizjoterapeute'),
    path('dodaj-pacjenta/', views.dodaj_pacjenta, name='dodaj_pacjenta'),
    path('dodaj-program/', views.dodaj_program, name='dodaj_program'),

    # Hiperłącza do bloków w panel-fizjo
=======
    path('wyloguj/', views.wyloguj, name='wyloguj'),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    
    # Panele główne
    path('panel-fizjo/', views.dashboard_fizjo, name='dashboard_fizjo'),
    path('panel-pacjent/', views.dashboard_pacjent, name='dashboard_pacjent'),

    # Wykonywanie ćwiczeń przez pacjenta (Nowe!)
    path('program/<int:program_id>/cwicz/', views.wykonaj_dzisiejszy_trening, name='wykonaj_trening'),
    path('sukces/', views.strona_sukces, name='dashboard_sukces'),

    # Zakładki Fizjoterapeuty
>>>>>>> Stashed changes
    path('kalendarz-fizjo/', views.kalendarz_fizjo, name='kalendarz_fizjo'),
    path('pacjenci-fizjo/', views.pacjenci_fizjo, name='pacjenci_fizjo'),
    path('programy-fizjo/', views.programy_fizjo, name='programy_fizjo'),
    path('log-fizjo/', views.log_fizjo, name='log_fizjo'),
    path('edit-fizjo/', views.edit_fizjo, name='edit_fizjo'),
<<<<<<< Updated upstream

    # Kalendarz
    path('lekarze/', views.wyszukiwarka_lekarzy, name='wyszukiwarka_lekarzy'),
    path('lekarz/<int:lekarz_id>/', views.profil_lekarza, name='profil_lekarza'),
    path('api/get-appointments/<int:lekarz_id>/', views.get_wizyty_pacjent, name='get_wizyty_pacjent'),
    path('api/add-appointment/<int:lekarz_id>/', views.dodaj_wizyte_pacjent, name='dodaj_wizyte_pacjent'),
    path('api/get-appointments/', views.get_wizyty, name='get_wizyty'),
    path('api/add-appointment/', views.dodaj_wizyte, name='dodaj_wizyte'),
    path('rezerwacja/<int:lekarz_id>/', views.formularz_rezerwacji, name='formularz_rezerwacji'),
    path('api/get-my-appointments/', views.get_moje_wizyty, name='get_moje_wizyty'),
    
    # ======== NOWE ŚCIEŻKI DLA PLANÓW TRENINGOWYCH ========
    path('plany/', views.plany_treningowe, name='plany_treningowe'),
    path('plan/<int:plan_id>/', views.szczegoly_planu, name='szczegoly_planu'),
    path('plan/<int:plan_id>/csv/', views.eksportuj_plan_csv, name='eksportuj_plan_csv'),
    path('sukces/', views.strona_sukcesu, name='dashboard_sukces'),
    path('dodaj-plan-treningowy/', views.dodaj_plan_treningowy, name='dodaj_plan_treningowy'),
    path('programy-fizjo/<int:plan_id>/', views.szczegoly_planu_fizjo, name='szczegoly_planu_fizjo'),
=======
    path('programy-fizjo/nowy/', views.dodaj_program, name='dodaj_program'),

    # API Kalendarza
    path('fizjoterapeuci/', views.wyszukiwarka_fizjo, name='wyszukiwarka_lekarzy'), # Nazwa 'wyszukiwarka_lekarzy' zachowana dla wstecznej kompatybilności HTML
    path('fizjo/<int:fizjo_id>/', views.profil_fizjo, name='profil_lekarza'),
    path('api/get-appointments/<int:fizjo_id>/', views.get_wizyty_pacjent, name='get_wizyty_pacjent'),
    path('api/add-appointment/<int:fizjo_id>/', views.dodaj_wizyte_pacjent, name='dodaj_wizyte_pacjent'),
    path('api/get-appointments/', views.get_wizyty, name='get_wizyty'),
    path('api/add-appointment/', views.dodaj_wizyte, name='dodaj_wizyte'),

    # Eksporty
    path('program/<int:program_id>/csv/', views.eksportuj_plan_csv, name='eksportuj_plan_csv'),
>>>>>>> Stashed changes
]