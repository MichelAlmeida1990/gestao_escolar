from django.contrib import admin
from .models import Comunicado

@admin.register(Comunicado)
class ComunicadoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'data_criacao', 'para_todos']
    list_filter = ['para_todos', 'data_criacao', 'autor']
    search_fields = ['titulo', 'conteudo']
    filter_horizontal = ['turmas', 'alunos']
