# zara/admin.py
from django.contrib import admin
from .models import (
    Perfil, Direccion,
    Producto, Cupon,
    Carrito, ItemCarrito,
    Pedido,
    CampaniaEncuesta, RespuestaEncuesta,
    TradeInCanje
)

# =============================
#  PERFIL / USUARIO
# =============================

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol", "nivel", "puntos", "tema", "creditos_circulares")
    list_filter = ("rol", "tema", "nivel")
    search_fields = ("user__username", "user__email", "nombre_mostrar")
    ordering = ("user__username",)


# =============================
#  DIRECCIONES
# =============================

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ("user", "alias", "ciudad", "pais", "es_principal")
    list_filter = ("pais", "es_principal")
    search_fields = ("user__username", "ciudad", "alias")


# =============================
#  PRODUCTOS / CUPONES
# =============================

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock")
    search_fields = ("nombre",)


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descuento_porcentaje", "vigente_desde", "vigente_hasta", "activo")
    list_filter = ("activo",)
    search_fields = ("codigo",)


# =============================
#  CARRITO / ITEMS
# =============================

class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ("id", "cupon", "creado_en", "actualizado_en")
    inlines = [ItemCarritoInline]


# =============================
#  PEDIDOS
# =============================

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "estado", "total_pagado", "creado_en")
    list_filter = ("estado",)
    search_fields = ("user__username", "email_cliente")


# =============================
#  ENCUESTAS
# =============================

@admin.register(CampaniaEncuesta)
class CampaniaEncuestaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre",)


@admin.register(RespuestaEncuesta)
class RespuestaEncuestaAdmin(admin.ModelAdmin):
    list_display = ("email", "campania", "rating_sustentabilidad", "rating_calidad", "enviado_en")
    list_filter = ("campania",)
    search_fields = ("email",)


# =============================
#  TRADE-IN / ECONOMÍA CIRCULAR
# =============================

@admin.register(TradeInCanje)
class TradeInCanjeAdmin(admin.ModelAdmin):
    list_display = ("usuario", "prenda", "material", "impacto", "puntos_obtenidos", "fecha")
    list_filter = ("material",)
    search_fields = ("usuario__username", "prenda")
    ordering = ("-fecha",)
