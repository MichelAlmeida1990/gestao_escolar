from django.urls import path
from . import views

app_name = 'matriculas'

urlpatterns = [
    # Páginas públicas
    path('', views.index_matriculas, name='index'),
    path('nova/', views.nova_matricula, name='nova_matricula'),
    path('confirmacao/<str:codigo>/', views.confirmacao_matricula, name='confirmacao'),
    path('consultar/', views.consultar_matricula, name='consultar'),
    path('detalhes/<str:codigo>/', views.detalhes_matricula, name='detalhes_matricula'),
    path('upload-documentos/<str:codigo>/', views.upload_documentos, name='upload_documentos'),
    
    # Páginas administrativas
    path('admin/', views.MatriculaListView.as_view(), name='matricula_list'),
    path('admin/<int:pk>/', views.MatriculaDetailView.as_view(), name='matricula_detail'),
    path('admin/<int:pk>/aprovar/', views.aprovar_matricula, name='aprovar_matricula'),
    path('admin/<int:pk>/rejeitar/', views.rejeitar_matricula, name='rejeitar_matricula'),
    path('admin/configuracao/', views.ConfiguracaoMatriculaView.as_view(), name='configuracao'),
    path('admin/documento/<int:pk>/excluir/', views.excluir_documento, name='excluir_documento'),
    
    # APIs
    path('api/matriculas-pendentes/', views.api_matriculas_pendentes, name='api_matriculas_pendentes'),
    path('api/estatisticas/', views.api_estatisticas_matriculas, name='api_estatisticas'),
] 