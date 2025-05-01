from django.urls import path
from . import views

urlpatterns = [
    path('', views.TurmaListView.as_view(), name='turma_list'),
    path('<int:pk>/', views.TurmaDetailView.as_view(), name='turma_detail'),
    path('nova/', views.TurmaCreateView.as_view(), name='turma_create'),
    path('<int:pk>/editar/', views.TurmaUpdateView.as_view(), name='turma_update'),
    path('<int:pk>/excluir/', views.TurmaDeleteView.as_view(), name='turma_delete'),
    path('<int:turma_id>/adicionar-alunos/', views.adicionar_alunos, name='adicionar_alunos'),
    path('<int:turma_id>/remover-aluno/<int:aluno_id>/', views.remover_aluno, name='remover_aluno'),
]
