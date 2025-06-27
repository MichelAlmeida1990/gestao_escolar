from django.contrib import admin
from .models import Responsavel, RelacaoAlunoResponsavel

@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'telefone', 'email', 'ativo')
    list_filter = ('ativo', 'cidade', 'estado')
    search_fields = ('nome_completo', 'cpf', 'email')
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('usuario', 'nome_completo', 'cpf', 'data_nascimento', 'profissao', 'local_trabalho')
        }),
        ('Contato', {
            'fields': ('telefone', 'celular', 'email')
        }),
        ('Endereço', {
            'fields': ('endereco', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
    )

@admin.register(RelacaoAlunoResponsavel)
class RelacaoAlunoResponsavelAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'responsavel', 'tipo_parentesco', 'responsavel_financeiro', 'autorizado_buscar')
    list_filter = ('tipo_parentesco', 'responsavel_financeiro', 'autorizado_buscar')
    search_fields = ('aluno__nome_completo', 'responsavel__nome_completo')
    autocomplete_fields = ['aluno', 'responsavel']
