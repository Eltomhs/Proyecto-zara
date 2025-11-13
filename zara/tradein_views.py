# zara/tradein_views.py
from datetime import date
from io import BytesIO
import qrcode

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


def tradein_home(request):
    wallet_points = request.session.get("wallet_points", 120)
    level = "Eco Plata" if wallet_points < 300 else "Eco Oro"
    wallet_progress = max(0, min(100, wallet_points))
    return render(request, "encuesta_zara/tradein.html", {
        "wallet_points": wallet_points,
        "level": level,
        "wallet_progress": wallet_progress,
    })


@require_GET
def tradein_valuar_api(request):
    cat = (request.GET.get("categoria") or "otro").strip().lower()
    estado = (request.GET.get("estado") or "bueno").strip().lower()

    try:
        anio = int(request.GET.get("anio", date.today().year))
    except (TypeError, ValueError):
        anio = date.today().year

    base_map = {
        "chaqueta": 18000, "pantalon": 12000, "polera": 8000,
        "vestido": 15000, "zapato": 16000, "cartera": 22000, "otro": 10000
    }
    base = base_map.get(cat, 10000)

    estado_map = {"nuevo": 1.00, "excelente": 0.90, "bueno": 0.75, "regular": 0.50}
    f_estado = estado_map.get(estado, 0.75)

    years = max(0, min(8, date.today().year - anio))
    f_age = max(0.55, 1 - years * 0.06)

    valor = int(base * f_estado * f_age)
    puntos = int(valor * 0.10)

    co2_kg = round((0.8 + years * 0.05) * f_estado, 2)
    agua_l = int((900 + years * 30) * f_estado)

    return JsonResponse({
        "valor": valor,
        "puntos": puntos,
        "impacto": {"co2_kg": co2_kg, "agua_l": agua_l}
    })


def tradein_qr(request, item_id: int):
    payload = f"TRADEIN:{item_id}"
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")


def tradein_scan(request):
    return render(request, "encuesta_zara/tradein_scan.html")


def wallet_home(request):
    wallet_points = request.session.get("wallet_points", 120)
    return render(request, "encuesta_zara/wallet.html", {"wallet_points": wallet_points})
