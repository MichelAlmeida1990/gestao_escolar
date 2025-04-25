from django.contrib import admin
from .models import Turma

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'serie', 'turno', 'ano_letivo', 'capacidade')
    search_fields = ('nome', 'serie')
    list_filter = ('turno', 'ano_letivo')
