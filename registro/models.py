# registro/models.py
from django.db import models
from django.contrib.auth.models import User

class RegistroHora(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.hora_inicio} a {self.hora_fin}"
