"""
URL configuration for mi_sitio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from zara import views as zara

urlpatterns = [
    path('admin/', admin.site.urls),

    # Páginas principales
    path('', zara.home, name='home'),
    path('tradein/', zara.tradein, name='tradein'),
    path('gracias/', zara.gracias, name='gracias'),

    # Catálogo 
    path('mujer/', zara.home, name='mujer'),
    path('hombre/', zara.home, name='hombre'),
    path('nina/', zara.home, name='nina'),
    path('nino/', zara.home, name='nino'),
    path('accesorios/', zara.home, name='accesorios'),

    path('informe/', zara.informe_encuesta, name='informe_encuesta'),
    path('api/encuesta.json', zara.encuesta_json, name='encuesta_json'),
]
