from os import path
from django.urls import path
from django.contrib.auth import views as auth_views

from django.conf.urls.i18n import urlpatterns


from . import views
from .views import mis_reservas

urlpatterns = [
    path('login/', views.login_view, name="login"),
    path('registro/', views.registro, name="registro"),
    path('mis-reservas/', mis_reservas, name='mis_reservas'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("delete-count/", views.delete_count, name="delete_count"),
]