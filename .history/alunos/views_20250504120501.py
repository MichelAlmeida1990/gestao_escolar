from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Aluno
from .forms import AlunoForm
from responsaveis.models import Responsavel, ResponsavelAluno


class StaffOrFilteredByResponsavelMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff ou responsável e filtrar alunos adequadamente"""
    
    def test_func(self):
        # Sempre permite acesso, mas o queryset será filtrado em get_queryset
        return True
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se for staff, retorna todos os alunos
        if self.request.user.is_staff:
            return queryset
        
        # Se for responsável, filtra pelos alunos vinculados
        try:
            responsavel = Responsavel.objects.get(usuario=self.request.user)
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            return queryset.filter(id__in=alunos_ids)
        except Responsavel.DoesNotExist:
            # Se não for responsável nem staff, não mostra nenhum aluno
            return queryset.none()

class AlunoListView(LoginRequiredMixin, StaffOrFilteredByResponsavelMixin, ListView):
    model = Aluno
    template_name = 'alunos/aluno_list.html'
    context_object_name = 'alunos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | 
                Q(matricula__icontains=search) |
                Q(cpf__icontains=search) |
                Q(status__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class AlunoDetailView(LoginRequiredMixin, StaffOrFilteredByResponsavelMixin, DetailView):
    model = Aluno
    template_name = 'alunos/aluno_detail.html'
    context_object_name = 'aluno'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Se não for staff, verificar se o aluno está vinculado ao responsável
        if not self.request.user.is_staff:
            try:
                responsavel = Responsavel.objects.get(usuario=self.request.user)
                if not ResponsavelAluno.objects.filter(responsavel=responsavel, aluno=obj).exists():
                    raise Http404("Você não tem permissão para visualizar este aluno.")
            except Responsavel.DoesNotExist:
                raise Http404("Você não tem permissão para visualizar este aluno.")
        
        return obj

class AlunoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/aluno_form.html'
    success_url = reverse_lazy('aluno_list')
    
    def test_func(self):
        # Apenas staff pode criar alunos
        return self.request.user.is_staff
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Cadastrar Novo Aluno'
        context['botao'] = 'Cadastrar'
        return context

class AlunoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/aluno_form.html'
    success_url = reverse_lazy('aluno_list')
    
    def test_func(self):
        # Apenas staff pode editar alunos
        return self.request.user.is_staff
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Aluno atualizado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Aluno'
        context['botao'] = 'Atualizar'
        return context

class AlunoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Aluno
    template_name = 'alunos/aluno_confirm_delete.html'
    success_url = reverse_lazy('aluno_list')
    context_object_name = 'aluno'
    
    def test_func(self):
        # Apenas staff pode excluir alunos
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Aluno excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

def dashboard(request):
    if request.user.is_staff:
        # Administradores veem estatísticas de todos os alunos
        total_alunos = Aluno.objects.count()
        alunos_ativos = Aluno.objects.filter(status='ativo').count()
        alunos_inativos = Aluno.objects.filter(status='inativo').count()
        alunos_transferidos = Aluno.objects.filter(status='transferido').count()
    else:
        # Responsáveis veem estatísticas apenas dos seus alunos
        try:
            responsavel = Responsavel.objects.get(usuario=request.user)
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            total_alunos = Aluno.objects.filter(id__in=alunos_ids).count()
            alunos_ativos = Aluno.objects.filter(id__in=alunos_ids, status='ativo').count()
            alunos_inativos = Aluno.objects.filter(id__in=alunos_ids, status='inativo').count()
            alunos_transferidos = Aluno.objects.filter(id__in=alunos_ids, status='transferido').count()
        except Responsavel.DoesNotExist:
            total_alunos = alunos_ativos = alunos_inativos = alunos_transferidos = 0
    
    # Calcular porcentagens para o gráfico
    if total_alunos > 0:
        porcentagem_ativos = (alunos_ativos / total_alunos) * 100
        porcentagem_inativos = (alunos_inativos / total_alunos) * 100
        porcentagem_transferidos = (alunos_transferidos / total_alunos) * 100
    else:
        porcentagem_ativos = porcentagem_inativos = porcentagem_transferidos = 0
    
    return render(request, 'alunos/dashboard.html', {
        'total_alunos': total_alunos,
        'alunos_ativos': alunos_ativos,
        'alunos_inativos': alunos_inativos,
        'alunos_transferidos': alunos_transferidos,
        'porcentagem_ativos': porcentagem_ativos,
        'porcentagem_inativos': porcentagem_inativos,
        'porcentagem_transferidos': porcentagem_transferidos
    })

def meus_alunos(request):
    """Exibe apenas os alunos vinculados ao responsável logado"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        responsavel = Responsavel.objects.get(usuario=request.user)
        alunos_ids = ResponsavelAluno.objects.filter(
            responsavel=responsavel
        ).values_list('aluno_id', flat=True)
        alunos = Aluno.objects.filter(id__in=alunos_ids)
        
        context = {
            'alunos': alunos,
            'titulo': 'Meus Alunos',
            'is_meus_alunos': True  # Para destacar no menu
        }
        return render(request, 'alunos/meus_alunos.html', context)
    
    except Responsavel.DoesNotExist:
        messages.error(request, 'Você não está cadastrado como responsável.')
        return redirect('home')
