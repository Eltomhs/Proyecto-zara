# zara/urls.py
from django.urls import path
from . import views

app_name = "zara"

urlpatterns = [
    # ----------- PÁGINAS PRINCIPALES -----------
    path("", views.home, name="home"),
    path("mujer/", views.mujer, name="mujer"),
    path("hombre/", views.hombre, name="hombre"),
    path("nina/", views.nina, name="nina"),
    path("nino/", views.nino, name="nino"),
    path("accesorios/", views.accesorios, name="accesorios"),
    path("carrito/", views.carrito, name="carrito"),

    # ----------- TRADE-IN / QR / WALLET -----------
    path("tradein/", views.trade_in, name="tradein"),
    path("wallet/", views.wallet_view, name="wallet_view"),
    path("qr_generar/", views.qr_generar, name="qr_generar"),
    path("qr_leer/", views.qr_leer, name="qr_leer"),

    # ----------- CUENTA / CONFIGURACIÓN -----------
    path("cuenta/", views.cuenta_home, name="cuenta_home"),
    path("cuenta/pedidos/", views.cuenta_pedidos, name="cuenta_pedidos"),
    path("cuenta/direcciones/", views.cuenta_direcciones, name="cuenta_direcciones"),

    # ----------- PANEL ADMINISTRATIVO -----------
    path("panel/", views.panel, name="panel"),

    # ----------- BUSCADOR (LUPA) -----------
    path("buscar/", views.buscar, name="buscar"),
]
