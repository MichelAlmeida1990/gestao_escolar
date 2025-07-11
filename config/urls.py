from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('alunos/', include('alunos.urls')),
    path('professores/', include('professores.urls', namespace='professores')),
    path('turmas/', include('turmas.urls', namespace='turmas')),  # Adicionado o namespace
    path('notas/', include('notas.urls')),
    path('responsaveis/', include('responsaveis.urls', namespace='responsaveis')),  # Adicionado o app 
    path('frequencia/', include('frequencia.urls', namespace='frequencia')),
    path('biblioteca/', include('biblioteca.urls', namespace='biblioteca')),
    path('financeiro/', include('financeiro.urls', namespace='financeiro')),
    path('comunicados/', include('comunicados.urls')),  # Adicionado o app de comunicados
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('matriculas/', include('matriculas.urls', namespace='matriculas')),
]

# Configuração para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
