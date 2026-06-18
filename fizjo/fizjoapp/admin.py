from django.contrib import admin
from .models import Fizjoterapeuta, Pacjent, Program, FizjoPacjent, TreningLog

# Register your models here.
admin.site.register(Fizjoterapeuta)
admin.site.register(Pacjent)
admin.site.register(Program)
admin.site.register(TreningLog)
admin.site.register(FizjoPacjent)
