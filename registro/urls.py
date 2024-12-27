# registro/urls.py (App)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Inicio del dashboard
    path('fin/', views.registrar_fin, name='registrar_fin'),  # Registrar fin de jornada
    path('resumen/', views.resumen, name='resumen'),  # Resumen de jornadas
    path('registrarse/', views.registrarse, name='registrarse'),  # Registro de usuario
path('eliminar/<int:pk>/', views.eliminar_registro, name='eliminar_registro'),
]
