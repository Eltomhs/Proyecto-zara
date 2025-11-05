from __future__ import annotations
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone


# CONFIG (reglas globales)
MAX_QTY_PER_ITEM = 10

# PRODUCTO / STOCK
class Producto(models.Model):
    nombre = models.CharField(max_length=160, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.0"))])
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(precio__gte=0), name="precio_no_negativo"),
            models.CheckConstraint(check=models.Q(stock__gte=0), name="stock_no_negativo"),
        ]

    def __str__(self) -> str:
        return self.nombre

# CUPONES / PROMOS
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

# CARRITO
class Carrito(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    cupon = models.ForeignKey('Cupon', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def esta_vacio(self) -> bool:
        return not self.items.exists()

    def subtotal(self) -> Decimal:
        return sum((it.cantidad * it.precio_unitario for it in self.items.all()), Decimal("0.00"))

    def total(self) -> Decimal:
        total = self.subtotal()
        if self.cupon and self.cupon.esta_vigente():
            total = total * (Decimal("1.0") - Decimal(self.cupon.descuento_porcentaje) / Decimal("100"))
        return total.quantize(Decimal("0.01"))

class ItemCarrito(models.Model):
    carrito = models.ForeignKey('Carrito', related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(MAX_QTY_PER_ITEM)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [("carrito", "producto")]
        constraints = [
            models.CheckConstraint(check=models.Q(cantidad__gte=1), name="cantidad_minima_1"),
            models.CheckConstraint(check=models.Q(cantidad__lte=MAX_QTY_PER_ITEM), name="cantidad_maxima_10"),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        # No superar stock ni el máximo por ítem (el máximo ya lo valida el field)
        if self.producto and self.cantidad > self.producto.stock:
            raise ValidationError("Cantidad supera el stock disponible.")

    def __str__(self) -> str:
        return f"{self.producto} x {self.cantidad}"

# PEDIDO (checkout)
class Pedido(models.Model):
    carrito = models.OneToOneField('Carrito', on_delete=models.PROTECT)
    email_cliente = models.EmailField(validators=[EmailValidator()])
    creado_en = models.DateTimeField(auto_now_add=True)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"Pedido #{self.pk} - {self.email_cliente}"

# ENCUESTA
class CampaniaEncuesta(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    activa = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.nombre

class RespuestaEncuesta(models.Model):
    campania = models.ForeignKey('CampaniaEncuesta', on_delete=models.PROTECT)
    email = models.EmailField()
    consentimiento = models.BooleanField(default=False)
    rating_sustentabilidad = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    rating_calidad = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    enviado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Un email solo una vez por campaña (case-insensitive)
            models.UniqueConstraint(
                models.functions.Lower("email"), "campania",
                name="unica_respuesta_por_email_y_campania"
            ),
            models.CheckConstraint(
                check=models.Q(rating_sustentabilidad__gte=1, rating_sustentabilidad__lte=5),
                name="rating_sustentabilidad_1_5"
            ),
            models.CheckConstraint(
                check=models.Q(rating_calidad__gte=1, rating_calidad__lte=5),
                name="rating_calidad_1_5"
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.consentimiento:
            raise ValidationError("Debes aceptar consentimiento para enviar la encuesta.")

    def __str__(self) -> str:
        return f"{self.email} · {self.campania}"