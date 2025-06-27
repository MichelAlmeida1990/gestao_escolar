from django.urls import path
from . import views

app_name = 'alunos'  # Isso já deve estar adicionado

urlpatterns = [
    # Views baseadas em classe
    path('', views.AlunoListView.as_view(), name='aluno_list'),
    path('<int:pk>/', views.AlunoDetailView.as_view(), name='aluno_detail'),
    path('novo/', views.AlunoCreateView.as_view(), name='aluno_create'),
    path('<int:pk>/editar/', views.AlunoUpdateView.as_view(), name='aluno_update'),
    path('<int:pk>/excluir/', views.AlunoDeleteView.as_view(), name='aluno_delete'),
    path('dashboard/', views.dashboard, name='aluno_dashboard'),
    
    # Adicione esta linha:
    path('meus-alunos/', views.meus_alunos, name='meus_alunos'),
]
