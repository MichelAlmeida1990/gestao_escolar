from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Mensalidade, ConfiguracaoFinanceira, PlanoContas, CategoriaFinanceira
from alunos.models import Aluno
from turmas.models import Turma

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff"""
    
    def test_func(self):
        return self.request.user.is_staff

@login_required
def index(request):
    """Dashboard financeiro"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado. Apenas administradores podem acessar o módulo financeiro.')
        return redirect('home')
    
    # Estatísticas do mês atual
    hoje = timezone.now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Mensalidades do mês atual
    mensalidades_mes = Mensalidade.objects.filter(
        mes_referencia=mes_atual,
        ano_referencia=ano_atual
    )
    
    total_mensalidades = mensalidades_mes.count()
    total_pagas = mensalidades_mes.filter(status='pago').count()
    total_pendentes = mensalidades_mes.filter(status='pendente').count()
    total_vencidas = mensalidades_mes.filter(status='vencido').count()
    
    # Valores
    valor_total = mensalidades_mes.aggregate(total=Sum('valor_total'))['total'] or 0
    valor_recebido = mensalidades_mes.filter(status='pago').aggregate(total=Sum('valor_total'))['total'] or 0
    valor_pendente = mensalidades_mes.filter(status__in=['pendente', 'vencido']).aggregate(total=Sum('valor_total'))['total'] or 0
    
    # Mensalidades vencidas (últimos 30 dias)
    data_limite = hoje - timedelta(days=30)
    mensalidades_vencidas = Mensalidade.objects.filter(
        data_vencimento__gte=data_limite,
        data_vencimento__lt=hoje,
        status__in=['pendente', 'vencido']
    ).select_related('aluno', 'turma')[:10]
    
    context = {
        'mes_atual': mes_atual,
        'ano_atual': ano_atual,
        'total_mensalidades': total_mensalidades,
        'total_pagas': total_pagas,
        'total_pendentes': total_pendentes,
        'total_vencidas': total_vencidas,
        'valor_total': valor_total,
        'valor_recebido': valor_recebido,
        'valor_pendente': valor_pendente,
        'mensalidades_vencidas': mensalidades_vencidas,
        'taxa_pagamento': (total_pagas / total_mensalidades * 100) if total_mensalidades > 0 else 0,
    }
    
    return render(request, 'financeiro/index.html', context)

class MensalidadeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Mensalidade
    template_name = 'financeiro/mensalidade_list.html'
    context_object_name = 'mensalidades'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')
        mes = self.request.GET.get('mes', '')
        ano = self.request.GET.get('ano', '')
        
        if search:
            queryset = queryset.filter(aluno__nome__icontains=search)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if mes:
            queryset = queryset.filter(mes_referencia=mes)
        
        if ano:
            queryset = queryset.filter(ano_referencia=ano)
        
        return queryset.select_related('aluno', 'turma').order_by('-ano_referencia', '-mes_referencia', 'aluno__nome')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search': self.request.GET.get('search', ''),
            'status_selecionado': self.request.GET.get('status', ''),
            'mes_selecionado': self.request.GET.get('mes', ''),
            'ano_selecionado': self.request.GET.get('ano', ''),
            'status_choices': Mensalidade.STATUS_CHOICES,
            'meses': [(i, f'{i:02d}') for i in range(1, 13)],
            'anos': range(2020, 2030),
        })
        return context

