# esto permite lanzar un error de validacion cuando algo no cumple las reglas del modelo
from django.core.exceptions import ValidationError

from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User


class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"

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


    def clean(self):
        reservas = Reserva.objects.filter(
            usuario = self.usuario,
            fecha = self.fecha,
        ).exclude(pk=self.pk)
        # evita que se compare consigo misma

        for x in reservas:
            if self.hora_inicio < x.hora_fin and self.hora_fin > x.hora_inicio:
                raise ValidationError("La reserva se solapa con otra existente")

    def save(self, *args , **kwargs):
        self.full_clean()
        # es mejor esta que "self.clean()", por que llama a clean , valida campos, valida modelos completos
        # tambien porque save() no garantiza validaciones en el admin ni el todos los flujos
        # en cambio full_clean() asegura coherencia a nivel modelo
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"


