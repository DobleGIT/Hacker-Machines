from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from accounts.models import Alumno, Maquina, Category


class CreateUserForm(UserCreationForm): #es una modificacion de Usercreation para poner el email... etcs
    username = forms.CharField(label='Nombre Usuario')
    email = forms.EmailField(label='Email', required=True)
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, help_text='La contraseña debe tener mínimo 8 caracteres')
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):	#esto lo usamos para poder actualizar el email 
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']


class AlumnoUpdateForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['profile_image']


class AddMachinesForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = ['nombre_maquina','categoria','dificultad','descripcion','ip','user_flag','root_flag','image_machine']

class AddCategoriesForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['nombre']


    