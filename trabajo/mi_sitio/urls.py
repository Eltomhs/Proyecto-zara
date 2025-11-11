# mi_sitio/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Rutas de tu app ZARA primero: /, /login/, etc. se resuelven aquí
    path("", include("zara.urls")),

    # Admin de Django
    path("admin/", admin.site.urls),

    # (Opcional) Auth nativo de Django con prefijo para NO chocar con /login/
    # Deja esta línea si quieres /accounts/login/ además de tu propio /login/
    path("accounts/", include("django.contrib.auth.urls")),
]

# Archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
