from django.urls import path
from . import views

from django.conf import settings
from django.views.static import serve
from django.urls import path,include,re_path
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name="home"),
    path('maquinas/', views.maquinas, name="maquinas"),
    path('maquinas/<str:nombre_maquina_url>', views.maquinas, name="maquinas"),
    path('addMachine/', views.addMachine, name="addMachine"),
    path('home/', views.home, name="home"),
    path('logout/', views.logoutUser, name='logout'),
    path('login/', views.loginUsername, name='login'),
    path('registrarse/', views.registrarse, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('userProfile/<int:id>', views.userProfile, name='userProfile'),
    path('access_to_machine/<str:nombre_maquina_url>', views.access_to_machine, name='access_to_machine'),
    path('openvpn/', views.openvpn, name='openvpn'),
    path('ranking/', views.ranking, name='ranking'),
    #path('media/openvpn/<str:file>',views.secureOpenVpnFiles, name='secureOpenVpnFiles'),
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) #añadimos a los archivos estaticos, 



# [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}), #esto es para el /media, lo he sacao de qui https://www.youtube.com/watch?v=aUsEbnoKjGQ&ab_channel=Developer.pe
#                ]       