@login_required
def gerar_mensalidades(request):
    """Gerar mensalidades para um mês/ano específico"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('financeiro:index')
    
    if request.method == 'POST':
        mes = int(request.POST.get('mes'))
        ano = int(request.POST.get('ano'))
        valor_base = float(request.POST.get('valor_base', 150.00))
        dia_vencimento = int(request.POST.get('dia_vencimento', 5))
        
        # Verificar se já existem mensalidades para este período
        mensalidades_existentes = Mensalidade.objects.filter(
            mes_referencia=mes,
            ano_referencia=ano
        ).count()
        
        if mensalidades_existentes > 0:
            messages.warning(request, f'Já existem {mensalidades_existentes} mensalidades para {mes:02d}/{ano}. Use a atualização para modificar.')
            return redirect('financeiro:mensalidade_list')
        
        # Data de vencimento
        try:
            data_vencimento = datetime(ano, mes, dia_vencimento).date()
        except ValueError:
            # Se o dia não existe no mês (ex: 31 de fevereiro), usar o último dia do mês
            if mes == 12:
                data_vencimento = datetime(ano + 1, 1, 1).date() - timedelta(days=1)
            else:
                data_vencimento = datetime(ano, mes + 1, 1).date() - timedelta(days=1)
        
        # Buscar todos os alunos ativos
        alunos = Aluno.objects.filter(ativo=True).select_related('turma_atual')
        
        mensalidades_criadas = 0
        for aluno in alunos:
            if aluno.turma_atual:
                mensalidade = Mensalidade.objects.create(
                    aluno=aluno,
                    turma=aluno.turma_atual,
                    mes_referencia=mes,
                    ano_referencia=ano,
                    valor_base=valor_base,
                    valor_total=valor_base,
                    data_vencimento=data_vencimento
                )
                mensalidades_criadas += 1
        
        messages.success(request, f'{mensalidades_criadas} mensalidades geradas para {mes:02d}/{ano}!')
        return redirect('financeiro:mensalidade_list')
    
    # GET request
    config = ConfiguracaoFinanceira.get_config()
    context = {
        'config': config,
        'meses': [(i, f'{i:02d}') for i in range(1, 13)],
        'anos': range(2020, 2030),
    }
    
    return render(request, 'financeiro/gerar_mensalidades.html', context)

@login_required
def pagar_mensalidade(request, mensalidade_id):
    """Marcar mensalidade como paga"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('financeiro:index')
    
    mensalidade = get_object_or_404(Mensalidade, id=mensalidade_id)
    
    if mensalidade.status == 'pago':
        messages.warning(request, 'Esta mensalidade já foi paga.')
        return redirect('financeiro:mensalidade_list')
    
    mensalidade.status = 'pago'
    mensalidade.data_pagamento = timezone.now()
    mensalidade.save()
    
    messages.success(request, f'Mensalidade de {mensalidade.aluno.nome} marcada como paga!')
    return redirect('financeiro:mensalidade_list')

@login_required
def relatorios(request):
    """Relatórios financeiros"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('financeiro:index')
    
    # Relatório do mês atual
    hoje = timezone.now().date()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Por ano
    dados_anuais = []
    for ano in range(ano_atual - 2, ano_atual + 1):
        mensalidades_ano = Mensalidade.objects.filter(ano_referencia=ano)
        valor_total = mensalidades_ano.aggregate(total=Sum('valor_total'))['total'] or 0
        valor_pago = mensalidades_ano.filter(status='pago').aggregate(total=Sum('valor_total'))['total'] or 0
        
        dados_anuais.append({
            'ano': ano,
            'valor_total': valor_total,
            'valor_pago': valor_pago,
            'percentual_pagamento': (valor_pago / valor_total * 100) if valor_total > 0 else 0
        })
    
    # Por mês (ano atual)
    dados_mensais = []
    for mes in range(1, 13):
        mensalidades_mes = Mensalidade.objects.filter(
            mes_referencia=mes,
            ano_referencia=ano_atual
        )
        valor_total = mensalidades_mes.aggregate(total=Sum('valor_total'))['total'] or 0
        valor_pago = mensalidades_mes.filter(status='pago').aggregate(total=Sum('valor_total'))['total'] or 0
        
        dados_mensais.append({
            'mes': mes,
            'valor_total': valor_total,
            'valor_pago': valor_pago,
            'percentual_pagamento': (valor_pago / valor_total * 100) if valor_total > 0 else 0
        })
    
    context = {
        'dados_anuais': dados_anuais,
        'dados_mensais': dados_mensais,
        'ano_atual': ano_atual,
    }
    
    return render(request, 'financeiro/relatorios.html', context)

@login_required
def configuracoes(request):
    """Configurações do sistema financeiro"""
    if not request.user.is_staff:
        messages.error(request, 'Acesso negado.')
        return redirect('financeiro:index')
    
    config = ConfiguracaoFinanceira.get_config()
    
    if request.method == 'POST':
        config.valor_padrao_mensalidade = float(request.POST.get('valor_padrao_mensalidade', 150.00))
        config.dia_vencimento_mensalidade = int(request.POST.get('dia_vencimento_mensalidade', 5))
        config.percentual_juros_mes = float(request.POST.get('percentual_juros_mes', 1.00))
        config.valor_multa_atraso = float(request.POST.get('valor_multa_atraso', 10.00))
        config.dias_carencia_juros = int(request.POST.get('dias_carencia_juros', 5))
        config.percentual_desconto_pontualidade = float(request.POST.get('percentual_desconto_pontualidade', 5.00))
        config.percentual_desconto_irmao = float(request.POST.get('percentual_desconto_irmao', 10.00))
        config.nome_escola = request.POST.get('nome_escola', 'Escola')
        config.cnpj_escola = request.POST.get('cnpj_escola', '')
        config.endereco_escola = request.POST.get('endereco_escola', '')
        
        config.save()
        
        messages.success(request, 'Configurações atualizadas com sucesso!')
        return redirect('financeiro:configuracoes')
    
    context = {
        'config': config,
    }
    
    return render(request, 'financeiro/configuracoes.html', context)
