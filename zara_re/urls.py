# zara_re/urls.py
from django.urls import path
from . import views

app_name = "zara_re"

urlpatterns = [
    path("", views.home, name="home"),
    path("pasaporte/", views.pasaporte, name="pasaporte"),
    # si tienes más vistas de zara_re, agrégalas aquí
]