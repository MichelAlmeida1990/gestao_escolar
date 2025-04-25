# alunos/admin.py
from django.contrib import admin
from .models import Aluno

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'status', 'data_ingresso')
    list_filter = ('status', 'data_ingresso')
    search_fields = ('nome', 'matricula', 'cpf')
    date_hierarchy = 'data_ingresso'
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'data_nascimento', 'matricula', 'foto')
        }),
        ('Documentos', {
            'fields': ('cpf', 'rg')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Responsável', {
            'fields': ('responsavel_nome', 'responsavel_telefone')
        }),
        ('Informações Escolares', {
            'fields': ('data_ingresso', 'status', 'observacoes')
        }),
    )
