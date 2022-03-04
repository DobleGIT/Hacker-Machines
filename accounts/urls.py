from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('maquinas/<str:pk_maquina>', views.maquinas, name="maquinas"),
    path('home/', views.home),
    path('iniciarSesion/', views.iniciarSesion),
    path('registrarse/', views.registrarse, name='register'),
]