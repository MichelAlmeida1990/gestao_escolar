from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from core.views import custom_logout  # Certifique-se de que esta função existe em core/views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('alunos/', include('alunos.urls')),
    path('professores/', include('professores.urls')),
    path('turmas/', include('turmas.urls', namespace='turmas')),  # Adicionado o namespace
    path('notas/', include('notas.urls')),
    path('responsaveis/', include('responsaveis.urls', namespace='responsaveis')),  # Adicionado o app 
    responsaveis
    path('frequencia/', include('frequencia.urls', namespace='frequencia')),

    
    # URLs de autenticação
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
]

# Configuração para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
