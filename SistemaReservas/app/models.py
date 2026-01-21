# esto permite lanzar un error de validacion cuando algo no cumple las reglas del modelo
from django.core.exceptions import ValidationError

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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "fecha", "hora_inicio", "hora_fin"],
                name="uniq_reserva_exacta"
            )
        ]

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la hora de inicio")

        reservas = Reserva.objects.filter(
            usuario=self.usuario,
            fecha=self.fecha,
        ).exclude(pk=self.pk)

        for x in reservas:
            if self.hora_inicio < x.hora_fin and self.hora_fin > x.hora_inicio:
                raise ValidationError("La reserva se solapa con otra existente")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.usuario} - {self.fecha} {self.hora_inicio}-{self.hora_fin}"

