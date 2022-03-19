from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home"),
    path('maquinas/', views.maquinas, name="maquinas"),
    path('maquinas/<str:pk_maquina>', views.maquinas, name="maquinas"),
    path('home/', views.home, name="home"),
    path('logout/', views.logoutUser, name='logout'),
    path('login/', views.loginUsername, name='login'),
    path('registrarse/', views.registrarse, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) #añadimos a las urls las rutas de static/images