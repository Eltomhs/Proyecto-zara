from django.urls import path
from .views import informe_encuesta, encuesta_json

urlpatterns = [
    path('informe/', informe_encuesta, name='informe_encuesta'),
    path('api/encuesta.json', encuesta_json, name='encuesta_json'),
]
