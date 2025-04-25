from django.urls import path
from . import views

urlpatterns = [
    # Views baseadas em classe
    path('', views.AlunoListView.as_view(), name='aluno_list'),
    path('<int:pk>/', views.AlunoDetailView.as_view(), name='aluno_detail'),
    path('novo/', views.AlunoCreateView.as_view(), name='aluno_create'),
    path('<int:pk>/editar/', views.AlunoUpdateView.as_view(), name='aluno_update'),
    path('<int:pk>/excluir/', views.AlunoDeleteView.as_view(), name='aluno_delete'),
    path('dashboard/', views.dashboard, name='aluno_dashboard'),
    
    # Alternativa: Views baseadas em função
    # path('', views.aluno_list, name='aluno_list'),
    # path('<int:pk>/', views.aluno_detail, name='aluno_detail'),
    # path('novo/', views.aluno_create, name='aluno_create'),
    # path('<int:pk>/editar/', views.aluno_update, name='aluno_update'),
    # path('<int:pk>/excluir/', views.aluno_delete, name='aluno_delete'),
]
