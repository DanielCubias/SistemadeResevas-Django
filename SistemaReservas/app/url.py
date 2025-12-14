from os import path
from django.urls import path

from django.conf.urls.i18n import urlpatterns


from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('registro/', views.registro, name="registro")
]