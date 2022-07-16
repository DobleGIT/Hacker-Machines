from django.http import HttpResponse, Http404
from django.shortcuts import redirect


def unauthenticathed_user(view_func):
    """
    Esta funcion es un decorator que verifica si el usuario está autentificado, en caso de que no lo esté 
    se le redirecciona a la pantalla home.

    """
   
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]): #función para controlar los grupos en el acceso a vistas
    """
    Este decorator es utilizado para controlar que funciones pueden ser ejecutadas por determinados grupos,
    en caso de que no se pertenezca al grupo en cuestión se le redirecciona a la pantalla home.
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

                group = None
                if request.user.groups.exists():
                    group = request.user.groups.all()[0].name

                if group in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('home')
        return wrapper_func
    return decorator
                