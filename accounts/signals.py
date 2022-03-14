from django.db.models.signals import post_save
from django.contrib.auth.models import User

from .models import *
from django.dispatch import receiver



@receiver(post_save, sender = User)
def create_profile(sender, instance, created, **kwargs):
    #cuando se crea un usuario se manda una señal para que se cree tambien un modelo alumno
    if created:
        Alumno.objects.create(user=instance)






