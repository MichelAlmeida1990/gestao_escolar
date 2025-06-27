# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
import secrets
import hashlib
from datetime import timedelta

from .models import PerfilUsuario, SessaoUsuario, TokenRecuperacaoSenha, TipoUsuario
from .forms import LoginCustomForm, RecuperacaoSenhaForm, RedefinirSenhaForm, PerfilUsuarioForm

def get_client_ip(request):
    """Obtém o IP real do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """Obtém o user agent do cliente"""
    return request.META.get('HTTP_USER_AGENT', '')

def get_or_create_user_profile(user):
    """Obtém ou cria o perfil do usuário"""
    try:
        return user.perfil
    except PerfilUsuario.DoesNotExist:
        # Determinar tipo de usuário baseado em is_staff
        tipo_usuario = TipoUsuario.ADMIN if user.is_staff else TipoUsuario.FUNCIONARIO
        
        perfil = PerfilUsuario.objects.create(
            user=user,
            tipo_usuario=tipo_usuario,
            session_timeout=3600,  # 1 hora padrão
            max_sessions=3,
            require_password_change=False,
            force_password_change=False
        )
        return perfil

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    form_class = LoginCustomForm
    redirect_authenticated_user = True
    
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        try:
            user = User.objects.get(username=username)
            perfil = get_or_create_user_profile(user)
            
            # Verificar se o usuário está bloqueado
            if not perfil.pode_fazer_login():
                messages.error(
                    self.request, 
                    f'Conta bloqueada até {perfil.bloqueado_ate.strftime("%d/%m/%Y %H:%M")} devido a muitas tentativas de login.'
                )
                return self.form_invalid(form)
            
            # Verificar se precisa forçar mudança de senha
            if perfil.force_password_change:
                messages.warning(
                    self.request,
                    'Você deve alterar sua senha antes de continuar.'
                )
                self.request.session['user_must_change_password'] = user.id
                return redirect('usuarios:alterar_senha')
            
        except User.DoesNotExist:
            pass
        
        # Tentar autenticar
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            # Login bem-sucedido
            perfil = get_or_create_user_profile(user)
            perfil.resetar_tentativas_login()
            perfil.ip_ultimo_login = get_client_ip(self.request)
            perfil.save()
            
            # Controlar sessões simultâneas
            self.controlar_sessoes(user)
            
            # Fazer login
            login(self.request, user)
            
            # Registrar sessão
            self.registrar_sessao(user)
            
            messages.success(
                self.request,
                f'Bem-vindo, {user.get_full_name() or user.username}!'
            )
            
            # Redirecionar baseado no tipo de usuário
            return self.redirecionar_por_perfil(user)
        else:
            # Login falhou
            try:
                user_obj = User.objects.get(username=username)
                perfil = get_or_create_user_profile(user_obj)
                perfil.incrementar_tentativas_login()
            except User.DoesNotExist:
                pass
            
            messages.error(
                self.request,
                'Usuário ou senha incorretos.'
            )
            return self.form_invalid(form)
    
    def controlar_sessoes(self, user):
        """Controla o número máximo de sessões simultâneas"""
        perfil = get_or_create_user_profile(user)
        sessoes_ativas = SessaoUsuario.objects.filter(user=user, ativa=True).count()
        
        if sessoes_ativas >= perfil.max_sessions:
            # Invalidar sessões mais antigas
            sessoes_antigas = SessaoUsuario.objects.filter(
                user=user, ativa=True
            ).order_by('data_ultima_atividade')[:-1]
            
            for sessao in sessoes_antigas:
                sessao.ativa = False
                sessao.save()
    
    def registrar_sessao(self, user):
        """Registra a nova sessão do usuário"""
        SessaoUsuario.objects.create(
            user=user,
            session_key=self.request.session.session_key,
            ip_address=get_client_ip(self.request),
            user_agent=get_user_agent(self.request)
        )
    
    def redirecionar_por_perfil(self, user):
        """Redireciona baseado no tipo de perfil do usuário"""
        perfil = get_or_create_user_profile(user)
        
        # Verificar se há URL de redirecionamento
        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)
        
        # Redirecionar baseado no tipo de usuário
        if perfil.tipo_usuario == TipoUsuario.ADMIN or user.is_staff:
            return redirect('core:home')
        elif perfil.tipo_usuario == TipoUsuario.PROFESSOR:
            return redirect('core:home')  # Mudando temporariamente para home
        elif perfil.tipo_usuario == TipoUsuario.RESPONSAVEL:
            return redirect('core:home')  # Mudando temporariamente para home
        else:
            return redirect('core:home')

@login_required
def custom_logout(request):
    """Logout customizado que registra o fim da sessão"""
    if request.user.is_authenticated:
        # Marcar sessão como inativa
        try:
            sessao = SessaoUsuario.objects.get(
                user=request.user,
                session_key=request.session.session_key,
                ativa=True
            )
            sessao.ativa = False
            sessao.save()
        except SessaoUsuario.DoesNotExist:
            pass
    
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('usuarios:login')

@login_required
def perfil_view(request):
    """Visualizar e editar perfil do usuário"""
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, request.FILES, instance=request.user.perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('usuarios:perfil')
    else:
        form = PerfilUsuarioForm(instance=request.user.perfil)
    
    # Buscar sessões ativas
    sessoes = SessaoUsuario.objects.filter(user=request.user, ativa=True)
    
    context = {
        'form': form,
        'user': request.user,
        'perfil': request.user.perfil,
        'sessoes': sessoes,
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def alterar_senha_view(request):
    """Alterar senha do usuário"""
    # Verificar se é mudança forçada
    user_must_change = request.session.get('user_must_change_password')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            # Remover flag de mudança forçada
            if user_must_change:
                request.user.perfil.force_password_change = False
                request.user.perfil.save()
                del request.session['user_must_change_password']
            
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'mudanca_forcada': bool(user_must_change)
    }
    return render(request, 'usuarios/alterar_senha.html', context)

def recuperar_senha_view(request):
    """Solicitar recuperação de senha"""
    if request.method == 'POST':
        form = RecuperacaoSenhaForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Gerar token único
                token = secrets.token_urlsafe(50)
                
                # Salvar token
                TokenRecuperacaoSenha.objects.create(
                    user=user,
                    token=token,
                    ip_solicitacao=get_client_ip(request)
                )
                
                # Enviar email (simulado por enquanto)
                # Em produção, configure o SMTP e envie o email real
                print(f"Token de recuperação para {user.email}: {token}")
                
                messages.success(
                    request,
                    'Se o email estiver cadastrado, você receberá instruções para recuperar sua senha.'
                )
                return redirect('usuarios:login')
                
            except User.DoesNotExist:
                # Não revelar se o email existe ou não por segurança
                messages.success(
                    request,
                    'Se o email estiver cadastrado, você receberá instruções para recuperar sua senha.'
                )
                return redirect('usuarios:login')
    else:
        form = RecuperacaoSenhaForm()
    
    return render(request, 'usuarios/recuperar_senha.html', {'form': form})

def redefinir_senha_view(request, token):
    """Redefinir senha usando token"""
    try:
        token_obj = TokenRecuperacaoSenha.objects.get(token=token)
        
        if not token_obj.esta_valido:
            messages.error(request, 'Token inválido ou expirado.')
            return redirect('usuarios:login')
        
        if request.method == 'POST':
            form = RedefinirSenhaForm(request.POST)
            if form.is_valid():
                nova_senha = form.cleaned_data['password1']
                user = token_obj.user
                user.set_password(nova_senha)
                user.save()
                
                # Marcar token como usado
                token_obj.marcar_como_usado()
                
                # Invalidar todas as sessões do usuário
                SessaoUsuario.objects.filter(user=user, ativa=True).update(ativa=False)
                
                messages.success(request, 'Senha redefinida com sucesso! Faça login com sua nova senha.')
                return redirect('usuarios:login')
        else:
            form = RedefinirSenhaForm()
        
        return render(request, 'usuarios/redefinir_senha.html', {'form': form, 'token': token})
        
    except TokenRecuperacaoSenha.DoesNotExist:
        messages.error(request, 'Token inválido.')
        return redirect('usuarios:login')

@login_required
def encerrar_sessao_view(request, sessao_id):
    """Encerrar uma sessão específica"""
    try:
        sessao = SessaoUsuario.objects.get(
            id=sessao_id,
            user=request.user,
            ativa=True
        )
        sessao.ativa = False
        sessao.save()
        
        messages.success(request, 'Sessão encerrada com sucesso!')
    except SessaoUsuario.DoesNotExist:
        messages.error(request, 'Sessão não encontrada.')
    
    return redirect('usuarios:perfil')

@login_required
def encerrar_todas_sessoes_view(request):
    """Encerrar todas as sessões do usuário exceto a atual"""
    sessao_atual = request.session.session_key
    
    SessaoUsuario.objects.filter(
        user=request.user,
        ativa=True
    ).exclude(session_key=sessao_atual).update(ativa=False)
    
    messages.success(request, 'Todas as outras sessões foram encerradas!')
    return redirect('usuarios:perfil')

@csrf_exempt
def check_session_status(request):
    """API para verificar status da sessão (AJAX)"""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'not_authenticated'})
    
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
            sessao.ativa = False
            sessao.save()
            return JsonResponse({'status': 'timeout'})
        
        # Atualizar última atividade
        sessao.data_ultima_atividade = timezone.now()
        sessao.save()
        
        return JsonResponse({'status': 'active'})
        
    except SessaoUsuario.DoesNotExist:
        return JsonResponse({'status': 'invalid_session'})
