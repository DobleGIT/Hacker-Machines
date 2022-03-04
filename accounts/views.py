from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  

# Create your views here.
from .models import *
from .forms import CreateUserForm

def home(request):
	return render(request, 'accounts/home.html')

def maquinas(request, pk_maquina):
	maquinas = Maquina.objects.all()
	maquina_individual = Maquina.objects.get(nombre_maquina=pk_maquina) 	#esto quiere decir que a la url se le pasa la clave primaria de la maquina

	contexto = {'lista_maquinas':maquinas} 						#este es el diccionario que le pasamos a la url 
	return render(request, 'accounts/maquinas.html',contexto)

def iniciarSesion(request):
	return render(request, 'accounts/iniciarSesion.html')

def registrarse(request):
	form = CreateUserForm()
	
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Account created successfully')		
		

	contexto = {'form':form}
	return render(request, 'accounts/registrarse.html', contexto)
# Create your views here.
