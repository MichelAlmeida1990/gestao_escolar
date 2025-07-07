from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import MatriculaOnline, DocumentoMatricula, ConfiguracaoMatricula
from django.utils import timezone

@admin.register(MatriculaOnline)
class MatriculaOnlineAdmin(admin.ModelAdmin):
    list_display = [
        'codigo_matricula', 'nome_completo', 'serie_desejada', 
        'turno_desejado', 'status', 'data_criacao', 'acoes'
    ]
    list_filter = [
        'status', 'serie_desejada', 'turno_desejado', 
        'data_criacao', 'data_aprovacao'
    ]
    search_fields = [
        'nome_completo', 'codigo_matricula', 'cpf', 
        'email', 'responsavel_nome'
    ]
    readonly_fields = [
        'codigo_matricula', 'data_criacao', 'data_atualizacao', 
        'token_confirmacao'
    ]
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Informações da Matrícula', {
            'fields': ('codigo_matricula', 'status', 'ano_letivo')
        }),
        ('Dados do Aluno', {
            'fields': (
                'nome_completo', 'data_nascimento', 'cpf', 'rg',
                'telefone', 'email'
            )
        }),
        ('Endereço', {
            'fields': ('endereco', 'bairro', 'cidade', 'estado', 'cep')
        }),
        ('Informações Escolares', {
            'fields': ('serie_desejada', 'turno_desejado', 'escola_anterior')
        }),
        ('Responsável', {
            'fields': (
                'responsavel_nome', 'responsavel_cpf', 
                'responsavel_telefone', 'responsavel_email'
            )
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao', 'motivo_rejeicao'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao', 'token_confirmacao'),
            'classes': ('collapse',)
        }),
    )
    
    def acoes(self, obj):
        """Botões de ação para cada matrícula"""
        if obj.status == 'pendente':
            aprovar_url = reverse('admin:matriculas_matriculaonline_aprovar', args=[obj.pk])
            rejeitar_url = reverse('admin:matriculas_matriculaonline_rejeitar', args=[obj.pk])
            
            return format_html(
                '<a href="{}" class="button" style="background: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px; margin-right: 5px;">Aprovar</a>'
                '<a href="{}" class="button" style="background: #dc3545; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">Rejeitar</a>',
                aprovar_url, rejeitar_url
            )
        elif obj.status == 'aprovada':
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Aprovada</span>'
            )
        elif obj.status == 'rejeitada':
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Rejeitada</span>'
            )
        else:
            return obj.get_status_display()
    
    acoes.short_description = 'Ações'
    acoes.allow_tags = True
    
    def get_queryset(self, request):
        """Adicionar contagem de documentos"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('documentos')
    
    def get_readonly_fields(self, request, obj=None):
        """Campos somente leitura baseados no status"""
        readonly_fields = list(super().get_readonly_fields(request, obj))
        
        if obj and obj.status in ['aprovada', 'rejeitada']:
            readonly_fields.extend([
                'nome_completo', 'data_nascimento', 'cpf', 'rg',
                'telefone', 'email', 'endereco', 'bairro', 'cidade', 
                'estado', 'cep', 'serie_desejada', 'turno_desejado',
                'responsavel_nome', 'responsavel_cpf', 'responsavel_telefone',
                'responsavel_email'
            ])
        
        return readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Salvar modelo com usuário que fez a alteração"""
        if not change:  # Nova matrícula
            obj.save()
        else:
            # Se está mudando o status, registrar quem fez a alteração
            if 'status' in form.changed_data:
                obj.aprovado_por = request.user
                obj.data_aprovacao = timezone.now()
            obj.save()
    
    actions = ['aprovar_selecionadas', 'rejeitar_selecionadas']
    
    def aprovar_selecionadas(self, request, queryset):
        """Aprovar matrículas selecionadas"""
        count = 0
        for matricula in queryset.filter(status='pendente'):
            matricula.aprovar(request.user)
            count += 1
        
        self.message_user(
            request, 
            f"{count} matrícula(s) aprovada(s) com sucesso!"
        )
    
    aprovar_selecionadas.short_description = "Aprovar matrículas selecionadas"
    
    def rejeitar_selecionadas(self, request, queryset):
        """Rejeitar matrículas selecionadas"""
        count = 0
        for matricula in queryset.filter(status='pendente'):
            matricula.rejeitar("Rejeição em massa", request.user)
            count += 1
        
        self.message_user(
            request, 
            f"{count} matrícula(s) rejeitada(s) com sucesso!"
        )
    
    rejeitar_selecionadas.short_description = "Rejeitar matrículas selecionadas"

