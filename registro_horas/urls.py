# registro_horas/urls.py (proyecto principal)
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from registro import views as registro_views  # Importar vistas específicas de la app registro

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', registro_views.landing_page, name='landing_page'),  # Página de presentación
    path('dashboard/', include('registro.urls')),  # Funcionalidades del dashboard
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
