from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms

from accounts.models import Alumno, Maquina, Category

class CreateUserForm(UserCreationForm): 
    """
        Modificación de UserCreatrionForm para poder cambiar el formulario del registro a español y especificar los valores que se quieran.
    """
    username = forms.CharField(label='Nombre Usuario')
    """Nombre de Usuario"""
    email = forms.EmailField(label='Email', required=True)
    """Email del Usuario"""
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, help_text='La contraseña debe tener mínimo 8 caracteres')
    """Contraseña del Usuario"""
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)
    """Repetir Contraseña del Usuario"""
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    """Formulario utilizado para poder editar el email"""
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email']


class AlumnoUpdateForm(forms.ModelForm):
    """Formulario utilizado para poder editar la imagen de perfil del Usuario"""
    class Meta:
        model = Alumno
        fields = ['profile_image']


class AddMachinesForm(forms.ModelForm):
    """Formulario utilizado para poder añadir y editar máquinas"""
    class Meta:
        model = Maquina
        fields = ['nombre_maquina','categoria','dificultad','descripcion','ip','user_flag','root_flag','image_machine']

class AddCategoriesForm(forms.ModelForm):
    """Formulario utilizado para poder añadir y editar categorías"""
    class Meta:
        model = Category
        fields = ['nombre']

class PasswordChangingForm(PasswordChangeForm):	
    """Formulario utilizado para poder cambiar la contraseña"""
    new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    new_password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    class Meta:
        model = User
        fields = ('new_password1','new_password2')

    