from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('maquinas/<str:pk_maquina>', views.maquinas, name="maquinas"),
    path('home/', views.home, name="home"),
    path('logout/', views.logoutUser, name='logout'),
    path('login/', views.loginUsername, name='login'),
    path('registrarse/', views.registrarse, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
]