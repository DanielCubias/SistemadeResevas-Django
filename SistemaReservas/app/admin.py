from django.contrib import admin
from .models import Usuario,Reserva
from django.contrib.auth.admin import UserAdmin
# Register your models here.

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff', 'is_active')
    list_filter = ('rol', 'is_staff')
    search_fields = ('username', 'email')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "check_in", "check_out", "created_at")
    list_filter = ("created_at",)
    search_fields = ("usuario__username",)