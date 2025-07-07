from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.conf import settings
import json

from .models import MatriculaOnline, DocumentoMatricula, ConfiguracaoMatricula
from .forms import (
    MatriculaOnlineForm, DocumentoMatriculaForm, 
    ConsultaMatriculaForm, ConfiguracaoMatriculaForm
)

def index_matriculas(request):
    """Página inicial do sistema de matrículas"""
    try:
        config = ConfiguracaoMatricula.get_config()
        matricula_ativa = config.matricula_ativa
        periodo_valido = (
            timezone.now().date() >= config.data_inicio_matriculas and 
            timezone.now().date() <= config.data_fim_matriculas
        )
    except:
        matricula_ativa = True
        periodo_valido = True
    
    context = {
        'matricula_ativa': matricula_ativa,
        'periodo_valido': periodo_valido,
        'config': config if 'config' in locals() else None,
    }
    return render(request, 'matriculas/index.html', context)

def nova_matricula(request):
    """Formulário de nova matrícula online"""
    try:
        config = ConfiguracaoMatricula.get_config()
        if not config.matricula_ativa:
            messages.error(request, "As matrículas online estão temporariamente desativadas.")
            return redirect('matriculas:index')
        
        hoje = timezone.now().date()
        if hoje < config.data_inicio_matriculas or hoje > config.data_fim_matriculas:
            messages.error(
                request, 
                f"As matrículas estão abertas apenas entre {config.data_inicio_matriculas.strftime('%d/%m/%Y')} "
                f"e {config.data_fim_matriculas.strftime('%d/%m/%Y')}."
            )
            return redirect('matriculas:index')
    except:
        pass
    
    if request.method == 'POST':
        form = MatriculaOnlineForm(request.POST)
        if form.is_valid():
            matricula = form.save()
            
            # Enviar email de confirmação
            try:
                enviar_email_confirmacao(matricula)
                messages.success(
                    request, 
                    f"Matrícula realizada com sucesso! Código: {matricula.codigo_matricula}. "
                    "Verifique seu e-mail para mais informações."
                )
            except Exception as e:
                messages.warning(
                    request, 
                    f"Matrícula realizada com sucesso! Código: {matricula.codigo_matricula}. "
                    "Houve um problema ao enviar o e-mail de confirmação."
                )
            
            return redirect('matriculas:confirmacao', codigo=matricula.codigo_matricula)
    else:
        form = MatriculaOnlineForm()
    
    context = {
        'form': form,
        'config': config if 'config' in locals() else None,
    }
    return render(request, 'matriculas/nova_matricula.html', context)

def confirmacao_matricula(request, codigo):
    """Página de confirmação da matrícula"""
    matricula = get_object_or_404(MatriculaOnline, codigo_matricula=codigo)
    
    context = {
        'matricula': matricula,
    }
    return render(request, 'matriculas/confirmacao.html', context)

def consultar_matricula(request):
    """Consulta de status da matrícula"""
    if request.method == 'POST':
        form = ConsultaMatriculaForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo_matricula']
            email = form.cleaned_data['email']
            
            try:
                matricula = MatriculaOnline.objects.get(
                    codigo_matricula=codigo,
                    email=email
                )
                return redirect('matriculas:detalhes_matricula', codigo=codigo)
            except MatriculaOnline.DoesNotExist:
                messages.error(request, "Matrícula não encontrada. Verifique o código e e-mail informados.")
    else:
        form = ConsultaMatriculaForm()
    
    context = {
        'form': form,
    }
    return render(request, 'matriculas/consultar.html', context)

def detalhes_matricula(request, codigo):
    """Detalhes da matrícula para consulta pública"""
    matricula = get_object_or_404(MatriculaOnline, codigo_matricula=codigo)
    
    context = {
        'matricula': matricula,
    }
    return render(request, 'matriculas/detalhes_publica.html', context)

def upload_documentos(request, codigo):
    """Upload de documentos para a matrícula"""
    matricula = get_object_or_404(MatriculaOnline, codigo_matricula=codigo)
    
    if request.method == 'POST':
        form = DocumentoMatriculaForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.matricula = matricula
            documento.nome_arquivo = request.FILES['arquivo'].name
            documento.tamanho_arquivo = request.FILES['arquivo'].size
            documento.save()
            
            messages.success(request, "Documento enviado com sucesso!")
            return redirect('matriculas:detalhes_matricula', codigo=codigo)
    else:
        form = DocumentoMatriculaForm()
    
    context = {
        'form': form,
        'matricula': matricula,
    }
    return render(request, 'matriculas/upload_documentos.html', context)

# Views administrativas (requerem login)

class MatriculaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Lista de matrículas para administradores"""
    model = MatriculaOnline
    template_name = 'matriculas/matricula_list.html'
    context_object_name = 'matriculas'
    paginate_by = 20
    permission_required = 'matriculas.view_matriculaonline'
    
    def get_queryset(self):
        queryset = MatriculaOnline.objects.all()
        
        # Filtros
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Busca
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(nome_completo__icontains=q) |
                Q(codigo_matricula__icontains=q) |
                Q(cpf__icontains=q) |
                Q(email__icontains=q)
            )
        
        return queryset.order_by('-data_criacao')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = MatriculaOnline.STATUS_CHOICES
        context['total_pendentes'] = MatriculaOnline.objects.filter(status='pendente').count()
        context['total_aprovadas'] = MatriculaOnline.objects.filter(status='aprovada').count()
        context['total_rejeitadas'] = MatriculaOnline.objects.filter(status='rejeitada').count()
        return context

class MatriculaDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Detalhes da matrícula para administradores"""
    model = MatriculaOnline
    template_name = 'matriculas/matricula_detail.html'
    context_object_name = 'matricula'
    permission_required = 'matriculas.view_matriculaonline'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documentos'] = self.object.documentos.all()
        return context

