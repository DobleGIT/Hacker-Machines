from enum import unique
from random import choices
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from PIL import Image       #Lo usamos para redimensionar la imagen de perfil

# Create your models here.

class Alumno(models.Model):
    """
        Modelo que guarda información extra sobre los usuarios, como el número de máquinas completadas, los puntos, la imagen de perfil y el archivo openvpn.
    """
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)  
    """Relación entre la tabla Alumno y User"""
    maquinas_completadas = models.IntegerField(default=0)
    """Número de máquinas completadas"""
    points = models.IntegerField(default=0)
    """Número total de puntos conseguidos"""
    profile_image = models.ImageField(default='images/profileImages/foto_perfil.png', upload_to='images/profileImages/')
    """Imagen de perfil"""
    openvpnFile = models.FileField(upload_to='openvpn/',null=True) 
    """Se guarda la dirección en donde está el archivo .ovpn de conexión"""
   

    def __str__(self):
        return f'{self.user.username}'

    
    def accesed_machines(self):
        """
        Retorna las máquinas a las que ha accedido el Alumno.
        """
        machines_ids = Acceso.objects.filter(alumnoA=self.user).values_list('maquinaA', flat=True)
        return Maquina.objects.filter(id__in=machines_ids)
        
    #cuando se crea un nuevo usuario se llama una señal en signals.py que crea un alumno


class Maquina(models.Model):
    """
        Modelo que guarda información sobre las Máquinas que hay en el sistema.
    """
    DIFICULTAD = [
        ('Fácil', 'Fácil'),
        ('Media', 'Media'),
        ('Difícil', 'Difífil'),
        ('Insana', 'Insana'),
    ]
    
    nombre_maquina = models.CharField(max_length=30, null=True, unique=True)
    """Nombre de la Máquina"""
    dificultad = models.CharField(max_length=30, null=True, choices = DIFICULTAD)
    """Dificultad que se le asigna a la Máquina pudiendo ser, Facil, Media, Difícil o Insana"""
    categoria = models.ManyToManyField('Category')
    """Relación ManyToMany entre Máquina y Categoría"""
    descripcion = models.CharField(max_length=1000, null=True)
    """Descripción de la Máquina"""
    ip = models.GenericIPAddressField(null = True)
    """IP que se le asigna a la Máquina"""
    dia_creada = models.DateTimeField(auto_now_add=True, null=True)
    """Fecha en la que se ha creado"""
    user_flag = models.CharField(max_length=30,null=True)
    """User Flag del reto"""
    root_flag = models.CharField(max_length=30, null=True)
    """Root Flag del reto"""
    image_machine = models.ImageField(default='images/machineImages/linuxLogo.png',upload_to='images/machineImages/')
    """Imagen de la Máquina"""
    activa= models.BooleanField(default=True)
    """Se utiliza para saber si la Máquina es visible o no en la plataforma"""
    reboot = models.DateTimeField(null=True)
    """Se guarda la fecha del último reinicio, para evitar que varios usuarios se reinicien la máquina a la vez"""

    def __str__(self):
        return f'{self.nombre_maquina}'
    
    def save(self, *args, **kwargs):
        """
        Comprueba si la imagen de la máquina tiene un ancho y alto mayor de 300, si es así la redimensiona a 300x300 y la guarda.
        """
        super().save(*args, **kwargs)

        img = Image.open(self.image_machine.path)

        if img.height > 300 or img.width < 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image_machine.path)

class Acceso(models.Model):
    """
        Este modelo se utiliza para mantener una relación entre User y Máquinas, añadiendose una nueva entrada cada vez que un 
        Usuario accede a una nueva Máquina y creando la información relativa a la resolución del reto.
    """
    alumnoA = models.ForeignKey(User, on_delete=models.CASCADE)
    """Relación con la tabla User"""
    maquinaA = models.ForeignKey(Maquina, on_delete=models.CASCADE)
    """Relación con la tabla Maquina"""
    accesed_date = models.DateTimeField(auto_now_add=True)
    """Guarda la fecha en la que accedió a la máquina"""
    finish_date = models.DateTimeField(null=True)
    """Guarda la fecha en la que resolvió a la máquina"""
    days_to_finish = models.IntegerField(default=False)
    """Días que ha tardado en resolver la máquina"""
    hours_to_finish = models.IntegerField(default=False)
    """Horas que ha tardado en resolver la máquina"""
    minutes_to_finish = models.IntegerField(default=False)
    """Minutos que ha tardado en resolver la máquina"""
    user_flag = models.BooleanField(default=False)
    """Booleano que indica si ha resuleto la User Flag"""
    root_flag = models.BooleanField(default=False)
    """Booleano que indica si ha resuleto la Root Flag"""
    completed = models.BooleanField(default=False)
    """Booleano que indica si ha completado la máquina"""
    
    def __str__(self):
        return f'{self.alumnoA} accede a {self.maquinaA}'
    
class Category(models.Model):
    """
        Este modelo se utiliza para guardar información sobre las categorías.
    """
    nombre = models.CharField(max_length=40, null=True)
    """Nombre de la categoría"""
    dia_creada = models.DateTimeField(auto_now_add=True, null=True)
    """Fecha en la que se creó la categoría"""
    def __str__(self):
        return f'{self.nombre}'
