from django.urls import path
from . import views

app_name = 'biblioteca'

urlpatterns = [
    # Página inicial
    path('', views.index, name='index'),
    
    # Livros
    path('livros/', views.LivroListView.as_view(), name='livro_list'),
    path('livros/<int:pk>/', views.LivroDetailView.as_view(), name='livro_detail'),
    path('livros/novo/', views.LivroCreateView.as_view(), name='livro_create'),
    path('livros/<int:pk>/editar/', views.LivroUpdateView.as_view(), name='livro_update'),
    
    # Autores
    path('autores/', views.AutorListView.as_view(), name='autor_list'),
    path('autores/novo/', views.AutorCreateView.as_view(), name='autor_create'),
    path('autores/<int:pk>/editar/', views.AutorUpdateView.as_view(), name='autor_update'),
    
    # Categorias
    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nova/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    
    # Empréstimos
    path('emprestimos/', views.EmprestimoListView.as_view(), name='emprestimo_list'),
    path('emprestimos/<int:pk>/', views.EmprestimoDetailView.as_view(), name='emprestimo_detail'),
    path('emprestimos/novo/', views.realizar_emprestimo, name='realizar_emprestimo'),
    path('emprestimos/<int:emprestimo_id>/devolver/', views.devolver_livro, name='devolver_livro'),
    path('emprestimos/<int:emprestimo_id>/renovar/', views.renovar_emprestimo, name='renovar_emprestimo'),
    
    # Reservas
    path('reservas/', views.ReservaListView.as_view(), name='reserva_list'),
    path('reservas/nova/', views.realizar_reserva, name='realizar_reserva'),
    path('reservas/<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # Relatórios e configurações
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/emprestimos/', views.relatorio_emprestimos, name='relatorio_emprestimos'),
    path('configuracoes/', views.configuracoes, name='configuracoes'),
    
    # APIs
    path('api/buscar-livros/', views.api_buscar_livros, name='api_buscar_livros'),
    path('api/buscar-usuarios/', views.api_buscar_usuarios, name='api_buscar_usuarios'),
] 