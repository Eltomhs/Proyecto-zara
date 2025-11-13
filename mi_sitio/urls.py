# mi_sitio/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Sitio principal (ZARA)
    path("", include("zara.urls")),

    # Módulo de circularidad / trade-in / pasaporte (Zara_Re)
    path("zara-re/", include("zara_re.urls")),

    # Admin de Django
    path("admin/", admin.site.urls),

    # Autenticación estándar (login, logout, password reset, etc.)
    path("accounts/", include("django.contrib.auth.urls")),
]

# Archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
