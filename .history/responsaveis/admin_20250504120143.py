from django.contrib import admin
from .models import Responsavel, ResponsavelAluno

@admin.register(Responsavel)
class ResponsavelAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cpf', 'telefone', 'email')
    search_fields = ('nome', 'cpf', 'telefone', 'email')
    list_filter = ('cidade', 'estado')

@admin.register(ResponsavelAluno)
class ResponsavelAlunoAdmin(admin.ModelAdmin):
    list_display = ('responsavel', 'aluno', 'tipo_relacao', 'data_vinculo')
    list_filter = ('tipo_relacao',)
    search_fields = ('responsavel__nome', 'aluno__nome')
    autocomplete_fields = ['responsavel', 'aluno']
