# zara/views.py
from datetime import datetime
from types import SimpleNamespace
import io, base64, qrcode

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from .models import Perfil, TradeInCanje


# =============================
#  PÁGINAS BÁSICAS / CATÁLOGO
# =============================

def home(request):
    return render(request, "encuesta_zara/home.html")

def mujer(request):
    return render(request, "encuesta_zara/mujer.html")

def hombre(request):
    return render(request, "encuesta_zara/hombre.html")

def nina(request):
    return render(request, "encuesta_zara/nina.html")

def nino(request):
    return render(request, "encuesta_zara/nino.html")

def accesorios(request):
    return render(request, "encuesta_zara/accesorios.html")


# =============================
#  TRADE-IN / QR / WALLET
# =============================

@login_required
def trade_in(request):
    """
    Página Trade-In:
    - GET: muestra el formulario.
    - POST: registra un canje, suma puntos al perfil y redirige a la wallet.
    """
    if request.method == "POST":
        prenda = (request.POST.get("prenda") or "Sin nombre").strip()
        material = (request.POST.get("material") or "Desconocido").strip()
        impacto_raw = (request.POST.get("impacto") or "0").strip()

        try:
            impacto = float(impacto_raw)
        except ValueError:
            impacto = 0.0

        # Regla simple de puntos: 10 puntos por cada unidad de "impacto"
        puntos = max(0, int(impacto * 10))

        # Guardar el registro del canje
        TradeInCanje.objects.create(
            usuario=request.user,
            prenda=prenda,
            material=material,
            impacto=impacto,
            puntos_obtenidos=puntos,
        )

        # Sumar puntos al perfil
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        perfil.puntos = (perfil.puntos or 0) + puntos
        perfil.save(update_fields=["puntos"])

        messages.success(request, f"Canje registrado (+{puntos} pts). ¡Gracias por reciclar!")
        return redirect("zara:wallet_view")

    return render(request, "encuesta_zara/tradein.html")


@login_required
def wallet_view(request):
    """
    Muestra saldo total de puntos y el historial de canjes del usuario.
    """
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    canjes = TradeInCanje.objects.filter(usuario=request.user).order_by("-fecha")
    total_puntos = getattr(perfil, "puntos", 0) or 0

    context = {
        "perfil": perfil,
        "canjes": canjes,
        "total_puntos": total_puntos,
    }
    return render(request, "encuesta_zara/wallet.html", context)


def qr_generar(request):
    """Genera un QR simple con texto recibido por GET."""
    data = request.GET.get("data", "Código vacío")
    qr_img = qrcode.make(data)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return render(request, "encuesta_zara/qr_generar.html", {"img_data": img_base64})


def qr_leer(request):
    """Plantilla con lector QR vía cámara (JS)."""
    return render(request, "encuesta_zara/qr_leer.html")


# =============================
#  CUENTA / PERFIL / CONFIGURACIÓN
# =============================

def _get_or_create_perfil(user):
    """Intenta obtener o crear un perfil real. Si no hay modelo, crea uno temporal."""
    try:
        perfil, _ = Perfil.objects.get_or_create(
            user=user,
            defaults={"nombre_mostrar": user.get_full_name() or user.username},
        )
        return perfil, True
    except Exception:
        data = {
            "nombre_mostrar": user.get_full_name() or user.username,
            "fecha_nacimiento": None,
            "preferencia_tema": "light",
        }
        return SimpleNamespace(**data), False


