from django.contrib import admin

# Register your models here.

from .models import *

#aqui ponemos lo que queremos que se vea en el admin panel de la base de datos
admin.site.register(Alumno)
admin.site.register(Maquina)