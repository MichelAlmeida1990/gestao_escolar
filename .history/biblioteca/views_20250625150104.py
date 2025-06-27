from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Livro, Autor, Categoria, Editora, Emprestimo, Reserva, 
    ConfiguracaoBiblioteca
)
from alunos.models import Aluno
from professores.models import Professor

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff"""
    
    def test_func(self):
        return self.request.user.is_staff

@login_required
def index(request):
    """View para a página inicial da biblioteca"""
    config = ConfiguracaoBiblioteca.get_config()
    
    # Estatísticas
    total_livros = Livro.objects.count()
    livros_disponiveis = Livro.objects.filter(status='disponivel').count()
    emprestimos_ativos = Emprestimo.objects.filter(status='ativo').count()
    emprestimos_atrasados = Emprestimo.objects.filter(
        status='ativo', 
        data_prevista_devolucao__lt=timezone.now().date()
    ).count()
    
    # Livros mais emprestados
    livros_populares = Livro.objects.annotate(
        total_emprestimos=Count('emprestimo')
    ).order_by('-total_emprestimos')[:5]
    
    # Empréstimos recentes
    emprestimos_recentes = Emprestimo.objects.select_related(
        'livro', 'aluno', 'professor'
    ).order_by('-data_emprestimo')[:10]
    
    context = {
        'config': config,
        'total_livros': total_livros,
        'livros_disponiveis': livros_disponiveis,
        'emprestimos_ativos': emprestimos_ativos,
        'emprestimos_atrasados': emprestimos_atrasados,
        'livros_populares': livros_populares,
        'emprestimos_recentes': emprestimos_recentes,
    }
    
    return render(request, 'biblioteca/index.html', context)

# =============== VIEWS DE AUTORES ===============

class AutorListView(LoginRequiredMixin, ListView):
    model = Autor
    template_name = 'biblioteca/autor_list.html'
    context_object_name = 'autores'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(nacionalidade__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class AutorCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Autor
    template_name = 'biblioteca/autor_form.html'
    fields = ['nome', 'nacionalidade', 'data_nascimento', 'biografia', 'foto']
    success_url = reverse_lazy('biblioteca:autor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Autor cadastrado com sucesso!')
        return super().form_valid(form)

class AutorUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Autor
    template_name = 'biblioteca/autor_form.html'
    fields = ['nome', 'nacionalidade', 'data_nascimento', 'biografia', 'foto']
    success_url = reverse_lazy('biblioteca:autor_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Autor atualizado com sucesso!')
        return super().form_valid(form)

# =============== VIEWS DE CATEGORIAS ===============

class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'biblioteca/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class CategoriaCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Categoria
    template_name = 'biblioteca/categoria_form.html'
    fields = ['nome', 'descricao', 'cor']
    success_url = reverse_lazy('biblioteca:categoria_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoria cadastrada com sucesso!')
        return super().form_valid(form)

class CategoriaUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Categoria
    template_name = 'biblioteca/categoria_form.html'
    fields = ['nome', 'descricao', 'cor']
    success_url = reverse_lazy('biblioteca:categoria_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Categoria atualizada com sucesso!')
        return super().form_valid(form)

# =============== VIEWS DE LIVROS ===============

class LivroListView(LoginRequiredMixin, ListView):
    model = Livro
    template_name = 'biblioteca/livro_list.html'
    context_object_name = 'livros'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        categoria_id = self.request.GET.get('categoria', '')
        status = self.request.GET.get('status', '')
        tipo = self.request.GET.get('tipo', '')
        
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(autores__nome__icontains=search) |
                Q(isbn__icontains=search) |
                Q(codigo_barras__icontains=search)
            ).distinct()
        
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.select_related('categoria', 'editora').prefetch_related('autores')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categorias': Categoria.objects.all(),
            'search': self.request.GET.get('search', ''),
            'categoria_selecionada': self.request.GET.get('categoria', ''),
            'status_selecionado': self.request.GET.get('status', ''),
            'tipo_selecionado': self.request.GET.get('tipo', ''),
            'status_choices': Livro.STATUS_CHOICES,
            'tipo_choices': Livro.TIPO_CHOICES,
        })
        return context

class LivroDetailView(LoginRequiredMixin, DetailView):
    model = Livro
    template_name = 'biblioteca/livro_detail.html'
    context_object_name = 'livro'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        livro = self.get_object()
        
        # Histórico de empréstimos
        emprestimos = Emprestimo.objects.filter(livro=livro).select_related(
            'aluno', 'professor'
        ).order_by('-data_emprestimo')[:10]
        
        # Reservas ativas
        reservas_ativas = Reserva.objects.filter(
            livro=livro, status='ativa'
        ).select_related('aluno', 'professor')
        
        context.update({
            'emprestimos': emprestimos,
            'reservas_ativas': reservas_ativas,
            'pode_emprestar': livro.esta_disponivel,
        })
        return context

class LivroCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Livro
    template_name = 'biblioteca/livro_form.html'
    fields = [
        'titulo', 'subtitulo', 'isbn', 'codigo_barras', 'categoria', 
        'autores', 'editora', 'ano_publicacao', 'edicao', 'idioma', 
        'paginas', 'tipo', 'status', 'localizacao', 'exemplares_total', 
        'exemplares_disponiveis', 'valor_livro', 'sinopse', 'observacoes', 'capa'
    ]
    success_url = reverse_lazy('biblioteca:livro_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Livro cadastrado com sucesso!')
        return super().form_valid(form)

class LivroUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Livro
    template_name = 'biblioteca/livro_form.html'
    fields = [
        'titulo', 'subtitulo', 'isbn', 'codigo_barras', 'categoria', 
        'autores', 'editora', 'ano_publicacao', 'edicao', 'idioma', 
        'paginas', 'tipo', 'status', 'localizacao', 'exemplares_total', 
        'exemplares_disponiveis', 'valor_livro', 'sinopse', 'observacoes', 'capa'
    ]
    success_url = reverse_lazy('biblioteca:livro_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Livro atualizado com sucesso!')
        return super().form_valid(form)

# =============== VIEWS DE EMPRÉSTIMOS ===============

@login_required
def realizar_emprestimo(request):
    """View para realizar empréstimo"""
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        tipo_usuario = request.POST.get('tipo_usuario')
        usuario_id = request.POST.get('usuario_id')
        observacoes = request.POST.get('observacoes', '')
        
        if not all([livro_id, tipo_usuario, usuario_id]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('biblioteca:realizar_emprestimo')
        
        livro = get_object_or_404(Livro, id=livro_id)
        config = ConfiguracaoBiblioteca.get_config()
        
        # Verificar disponibilidade
        if not livro.esta_disponivel:
            messages.error(request, 'Livro não está disponível para empréstimo.')
            return redirect('biblioteca:realizar_emprestimo')
        
        # Preparar dados do empréstimo
        emprestimo_data = {
            'livro': livro,
            'tipo_usuario': tipo_usuario,
            'observacoes': observacoes,
        }
        
        # Definir usuário e data de devolução
        if tipo_usuario == 'aluno':
            aluno = get_object_or_404(Aluno, id=usuario_id)
            emprestimo_data['aluno'] = aluno
            dias_emprestimo = config.dias_emprestimo_aluno
        else:
            professor = get_object_or_404(Professor, id=usuario_id)
            emprestimo_data['professor'] = professor
            dias_emprestimo = config.dias_emprestimo_professor
        
        emprestimo_data['data_prevista_devolucao'] = (
            timezone.now().date() + timedelta(days=dias_emprestimo)
        )
        
        # Criar empréstimo
        emprestimo = Emprestimo.objects.create(**emprestimo_data)
        
        # Atualizar estoque do livro
        livro.exemplares_disponiveis -= 1
        if livro.exemplares_disponiveis == 0:
            livro.status = 'emprestado'
        livro.save()
        
        messages.success(
            request, 
            f'Empréstimo realizado com sucesso! Devolução prevista para {emprestimo.data_prevista_devolucao.strftime("%d/%m/%Y")}'
        )
        return redirect('biblioteca:emprestimo_detail', pk=emprestimo.pk)
    
    # GET request
    livro_id = request.GET.get('livro')
    context = {
        'livros': Livro.objects.filter(status='disponivel'),
        'alunos': Aluno.objects.all().order_by('nome'),
        'professores': Professor.objects.all().order_by('nome'),
        'livro_selecionado': livro_id,
    }
    
    return render(request, 'biblioteca/realizar_emprestimo.html', context)

class EmprestimoListView(LoginRequiredMixin, ListView):
    model = Emprestimo
    template_name = 'biblioteca/emprestimo_list.html'
    context_object_name = 'emprestimos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')
        usuario_tipo = self.request.GET.get('usuario_tipo', '')
        
        if search:
            queryset = queryset.filter(
                Q(livro__titulo__icontains=search) |
                Q(aluno__nome__icontains=search) |
                Q(professor__nome__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if usuario_tipo:
            queryset = queryset.filter(tipo_usuario=usuario_tipo)
        
        # Atualizar status de empréstimos atrasados
        emprestimos_atrasados = queryset.filter(
            status='ativo',
            data_prevista_devolucao__lt=timezone.now().date()
        )
        emprestimos_atrasados.update(status='atrasado')
        
        return queryset.select_related('livro', 'aluno', 'professor').order_by('-data_emprestimo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search': self.request.GET.get('search', ''),
            'status_selecionado': self.request.GET.get('status', ''),
            'usuario_tipo_selecionado': self.request.GET.get('usuario_tipo', ''),
            'status_choices': Emprestimo.STATUS_CHOICES,
            'usuario_tipo_choices': Emprestimo.TIPO_USUARIO_CHOICES,
        })
        return context

class EmprestimoDetailView(LoginRequiredMixin, DetailView):
    model = Emprestimo
    template_name = 'biblioteca/emprestimo_detail.html'
    context_object_name = 'emprestimo'

@login_required
def devolver_livro(request, emprestimo_id):
    """View para devolver livro"""
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    
    if emprestimo.status == 'devolvido':
        messages.warning(request, 'Este livro já foi devolvido.')
        return redirect('biblioteca:emprestimo_detail', pk=emprestimo.pk)
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        
        # Marcar como devolvido
        emprestimo.status = 'devolvido'
        emprestimo.data_devolucao = timezone.now()
        emprestimo.observacoes = f"{emprestimo.observacoes}\n\nDevolução: {observacoes}".strip()
        
        # Calcular multa se atrasado
        if emprestimo.esta_atrasado:
            config = ConfiguracaoBiblioteca.get_config()
            emprestimo.valor_multa = emprestimo.calcular_multa(config.valor_multa_dia)
        
        emprestimo.save()
        
        # Atualizar estoque do livro
        livro = emprestimo.livro
        livro.exemplares_disponiveis += 1
        if livro.status == 'emprestado' and livro.exemplares_disponiveis > 0:
            livro.status = 'disponivel'
        livro.save()
        
        # Verificar se há reservas para este livro
        reserva_ativa = Reserva.objects.filter(
            livro=livro, status='ativa'
        ).order_by('data_reserva').first()
        
        if reserva_ativa:
            messages.info(
                request, 
                f'Livro devolvido! Há uma reserva ativa para {reserva_ativa.nome_usuario}.'
            )
        else:
            messages.success(request, 'Livro devolvido com sucesso!')
        
        return redirect('biblioteca:emprestimo_detail', pk=emprestimo.pk)
    
    context = {
        'emprestimo': emprestimo,
    }
    
    return render(request, 'biblioteca/devolver_livro.html', context)

@login_required
def renovar_emprestimo(request, emprestimo_id):
    """View para renovar empréstimo"""
    emprestimo = get_object_or_404(Emprestimo, id=emprestimo_id)
    config = ConfiguracaoBiblioteca.get_config()
    
    if not emprestimo.pode_renovar(config.max_renovacoes):
        messages.error(request, 'Este empréstimo não pode ser renovado.')
        return redirect('biblioteca:emprestimo_detail', pk=emprestimo.pk)
    
    # Verificar se há reservas para este livro
    reserva_ativa = Reserva.objects.filter(
        livro=emprestimo.livro, status='ativa'
    ).exists()
    
    if reserva_ativa:
        messages.error(request, 'Não é possível renovar: há reservas ativas para este livro.')
        return redirect('biblioteca:emprestimo_detail', pk=emprestimo.pk)
    
    # Renovar
    if emprestimo.tipo_usuario == 'aluno':
        dias_adicional = config.dias_emprestimo_aluno
    else:
        dias_adicional = config.dias_emprestimo_professor
    
    emprestimo.data_prevista_devolucao += timedelta(days=dias_adicional)
    emprestimo.renovacoes += 1
    emprestimo.status = 'renovado'
    emprestimo.save()
    
    messages.success(
        request, 
        f'Empréstimo renovado! Nova data de devolução: {emprestimo.data_prevista_devolucao.strftime("%d/%m/%Y")}'
    )
    
    return redirect('biblioteca:emprestimo_detail', pk=emprestimo.pk)

# =============== VIEWS DE RESERVAS ===============

@login_required
def realizar_reserva(request):
    """View para realizar reserva"""
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        tipo_usuario = request.POST.get('tipo_usuario')
        usuario_id = request.POST.get('usuario_id')
        observacoes = request.POST.get('observacoes', '')
        
        if not all([livro_id, tipo_usuario, usuario_id]):
            messages.error(request, 'Todos os campos são obrigatórios.')
            return redirect('biblioteca:realizar_reserva')
        
        livro = get_object_or_404(Livro, id=livro_id)
        
        # Verificar se livro está disponível
        if livro.esta_disponivel:
            messages.info(request, 'Este livro está disponível para empréstimo direto.')
            return redirect('biblioteca:realizar_emprestimo', livro=livro.id)
        
        # Preparar dados da reserva
        reserva_data = {
            'livro': livro,
            'tipo_usuario': tipo_usuario,
            'observacoes': observacoes,
        }
        
        # Definir usuário
        if tipo_usuario == 'aluno':
            aluno = get_object_or_404(Aluno, id=usuario_id)
            reserva_data['aluno'] = aluno
            
            # Verificar se já tem reserva ativa para este livro
            if Reserva.objects.filter(livro=livro, aluno=aluno, status='ativa').exists():
                messages.error(request, 'Você já tem uma reserva ativa para este livro.')
                return redirect('biblioteca:realizar_reserva')
        else:
            professor = get_object_or_404(Professor, id=usuario_id)
            reserva_data['professor'] = professor
            
            # Verificar se já tem reserva ativa para este livro
            if Reserva.objects.filter(livro=livro, professor=professor, status='ativa').exists():
                messages.error(request, 'Você já tem uma reserva ativa para este livro.')
                return redirect('biblioteca:realizar_reserva')
        
        # Criar reserva
        reserva = Reserva.objects.create(**reserva_data)
        
        messages.success(
            request, 
            f'Reserva realizada com sucesso! Você será notificado quando o livro estiver disponível.'
        )
        return redirect('biblioteca:reserva_list')
    
    # GET request
    livro_id = request.GET.get('livro')
    context = {
        'livros': Livro.objects.exclude(status='disponivel'),
        'alunos': Aluno.objects.all().order_by('nome'),
        'professores': Professor.objects.all().order_by('nome'),
        'livro_selecionado': livro_id,
    }
    
    return render(request, 'biblioteca/realizar_reserva.html', context)

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'biblioteca/reserva_list.html'
    context_object_name = 'reservas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        status = self.request.GET.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(livro__titulo__icontains=search) |
                Q(aluno__nome__icontains=search) |
                Q(professor__nome__icontains=search)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        # Atualizar reservas expiradas
        reservas_expiradas = queryset.filter(
            status='ativa',
            data_expiracao__lt=timezone.now()
        )
        reservas_expiradas.update(status='expirada')
        
        return queryset.select_related('livro', 'aluno', 'professor').order_by('-data_reserva')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'search': self.request.GET.get('search', ''),
            'status_selecionado': self.request.GET.get('status', ''),
            'status_choices': Reserva.STATUS_CHOICES,
        })
        return context

@login_required
def cancelar_reserva(request, reserva_id):
    """View para cancelar reserva"""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.status != 'ativa':
        messages.warning(request, 'Esta reserva não pode ser cancelada.')
        return redirect('biblioteca:reserva_list')
    
    reserva.status = 'cancelada'
    reserva.save()
    
    messages.success(request, 'Reserva cancelada com sucesso!')
    return redirect('biblioteca:reserva_list')

# =============== VIEWS DE RELATÓRIOS ===============

@login_required
def relatorios(request):
    """View para relatórios da biblioteca"""
    # Estatísticas gerais
    total_livros = Livro.objects.count()
    total_emprestimos = Emprestimo.objects.count()
    emprestimos_ativos = Emprestimo.objects.filter(status='ativo').count()
    emprestimos_atrasados = Emprestimo.objects.filter(status='atrasado').count()
    
    # Livros mais emprestados
    livros_populares = Livro.objects.annotate(
        total_emprestimos=Count('emprestimo')
    ).order_by('-total_emprestimos')[:10]
    
    # Usuários que mais emprestam
    usuarios_ativos = []
    
    # Alunos
    alunos_ativos = Aluno.objects.annotate(
        total_emprestimos=Count('emprestimo')
    ).filter(total_emprestimos__gt=0).order_by('-total_emprestimos')[:5]
    
    for aluno in alunos_ativos:
        usuarios_ativos.append({
            'nome': aluno.nome,
            'tipo': 'Aluno',
            'total_emprestimos': aluno.total_emprestimos
        })
    
    # Professores
    professores_ativos = Professor.objects.annotate(
        total_emprestimos=Count('emprestimo')
    ).filter(total_emprestimos__gt=0).order_by('-total_emprestimos')[:5]
    
    for professor in professores_ativos:
        usuarios_ativos.append({
            'nome': professor.nome,
            'tipo': 'Professor',
            'total_emprestimos': professor.total_emprestimos
        })
    
    usuarios_ativos.sort(key=lambda x: x['total_emprestimos'], reverse=True)
    usuarios_ativos = usuarios_ativos[:10]
    
    context = {
        'total_livros': total_livros,
        'total_emprestimos': total_emprestimos,
        'emprestimos_ativos': emprestimos_ativos,
        'emprestimos_atrasados': emprestimos_atrasados,
        'livros_populares': livros_populares,
        'usuarios_ativos': usuarios_ativos,
    }
    
    return render(request, 'biblioteca/relatorios.html', context)

# =============== VIEWS DE CONFIGURAÇÃO ===============

@login_required
def configuracoes(request):
    """View para configurações da biblioteca"""
    if not request.user.is_staff:
        messages.error(request, 'Apenas administradores podem acessar as configurações.')
        return redirect('biblioteca:index')
    
    config = ConfiguracaoBiblioteca.get_config()
    
    if request.method == 'POST':
        # Atualizar configurações
        config.dias_emprestimo_aluno = int(request.POST.get('dias_emprestimo_aluno', 7))
        config.dias_emprestimo_professor = int(request.POST.get('dias_emprestimo_professor', 14))
        config.max_renovacoes = int(request.POST.get('max_renovacoes', 2))
        config.max_livros_aluno = int(request.POST.get('max_livros_aluno', 3))
        config.max_livros_professor = int(request.POST.get('max_livros_professor', 5))
        config.valor_multa_dia = float(request.POST.get('valor_multa_dia', 1.00))
        config.dias_reserva = int(request.POST.get('dias_reserva', 3))
        config.nome_biblioteca = request.POST.get('nome_biblioteca', 'Biblioteca Escolar')
        config.endereco = request.POST.get('endereco', '')
        config.horario_funcionamento = request.POST.get('horario_funcionamento', '')
        config.telefone = request.POST.get('telefone', '')
        config.email = request.POST.get('email', '')
        
        config.save()
        
        messages.success(request, 'Configurações atualizadas com sucesso!')
        return redirect('biblioteca:configuracoes')
    
    context = {
        'config': config,
    }
    
    return render(request, 'biblioteca/configuracoes.html', context)

# =============== APIs ===============

@login_required
def api_buscar_livros(request):
    """API para buscar livros via AJAX"""
    search = request.GET.get('search', '')
    
    if len(search) < 3:
        return JsonResponse({'livros': []})
    
    livros = Livro.objects.filter(
        Q(titulo__icontains=search) |
        Q(codigo_barras__icontains=search) |
        Q(isbn__icontains=search)
    ).values('id', 'titulo', 'codigo_barras', 'status', 'exemplares_disponiveis')[:10]
    
    return JsonResponse({'livros': list(livros)})

@login_required
def api_buscar_usuarios(request):
    """API para buscar usuários (alunos e professores) via AJAX"""
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    
    if len(search) < 2:
        return JsonResponse({'usuarios': []})
    
    usuarios = []
    
    if tipo == 'aluno' or not tipo:
        alunos = Aluno.objects.filter(
            nome__icontains=search
        ).values('id', 'nome', 'matricula')[:10]
        
        for aluno in alunos:
            usuarios.append({
                'id': aluno['id'],
                'nome': aluno['nome'],
                'identificacao': aluno['matricula'],
                'tipo': 'aluno'
            })
    
    if tipo == 'professor' or not tipo:
        professores = Professor.objects.filter(
            nome__icontains=search
        ).values('id', 'nome', 'registro_profissional')[:10]
        
        for professor in professores:
            usuarios.append({
                'id': professor['id'],
                'nome': professor['nome'],
                'identificacao': professor['registro_profissional'],
                'tipo': 'professor'
            })
    
    return JsonResponse({'usuarios': usuarios})
