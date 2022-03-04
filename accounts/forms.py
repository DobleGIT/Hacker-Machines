from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class CreateUserForm(UserCreationForm): #es una modificacion de Usercreation para poner el email... etcs
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']