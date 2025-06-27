from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario, SessaoUsuario, TokenRecuperacaoSenha

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    inlines = [PerfilUsuarioInline]
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'tipo_usuario', 'telefone', 'ultimo_login', 
        'tentativas_login', 'esta_bloqueado'
    ]
    list_filter = [
        'tipo_usuario', 'force_password_change', 'dois_fatores_ativo', 
        'data_criacao'
    ]
    search_fields = ['user__username', 'user__email', 'telefone']
    readonly_fields = [
        'data_criacao', 'data_atualizacao', 'ultimo_login', 
        'tentativas_login', 'ip_ultimo_login'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'tipo_usuario', 'telefone', 'foto', 'data_nascimento', 'endereco')
        }),
        ('Controle de Sessão', {
            'fields': ('session_timeout', 'max_sessions', 'force_password_change')
        }),
        ('Segurança', {
            'fields': ('dois_fatores_ativo', 'tentativas_login', 'bloqueado_ate')
        }),
        ('Auditoria', {
            'fields': ('ultimo_login', 'ip_ultimo_login', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SessaoUsuario)
class SessaoUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ip_address', 'data_inicio', 'data_ultima_atividade', 
        'ativa', 'duracao_sessao'
    ]
    list_filter = ['ativa', 'data_inicio']
    search_fields = ['user__username', 'ip_address']
    readonly_fields = ['session_key', 'data_inicio', 'duracao_sessao']
    
    def duracao_sessao(self, obj):
        return obj.duracao_sessao
    duracao_sessao.short_description = 'Duração'

@admin.register(TokenRecuperacaoSenha)
class TokenRecuperacaoSenhaAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'criado_em', 'usado', 'esta_valido', 'ip_solicitacao'
    ]
    list_filter = ['usado', 'criado_em']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['token', 'criado_em', 'esta_valido']
    
    def esta_valido(self, obj):
        return obj.esta_valido
    esta_valido.boolean = True
    esta_valido.short_description = 'Válido'
