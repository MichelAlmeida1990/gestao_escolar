from django.urls import path
from . import views

app_name = 'frequencia'

urlpatterns = [
    # Página inicial
    path('', views.index, name='index'),
    
    # Dashboard
    path('dashboard/', views.dashboard_frequencia, name='dashboard'),
    
    # Registros de frequência
    path('registros/', views.RegistroFrequenciaListView.as_view(), name='registro_list'),
    path('registrar/', views.registrar_frequencia, name='registrar_frequencia'),
    
    # Relatórios
    path('relatorio/', views.relatorio_frequencia, name='relatorio_frequencia'),
    
    # Justificativas
    path('justificar/<int:registro_id>/', views.justificar_falta, name='justificar_falta'),
    path('aprovar-justificativa/<int:justificativa_id>/', views.aprovar_justificativa, name='aprovar_justificativa'),
    path('justificativas-pendentes/', views.justificativas_pendentes, name='justificativas_pendentes'),
    
    # API endpoints
    path('api/disciplinas-turma/', views.get_disciplinas_turma, name='api_disciplinas_turma'),
    
    # Página de teste
    path('teste-aprovacao/', views.teste_aprovacao, name='teste_aprovacao'),
]
