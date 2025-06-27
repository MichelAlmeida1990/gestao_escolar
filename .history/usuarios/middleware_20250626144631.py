from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from .models import SessaoUsuario

class SessionControlMiddleware:
    """
    Middleware para controle automático de sessões
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs que não precisam de verificação de sessão
        skip_urls = [
            '/login/',
            '/usuarios/login/',
            '/usuarios/logout/',
            '/usuarios/recuperar-senha/',
            '/usuarios/redefinir-senha/',
            '/auth/login/',
            '/auth/logout/',
            '/auth/recuperar-senha/',
            '/auth/redefinir-senha/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Verificar se deve pular a verificação
        should_skip = any(request.path.startswith(url) for url in skip_urls)
        
        if not should_skip and request.user.is_authenticated:
            self.verificar_sessao(request)
        
        response = self.get_response(request)
        
        # Atualizar última atividade se usuário autenticado
        if request.user.is_authenticated and not should_skip:
            self.atualizar_atividade(request)
        
        return response
    
    def verificar_sessao(self, request):
        """Verifica se a sessão é válida"""
        try:
            sessao = SessaoUsuario.objects.get(
                user=request.user,
                session_key=request.session.session_key,
                ativa=True
            )
            
            # Verificar timeout
            perfil = request.user.perfil
            tempo_limite = sessao.data_ultima_atividade + timedelta(seconds=perfil.session_timeout)
            
            if timezone.now() > tempo_limite:
                # Sessão expirou
                self.encerrar_sessao(request, sessao, 'Sessão expirada por inatividade.')
                return
            
            # Verificar IP (opcional - pode ser configurável)
            if hasattr(request.user.perfil, 'verificar_ip') and request.user.perfil.verificar_ip:
                ip_atual = self.get_client_ip(request)
                if sessao.ip_address != ip_atual:
                    self.encerrar_sessao(request, sessao, 'IP de acesso alterado por segurança.')
                    return
        
        except SessaoUsuario.DoesNotExist:
            # Sessão não encontrada ou inválida
            self.encerrar_sessao_sem_objeto(request, 'Sessão inválida.')
    
    def atualizar_atividade(self, request):
        """Atualiza a última atividade da sessão"""
        try:
            sessao = SessaoUsuario.objects.get(
                user=request.user,
                session_key=request.session.session_key,
                ativa=True
            )
            sessao.data_ultima_atividade = timezone.now()
            sessao.save(update_fields=['data_ultima_atividade'])
        except SessaoUsuario.DoesNotExist:
            pass
    
    def encerrar_sessao(self, request, sessao, motivo):
        """Encerra uma sessão específica"""
        sessao.ativa = False
        sessao.save()
        logout(request)
        messages.warning(request, motivo)
        return redirect('usuarios:login')
    
    def encerrar_sessao_sem_objeto(self, request, motivo):
        """Encerra sessão quando o objeto não existe"""
        logout(request)
        messages.warning(request, motivo)
        return redirect('usuarios:login')
    
    def get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class ForcePasswordChangeMiddleware:
    """
    Middleware para forçar mudança de senha
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs permitidas mesmo com mudança de senha forçada
        allowed_urls = [
            '/auth/alterar-senha/',
            '/auth/logout/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        should_skip = any(request.path.startswith(url) for url in allowed_urls)
        
        if (request.user.is_authenticated and 
            not should_skip and 
            hasattr(request.user, 'perfil') and 
            request.user.perfil.force_password_change):
            
            messages.warning(
                request, 
                'Você deve alterar sua senha antes de continuar.'
            )
            return redirect('usuarios:alterar_senha')
        
        return self.get_response(request)

class SecurityAuditMiddleware:
    """
    Middleware para auditoria de segurança
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Log de atividades suspeitas (implementar conforme necessário)
        if request.user.is_authenticated:
            self.log_user_activity(request)
        
        return response
    
    def log_user_activity(self, request):
        """Log das atividades do usuário (implementar conforme necessário)"""
        # Aqui você pode implementar logs de auditoria
        # Por exemplo, salvar em um modelo de Log ou arquivo
        pass 