@admin.register(DocumentoMatricula)
class DocumentoMatriculaAdmin(admin.ModelAdmin):
    list_display = [
        'matricula', 'tipo', 'nome_arquivo', 'tamanho_formatado', 
        'data_upload', 'link_download'
    ]
    list_filter = ['tipo', 'data_upload']
    search_fields = ['matricula__nome_completo', 'matricula__codigo_matricula']
    readonly_fields = ['nome_arquivo', 'tamanho_arquivo', 'data_upload']
    date_hierarchy = 'data_upload'
    
    fieldsets = (
        ('Informações do Documento', {
            'fields': ('matricula', 'tipo', 'arquivo')
        }),
        ('Detalhes do Arquivo', {
            'fields': ('nome_arquivo', 'tamanho_arquivo', 'data_upload'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
    
    def tamanho_formatado(self, obj):
        """Formata o tamanho do arquivo"""
        if obj.tamanho_arquivo:
            if obj.tamanho_arquivo < 1024:
                return f"{obj.tamanho_arquivo} B"
            elif obj.tamanho_arquivo < 1024 * 1024:
                return f"{obj.tamanho_arquivo / 1024:.1f} KB"
            else:
                return f"{obj.tamanho_arquivo / (1024 * 1024):.1f} MB"
        return "N/A"
    
    tamanho_formatado.short_description = 'Tamanho'
    
    def link_download(self, obj):
        """Link para download do arquivo"""
        if obj.arquivo:
            return format_html(
                '<a href="{}" target="_blank" style="background: #007bff; color: white; padding: 3px 8px; text-decoration: none; border-radius: 3px;">Download</a>',
                obj.arquivo.url
            )
        return "N/A"
    
    link_download.short_description = 'Download'
    link_download.allow_tags = True

@admin.register(ConfiguracaoMatricula)
class ConfiguracaoMatriculaAdmin(admin.ModelAdmin):
    list_display = [
        'nome_configuracao', 'matricula_ativa', 'periodo_matriculas', 
        'total_series', 'total_turnos'
    ]
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Período de Matrículas', {
            'fields': ('data_inicio_matriculas', 'data_fim_matriculas')
        }),
        ('Opções Disponíveis', {
            'fields': ('series_disponiveis', 'turnos_disponiveis', 'documentos_obrigatorios')
        }),
        ('Configurações de Email', {
            'fields': (
                'email_confirmacao_ativa', 'email_aprovacao_ativa', 
                'email_rejeicao_ativa'
            )
        }),
        ('Configurações Gerais', {
            'fields': (
                'matricula_ativa', 'max_documentos_por_matricula', 
                'tamanho_max_arquivo'
            )
        }),
        ('Metadados', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def nome_configuracao(self, obj):
        return f"Configuração {obj.data_inicio_matriculas.year}"
    
    nome_configuracao.short_description = 'Configuração'
    
    def periodo_matriculas(self, obj):
        return f"{obj.data_inicio_matriculas.strftime('%d/%m/%Y')} a {obj.data_fim_matriculas.strftime('%d/%m/%Y')}"
    
    periodo_matriculas.short_description = 'Período'
    
    def total_series(self, obj):
        return len(obj.series_disponiveis) if obj.series_disponiveis else 0
    
    total_series.short_description = 'Séries'
    
    def total_turnos(self, obj):
        return len(obj.turnos_disponiveis) if obj.turnos_disponiveis else 0
    
    total_turnos.short_description = 'Turnos'
    
    def has_add_permission(self, request):
        """Permitir apenas uma configuração"""
        return not ConfiguracaoMatricula.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Não permitir exclusão da configuração"""
        return False

# Personalização do admin
admin.site.site_header = "Sistema de Gestão Escolar - Administração"
admin.site.site_title = "Gestão Escolar"
admin.site.index_title = "Painel de Controle"
