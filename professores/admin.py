from django.contrib import admin
from .models import Professor

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'disciplina', 'email', 'telefone')
    search_fields = ('nome', 'email', 'disciplina')
    filter_horizontal = ('turmas',)
