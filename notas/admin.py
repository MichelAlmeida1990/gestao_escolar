from django.contrib import admin
from .models import Disciplina, Avaliacao, Nota

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'carga_horaria')
    search_fields = ('nome', 'codigo')

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'disciplina', 'turma', 'tipo', 'data', 'periodo')
    list_filter = ('disciplina', 'turma', 'tipo', 'periodo')
    search_fields = ('nome',)
    date_hierarchy = 'data'

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'avaliacao', 'valor', 'data_lancamento')
    list_filter = ('avaliacao__disciplina', 'avaliacao__turma', 'avaliacao__periodo')
    search_fields = ('aluno__nome', 'avaliacao__nome')
    date_hierarchy = 'data_lancamento'

