from enum import unique
from random import choices
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# jaimeAdmin
# SuperJaime23


class Alumno(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)  #creamos una relacion entre la tabla alumno y la de usuarios
    maquinas_completadas = models.IntegerField(null=True)
    puntos_conseguidos = models.IntegerField(null=True)
    user_flag = models.IntegerField(null=True)
    root_flag = models.IntegerField(null=True)
    profile_image = models.ImageField(null=True, blank = True)
    

    # def __str__(self):
    #     return self.user
#cuando se crea un nuevo usuario se llama una señal en signals.py que crea un alumno

class Maquina(models.Model):

    ESTADO = (
        ('Encendida', 'Apagada'),
    )
    
    #nombre_creador = models.ForeignKey(Usuario, null= True, on_delete=models.SET_NULL)
    nombre_maquina = models.CharField(max_length=30, null=True, unique=True)
    estado = models.CharField(max_length=30, null=True, choices = ESTADO)
    categoria = models.CharField(max_length=30, null=True)
    descripcion = models.CharField(max_length=200, null=True)
    ip = models.GenericIPAddressField(null = True)
    dia_creada = models.DateTimeField(auto_now_add=True, null=True)
