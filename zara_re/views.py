# zara_re/views.py
from types import SimpleNamespace
import io
import base64
import qrcode

from django.shortcuts import render

# ============================================================
#  DATOS DEMO PARA PASAPORTE DIGITAL
# ============================================================

CATALOGO_PASAPORTE = {
    "conjunto-formal-gris": {
        "slug": "conjunto-formal-gris",
        "nombre": "Conjunto formal gris",
        "categoria": "Mujer",
        "fibra": "Mezcla de poliéster reciclado y viscosa",
        "origen_fibra": "Fibras recicladas post-consumo · Europa",
        "proveedores": "Proveedores auditados Tier 1 y 2",
        "co2_total": 18.4,
        "agua_total": 2100,
        "co2_fabricacion": 7.2,
        "co2_transporte": 3.1,
        "co2_uso": 5.0,
        "co2_fin_de_vida": 3.1,
        "cuidado": [
            "Lavar en frío (máx. 30°C) y solo cuando sea necesario.",
            "Secar al aire, evitar la secadora.",
            "Planchar a temperatura baja si es necesario.",
            "Preferir lavado en bolsa de lavado para microfibras.",
        ],
        "reciclaje": (
            "Puedes devolver esta prenda mediante el programa Trade-In para "
            "reciclarla o darle una segunda vida en Zara_Re."
        ),
    }
}

DEFAULT_SLUG = "conjunto-formal-gris"


# ============================================================
#  HOME ZARA_RE
# ============================================================

def home(request):
    """
    Página principal de Zara_Re.
    """
    return render(request, "zara_re/home.html")


# ============================================================
#  PASAPORTE DIGITAL
# ============================================================

def pasaporte(request):
    """
    Muestra un pasaporte digital de producto.
    """
    slug = request.GET.get("producto") or DEFAULT_SLUG
    data = CATALOGO_PASAPORTE.get(slug, CATALOGO_PASAPORTE[DEFAULT_SLUG])

    qr_text = (
        f"{data['nombre']} · {data['categoria']}\n"
        f"Fibra: {data['fibra']}\n"
        f"Origen fibras: {data['origen_fibra']}\n"
        f"CO₂ total estimado: {data['co2_total']} kg\n"
        f"Agua total estimada: {data['agua_total']} L"
    )

    qr_img = qrcode.make(qr_text)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    p = SimpleNamespace(**data, qr_base64=qr_base64)

    return render(request, "zara_re/pasaporte.html", {"p": p})