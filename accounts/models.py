from random import choices
from unicodedata import category
from django.db import models

# Create your models here.
# jaimeAdmin
# SuperJaime23


class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    dia_creado = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.nombre_usuario


class Maquina(models.Model):

    ESTADO = (('Encendida', 'Apagada'),)
    

    nombre_maquina = models.CharField(max_length=30, null=True)
    estado = models.CharField(max_length=30, null=True, choices = ESTADO)
    categoria = models.CharField(max_length=30, null=True)
    descripcion = models.CharField(max_length=200, null=True)
    dia_creada = models.DateTimeField(auto_now_add=True, null=True)
