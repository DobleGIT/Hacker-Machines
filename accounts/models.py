from enum import unique
from random import choices
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# jaimeAdmin
# SuperJaime23


class Alumno(models.Model):
    maquinas_completadas = models.IntegerField()
    puntos_conseguidos = models.IntegerField()
    user_flag = models.IntegerField()
    root_flag = models.IntegerField()
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)  #creamos una relacion entre la tabla alumno y la de usuarios

    def __str__(self):
        return self.nombre_usuario


class Maquina(models.Model):

    ESTADO = (
        ('Encendida', 'Apagada'),
    )
    
    #nombre_creador = models.ForeignKey(Usuario, null= True, on_delete=models.SET_NULL)
    nombre_maquina = models.CharField(max_length=30, null=True, unique=True)
    estado = models.CharField(max_length=30, null=True, choices = ESTADO)
    categoria = models.CharField(max_length=30, null=True)
    descripcion = models.CharField(max_length=200, null=True)
    dia_creada = models.DateTimeField(auto_now_add=True, null=True)
