from enum import unique
from random import choices
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from PIL import Image       #Lo usamos para redimensionar la imagen de perfil

# Create your models here.
# jaimeAdmin
# SuperJaime23


class Alumno(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)  #creamos una relacion entre la tabla alumno y la de usuarios
    maquinas_completadas = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    profile_image = models.ImageField(default='images/profileImages/foto_perfil.png', upload_to='images/profileImages/')
    openvpnFile = models.FileField(upload_to='openvpn/',null=True) #cambiar el default
    position = models.IntegerField(default=0)
    #accessed_machines = models.ManyToManyField('Maquina', through='Acceso')
    

    def __str__(self):
        return f'{self.user.username}'

    
    def accesed_machines(self):
        """
        It returns the machines that the user has accessed
        :return: A QuerySet of the machines that the user has accessed.
        """
        machines_ids = Acceso.objects.filter(alumnoA=self.user).values_list('maquinaA', flat=True)
        return Maquina.objects.filter(id__in=machines_ids)
    


    # def save(self):           esto es para redimensionar las imagenes que se suben pero no funciona y me da pereza ver el por que
    #     super().save()

    #     img = Image.open(self.profile_image.path)

    #     if img.height > 300 or img.width < 300:
    #         output_size = (300,300)
    #         img.thumbnail(output_size)
    #         img.save(self.profile_image.path)


#cuando se crea un nuevo usuario se llama una señal en signals.py que crea un alumno

class Maquina(models.Model):

    ESTADO = (
        ('Encendida', 'Apagada'),
    )
    
    nombre_maquina = models.CharField(max_length=30, null=True, unique=True)
    estado = models.CharField(max_length=30, null=True, choices = ESTADO)
    categoria = models.CharField(max_length=30, null=True)
    descripcion = models.CharField(max_length=1000, null=True)
    ip = models.GenericIPAddressField(null = True)
    dia_creada = models.DateTimeField(auto_now_add=True, null=True)
    user_flag = models.CharField(max_length=30,null=True)
    root_flag = models.CharField(max_length=30, null=True)
    image_machine = models.ImageField(default='images/machineImages/linuxLogo.png',upload_to='images/machineImages/')

    def __str__(self):
        return f'{self.nombre_maquina}'

    
    # def accesed_users(self):
    #     """
    #     It returns the list of users that have accessed a given machine
    #     :return: A QuerySet of Alumno objects.
    #     """
    #     users_ids = Acceso.objects.filter(maquina=self.pk).values_list('alumno', flat=True)
    #     return Alumno.objects.filter(pk__in=users_ids)
    

class Acceso(models.Model):
    
    alumnoA = models.ForeignKey(User, on_delete=models.CASCADE)
    maquinaA = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    accesed_date = models.DateTimeField(auto_now_add=True)
    finish_date = models.DateTimeField(null=True)
    user_flag = models.BooleanField(default=False)
    root_flag = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.alumnoA} accede a {self.maquinaA}'
    

