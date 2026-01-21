from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('registro/', views.registro, name="registro"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path("calendario/", views.calendario, name="calendario"),

    # path("delete-count/", views.delete_count, name="delete_count"),
    path("reservas/rango/", views.reservar_rango, name="reservar_rango"),
    path("reservas/mes/", views.reservas_mes, name="reservas_mes"),

]
