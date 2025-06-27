# usuarios/urls.py
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticação
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    path('alterar-senha/', views.alterar_senha_view, name='alterar_senha'),
    
    # Debug (temporário)
    path('debug-perfil/', TemplateView.as_view(template_name='debug_perfil.html'), name='debug_perfil'),
    
    # Recuperação de senha
    path('recuperar-senha/', views.recuperar_senha_view, name='recuperar_senha'),
    path('redefinir-senha/<str:token>/', views.redefinir_senha_view, name='redefinir_senha'),
    
    # Controle de sessões
    path('encerrar-sessao/<int:sessao_id>/', views.encerrar_sessao_view, name='encerrar_sessao'),
    path('encerrar-todas-sessoes/', views.encerrar_todas_sessoes_view, name='encerrar_todas_sessoes'),
    
    # API para verificação de sessão
    path('api/check-session/', views.check_session_status, name='check_session'),
]
