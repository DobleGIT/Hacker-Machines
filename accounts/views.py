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

import random #random y string lo usamos para generar las urls aleatorias al crear el archivo ovpn
import string




def home(request):
	"""
    La función home() muestra la pantalla de inicio del sistema 

    :param request: Objeto http
    :return: El render del template home.html
    """
	return render(request, 'accounts/home.html')


@login_required(login_url='login') #comprobamos que esté loggeado y si no es así se le manda al /login
def profile(request):				#esta sacado de aqui https://www.youtube.com/watch?v=CQ90L5jfldw&ab_channel=CoreySchafer

    """
    Esta funcion se utiliza para editar el perfil, se crean dos formularios uno para
    el modelo Alumno y otro para el modelo Usuario.
    Si el método es post se comprueban y se guardan los datos
    Si el método es get se envían los formularios
    
    :param request: Objeto http
    :return del GET: El render del template editProfile.html.
    :return del POST: El render del template userProfile.html.
    """
	
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
    return render(request, 'accounts/EditProfile.html',context)

@login_required(login_url='login')
def userProfile(request, id):
    """
    Muestra el perfil de un usuario.
    
    :param request: Objeto http
    :param id: El id del usuario que se quiere ver
    :return: El render del template userProfile.html
    """
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
    """
    Obtiene una lista de todos los usuarios, los ordena por puntos y los muestra por pantalla en forma de tabla.

    :param request: Objeto http
    :return: El render del template ranking.html
    """
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
    """
    Si solo se le pasa un argumento, es decir, el request mostrará una lista de todas las máquinas del sistema.
    En cambio si se le pasa un argumento va a ser el nombre de la máquina, mostrando los detalles de la misma y realizando las siguientes acciones:
    -Si es un método POST pueden ser dos cosas:
        1º) Si en el POST está el argumento restart se reinicia la máquina conectandose por ssh a la máquina principal donde se está ejecutando.
        2º) Sino significa que se están enviando las respuestas del reto, por lo que comprueba si son correctas y se suman los determinados puntos
   
    :param request: Objeto http
    :return: El render del template maquinas.html
    """
    
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
        usersUserFlag = Acceso.objects.filter(maquinaA=maquina_individual, user_flag=True).count() #usuario que ha accedido a la maquina y que está loggeado
        usersRootFlag = Acceso.objects.filter(maquinaA=maquina_individual, root_flag=True).count() #usuario que ha accedido a la maquina y que es root        
        
        if Acceso.objects.filter(alumnoA=current_user, maquinaA=maquina_individual).exists(): #esto lo hacemos para evitar errores
            acceso = Acceso.objects.get(alumnoA=current_user, maquinaA=maquina_individual)
            # print(acceso.accesed_date)
            # print(timezone.now())
        else:
            pass
        if request.method == 'POST':        
            flagUserInput = request.POST.get('flagUserInput')
            flagRootInput = request.POST.get('flagRootInput')
            urlMachine = '/maquinas/'
            urlMachine += nombre_maquina_url

            if request.POST.get('restart') != None and maquina_individual.activa: #si se ha pulsado el botón de reinciar
                #eso hacerlo asi si se ejecuta en mi pc
                #comandReset = 'vboxmanage controlvm' + ' ' + nombre_maquina_url + ' ' + 'reset'
                #os.system(comandReset)

                #esto ejecutarlo asi si está en la maquina virtual
                actualTime = timezone.now()
                if maquina_individual.reboot != None:
                    rest = actualTime - maquina_individual.reboot
                    rest = str(rest)
                    rest = rest.split(':')
                    
                    if int(rest[1]) <5: #300 segundos tienen que pasar para volver a reiniciar la maquina
                        messages.success(request, 'El ya se está reiniciando, por favor espera a que se despliegue la máquina')
                    else:
                        maquina_individual.reboot = actualTime
                        maquina_individual.save()
                        comandReset = "ssh jaime@192.168.1.136 'vboxmanage controlvm" + ' ' + nombre_maquina_url + ' ' + "reset'"
                        os.system(comandReset)
                        messages.success(request, 'El reto se está reiniciando, espera unos minutos a que se desplieguen la máquina')
                else:
                    maquina_individual.reboot = actualTime
                    maquina_individual.save()
                    comandReset = "ssh jaime@192.168.1.136 'vboxmanage controlvm" + ' ' + nombre_maquina_url + ' ' + "reset'"
                    os.system(comandReset)
                    messages.success(request, 'El reto se está reiniciando, espera unos minutos a que se desplieguen la máquina')
            
            elif flagUserInput == maquina_individual.user_flag and maquina_individual.activa:
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
                        #print(actualDate)
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
        
            elif flagRootInput == maquina_individual.root_flag and maquina_individual.activa:
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
                messages.warning(request, 'La FLAG introducida es incorrecta')
                
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

