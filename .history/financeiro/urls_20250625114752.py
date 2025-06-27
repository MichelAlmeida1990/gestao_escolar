from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),
    
    # Mensalidades
    path('mensalidades/', views.MensalidadeListView.as_view(), name='mensalidade_list'),
    path('mensalidades/gerar/', views.gerar_mensalidades, name='gerar_mensalidades'),
    path('mensalidades/<int:mensalidade_id>/pagar/', views.pagar_mensalidade, name='pagar_mensalidade'),
    
    # Relatórios e configurações
    path('relatorios/', views.relatorios, name='relatorios'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
] 