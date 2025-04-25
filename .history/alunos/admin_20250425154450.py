from django.contrib import admin
from .models import Aluno

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turma', 'email', 'telefone')
    search_fields = ('nome', 'email')
    list_filter = ('turma',)
