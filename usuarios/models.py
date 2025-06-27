from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class TipoUsuario(models.TextChoices):
    ADMIN = 'admin', 'Administrador'
    PROFESSOR = 'professor', 'Professor'
    RESPONSAVEL = 'responsavel', 'Responsável'
    FUNCIONARIO = 'funcionario', 'Funcionário'

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TipoUsuario.choices, default=TipoUsuario.FUNCIONARIO)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='perfis/', blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    endereco = models.TextField(blank=True, null=True)
    
    # Controle de sessão
    session_timeout = models.IntegerField(default=3600, help_text='Timeout da sessão em segundos')
    max_sessions = models.IntegerField(default=1, help_text='Máximo de sessões simultâneas')
    force_password_change = models.BooleanField(default=False, help_text='Forçar mudança de senha no próximo login')
    
    # Auditoria
    ultimo_login = models.DateTimeField(null=True, blank=True)
    tentativas_login = models.IntegerField(default=0)
    bloqueado_ate = models.DateTimeField(null=True, blank=True)
    
    # Configurações de segurança
    dois_fatores_ativo = models.BooleanField(default=False)
    ip_ultimo_login = models.GenericIPAddressField(null=True, blank=True)
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuário'
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_tipo_usuario_display()})"
    
    @property
    def esta_bloqueado(self):
        if self.bloqueado_ate:
            return timezone.now() < self.bloqueado_ate
        return False
    
    def pode_fazer_login(self):
        return not self.esta_bloqueado
    
    def incrementar_tentativas_login(self):
        self.tentativas_login += 1
        if self.tentativas_login >= 5:  # Bloquear após 5 tentativas
            self.bloqueado_ate = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def resetar_tentativas_login(self):
        self.tentativas_login = 0
        self.bloqueado_ate = None
        self.ultimo_login = timezone.now()
        self.save()

class SessaoUsuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessoes')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    data_inicio = models.DateTimeField(auto_now_add=True)
    data_ultima_atividade = models.DateTimeField(auto_now=True)
    ativa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Sessão de Usuário'
        verbose_name_plural = 'Sessões de Usuário'
        ordering = ['-data_ultima_atividade']
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.data_inicio})"
    
    @property
    def duracao_sessao(self):
        return self.data_ultima_atividade - self.data_inicio

class TokenRecuperacaoSenha(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    ip_solicitacao = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Token de Recuperação de Senha'
        verbose_name_plural = 'Tokens de Recuperação de Senha'
    
    def __str__(self):
        return f"Token para {self.user.username}"
    
    @property
    def esta_valido(self):
        # Token válido por 24 horas
        validade = self.criado_em + timezone.timedelta(hours=24)
        return not self.usado and timezone.now() < validade
    
    def marcar_como_usado(self):
        self.usado = True
        self.save()

# Signals para criar perfil automaticamente
@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
