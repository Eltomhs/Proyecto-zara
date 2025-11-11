# zara/urls.py
from django.urls import path
from django.conf import settings
from . import views

app_name = "zara"

urlpatterns = [
    # =====================
    # PÁGINAS PÚBLICAS
    # =====================
    path("", views.home, name="home"),
    path("invitado/", views.invitado, name="invitado"),
    path("mujer/", views.mujer, name="mujer"),
    path("hombre/", views.hombre, name="hombre"),
    path("nina/", views.nina, name="nina"),
    path("nino/", views.nino, name="nino"),
    path("accesorios/", views.accesorios, name="accesorios"),
    path("perfume/", views.perfume, name="perfume"),
    path("carrito/", views.carrito, name="carrito"),
    path("tradein/", views.tradein, name="tradein"),

    # =====================
    # ENCUESTA / DASHBOARD
    # =====================
    path("informe/", views.informe_encuesta, name="informe_encuesta"),
    path("chart/<str:key>/", views.chart_detail, name="chart_detail"),

    # =====================
    # LOGIN / LOGOUT
    # =====================
    path("login/", views.login_cliente, name="login_cliente"),
    path("logout/", views.logout_view, name="logout"),

    # =====================
    # PANEL ADMINISTRATIVO (staff)
    # =====================
    path(f"{settings.PANEL_SLUG}/", views.administrativo, name="administrativo"),

    # =====================
    # APIs DEMO
    # =====================
    path("api/validar-cupon/", views.api_validar_cupon, name="api_validar_cupon"),
    path("api/carrito-validar/", views.api_carrito_validar, name="api_carrito_validar"),
    path("api/checkout-simulado/", views.api_checkout_simulado, name="api_checkout_simulado"),
]
