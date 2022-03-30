from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required # lo usamos para los decorators, para que no se pueda acceder a diferentes paginas sin estar loggeado

# Create your views here.
from .models import *
from .forms import CreateUserForm, UserUpdateForm, AlumnoUpdateForm  
from .decorators import unauthenticathed_user #decorador creado para que si estas loggeado no puedas entrar a la pagina

def home(request):
	
	return render(request, 'accounts/home.html')

@login_required(login_url='login') #comprobamos que esté loggeado y si no es así se le manda al /login
def dashboard(request):
	current_user = request.user
	#current_alumno = User.objects.get()
	user = User.objects.all()
	context = {'user_list':user}



	return render(request, 'accounts/dashboard.html',context)


@login_required(login_url='login') #comprobamos que esté loggeado y si no es así se le manda al /login
def profile(request):				#esta sacado de aqui https://www.youtube.com/watch?v=CQ90L5jfldw&ab_channel=CoreySchafer

	
	# lo que hacemos aqui es crear dos forms que saquen solo el email y la foto de perfil en caso de que no sea POST y en caso de que lo sea see guardan los forms
	if request.method == 'POST': #creamos dos forms distintos porque uno es para la tabla Alumno y otra para la tabla User
		alumno_form = AlumnoUpdateForm(request.POST, request.FILES, instance = request.user.alumno)
		user_form = UserUpdateForm(request.POST, instance=request.user)
		
		if user_form.is_valid() and alumno_form.is_valid():
			user_form.save()
			alumno_form.save()
			messages.success(request, f'Se ha actualizado tu perfil')
			return redirect('profile')
	else:
		alumno_form = AlumnoUpdateForm(instance = request.user.alumno)		#creamos dos forms distintos porque uno es para la tabla Alumno y otra para la tabla User
		user_form = UserUpdateForm(instance = request.user)
	
	context={'alumno_form':alumno_form, 'user_form':user_form}
	return render(request, 'accounts/profile.html',context)


@login_required(login_url='login')
def maquinas(request, nombre_maquina_url=None):
    
    maquinas = Maquina.objects.all()
    current_user = request.user
    lista_vacia = [] 

    if nombre_maquina_url != None: #si se le pasa como argumento el nombre de la maquina

        maquina_individual = Maquina.objects.get(nombre_maquina=nombre_maquina_url) 	#esto quiere decir que a la url se le pasa la clave primaria de la maquina
        
        context = {'lista_maquinas':lista_vacia, 'maquina_individual':maquina_individual} 

    else: #si no se le pasa ninguna maquina se muestran todas las maquinas
        context = {'lista_maquinas':maquinas} 						#este es el diccionario que le pasamos a la url 
    return render(request, 'accounts/maquinas.html',context)

@login_required(login_url='login')
def access_to_machine(request, nombre_maquina_url): #a esta url se llega cuando le da el alumno a acceder a la maquina desde /machines/<nombreMaquina> creamos la relación muchos a muchos entre el usuario y la maquina

    urlMachine = '/maquinas/'
    urlMachine += nombre_maquina_url

    current_user = request.user
    machine_to_access = Maquina.objects.get(nombre_maquina=nombre_maquina_url)

    
    access = Acceso(alumnoA=current_user, maquinaA=machine_to_access)
    access.save()
    return redirect(urlMachine)

#@unauthenticathed_user
def loginUsername(request):     #la pagina del login

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

def logoutUser(request):	#cuando el usuario pulsa el boton de logout se le direcciona a la pagina /logout que llama al metodo logout para hacer el que? pues si, el logout
	logout(request)
	return redirect('login')

def registrarse(request):

	#if request.user.is_authenticated: #esto se usa para comprobar que si está autentificado no pueda acceder a registrarse
	#	return redirect('home')
	#else:
	
		
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()

			#Alumno.objects.create(user=user)
			username = form.cleaned_data['username']
			messages.success(request, f'Usuario {username} creado')
			return redirect('login')
	else:
		form = CreateUserForm()

	contexto = {'form':form}			
	return render(request, 'accounts/registrarse.html', contexto)
