from os import path
from django.urls import path

from django.conf.urls.i18n import urlpatterns


from . import views
from .views import mis_reservas

urlpatterns = [
    path('', views.index, name="index"),
    path('registro/', views.registro, name="registro"),
    path('', views.volverlogin , name="volverlogin"),
    path('mis-reservas/', mis_reservas, name='mis_reservas')

]