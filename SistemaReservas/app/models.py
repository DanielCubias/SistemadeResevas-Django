# esto permite lanzar un error de validacion cuando algo no cumple las reglas del modelo
from django.core.exceptions import ValidationError

from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError



class Usuario(AbstractUser):
    rol = models.CharField(
        max_length=20,
        choices=[('admin', 'Admin'), ('usuario', 'Usuario')],
        default='usuario'
    )





class Reserva(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservas"
    )
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["check_in", "check_out"]),
        ]

    def clean(self):
        if self.check_in and self.check_out and self.check_in > self.check_out:
            raise ValidationError("check_in no puede ser mayor que check_out.")

    def __str__(self):
        return f"{self.usuario} {self.check_in} -> {self.check_out}"
