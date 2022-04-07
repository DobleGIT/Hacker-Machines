from urllib import response
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse, HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required # lo usamos para los decorators, para que no se pueda acceder a diferentes paginas sin estar loggeado

# Create your views here.
from .models import *
import os
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
def userProfile(request, id):
    machinesInside=0
    user = get_object_or_404(User, pk=id)
    userFlags = 0
    rootFlags = 0
    alumno = Alumno.objects.get(user=user)

    machinesInside = Acceso.objects.filter(alumnoA=user).count()
    completedRooms = Acceso.objects.filter(alumnoA=user, completed=True).count()
    rootFlags = Acceso.objects.filter(alumnoA=user, root_flag=True).count()
    context = {'user':user, 'machinesInside':machinesInside, 'completedRooms':completedRooms, 'points':alumno.points}
    return render(request, 'accounts/userProfile.html', context)

@login_required(login_url='login')
def ranking(request):
    
    listaUsuarios = User.objects.all()
    listaUsuariosOrdenada = listaUsuarios.order_by('-alumno__points')
    #lista_alumnos_ordenada = lista_alumnos.order_by('-puntos')
    context = {"listaUsuariosOrdenada":listaUsuariosOrdenada}
    return render(request, 'accounts/ranking.html',context)


@login_required(login_url='login')
def maquinas(request, nombre_maquina_url=None):

    
    maquinas = Maquina.objects.all()
    current_user = request.user
    alumnoBD = Alumno.objects.get(user=current_user)
    lista_vacia = [] 
    individualUserFlag = False
    individualRootFlag= False
    individualCompleted= False

    if nombre_maquina_url != None: #si se le pasa como argumento el nombre de la maquina
        

        maquina_individual = Maquina.objects.get(nombre_maquina=nombre_maquina_url) 	#esto quiere decir que a la url se le pasa la clave primaria de la maquina
        
        #seleccionamos los datos globales de la maquina
        usersInside = Acceso.objects.filter(maquinaA=maquina_individual).count() #usuarios que han accedido a la maquina
        #usersInside = usersInside.count()
        usersUserFlag = Acceso.objects.filter(maquinaA=maquina_individual, user_flag=True).count() #usuario que ha accedido a la maquina y que está loggeado
        usersRootFlag = Acceso.objects.filter(maquinaA=maquina_individual, root_flag=True).count() #usuario que ha accedido a la maquina y que es root        
        
        if Acceso.objects.filter(alumnoA=current_user, maquinaA=maquina_individual).exists(): #esto lo hacemos para evitar errores
            acceso = Acceso.objects.get(alumnoA=current_user, maquinaA=maquina_individual)
        else:
            pass
        if request.method == 'POST':        #si se hac un post, siginfica que se estan mandando flags
            flagUserInput = request.POST.get('flagUserInput')
            flagRootInput = request.POST.get('flagRootInput')
            urlMachine = '/maquinas/'
            urlMachine += nombre_maquina_url

            if flagUserInput == maquina_individual.user_flag:
                #modificar el valor user_flag de la tabla acceso
                
                if acceso.user_flag == True:
                    messages.warning(request, 'Ya conseguiste esta flag')
                else:
                    acceso.user_flag = True
                    acceso.save()
                    alumnoBD.points += 50
                    alumnoBD.save()
                    if acceso.completed == False and acceso.user_flag == True and acceso.root_flag == True: #comprobamos si al meter la flag ha completado ya la maquina
                        acceso.completed = True
                        acceso.save()
                        alumnoBD.points += 50
                        alumnoBD.save()
                        messages.success(request, '¡Enhorabuena, has completado el reto +100 puntos!')
                        
                    else:
                        messages.success(request, '¡Genial has acertado, +50 puntos!')
        
            elif flagRootInput == maquina_individual.root_flag:
                #modificar el valor root_flag de la tabla acceso
                acceso = Acceso.objects.get(alumnoA=current_user, maquinaA=maquina_individual)
                if acceso.root_flag == True:
                    messages.warning(request, 'Ya conseguiste esta flag')
                else:
                    acceso.root_flag = True
                    acceso.save()
                    alumnoBD.points += 50
                    alumnoBD.save()
                    if acceso.completed == False and acceso.user_flag == True and acceso.root_flag == True:
                        acceso.completed = True
                        acceso.save()
                        alumnoBD.points += 50
                        alumnoBD.save()
                        messages.success(request, '¡Enhorabuena, has completado el reto +100 puntos!')
                        
                    else:
                        messages.success(request, '¡Genial has acertado, +50 puntos!')

            else:
                messages.warning(request, 'La flag es incorrecta')
                
        if Acceso.objects.filter(alumnoA=current_user, maquinaA=maquina_individual).exists(): 
            acceso = Acceso.objects.get(alumnoA=current_user, maquinaA=maquina_individual)
            individualUserFlag = acceso.user_flag # le pasamos la user_flag y root_flag del usuario para comprobar si la ha completado ya o no
            individualRootFlag = acceso.root_flag
            individualCompleted = acceso.completed #le pasamos el valor completed del usuario para comprobar si ha completado ya o no la maquina
        else:
            pass
        

        
        context = {'lista_maquinas':lista_vacia, 'maquina_individual':maquina_individual, 'usersInside':usersInside, 'usersUserFlag':usersUserFlag, 'usersRootFlag':usersRootFlag, 'individualUserFlag':individualUserFlag, 'individualRootFlag':individualRootFlag, 'individualCompleted':individualCompleted}
        render(request, 'accounts/maquinas.html',context)

    else: #si no se le pasa ninguna maquina se muestran todas las maquinas
        context = {'lista_maquinas':maquinas} 						#este es el diccionario que le pasamos a la url 
    return render(request, 'accounts/maquinas.html',context)

