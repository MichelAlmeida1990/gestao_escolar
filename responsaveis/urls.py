from django.urls import path
from . import views

app_name = 'responsaveis'


urlpatterns = [
    path('', views.responsavel_list, name='responsavel_list'),
    path('<int:pk>/', views.responsavel_detail, name='responsavel_detail'),
    path('novo/', views.responsavel_create, name='responsavel_create'),
    path('<int:pk>/editar/', views.responsavel_update, name='responsavel_update'),
    path('<int:pk>/excluir/', views.responsavel_delete, name='responsavel_delete'),
    path('<int:responsavel_id>/vincular-aluno/', views.vincular_aluno, name='vincular_aluno'),
    path('desvincular-aluno/<int:relacao_id>/', views.desvincular_aluno, name='desvincular_aluno'),
]
