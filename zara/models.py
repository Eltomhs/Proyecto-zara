# zara/models.py
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone

# ============================================
# CONFIG / CONSTANTES
# ============================================

MAX_QTY_PER_ITEM = 10

# ============================================
# PERFILES / USUARIOS
# ============================================

class Perfil(models.Model):
    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        PROFESIONAL = "profesional", "Profesional"
        INNOVADOR = "innovador", "Innovador"

    class Tema(models.TextChoices):
        CLARO = "claro", "Claro"
        OSCURO = "oscuro", "Oscuro"
        SISTEMA = "sistema", "Seguir sistema"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)

    # Personalización / “branding” de perfil
    nombre_mostrar = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)

    # Gamificación / valor
    creditos_circulares = models.PositiveIntegerField(default=0)
    nivel = models.PositiveIntegerField(default=1)
    puntos = models.PositiveIntegerField(default=0)

    # Apariencia
    tema = models.CharField(max_length=10, choices=Tema.choices, default=Tema.CLARO)
    color_acento = models.CharField(max_length=7, default="#111111")  # hex (#RRGGBB)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["rol"]), models.Index(fields=["nivel"])]
        verbose_name = "perfil"
        verbose_name_plural = "perfiles"

    def __str__(self) -> str:
        return f"{self.user.username} · {self.rol}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    """Crea Perfil cliente en alta de usuario."""
    if created:
        Perfil.objects.create(user=instance, rol=Perfil.Rol.CLIENTE)


# ============================================
# DIRECCIONES DEL USUARIO
# ============================================

class Direccion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="direcciones")
    alias = models.CharField(max_length=80, default="Casa")
    linea1 = models.CharField(max_length=160)
    linea2 = models.CharField(max_length=160, blank=True)
    ciudad = models.CharField(max_length=80)
    region = models.CharField(max_length=80, blank=True)
    codigo_postal = models.CharField(max_length=20, blank=True)
    pais = models.CharField(max_length=60, default="Chile")
    es_principal = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-es_principal", "id"]

    def __str__(self) -> str:
        return f"{self.alias} · {self.ciudad}"


# ============================================
# PRODUCTO / STOCK
# ============================================

class Producto(models.Model):
    nombre = models.CharField(max_length=160, unique=True)
    precio = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]
    )
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(precio__gte=0), name="precio_no_negativo"),
            models.CheckConstraint(check=Q(stock__gte=0), name="stock_no_negativo"),
        ]
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


# ============================================
# CUPONES / PROMOS
# ============================================

class Cupon(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    descuento_porcentaje = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(90)]
    )
    vigente_desde = models.DateTimeField()
    vigente_hasta = models.DateTimeField()
    activo = models.BooleanField(default=True)

    def esta_vigente(self) -> bool:
        now = timezone.now()
        return self.activo and self.vigente_desde <= now <= self.vigente_hasta

    def __str__(self) -> str:
        return f"{self.codigo} (-{self.descuento_porcentaje}%)"


# ============================================
# CARRITO / ITEMS
# ============================================

class Carrito(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    cupon = models.ForeignKey("Cupon", null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def esta_vacio(self) -> bool:
        return not self.items.exists()

    def subtotal(self) -> Decimal:
        total = sum(
            (it.cantidad * it.precio_unitario for it in self.items.all()),
            start=Decimal("0.00"),
        )
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def total(self) -> Decimal:
        total = self.subtotal()
        if self.cupon and self.cupon.esta_vigente():
            factor = Decimal("1.00") - (Decimal(self.cupon.descuento_porcentaje) / Decimal("100"))
            total = (total * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return total

    def __str__(self) -> str:
        return f"Carrito #{self.pk or '–'}"


class ItemCarrito(models.Model):
    carrito = models.ForeignKey("Carrito", related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey("Producto", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(MAX_QTY_PER_ITEM)]
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [("carrito", "producto")]
        constraints = [
            models.CheckConstraint(check=Q(cantidad__gte=1), name="cantidad_minima_1"),
            models.CheckConstraint(check=Q(cantidad__lte=MAX_QTY_PER_ITEM), name="cantidad_maxima_10"),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.producto and self.cantidad > self.producto.stock:
            raise ValidationError("Cantidad supera el stock disponible.")

    def __str__(self) -> str:
        return f"{self.producto} x {self.cantidad}"


# ============================================
# PEDIDOS (CHECKOUT)
# ============================================

class Pedido(models.Model):
    ESTADOS = [
        ("CREADO", "Creado"),
        ("PAGADO", "Pagado"),
        ("ENVIADO", "Enviado"),
        ("ENTREGADO", "Entregado"),
        ("CANCELADO", "Cancelado"),
    ]
    carrito = models.OneToOneField("Carrito", on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="pedidos"
    )
    email_cliente = models.EmailField(validators=[EmailValidator()])
    creado_en = models.DateTimeField(auto_now_add=True)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="CREADO")

    def __str__(self) -> str:
        return f"Pedido #{self.pk}"


# ============================================
# ENCUESTA
# ============================================

class CampaniaEncuesta(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    activa = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nombre


class RespuestaEncuesta(models.Model):
    campania = models.ForeignKey("CampaniaEncuesta", on_delete=models.PROTECT)
    email = models.EmailField()
    consentimiento = models.BooleanField(default=False)

    rating_sustentabilidad = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    rating_calidad = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField(blank=True)
    enviado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Un email solo una vez por campaña (case-insensitive)
            models.UniqueConstraint(
                models.functions.Lower("email"), "campania",
                name="unica_respuesta_por_email_y_campania",
            ),
            models.CheckConstraint(
                check=Q(rating_sustentabilidad__gte=1, rating_sustentabilidad__lte=5),
                name="rating_sustentabilidad_1_5",
            ),
            models.CheckConstraint(
                check=Q(rating_calidad__gte=1, rating_calidad__lte=5),
                name="rating_calidad_1_5",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.consentimiento:
            raise ValidationError("Debes aceptar consentimiento para enviar la encuesta.")

    def __str__(self) -> str:
        return f"{self.email} · {self.campania}"

# ============================================
# TRADE-IN / ECONOMÍA CIRCULAR
# ============================================

class TradeInCanje(models.Model):
    """
    Historial de canjes en Trade-In:
    guarda prenda, material, impacto y puntos generados.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="canjes_tradein"
    )
    prenda = models.CharField(max_length=100)
    material = models.CharField(max_length=50)
    impacto = models.DecimalField(max_digits=6, decimal_places=2)
    puntos_obtenidos = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self) -> str:
        return f"{self.usuario.username} · {self.prenda} (+{self.puntos_obtenidos} pts)"
