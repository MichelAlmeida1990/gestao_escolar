from django.urls import path
from . import views

app_name = 'notas'

urlpatterns = [
    # Disciplinas
    path('disciplinas/', views.DisciplinaListView.as_view(), name='disciplina_list'),
    path('disciplinas/nova/', views.DisciplinaCreateView.as_view(), name='disciplina_create'),
    path('disciplinas/<int:pk>/editar/', views.DisciplinaUpdateView.as_view(), name='disciplina_update'),
    path('disciplinas/<int:pk>/excluir/', views.DisciplinaDeleteView.as_view(), name='disciplina_delete'),
    
    # Avaliações
    path('avaliacoes/', views.AvaliacaoListView.as_view(), name='avaliacao_list'),
    path('avaliacoes/nova/', views.AvaliacaoCreateView.as_view(), name='avaliacao_create'),
    path('avaliacoes/<int:pk>/editar/', views.AvaliacaoUpdateView.as_view(), name='avaliacao_update'),
    path('avaliacoes/<int:pk>/excluir/', views.AvaliacaoDeleteView.as_view(), name='avaliacao_delete'),
    
    # Lançamento de notas
    path('lancar-notas/<int:avaliacao_id>/', views.lancar_notas, name='lancar_notas'),
    
    # Boletim
    path('boletim/', views.selecionar_aluno_boletim, name='selecionar_aluno_boletim'),
    path('boletim/<int:aluno_id>/', views.boletim_aluno, name='boletim_aluno'),
    
    # Desempenho da turma
    path('desempenho-turma/', views.selecionar_turma_desempenho, name='selecionar_turma_desempenho'),
    path('desempenho-turma/<int:turma_id>/', views.desempenho_turma, name='desempenho_turma'),
]
