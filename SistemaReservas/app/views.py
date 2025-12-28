from lib2to3.fixes.fix_input import context
from tempfile import template

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect


# utilizo lo siguinete porque tengo un modelo de usuario personalizado
# si no, dara error : Manager isn't available; 'auth.User' has been swapped for 'app.Usuario'
# para arreglarlo he importado mi modelo personalizado

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Reserva


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

        if password != password2:
            return render(request, "registro.html", {"error": "Las contraseñas no coinciden"})

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return render(request, "registro.html", {"error": "El nombre de usuario ya existe"})


        User.objects.create_user(username=username, email=email, password=password)

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
