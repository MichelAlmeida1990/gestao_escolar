from django.urls import path
from . import views

app_name = 'responsaveis'

urlpatterns = [
    path('dashboard/', views.dashboard_responsavel, name='dashboard'),
    path('boletim/<int:aluno_id>/', views.boletim_aluno, name='boletim'),
    path('perfil/', views.perfil_responsavel, name='perfil'),
    path('', views.responsavel_list, name='responsavel_list'),
]
