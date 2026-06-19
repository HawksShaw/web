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
    
    # Widoki bloków dashboardów
    path('dodaj-fizjoterapeute/', views.dodaj_fizjoterapeute, name='dodaj_fizjoterapeute'),
    path('dodaj-pacjenta/', views.dodaj_pacjenta, name='dodaj_pacjenta'),
    path('dodaj-program/', views.dodaj_program, name='dodaj_program'),

    # Hiperłącza do bloków w panel-fizjo
    path('kalendarz-fizjo/', views.kalendarz_fizjo, name='kalendarz_fizjo'),
    path('pacjenci-fizjo/', views.pacjenci_fizjo, name='pacjenci_fizjo'),
    path('programy-fizjo/', views.programy_fizjo, name='programy_fizjo'),

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
]