@login_required(login_url='login')
def access_to_machine(request, nombre_maquina_url): #a esta url se llega cuando le da el alumno a acceder a la maquina desde /machines/<nombreMaquina> creamos la relación muchos a muchos entre el usuario y la maquina
    #comprobar que no se puede acceder dos veces a la mierda esta
    urlMachine = '/maquinas/'
    urlMachine += nombre_maquina_url

    current_user = request.user
    machine_to_access = Maquina.objects.get(nombre_maquina=nombre_maquina_url)
    machineUserAcess = Acceso.objects.filter(alumnoA=current_user, maquinaA=machine_to_access)

    if machineUserAcess: #esto se hace para no acceder dos veces a la misma máquina
        messages.warning(request, 'Ya has accedido a esta maquina')
        return redirect(urlMachine)
    else:
        access = Acceso(alumnoA=current_user, maquinaA=machine_to_access)
        access.save()
        return redirect(urlMachine)

@login_required(login_url='login')
def openvpn(request):
    current_user = request.user
    alumnoBD = Alumno.objects.get(user=current_user)
    
    context = {}
    return render(request, 'accounts/openvpn.html',context)

@login_required(login_url='login')
def secureOpenVpnFiles(request,file):
    # urlFileOpenVpn = 'openvpn/'
    # urlFileOpenVpn += file
    # current_user = request.user
    # if Alumno.objects.filter(user=current_user, openvpnFile=urlFileOpenVpn).exists(): #comprobamos que el archivo que quiere descargar es el suyo propio
    #     return HttpResponse(file, content_type='application/octet-stream')
    # else:
    #     return redirect('home')
    urlFileOpenVpn = 'openvpn/'
    urlFileOpenVpn += file
    pathPc = '/home/jaime/Escritorio/TFG/media/openvpn/'
    pathPc += file
    current_user = request.user
    if Alumno.objects.filter(user=current_user, openvpnFile=urlFileOpenVpn).exists(): #comprobamos que el archivo que quiere descargar es el suyo propio
        fileRead = open(pathPc, 'rb')
        return FileResponse(fileRead, content_type='application/octet-stream')
    else:
        return redirect('home')

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