@login_required
def cuenta_home(request):
    """Página de cuenta con datos personales y cambio de contraseña."""
    user = request.user
    perfil, has_model = _get_or_create_perfil(user)

    if request.method == "POST":
        action = request.POST.get("action")

        # -------- Actualizar datos del perfil --------
        if action == "perfil_update":
            nombre_mostrar = (request.POST.get("nombre_mostrar") or "").strip()
            email = (request.POST.get("email") or "").strip()
            fecha_raw = (request.POST.get("fecha_nacimiento") or "").strip()
            tema = (request.POST.get("preferencia_tema") or "light").strip()

            if email:
                user.email = email
                user.save(update_fields=["email"])

            fecha_dt = None
            if fecha_raw:
                try:
                    fecha_dt = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
                except ValueError:
                    messages.warning(request, "Formato de fecha inválido. Usa AAAA-MM-DD.")

            if has_model:
                if hasattr(perfil, "nombre_mostrar"):
                    perfil.nombre_mostrar = nombre_mostrar or perfil.nombre_mostrar
                if fecha_dt is not None and hasattr(perfil, "fecha_nacimiento"):
                    perfil.fecha_nacimiento = fecha_dt
                if hasattr(perfil, "preferencia_tema"):
                    perfil.preferencia_tema = tema
                perfil.save()
            else:
                request.session["perfil_nombre_mostrar"] = nombre_mostrar or (user.get_full_name() or user.username)
                if fecha_dt:
                    request.session["perfil_fecha_nacimiento"] = fecha_dt.isoformat()
                request.session["perfil_preferencia_tema"] = tema

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("zara:cuenta_home")

        # -------- Cambio de contraseña --------
        if action == "password_change":
            old_password = request.POST.get("old_password") or ""
            new1 = request.POST.get("new_password1") or ""
            new2 = request.POST.get("new_password2") or ""

            if not user.check_password(old_password):
                messages.error(request, "La contraseña actual no es correcta.")
                return redirect("zara:cuenta_home")
            if new1 != new2:
                messages.error(request, "Las contraseñas nuevas no coinciden.")
                return redirect("zara:cuenta_home")
            if len(new1) < 8:
                messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
                return redirect("zara:cuenta_home")

            user.set_password(new1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect("zara:cuenta_home")

    return render(request, "encuesta_zara/cuenta/home.html", {"perfil": perfil})


@login_required
def cuenta_pedidos(request):
    """Listado de pedidos (demo)."""
    # Si luego conectas a tu modelo de pedidos, reemplace el contexto.
    return render(request, "encuesta_zara/cuenta/pedidos.html")


@login_required
def cuenta_direcciones(request):
    """Direcciones (demo)."""
    return render(request, "encuesta_zara/cuenta/direcciones.html")


# =============================
#  PANEL ADMINISTRATIVO
# =============================

@login_required
def panel(request):
    """Dashboard administrativo (Chart.js)."""
    return render(request, "encuesta_zara/panel.html")


# =============================
#  BUSCADOR (LUPA)
# =============================
def carrito(request):
    """Página del carrito (usa localStorage en el cliente)."""
    return render(request, "encuesta_zara/carrito.html")

def buscar(request):
    """
    Vista de búsqueda de demo.
    Filtra contra un catálogo estático (nombre, categoría). 
    Cuando tengas BD, reemplaza por queries reales.
    """
    q = (request.GET.get("q") or "").strip()
    catalogo = [
        {"nombre": "Conjunto formal gris", "categoria": "Mujer", "slug": "conjunto-formal-gris"},
        {"nombre": "Trench liviano", "categoria": "Mujer", "slug": "trench-liviano"},
        {"nombre": "Blazer Mocha", "categoria": "Hombre", "slug": "blazer-mocha"},
        {"nombre": "Pantalón lino beige", "categoria": "Hombre", "slug": "pantalon-lino-beige"},
        {"nombre": "Chaqueta acolchada niña", "categoria": "Niña", "slug": "chaqueta-acolchada-nina"},
        {"nombre": "Polera niño básica", "categoria": "Niño", "slug": "polera-nino-basica"},
        {"nombre": "Cartera Safari", "categoria": "Accesorios", "slug": "cartera-safari"},
        {"nombre": "Perfume Rose Tan", "categoria": "Perfumes", "slug": "perfume-rose-tan"},
    ]

    if q:
        ql = q.lower()
        resultados = [
            item for item in catalogo
            if ql in item["nombre"].lower() or ql in item["categoria"].lower()
        ]
    else:
        resultados = []

    ctx = {
        "q": q,
        "resultados": resultados,
        "total": len(resultados),
    }
    return render(request, "encuesta_zara/buscar.html", ctx)
