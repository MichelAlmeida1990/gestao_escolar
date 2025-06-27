# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('perfil/', views.perfil_view, name='perfil'),
    path('alterar-senha/', views.alterar_senha_view, name='alterar_senha'),
]
