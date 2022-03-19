from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from accounts.models import Alumno


class CreateUserForm(UserCreationForm): #es una modificacion de Usercreation para poner el email... etcs
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']

class ProfileForm(ModelForm): #https://www.youtube.com/watch?v=15UrLdnjlpQ&ab_channel=Codemy.com
	class Meta:
		#model = User
		#fields = ['username', 'email', 'password1', 'password2']
		model = Alumno
		fields = '__all__'
		#exclude = ['maquinas_completadas','puntos_conseguidos','user_flag','root_flag','profile_image']
		exclude = ['user']

class UserUpdateForm(forms.ModelForm):	#esto lo usamos para poder actualizar el email 
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']


class AlumnoUpdateForm(forms.ModelForm):
    class Meta:
        model = Alumno
        fields = ['profile_image']
