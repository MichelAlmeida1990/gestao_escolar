from django.urls import path
from . import views

app_name = 'comunicados'  # Namespace necessário

urlpatterns = [
    path('', views.comunicado_list, name='comunicado_list'),
    path('novo/', views.comunicado_create, name='comunicado_create'),
    path('meus/', views.meus_comunicados, name='meus_comunicados'),
]
