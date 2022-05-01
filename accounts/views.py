from urllib import response
from django.shortcuts import get_object_or_404, redirect, render
from django.http import FileResponse, HttpResponse, Http404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import *
from django.contrib.auth.decorators import login_required  # lo usamos para los decorators, para que no se pueda acceder a diferentes paginas sin estar loggeado 
from django.contrib.auth.models import Group
from django.utils import timezone
from django.db.models.functions import Now

# Create your views here.
from .models import *
from .decorators import allowed_users #allowed_users es usado para controlar los grupos y permisos para acceder a determinadas paginas
from django.core.paginator import Paginator
import docker, datetime, os
from .forms import CreateUserForm, UserUpdateForm, AlumnoUpdateForm, AddCategoriesForm, AddMachinesForm
from .decorators import unauthenticathed_user #decorador creado para que si estas loggeado no puedas entrar a la pagina
from .filters import UserFilter                 #filtro para buscar por usuarios

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
    machinesCompleted=[]
    machinesCompletedList = []
    user = get_object_or_404(User, pk=id)
    userFlags = 0
    rootFlags = 0
    alumno = Alumno.objects.get(user=user)
    countMachinesInside = Acceso.objects.filter(alumnoA=user).count()
    countCompletedRooms = Acceso.objects.filter(alumnoA=user, completed=True).count()
    
    if countCompletedRooms != 0:
        
        machinesCompleted= Acceso.objects.filter(alumnoA=user,completed=True)
        for machine in machinesCompleted:
            maquinaIndividual = Maquina.objects.get(pk=machine.maquinaA.pk)
            machinesCompletedList.append(maquinaIndividual)

        
    
    rootFlags = Acceso.objects.filter(alumnoA=user, root_flag=True).count()
    context = {'user':user, 'countMachinesInside':countMachinesInside, 'countCompletedRooms':countCompletedRooms, 'points':alumno.points , 'machinesCompleted':machinesCompleted}
    
    return render(request, 'accounts/userProfile.html', context)