@login_required(login_url='/login/')
#@allowed_users(allowed_roles=['admin']))
def visibleMachine(request, nombre_maquina_url):
    """
    Si la máquina está activa, esta será desactivada, sino será activada.
    
    :param request: Objeto http.
    :param nombre_maquina_url: Es el nombre de la máquina que queremos activar/desactivar
    :return: El render del template maquinas.html
    """
    maquina_individual = Maquina.objects.get(nombre_maquina=nombre_maquina_url)
    if maquina_individual.activa == False:
        maquina_individual.activa = True
        maquina_individual.save()
        messageText= 'La maquina ' + maquina_individual.nombre_maquina + ' ha sido activada'
        messages.success(request, messageText)
        return redirect('maquinas')
    else:
        maquina_individual.activa = False
        maquina_individual.save()
        messageText= 'La maquina ' + maquina_individual.nombre_maquina + ' ha sido desactivada'
        messages.success(request, messageText)
        return redirect('maquinas')

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin']))
def addMachine(request):
    """
    Si el método es POST entonces se comprueba y se añade la nueva máquina en la base de datos.
    
    Pero si el método es GET, entonces sólo muestra el formulario para añadir una máquina.
    
    :param request: Objeto Http.
    :return del GET: El render del template addMachine.html
    :return del POST: El render del template maquinas.html
    """
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
#@allowed_users(allowed_roles=['admin']))
def editMachine(request, nombre_maquina_url):
    """
    Si el método es POST entonces se comprueba y se edita la máquina en la base de datos, pero si
    el método es GET, entonces sólo muestra el formulario para editar una máquina.
    
    :param request: Objeto Http.
    :param nombre_maquina_url: Nombre de la máquina que se quiere editar.
    :return del GET: El render del template editMachine.html
    :return del POST: El render del template maquinas.html
    """
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
#@allowed_users(allowed_roles=['admin']))
def deleteMachine(request, nombre_maquina_url):
    """
    Si el método es POST entonces borra la máquina en la base de datos, pero si
    el método es GET, entonces sólo muestra el template deleteMachine.html
    
    :param request: Objeto Http.
    :param nombre_maquina_url: Nombre de la máquina que se quiere borrar.
    :return del GET: El render del template deleteMachine.html
    :return del POST: El render del template maquinas.html
    """
    maquina = Maquina.objects.get(nombre_maquina=nombre_maquina_url)
    if request.method == 'POST':
        maquina.delete()
        messages.success(request, '¡Maquina eliminada con éxito!')
        return redirect('maquinas')
    context = {'maquina':maquina}
    return render(request, 'accounts/deleteMachine.html', context)

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin']))
def categories(request):
    """
    Muestra una lista de las categorías que hay en el sistema.
    
    :param request: Objeto Http.
    :return: El render del template categories.html
    """
    categories = Category.objects.all()
    context = {'categories':categories}
    return render(request, 'accounts/categories.html',context)

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin']))
def addCategories(request):
    """
    Si el método es POST entonces añade la nueva categoría a la base de datos, pero si
    el método es GET, entonces sólo muestra el template categories.html
    
    :param request: Objeto Http.
    :return del GET: El render del template addCategories.html
    :return del POST: El render del template categories.html
    """    
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
#@allowed_users(allowed_roles=['admin']))
def editCategories(request, nombre_categoria_url):
    """
    Si el método es POST entonces edita la categoría en la base de datos, pero si
    el método es GET, entonces sólo muestra el template editCategories.html
    
    :param request: Objeto Http.
    :param nombre_maquina_url: Nombre de la categoróa que se quiere editar.
    :return del GET: El render del template editCategories.html
    :return del POST: El render del template categories.html
    """
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
#@allowed_users(allowed_roles=['admin']))
def deleteCategories(request, nombre_categoria_url):
    """
    Si el método es POST entonces elimina la categoría en la base de datos, pero si
    el método es GET, entonces sólo muestra el template deleteCategories.html
    
    :param request: Objeto Http.
    :param nombre_maquina_url: Nombre de la categoróa que se quiere borrar.
    :return del GET: El render del template deleteCategories.html
    :return del POST: El render del template categories.html
    """
    categoria = Category.objects.get(nombre=nombre_categoria_url)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, '¡Categoría eliminada con éxito!')
        return redirect('categories')
    context = {'categoria':categoria}
    return render(request, 'accounts/deleteCategories.html', context)

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin']))
def createAdminUser(request, id):
    """
    Si el método es POST entonces eleva de privilegios a un usuario, pero si
    el método es GET, entonces sólo muestra el template createAdminUser.html
    
    :param request: Objeto Http.
    :param id: Id del usuario que se quiere hacer administrador.
    :return del GET: El render del template createAdminUser.html
    :return del POST: El render del template userProfile.html
    """
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
    
    if request.method == 'POST':
        group = Group.objects.get(name='admin') #lo añadimos al grupo de admin
        user.groups.add(group)
        user.is_staff=True
        user.save()
        
        messages.success(request, '¡Usuario elevado a administrador!')
        return render(request, 'accounts/userProfile.html', context)

    return render(request, 'accounts/createAdminUser.html', context)

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin']))
def deleteAdminUser(request, id):
    """
    Si el método es POST entonces eleva de quita privilegios a un usuario, pero si
    el método es GET, entonces sólo muestra el template deleteAdminUser.html
    
    :param request: Objeto Http.
    :param id: Id del usuario que se quiere quitar permisos de administrador.
    :return del GET: El render del template deleteAdminUser.html
    :return del POST: El render del template userProfile.html
    """
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
    if request.method == 'POST':
        group = Group.objects.get(name='admin') #lo añadimos al grupo de admin
        user.groups.remove(group)
        user.is_staff=False
        user.save()
        
        messages.success(request, '¡Usuario actualizado!')
        return render(request, 'accounts/userProfile.html', context)

    return render(request, 'accounts/deleteAdminUser.html', context)

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin']))
def deleteUser(request, id):
    """
    Si el método es POST entonces elimina a un usuario, pero si
    el método es GET, entonces sólo muestra el template deleteUser.html
    
    :param request: Objeto Http.
    :param id: Id del usuario que se quiere eliminar.
    :return del GET: El render del template deleteUser.html
    :return del POST: El render del template ranking.html
    """
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
    if request.method == 'POST':
        user.delete()
        
        messages.success(request, '¡Usuario Eliminado Correctamente!')
        return redirect('ranking')

    return render(request, 'accounts/deleteUser.html', context)

