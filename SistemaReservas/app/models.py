from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Usuario(AbstractUser):
    rol = models.CharField(
        max_length=20,
        choices=[('admin', 'Admin'), ('usuario', 'Usuario')],
        default='usuario'
    )



class Reserva(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"