@login_required
@permission_required('matriculas.change_matriculaonline')
def aprovar_matricula(request, pk):
    """Aprova uma matrícula"""
    matricula = get_object_or_404(MatriculaOnline, pk=pk)
    
    if request.method == 'POST':
        matricula.aprovar(request.user)
        
        # Enviar email de aprovação
        try:
            enviar_email_aprovacao(matricula)
            messages.success(request, "Matrícula aprovada com sucesso!")
        except Exception as e:
            messages.warning(request, "Matrícula aprovada, mas houve problema ao enviar e-mail.")
        
        return redirect('matriculas:matricula_detail', pk=pk)
    
    context = {
        'matricula': matricula,
    }
    return render(request, 'matriculas/aprovar_matricula.html', context)

@login_required
@permission_required('matriculas.change_matriculaonline')
def rejeitar_matricula(request, pk):
    """Rejeita uma matrícula"""
    matricula = get_object_or_404(MatriculaOnline, pk=pk)
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo_rejeicao')
        if motivo:
            matricula.rejeitar(motivo, request.user)
            
            # Enviar email de rejeição
            try:
                enviar_email_rejeicao(matricula, motivo)
                messages.success(request, "Matrícula rejeitada com sucesso!")
            except Exception as e:
                messages.warning(request, "Matrícula rejeitada, mas houve problema ao enviar e-mail.")
            
            return redirect('matriculas:matricula_detail', pk=pk)
        else:
            messages.error(request, "É necessário informar o motivo da rejeição.")
    
    context = {
        'matricula': matricula,
    }
    return render(request, 'matriculas/rejeitar_matricula.html', context)

class ConfiguracaoMatriculaView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Configurações do sistema de matrículas"""
    model = ConfiguracaoMatricula
    form_class = ConfiguracaoMatriculaForm
    template_name = 'matriculas/configuracao.html'
    permission_required = 'matriculas.change_configuracaomatricula'
    
    def get_object(self):
        return ConfiguracaoMatricula.get_config()
    
    def get_success_url(self):
        messages.success(self.request, "Configurações atualizadas com sucesso!")
        return reverse('matriculas:configuracao')

@login_required
@permission_required('matriculas.delete_documentomatricula')
def excluir_documento(request, pk):
    """Exclui um documento da matrícula"""
    documento = get_object_or_404(DocumentoMatricula, pk=pk)
    matricula = documento.matricula
    
    if request.method == 'POST':
        documento.delete()
        messages.success(request, "Documento excluído com sucesso!")
        return redirect('matriculas:matricula_detail', pk=matricula.pk)
    
    context = {
        'documento': documento,
        'matricula': matricula,
    }
    return render(request, 'matriculas/excluir_documento.html', context)

# Funções auxiliares para envio de emails

def enviar_email_confirmacao(matricula):
    """Envia email de confirmação da matrícula"""
    try:
        config = ConfiguracaoMatricula.get_config()
        if not config.email_confirmacao_ativa:
            return
        
        subject = f"Confirmação de Matrícula - {matricula.codigo_matricula}"
        
        context = {
            'matricula': matricula,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
        }
        
        html_message = render_to_string('matriculas/emails/confirmacao.html', context)
        plain_message = render_to_string('matriculas/emails/confirmacao.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[matricula.email, matricula.responsavel_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar email de confirmação: {e}")

def enviar_email_aprovacao(matricula):
    """Envia email de aprovação da matrícula"""
    try:
        config = ConfiguracaoMatricula.get_config()
        if not config.email_aprovacao_ativa:
            return
        
        subject = f"Matrícula Aprovada - {matricula.codigo_matricula}"
        
        context = {
            'matricula': matricula,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
        }
        
        html_message = render_to_string('matriculas/emails/aprovacao.html', context)
        plain_message = render_to_string('matriculas/emails/aprovacao.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[matricula.email, matricula.responsavel_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar email de aprovação: {e}")

def enviar_email_rejeicao(matricula, motivo):
    """Envia email de rejeição da matrícula"""
    try:
        config = ConfiguracaoMatricula.get_config()
        if not config.email_rejeicao_ativa:
            return
        
        subject = f"Matrícula Rejeitada - {matricula.codigo_matricula}"
        
        context = {
            'matricula': matricula,
            'motivo': motivo,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
        }
        
        html_message = render_to_string('matriculas/emails/rejeicao.html', context)
        plain_message = render_to_string('matriculas/emails/rejeicao.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[matricula.email, matricula.responsavel_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar email de rejeição: {e}")

# API endpoints

def api_matriculas_pendentes(request):
    """API para obter número de matrículas pendentes"""
    if request.user.is_authenticated and request.user.has_perm('matriculas.view_matriculaonline'):
        count = MatriculaOnline.objects.filter(status='pendente').count()
        return JsonResponse({'count': count})
    return JsonResponse({'error': 'Unauthorized'}, status=403)

def api_estatisticas_matriculas(request):
    """API para obter estatísticas de matrículas"""
    if request.user.is_authenticated and request.user.has_perm('matriculas.view_matriculaonline'):
        stats = {
            'total': MatriculaOnline.objects.count(),
            'pendentes': MatriculaOnline.objects.filter(status='pendente').count(),
            'aprovadas': MatriculaOnline.objects.filter(status='aprovada').count(),
            'rejeitadas': MatriculaOnline.objects.filter(status='rejeitada').count(),
            'canceladas': MatriculaOnline.objects.filter(status='cancelada').count(),
            'concluidas': MatriculaOnline.objects.filter(status='concluida').count(),
        }
        return JsonResponse(stats)
    return JsonResponse({'error': 'Unauthorized'}, status=403)
