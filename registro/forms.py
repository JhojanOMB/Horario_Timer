from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True, label="Nombre")
    last_name = forms.CharField(max_length=100, required=True, label="Apellidos")
    email = forms.EmailField(max_length=100, required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    # Mensajes personalizados para validaciones de contraseñas
    error_messages = {
        'password1': {
            'password_too_similar': "La contraseña no puede ser demasiado similar a otra información personal.",
            'password_too_common': "La contraseña no puede ser una contraseña común.",
            'password_entirely_numeric': "La contraseña no puede ser completamente numérica.",
        },
        'password2': {
            'password_mismatch': "Las contraseñas no coinciden.",
        }
    }

class RegistroInicioForm(forms.ModelForm):
    class Meta:
        model = RegistroHora
        fields = ['hora_inicio']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class RegistroFinForm(forms.ModelForm):
    class Meta:
        model = RegistroHora
        fields = ['hora_fin']
        widgets = {
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

