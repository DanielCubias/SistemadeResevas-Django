from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
path("calendario/", views.calendario_view, name="calendario"),
    path("mis-reservas/", views.mis_reservas_view, name="mis_reservas"),
    path("login/", views.login, name="login"),

    # API (fetch / ajax)
    path("api/reservas/crear/", views.api_crear_reserva, name="api_crear_reserva"),
    path("api/reservas/eliminar/<int:reserva_id>/", views.api_eliminar_reserva, name="api_eliminar_reserva"),


]