@login_required(login_url='login')
def access_to_machine(request, nombre_maquina_url): #a esta url se llega cuando le da el alumno a acceder a la maquina desde /machines/<nombreMaquina> creamos la relación muchos a muchos entre el usuario y la maquina
    #comprobar que no se puede acceder dos veces a la mierda esta
    """
    Crea una nueva fila en la base de datos del modelo Acceso, haciendo que el usuario haya accedido a la máquina. 

    :param request: Objeto Http.
    :param nombre_maquina_url: Nombre de la máquina que se quiere acceder.
    :return: El render del template maquinas.html
    """
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
    """
    Se muestra la información relativa a la VPN.

    :param request: Objeto Http.
    :return: El render del template openvpn.html
    """
    current_user = request.user
    alumnoBD = Alumno.objects.get(user=current_user)
    
    context = {}
    return render(request, 'accounts/openvpn.html',context)


#@unauthenticathed_user
def loginUsername(request):     #la pagina del login
    """
    Si el método es POST se comprueba si el usuario y contraseña es correcto, por el contrario se 
    muestra el render del template login.html.

    :param request: Objeto Http.
    :return: El render del template login.html
    """

    contexto={}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:		#si se autentifica bien 
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'El Usuario o la Contraseña es incorrecta') #ESTO NO FUNCIONA ARREGLARLO
            
    return render(request, 'accounts/login.html',contexto)

def logoutUser(request):	#cuando el usuario pulsa el boton de logout se le direcciona a la pagina /logout que llama al metodo logout para hacer el que? pues si, el logout
    """
    Se cierra la sesión del usuario.

    :param request: Objeto Http.
    :return: El render del template login.html
    """
    logout(request)
    return redirect('login')

def registrarse(request):
    """
    Si el método es POST se valida que los datos sean correctos, en tal caso se crea el usuario junto con su archivo de conexión openvpn, pero si 
    el método es GET se muestra el template registrarse.html

    :param request: Objeto Http.
    :return del GET: El render del template registrarse.html
    :return del POST: El render del template login.html
    """
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
            
            #generamos una url random para que no se pueda acceder a ella desde el navegador
            
            characters = string.ascii_letters + string.digits
            urlRandom = ''.join(random.choice(characters) for i in range(50))
            
            #guardamos el archivo en el directorio de la base de datos
            nameFile = '/home/jaime/Escritorio/TFG/media/openvpn/'+urlRandom+'/'+username+'.ovpn'

            os.makedirs(os.path.dirname(nameFile)) #creamos el directorio con la .ovpn

            archivoOpenVpn=open(nameFile,"w")
            archivoOpenVpn.write(cosa.decode('utf-8'))
            archivoOpenVpn.close()

            #guardamos en la base de datos
            userCreated = User.objects.get(username=username)
            alumnoCreated = Alumno.objects.get(user=userCreated)
            alumnoCreated.openvpnFile = '/media/openvpn/'+urlRandom+'/'+username+'.ovpn'
            alumnoCreated.save()

            login(request, userCreated)
            return redirect('home')
        else:
            messages.info(request, 'Completa correctamente los campos')
    else:
        form = CreateUserForm()
    contexto = {'form':form}
    return render(request, 'accounts/registrarse.html',contexto)


