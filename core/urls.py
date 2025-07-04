from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'core'

def redirect_to_login(request):
    """Redireciona para a página de login"""
    return redirect('usuarios:login')

urlpatterns = [
    path('', redirect_to_login, name='home'),
    path('dashboard/', views.home, name='dashboard'),
]
