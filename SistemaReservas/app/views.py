from http.client import HTTPResponse
from lib2to3.fixes.fix_input import context
from tempfile import template

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Reserva


# utilizo lo siguinete porque tengo un modelo de usuario personalizado
# si no, dara error : Manager isn't available; 'auth.User' has been swapped for 'app.Usuario'
# para arreglarlo he importado mi modelo personalizado




User = get_user_model()




# Create your views here.

# Usa loader.get_template + HttpResponse
# solo si necesito un control muy específico sobre el proceso de renderizado.

# def index(request):
#     template = loader.get_template('login.html')
#     return HttpResponse(template.render())

def registro(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if not username or not email or not password or not password2:
            messages.error(request, "hacen faltan campos por rellenar")
            return  render(request, "registro.html")

        if password != password2:
            messages.error(request, "las contraseñas no coinciden")
            return render(request,"registro.html")

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe")
            return render(request, "registro.html")

        User.objects.create_user(
            username=username,
            email = email,
            password= password
        )

        messages.success(request,"Usuari creado correctamente")
        return redirect("login")

    return render(request, "registro.html")
# def volverlogin(request):
#     return render(request, 'login.html')

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('fecha', 'hora_inicio')
    return render(request, 'mis_reservas.html', {'reservas': reservas})



def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("mis_reservas")

        return render(request, "login.html", {
            "error": "Usuario o contraseña incorrectos"
        })

    return render(request, "login.html")

@login_required
def delete_count(request):
    if request.method == "POST":
        request.user.delete()
        return redirect("login")


def reserva(request):
    return render(request, "Reserva.html")