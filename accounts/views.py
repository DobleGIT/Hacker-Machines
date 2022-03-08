from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth import authenticate,login,logout

from django.contrib.auth.decorators import login_required # lo usamos para los decorators, para que no se pueda acceder a diferentes paginas sin estar loggeado

# Create your views here.
from .models import *
from .forms import CreateUserForm

def home(request):
	messages.warning(request, 'Your account expires in three days.')
	return render(request, 'accounts/home.html')

@login_required(login_url='login') #comprobamos que esté loggeado
def dashboard(request):
	return render(request, 'accounts/dashboard.html')

@login_required(login_url='login')
def maquinas(request, pk_maquina):
	maquinas = Maquina.objects.all()
	maquina_individual = Maquina.objects.get(nombre_maquina=pk_maquina) 	#esto quiere decir que a la url se le pasa la clave primaria de la maquina

	contexto = {'lista_maquinas':maquinas} 						#este es el diccionario que le pasamos a la url 
	return render(request, 'accounts/maquinas.html',contexto)

def loginUsername(request):

	contexto={}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:		#si se autentifica bien 
			login(request, user)
			return redirect('dashboard')
		else:
			messages.info(request, 'El usuario o la password es incorrecta') #ESTO NO FUNCIONA ARREGLARLO
		
	
	return render(request, 'accounts/login.html',contexto)

def logoutUser(request):
	logout(request)
	return redirect('login')

def registrarse(request):

	if request.user.is_authenticated: #esto se usa para comprobar que si está autentificado no pueda acceder a registrarse
		return redirect('home')
	else:
		form = CreateUserForm()
		
		if request.method == 'POST':
			form = CreateUserForm(request.POST)
			if form.is_valid():
				form.save()
				redirect('login')
					
			

		contexto = {'form':form}
		return render(request, 'accounts/registrarse.html', contexto)
