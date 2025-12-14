from lib2to3.fixes.fix_input import context
from tempfile import template

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

# Usa loader.get_template + HttpResponse
# solo si necesito un control muy específico sobre el proceso de renderizado.

def index(request):
    template = loader.get_template('login.html')
    return HttpResponse(template.render())

def registro(request):
    return render(request, 'registro.html')