from django.urls import path
from . import views

from django.conf import settings
from django.views.static import serve
from django.urls import path,include,re_path
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



urlpatterns = [
    
    path('', views.home, name="home"),
    path('maquinas/', views.maquinas, name="maquinas"), 
    path('maquinas/<str:nombre_maquina_url>', views.maquinas, name="maquinas"),
    path('addMachine/', views.addMachine, name="addMachine"),
    path('categories/', views.categories, name="categories"),
    path('addCategories/', views.addCategories, name="addCategories"),
    path('editCategories/<str:nombre_categoria_url>', views.editCategories, name="editCategories"),
    path('deleteCategories/<str:nombre_categoria_url>', views.deleteCategories, name="deleteCategories"),
    path('editMachine/<str:nombre_maquina_url>', views.editMachine, name="editMachine"),
    path('deleteMachine/<str:nombre_maquina_url>', views.deleteMachine, name="deleteMachine"),
    path('visibleMachine/<str:nombre_maquina_url>', views.visibleMachine, name="visibleMachine"),
    path('home/', views.home, name="home"),
    path('logout/', views.logoutUser, name='logout'),
    path('login/', views.loginUsername, name='login'),
    path('registrarse/', views.registrarse, name='register'),
    path('profile/', views.profile, name='profile'),
    path('userProfile/<int:id>', views.userProfile, name='userProfile'),
    path('access_to_machine/<str:nombre_maquina_url>', views.access_to_machine, name='access_to_machine'),
    path('openvpn/', views.openvpn, name='openvpn'),
    path('ranking/', views.ranking, name='ranking'),
    path('createAdminUser/<int:id>',views.createAdminUser, name='createAdminUser'), 
    path('deleteAdminUser/<int:id>',views.deleteAdminUser, name='deleteAdminUser'),
    path('deleteUser/<int:id>',views.deleteUser, name='deleteUser'), 
    path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/',
     auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), 
     name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), 
        name="password_reset_complete"),

    path('admin/doc/', include('django.contrib.admindocs.urls')),

    
]


urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) #añadimos a los archivos estaticos, 



# [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}), #esto es para el /media, lo he sacao de qui https://www.youtube.com/watch?v=aUsEbnoKjGQ&ab_channel=Developer.pe
#                ]       
