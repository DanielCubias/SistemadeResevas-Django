import calendar
import json
from datetime import date, timedelta, datetime

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import request
from django.views.decorators.http import require_POST
from pyexpat.errors import messages

from .models import Reserva



def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # nombre de tu url principal
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, "login.html")






def _month_prev_next(year: int, month: int):
    if month == 1:
        return (year - 1, 12), (year, 2)
    if month == 12:
        return (year, 11), (year + 1, 1)
    return (year, month - 1), (year, month + 1)


def _date_range_inclusive(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


@login_required
def calendario_view(request):
    today = date.today()

    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # Construye semanas del mes (lunes = 0)
    cal = calendar.Calendar(firstweekday=0)
    weeks = []
    for week in cal.monthdatescalendar(year, month):
        weeks.append([{
            "day": d.day,
            "date": d.isoformat(),
            "in_month": (d.month == month),
            "is_today": (d == today),
        } for d in week])

    (prev_year, prev_month), (next_year, next_month) = _month_prev_next(year, month)
    month_name = calendar.month_name[month].capitalize()

    # Reservas que solapan con este mes (para pintar en verde)
    month_start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    month_end = date(year, month, last_day)

    reservas_mes = Reserva.objects.filter(
        check_in__lte=month_end,
        check_out__gte=month_start,
    )

    reserved_dates = set()
    reserved_ranges = []
    for r in reservas_mes:
        # recorta al mes para no mandar 2000 días si alguien reserva meses
        start = max(r.check_in, month_start)
        end = min(r.check_out, month_end)
        for d in _date_range_inclusive(start, end):
            reserved_dates.add(d.isoformat())
        reserved_ranges.append({
            "id": r.id,
            "check_in": r.check_in.isoformat(),
            "check_out": r.check_out.isoformat(),
        })

    context = {
        "year": year,
        "month": month,
        "month_name": month_name,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "weeks": weeks,
        # para JS
        "reserved_dates_json": json.dumps(sorted(reserved_dates)),
        "reserved_ranges_json": json.dumps(reserved_ranges),
    }
    return render(request, "calendario.html", context)


@require_POST
@login_required
def api_crear_reserva(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        start_s = payload.get("check_in")
        end_s = payload.get("check_out")
        check_in = datetime.strptime(start_s, "%Y-%m-%d").date()
        check_out = datetime.strptime(end_s, "%Y-%m-%d").date()
    except Exception:
        return JsonResponse({"ok": False, "error": "Payload inválido. Usa YYYY-MM-DD."}, status=400)

    if check_in > check_out:
        return JsonResponse({"ok": False, "error": "check_in no puede ser mayor que check_out."}, status=400)

    # Reglas “hotel”: no permitir solapes (globales)
    solape = Reserva.objects.filter(
        check_in__lte=check_out,
        check_out__gte=check_in,
    ).exists()

    if solape:
        return JsonResponse({"ok": False, "error": "Ese rango ya está reservado."}, status=409)

    reserva = Reserva.objects.create(
        usuario=request.user,
        check_in=check_in,
        check_out=check_out,
    )

    return JsonResponse({
        "ok": True,
        "reserva": {
            "id": reserva.id,
            "check_in": reserva.check_in.isoformat(),
            "check_out": reserva.check_out.isoformat(),
        }
    }, status=201)


@login_required
def mis_reservas_view(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by("-created_at")
    return render(request, "mis_reservas.html", {"reservas": reservas})


@require_POST
@login_required
def api_eliminar_reserva(request, reserva_id: int):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    reserva.delete()
    return JsonResponse({"ok": True})

