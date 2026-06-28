from django.urls import path
from . import views
from .forms import LoginForm

urlpatterns = [
    # Auth
    path('', views.dashboard, name='dashboard'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    path('wyloguj/', views.wyloguj, name='wyloguj'),

    # Dashboards
    path('panel-fizjo/', views.dashboard_fizjo, name='dashboard_fizjo'),
    path('panel-pacjent/', views.dashboard_pacjent, name='dashboard_pacjent'),

    # Generic add forms
    path('dodaj-fizjoterapeute/', views.dodaj_fizjoterapeute, name='dodaj_fizjoterapeute'),
    path('dodaj-pacjenta/', views.dodaj_pacjenta, name='dodaj_pacjenta'),
    path('dodaj-program/', views.dodaj_program, name='dodaj_program'),

    # Physio panel pages
    path('kalendarz-fizjo/', views.kalendarz_fizjo, name='kalendarz_fizjo'),
    path('pacjenci-fizjo/', views.pacjenci_fizjo, name='pacjenci_fizjo'),
    path('programy-fizjo/', views.programy_fizjo, name='programy_fizjo'),
    path('log-fizjo/', views.log_fizjo, name='log_fizjo'),
    path('edit-fizjo/', views.edit_fizjo, name='edit_fizjo'),

    # Doctor search & profile (patient-facing)
    path('lekarze/', views.wyszukiwarka_lekarzy, name='wyszukiwarka_lekarzy'),
    path('lekarz/<int:lekarz_id>/', views.profil_lekarza, name='profil_lekarza'),

    # Calendar APIs – patient
    path('api/get-appointments/<int:lekarz_id>/', views.get_wizyty_pacjent, name='get_wizyty_pacjent'),
    path('api/get-my-appointments/', views.get_moje_wizyty, name='get_moje_wizyty'),
    path('rezerwacja/<int:lekarz_id>/', views.formularz_rezerwacji, name='formularz_rezerwacji'),

    # Calendar APIs – physio
    path('api/get-appointments/', views.get_wizyty, name='get_wizyty'),
    path('api/add-appointment/', views.dodaj_wizyte, name='dodaj_wizyte'),

    # Appointment approval / rejection (physio)
    path('api/zatwierdz-wizyte/<int:wizyta_id>/', views.zatwierdz_wizyte, name='zatwierdz_wizyte'),
    path('api/odrzuc-wizyte/<int:wizyta_id>/', views.odrzuc_wizyte, name='odrzuc_wizyte'),

    # Patient code system
    path('pacjenci-fizjo/dodaj-po-kodzie/', views.dodaj_pacjenta_po_kodzie, name='dodaj_pacjenta_po_kodzie'),
    path('zaproszenie/<int:relacja_id>/zaakceptuj/', views.zaakceptuj_zaproszenie, name='zaakceptuj_zaproszenie'),
    path('zaproszenie/<int:relacja_id>/odrzuc/', views.odrzuc_zaproszenie, name='odrzuc_zaproszenie'),

    # Training plans – physio
    path('dodaj-plan-treningowy/', views.dodaj_plan_treningowy, name='dodaj_plan_treningowy'),
    path('programy-fizjo/<int:plan_id>/', views.szczegoly_planu_fizjo, name='szczegoly_planu_fizjo'),

    # Training plans – patient
    path('plany/', views.plany_treningowe, name='plany_treningowe'),
    path('plan/<int:plan_id>/', views.szczegoly_planu, name='szczegoly_planu'),
    path('plan/<int:plan_id>/csv/', views.eksportuj_plan_csv, name='eksportuj_plan_csv'),
    path('sukces/', views.strona_sukcesu, name='dashboard_sukces'),

    path('usun-plan/<int:plan_id>/', views.usun_plan, name='usun_plan'),
    path('edytuj-plan/<int:plan_id>/', views.edytuj_plan_treningowy, name='edytuj_plan_treningowy'),
]