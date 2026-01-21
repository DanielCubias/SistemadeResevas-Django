import calendar
import json
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, require_GET

from .models import Reserva

User = get_user_model()

def registro(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if not username or not email or not password or not password2:
            messages.error(request, "Faltan campos por rellenar")
            return render(request, "registro.html")

        if password != password2:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "registro.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe")
            return render(request, "registro.html")

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Usuario creado correctamente")
        return redirect("login")

    return render(request, "registro.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("calendario")

        return render(request, "login.html", {"error": "Usuario o contraseña incorrectos"})

    return render(request, "login.html")

@login_required
def mis_reservas(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by("fecha", "hora_inicio")
    return render(request, "mis_reservas.html", {"reservas": reservas})

@login_required
def calendario(request):
    today = date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    calendar.setfirstweekday(calendar.MONDAY)
    month_matrix = calendar.monthcalendar(year, month)

    month_days = []
    for week in month_matrix:
        week_days = []
        for d in week:
            week_days.append({"num": d} if d != 0 else None)
        month_days.append(week_days)

    month_name = calendar.month_name[month]

    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    return render(request, "calendario.html", {
        "year": year,
        "month": month,
        "month_name": month_name,
        "month_days": month_days,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    })

def _parse_time(payload, key, default):
    return datetime.strptime(payload.get(key, default), "%H:%M").time()

@require_POST
@login_required
def reservar_rango(request):
    payload = json.loads(request.body.decode("utf-8"))

    year = int(payload["year"])
    month = int(payload["month"])
    day_from = int(payload["from"])
    day_to = int(payload["to"])

    hora_inicio = _parse_time(payload, "hora_inicio", "09:00")
    hora_fin = _parse_time(payload, "hora_fin", "10:00")

    a, b = sorted([day_from, day_to])

    created = 0
    errors = []

    for d in range(a, b + 1):
        try:
            Reserva.objects.create(
                usuario=request.user,
                fecha=date(year, month, d),
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
            )
            created += 1
        except Exception as e:
            errors.append({"day": d, "error": str(e)})

    return JsonResponse({"ok": True, "created": created, "errors": errors})

@require_POST
@login_required
def cancelar_rango(request):
    payload = json.loads(request.body.decode("utf-8"))

    year = int(payload["year"])
    month = int(payload["month"])
    day_from = int(payload["from"])
    day_to = int(payload["to"])

    hora_inicio = _parse_time(payload, "hora_inicio", "09:00")
    hora_fin = _parse_time(payload, "hora_fin", "10:00")

    a, b = sorted([day_from, day_to])

    qs = Reserva.objects.filter(
        usuario=request.user,
        fecha__gte=date(year, month, a),
        fecha__lte=date(year, month, b),
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
    )

    deleted, _ = qs.delete()
    return JsonResponse({"ok": True, "deleted": deleted})

@require_GET
@login_required
def reservas_mes(request):
    year = int(request.GET["year"])
    month = int(request.GET["month"])

    reservas = Reserva.objects.filter(
        usuario=request.user,
        fecha__year=year,
        fecha__month=month
    ).values_list("fecha", flat=True)

    days = sorted({d.day for d in reservas})
    return JsonResponse({"ok": True, "days": days})
