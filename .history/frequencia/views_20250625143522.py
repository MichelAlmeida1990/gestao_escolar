from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import RegistroFrequencia, RelatorioFrequencia, JustificativaFalta
from alunos.models import Aluno
from turmas.models import Turma, TurmaAluno
from professores.models import Professor
from notas.models import Disciplina

class StaffOrProfessorMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff ou professor"""
    
    def test_func(self):
        return self.request.user.is_staff or hasattr(self.request.user, 'professor')

@login_required
def index(request):
    """View para a página inicial do módulo de frequência"""
    total_registros_hoje = RegistroFrequencia.objects.filter(data=timezone.now().date()).count()
    total_presentes_hoje = RegistroFrequencia.objects.filter(data=timezone.now().date(), status='presente').count()
    total_ausentes_hoje = RegistroFrequencia.objects.filter(data=timezone.now().date(), status='ausente').count()
    
    # Calcular taxa de presença
    if total_registros_hoje > 0:
        taxa_presenca = round((total_presentes_hoje / total_registros_hoje) * 100, 1)
    else:
        taxa_presenca = 0
    
    context = {
        'titulo': 'Sistema de Frequência',
        'total_registros_hoje': total_registros_hoje,
        'total_presentes_hoje': total_presentes_hoje,
        'total_ausentes_hoje': total_ausentes_hoje,
        'taxa_presenca': taxa_presenca,
        'turmas': Turma.objects.all()[:5],
    }
    return render(request, 'frequencia/index.html', context)

class RegistroFrequenciaListView(LoginRequiredMixin, StaffOrProfessorMixin, ListView):
    model = RegistroFrequencia
    template_name = 'frequencia/registro_list.html'
    context_object_name = 'registros'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        turma_id = self.request.GET.get('turma', '')
        data = self.request.GET.get('data', '')
        status = self.request.GET.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(aluno__nome__icontains=search) |
                Q(disciplina__nome__icontains=search) |
                Q(professor__nome__icontains=search)
            )
        
        if turma_id:
            queryset = queryset.filter(turma_id=turma_id)
        
        if data:
            queryset = queryset.filter(data=data)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('aluno', 'turma', 'disciplina', 'professor')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'turmas': Turma.objects.all(),
            'search': self.request.GET.get('search', ''),
            'turma_selecionada': self.request.GET.get('turma', ''),
            'data_selecionada': self.request.GET.get('data', ''),
            'status_selecionado': self.request.GET.get('status', ''),
            'status_choices': RegistroFrequencia.STATUS_CHOICES,
        })
        return context

@login_required
def registrar_frequencia(request):
    """View para registrar frequência de uma turma"""
    if request.method == 'POST':
        turma_id = request.POST.get('turma_id')
        disciplina_id = request.POST.get('disciplina_id')
        data = request.POST.get('data')
        
        if not all([turma_id, disciplina_id, data]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('frequencia:registrar_frequencia')
        
        turma = get_object_or_404(Turma, id=turma_id)
        disciplina = get_object_or_404(Disciplina, id=disciplina_id)
        professor = disciplina.professor
        
        # Processar registros de frequência
        for aluno in turma.alunos.all():
            status = request.POST.get(f'status_{aluno.id}', 'presente')
            observacoes = request.POST.get(f'obs_{aluno.id}', '')
            
            registro, created = RegistroFrequencia.objects.get_or_create(
                aluno=aluno,
                turma=turma,
                disciplina=disciplina,
                professor=professor,
                data=data,
                defaults={
                    'status': status,
                    'observacoes': observacoes
                }
            )
            
            if not created:
                registro.status = status
                registro.observacoes = observacoes
                registro.save()
        
        messages.success(request, f'Frequência registrada com sucesso para a turma {turma.nome}!')
        return redirect('frequencia:registro_list')
    
    # GET request
    turma_id = request.GET.get('turma')
    disciplina_id = request.GET.get('disciplina')
    data = request.GET.get('data', timezone.now().date())
    
    context = {
        'turmas': Turma.objects.all(),
        'disciplinas': Disciplina.objects.all(),
        'turma_selecionada': turma_id,
        'disciplina_selecionada': disciplina_id,
        'data_selecionada': data,
    }
    
    if turma_id and disciplina_id:
        turma = get_object_or_404(Turma, id=turma_id)
        disciplina = get_object_or_404(Disciplina, id=disciplina_id)
        
        # Buscar registros existentes para a data
        registros_existentes = RegistroFrequencia.objects.filter(
            turma=turma,
            disciplina=disciplina,
            data=data
        ).select_related('aluno')
        
        # Criar dicionário para facilitar lookup
        registros_dict = {reg.aluno.id: reg for reg in registros_existentes}
        
        # Preparar dados dos alunos
        alunos_data = []
        for aluno in turma.alunos.all():
            registro_existente = registros_dict.get(aluno.id)
            alunos_data.append({
                'aluno': aluno,
                'status': registro_existente.status if registro_existente else 'presente',
                'observacoes': registro_existente.observacoes if registro_existente else '',
            })
        
        context.update({
            'turma': turma,
            'disciplina': disciplina,
            'alunos_data': alunos_data,
            'status_choices': RegistroFrequencia.STATUS_CHOICES,
        })
    
    return render(request, 'frequencia/registrar_frequencia.html', context)

@login_required
def relatorio_frequencia(request):
    """View para gerar relatórios de frequência"""
    if request.method == 'POST':
        turma_id = request.POST.get('turma_id')
        disciplina_id = request.POST.get('disciplina_id')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        periodo = request.POST.get('periodo', 'mensal')
        
        if not all([turma_id, data_inicio, data_fim]):
            messages.error(request, 'Turma, data de início e fim são obrigatórios.')
            return redirect('frequencia:relatorio_frequencia')
        
        turma = get_object_or_404(Turma, id=turma_id)
        disciplina = None
        if disciplina_id:
            disciplina = get_object_or_404(Disciplina, id=disciplina_id)
        
        # Filtrar registros
        registros = RegistroFrequencia.objects.filter(
            turma=turma,
            data__range=[data_inicio, data_fim]
        )
        
        if disciplina:
            registros = registros.filter(disciplina=disciplina)
        
        # Calcular estatísticas
        total_registros = registros.count()
        total_presencas = registros.filter(status='presente').count()
        total_faltas = registros.filter(status='ausente').count()
        total_atrasados = registros.filter(status='atrasado').count()
        total_justificados = registros.filter(status='justificado').count()
        
        percentual_presenca = (total_presencas / total_registros * 100) if total_registros > 0 else 0
        
        # Estatísticas por aluno
        alunos_stats = {}
        for aluno in turma.alunos.all():
            registros_aluno = registros.filter(aluno=aluno)
            presencas = registros_aluno.filter(status='presente').count()
            faltas = registros_aluno.filter(status='ausente').count()
            total_aluno = registros_aluno.count()
            
            alunos_stats[aluno.id] = {
                'aluno': aluno,
                'presencas': presencas,
                'faltas': faltas,
                'total': total_aluno,
                'percentual': (presencas / total_aluno * 100) if total_aluno > 0 else 0
            }
        
        context = {
            'turma': turma,
            'disciplina': disciplina,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'periodo': periodo,
            'total_registros': total_registros,
            'total_presencas': total_presencas,
            'total_faltas': total_faltas,
            'total_atrasados': total_atrasados,
            'total_justificados': total_justificados,
            'percentual_presenca': round(percentual_presenca, 2),
            'alunos_stats': alunos_stats.values(),
            'registros': registros.select_related('aluno', 'disciplina').order_by('data', 'aluno__nome'),
        }
        
        return render(request, 'frequencia/relatorio_resultado.html', context)
    
    # GET request
    context = {
        'turmas': Turma.objects.all(),
        'disciplinas': Disciplina.objects.all(),
        'periodo_choices': RelatorioFrequencia.PERIODO_CHOICES,
    }
    
    return render(request, 'frequencia/relatorio_frequencia.html', context)

@login_required
def justificar_falta(request, registro_id):
    """View para justificar uma falta"""
    registro = get_object_or_404(RegistroFrequencia, id=registro_id, status='ausente')
    
    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        documento = request.FILES.get('documento')
        
        if not motivo:
            messages.error(request, 'O motivo da justificativa é obrigatório.')
            return redirect('frequencia:justificar_falta', registro_id=registro_id)
        
        justificativa, created = JustificativaFalta.objects.get_or_create(
            registro_frequencia=registro,
            defaults={
                'motivo': motivo,
                'documento': documento
            }
        )
        
        if not created:
            justificativa.motivo = motivo
            if documento:
                justificativa.documento = documento
            justificativa.save()
        
        messages.success(request, 'Justificativa enviada com sucesso! Aguarde a aprovação.')
        return redirect('frequencia:registro_list')
    
    context = {
        'registro': registro,
    }
    
    return render(request, 'frequencia/justificar_falta.html', context)

@login_required
def aprovar_justificativa(request, justificativa_id):
    """View para aprovar/reprovar justificativa"""
    if not request.user.is_staff:
        messages.error(request, 'Apenas administradores podem aprovar justificativas.')
        return redirect('frequencia:registro_list')
    
    justificativa = get_object_or_404(JustificativaFalta, id=justificativa_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'aprovar':
            justificativa.aprovado = True
            justificativa.data_aprovacao = timezone.now()
            # Atualizar o status do registro para justificado
            justificativa.registro_frequencia.status = 'justificado'
            justificativa.registro_frequencia.save()
            messages.success(request, 'Justificativa aprovada com sucesso!')
        
        elif acao == 'reprovar':
            justificativa.aprovado = False
            justificativa.data_aprovacao = timezone.now()
            messages.success(request, 'Justificativa reprovada.')
        
        justificativa.save()
        return redirect('frequencia:justificativas_pendentes')
    
    context = {
        'justificativa': justificativa,
    }
    
    return render(request, 'frequencia/aprovar_justificativa.html', context)

@login_required
def justificativas_pendentes(request):
    """View para listar justificativas pendentes"""
    if not request.user.is_staff:
        messages.error(request, 'Apenas administradores podem acessar esta página.')
        return redirect('frequencia:index')
    
    justificativas = JustificativaFalta.objects.filter(
        data_aprovacao__isnull=True
    ).select_related('registro_frequencia__aluno', 'registro_frequencia__turma', 'registro_frequencia__disciplina')
    
    context = {
        'justificativas': justificativas,
    }
    
    return render(request, 'frequencia/justificativas_pendentes.html', context)

@login_required
def get_disciplinas_turma(request):
    """API para buscar disciplinas de uma turma"""
    turma_id = request.GET.get('turma_id')
    
    if not turma_id:
        return JsonResponse({'disciplinas': []})
    
    try:
        turma = Turma.objects.get(id=turma_id)
        # Assumindo que há uma relação entre turma e disciplinas
        # Se não houver, retorne todas as disciplinas
        disciplinas = Disciplina.objects.all().values('id', 'nome')
        
        return JsonResponse({
            'disciplinas': list(disciplinas)
        })
    except Turma.DoesNotExist:
        return JsonResponse({'disciplinas': []})

@login_required
def dashboard_frequencia(request):
    """Dashboard com estatísticas de frequência"""
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Estatísticas gerais
    stats = {
        'registros_hoje': RegistroFrequencia.objects.filter(data=hoje).count(),
        'presencas_hoje': RegistroFrequencia.objects.filter(data=hoje, status='presente').count(),
        'faltas_hoje': RegistroFrequencia.objects.filter(data=hoje, status='ausente').count(),
        'registros_mes': RegistroFrequencia.objects.filter(data__gte=inicio_mes).count(),
        'justificativas_pendentes': JustificativaFalta.objects.filter(data_aprovacao__isnull=True).count(),
    }
    
    # Frequência por turma (últimos 7 dias)
    sete_dias_atras = hoje - timedelta(days=7)
    frequencia_turmas = []
    
    for turma in Turma.objects.all():
        registros = RegistroFrequencia.objects.filter(
            turma=turma,
            data__gte=sete_dias_atras
        )
        total = registros.count()
        presencas = registros.filter(status='presente').count()
        percentual = (presencas / total * 100) if total > 0 else 0
        
        frequencia_turmas.append({
            'turma': turma.nome,
            'total': total,
            'presencas': presencas,
            'percentual': round(percentual, 2)
        })
    
    context = {
        'stats': stats,
        'frequencia_turmas': frequencia_turmas,
        'data_atual': hoje,
    }
    
    return render(request, 'frequencia/dashboard.html', context)