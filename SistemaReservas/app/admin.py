from django.contrib import admin
from .models import Usuario,Reserva

# Register your models here.

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'hora_inicio', 'hora_fin', 'creado_en')
    list_filter = ('fecha',)