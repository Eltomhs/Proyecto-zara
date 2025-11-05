from django.urls import path
from . import views

app_name = 'zara'

urlpatterns = [
    path('', views.home, name='home'),

    # Catálogo
    path('mujer/', views.mujer, name='mujer'),
    path('hombre/', views.hombre, name='hombre'),
    path('nina/', views.nina, name='nina'),
    path('nino/', views.nino, name='nino'),
    path('accesorios/', views.accesorios, name='accesorios'),

    # 🛒 Carrito
    path('carrito/', views.carrito, name='carrito'),

    # Checkout invitado
    path('invitado/', views.invitado, name='invitado'),

    # Extras
    path('perfume/', views.perfume, name='perfume'),
    path('tradein/', views.tradein, name='tradein'),
    
    # Dashboard
    path('informe/', views.informe_encuesta, name='informe_encuesta'),
    path('chart/<str:key>/', views.chart_detail, name='chart_detail'),
]