@login_required(login_url='login')
def ranking(request):
    
    count=0
    page_objO=[]
    listaUsuarios = User.objects.all()
    listaUsuariosOrdenada = listaUsuarios.order_by('-alumno__points')
    myFilter = UserFilter(request.GET, queryset=listaUsuariosOrdenada)
    
    listaUsuariosOrdenadaFiltrada = myFilter.qs
    print(listaUsuariosOrdenadaFiltrada)

    if listaUsuariosOrdenadaFiltrada.count() == 1: #en caso de que se haya filtrado y solo haya un usuario se recorre la lista para calcular cual es su posicion
        for iterator in listaUsuariosOrdenada:
            count+=1
            if iterator.username == listaUsuariosOrdenadaFiltrada[0].username:
                print(count)
                iterator.alumno.position = count
                page_objO.append(iterator)
                break
    else:                                       #en caso de que no se filtre y se muestren todos los usuarios se calcula su posicion para todos
        for iterator in listaUsuariosOrdenadaFiltrada:
            count+=1
            iterator.alumno.position=count
            page_objO.append(iterator)

    
    paginator = Paginator(page_objO, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
        
    # print(listaUsuariosOrdenada)
    #lista_alumnos_ordenada = lista_alumnos.order_by('-puntos')
    context = {"listaUsuariosOrdenada":listaUsuariosOrdenada,'page_obj': page_obj, 'paginator':paginator, 'myFilter':myFilter}
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
    acceso = []

    # actualDate = timezone.now()
    # print(actualDate)

    if nombre_maquina_url != None: #si se le pasa como argumento el nombre de la maquina
        
        #print(timezone.now())
        # print(datetime.datetime.now())
        maquina_individual = Maquina.objects.get(nombre_maquina=nombre_maquina_url) 	#esto quiere decir que a la url se le pasa la clave primaria de la maquina
        
        #seleccionamos los datos globales de la maquina
        usersInside = Acceso.objects.filter(maquinaA=maquina_individual).count() #usuarios que han accedido a la maquina
        #usersInside = usersInside.count()
        usersUserFlag = Acceso.objects.filter(maquinaA=maquina_individual, user_flag=True).count() #usuario que ha accedido a la maquina y que está loggeado
        usersRootFlag = Acceso.objects.filter(maquinaA=maquina_individual, root_flag=True).count() #usuario que ha accedido a la maquina y que es root        
        
        if Acceso.objects.filter(alumnoA=current_user, maquinaA=maquina_individual).exists(): #esto lo hacemos para evitar errores
            acceso = Acceso.objects.get(alumnoA=current_user, maquinaA=maquina_individual)
            # print(acceso.accesed_date)
            # print(timezone.now())
        else:
            pass
        if request.method == 'POST':        #si se hac un post, siginfica que se estan mandando flags
            flagUserInput = request.POST.get('flagUserInput')
            flagRootInput = request.POST.get('flagRootInput')
            urlMachine = '/maquinas/'
            urlMachine += nombre_maquina_url

            if request.POST.get('restart') != None: #si se ha pulsado el botón de reinciar
                #eso hacerlo asi si se ejecuta en mi pc
                comandReset = 'vboxmanage controlvm' + ' ' + nombre_maquina_url + ' ' + 'reset'
                os.system(comandReset)

                #esto ejecutarlo asi si está en la maquina virtual
                comandReset = "ssh jaime@192.168.1.136 'vboxmanage controlvm" + ' ' + nombre_maquina_url + ' ' + "reset'"
                print(comandReset)
                messages.success(request, 'El reto se está reiniciando, espera unos minutos a que se desplieguen todos los servicios')

            elif flagUserInput == maquina_individual.user_flag:
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
                        actualDate = timezone.now()
                        print(actualDate)
                        acceso.finish_date = actualDate

                        #calculamos el tiempo en dias horas y minutos para guardarlo en la base de datos
                        rest = actualDate - acceso.accesed_date
                        #calculamos el tiempo en dias horas y minutos para guardarlo en la base de datos,
                        #se hacen todas estas conversiones para que no dan error con el split
                        rest = actualDate - acceso.accesed_date
                        print(rest)
                        rest = str(rest)
                        rest = rest.split(':')
                        rest[2] = float(rest[2])
                        rest[2]= f'{rest[2]:.0f}'
                        if int(rest[0]) >= 1:
                            acceso.days_to_finish = int(rest[0])
                        if int(rest[1]) >= 1:
                            acceso.hours_to_finish = int(rest[1])
                        if int(rest[2]) >= 1:
                            acceso.minutes_to_finish = int(rest[2])
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
                        actualDate = timezone.now()
                        
                        acceso.finish_date = actualDate
                        
                        #calculamos el tiempo en dias horas y minutos para guardarlo en la base de datos,
                        #se hacen todas estas conversiones para que no dan error con el split
                        rest = actualDate - acceso.accesed_date
                        print(rest)
                        rest = str(rest)
                        rest = rest.split(':')
                        rest[2] = float(rest[2])
                        rest[2]= f'{rest[2]:.0f}'
                        if int(rest[0]) >= 1:
                            acceso.days_to_finish = int(rest[0])
                        if int(rest[1]) >= 1:
                            acceso.hours_to_finish = int(rest[1])
                        if int(rest[2]) >= 1:
                            acceso.minutes_to_finish = int(rest[2])

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
        

        
        context = {'lista_maquinas':lista_vacia, 'maquina_individual':maquina_individual, 'usersInside':usersInside, 'usersUserFlag':usersUserFlag, 'usersRootFlag':usersRootFlag, 'individualUserFlag':individualUserFlag, 'individualRootFlag':individualRootFlag, 'individualCompleted':individualCompleted, 'acceso':acceso}
        render(request, 'accounts/maquinas.html',context)

    else: #si no se le pasa ninguna maquina se muestran todas las maquinas
        context = {'lista_maquinas':maquinas} 						#este es el diccionario que le pasamos a la url 
    return render(request, 'accounts/maquinas.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def addMachine(request):
    
    if request.method == 'POST':

        machineForm = AddMachinesForm(request.POST, request.FILES)
        if machineForm.is_valid():
            machineForm.save()
            messages.success(request, '¡Maquina añadida con éxito!')
            return redirect('maquinas')

    else:
        machineForm = AddMachinesForm()
    context = {'machineForm':machineForm}
    return render(request, 'accounts/addMachine.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def editMachine(request, nombre_maquina_url):

    maquina = Maquina.objects.get(nombre_maquina=nombre_maquina_url)
    if request.method == 'POST':
        machineForm = AddMachinesForm(request.POST, request.FILES, instance=maquina)
        if machineForm.is_valid():
            machineForm.save()
            messages.success(request, '¡Maquina editada con éxito!')
            return redirect('maquinas')
    else:
        machineForm = AddMachinesForm(instance=maquina)
    context = {'machineForm':machineForm}
    return render(request, 'accounts/editMachine.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteMachine(request, nombre_maquina_url):

    maquina = Maquina.objects.get(nombre_maquina=nombre_maquina_url)
    if request.method == 'POST':
        maquina.delete()
        messages.success(request, '¡Maquina eliminada con éxito!')
        return redirect('maquinas')
    context = {'maquina':maquina}
    return render(request, 'accounts/deleteMachine.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def categories(request):
    
    categories = Category.objects.all()
    context = {'categories':categories}
    return render(request, 'accounts/categories.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def addCategories(request):
        
    if request.method == 'POST':
        categoryForm = AddCategoriesForm(request.POST)
        if categoryForm.is_valid():
            categoryForm.save()
            messages.success(request, '¡Categoría añadida con éxito!')
            return redirect('categories')
    else:
        categoryForm = AddCategoriesForm()
    context = {'categoryForm':categoryForm}
    return render(request, 'accounts/addCategories.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def editCategories(request, nombre_categoria_url):

    categoria = Category.objects.get(nombre=nombre_categoria_url)
    if request.method == 'POST':
        categoryForm = AddCategoriesForm(request.POST, instance=categoria)
        if categoryForm.is_valid():
            categoryForm.save()
            messages.success(request, '¡Categoría editada con éxito!')
            return redirect('categories')
    else:
        categoryForm = AddCategoriesForm(instance=categoria)
    context = {'categoryForm':categoryForm}
    return render(request, 'accounts/editCategories.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteCategories(request, nombre_categoria_url):
    
    categoria = Category.objects.get(nombre=nombre_categoria_url)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, '¡Categoría eliminada con éxito!')
        return redirect('categories')
    context = {'categoria':categoria}
    return render(request, 'accounts/deleteCategories.html', context)

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
    contexto={}
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            newAlumno=form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='alumno') #añadimos al alumno al grupo alumno
            newAlumno.groups.add(group)
            # if request.user.is_staff
            # messages.success(request, f'Usuario {username} creado')
            #Generamos el archivo openvpn para el alumno
            #comando equivalente a docker run -v hacker-machines-openvpn:/etc/openvpn --rm -it kylemanna/openvpn easyrsa build-client-full username nopass
            client = docker.from_env()
            volumenes = ['hacker-machines-openvpn:/etc/openvpn']
            commandoGenerar =['easyrsa', 'build-client-full', username, 'nopass']
            imagen = 'kylemanna/openvpn'
            variable=['EASYRSA_PASSIN=pass:SuperJaime23'] #contraseña del docker
            client.containers.run(image=imagen,command=commandoGenerar,volumes=volumenes,environment=variable,auto_remove=True)
            
            #comando equivalente a docker run -v hacker-machines-openvpn:/etc/openvpn --rm kylemanna/openvpn ovpn_getclient username > username.ovpn
            comandoObtener = ['ovpn_getclient', username]
            cosa = client.containers.run(image=imagen,command=comandoObtener,volumes=volumenes,auto_remove=True)
            
            #guardamos el archivo en el directorio de la base de datos
            nameFile = '/home/jaime/Escritorio/TFG/media/openvpn/'+username+'.ovpn'

            archivoOpenVpn=open(nameFile,"w")
            archivoOpenVpn.write(cosa.decode('utf-8'))
            archivoOpenVpn.close()

            #guardamos en la base de datos
            userCreated = User.objects.get(username=username)
            alumnoCreated = Alumno.objects.get(user=userCreated)
            alumnoCreated.openvpnFile = '/media/openvpn/'+username+'.ovpn'
            alumnoCreated.save()

            login(request, userCreated)
            return redirect('home')
        else:
            messages.info(request, 'Completa correctamente los campos')
    else:
        form = CreateUserForm()
    contexto = {'form':form}
    return render(request, 'accounts/registrarse.html',contexto)


