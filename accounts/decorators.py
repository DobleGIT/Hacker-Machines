from django.http import HttpResponse, Http404
from django.shortcuts import redirect


def unauthenticathed_user(view_func):
    """
    This function is a decorator that takes in a view function as an argument and returns a new view
    function. 
    
    The new view function will check if the user is authenticated. If the user is authenticated, 
    the user will be redirected to the home page. If the user is not authenticated, the view function
    will execute as normal
    
    :param view_func: The view function that we are decorating
    :return: A function
    """
   
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]): #función para controlar los grupos en el acceso a vistas
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
                