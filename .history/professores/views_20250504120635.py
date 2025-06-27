from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.db.models import Q

from .models import Professor
from responsaveis.models import Responsavel, ResponsavelAluno
from turmas.models import TurmaAluno, TurmaProfessor

class StaffOrFilteredByResponsavelMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff ou responsável e filtrar professores adequadamente"""
    
    def test_func(self):
        # Sempre permite acesso, mas o queryset será filtrado em get_queryset
        return True
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se for staff, retorna todos os professores
        if self.request.user.is_staff:
            return queryset
            
        # Se for responsável, filtra pelos professores dos alunos vinculados
        try:
            responsavel = Responsavel.objects.get(usuario=self.request.user)
            
            # Obtém IDs dos alunos vinculados ao responsável
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            # Obtém as turmas desses alunos
            turmas_ids = TurmaAluno.objects.filter(
                aluno_id__in=alunos_ids
            ).values_list('turma_id', flat=True)
            
            # Retorna apenas professores que lecionam nessas turmas
            professor_ids = TurmaProfessor.objects.filter(
                turma_id__in=turmas_ids
            ).values_list('professor_id', flat=True)
            
            return queryset.filter(id__in=professor_ids).distinct()
            
        except Responsavel.DoesNotExist:
            # Se não for responsável nem staff, não mostra nenhum professor
            return queryset.none()

class ProfessorListView(LoginRequiredMixin, StaffOrFilteredByResponsavelMixin, ListView):
    model = Professor
    context_object_name = 'professores'
    template_name = 'professores/professor_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | 
                Q(email__icontains=search) |
                Q(telefone__icontains=search)
            )
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class ProfessorDetailView(LoginRequiredMixin, StaffOrFilteredByResponsavelMixin, DetailView):
    model = Professor
    context_object_name = 'professor'
    template_name = 'professores/professor_detail.html'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Se não for staff, verificar se o professor leciona para algum aluno do responsável
        if not self.request.user.is_staff:
            try:
                responsavel = Responsavel.objects.get(usuario=self.request.user)
                alunos_ids = ResponsavelAluno.objects.filter(
                    responsavel=responsavel
                ).values_list('aluno_id', flat=True)
                
                turmas_ids = TurmaAluno.objects.filter(
                    aluno_id__in=alunos_ids
                ).values_list('turma_id', flat=True)
                
                if not TurmaProfessor.objects.filter(
                    professor=obj, 
                    turma_id__in=turmas_ids
                ).exists():
                    raise Http404("Você não tem permissão para visualizar este professor.")
            except Responsavel.DoesNotExist:
                raise Http404("Você não tem permissão para visualizar este professor.")
        
        return obj

class ProfessorCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Professor
    template_name = 'professores/professor_form.html'
    fields = ['nome', 'email', 'telefone', 'formacao', 'especializacao', 'data_contratacao', 'usuario']
    success_url = reverse_lazy('professores:professor_list')
    success_message = "Professor cadastrado com sucesso!"
    
    def test_func(self):
        # Apenas staff pode criar professores
        return self.request.user.is_staff

class ProfessorUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Professor
    template_name = 'professores/professor_form.html'
    fields = ['nome', 'email', 'telefone', 'formacao', 'especializacao', 'data_contratacao', 'usuario']
    success_url = reverse_lazy('professores:professor_list')
    success_message = "Professor atualizado com sucesso!"
    
    def test_func(self):
        # Apenas staff pode atualizar professores
        return self.request.user.is_staff

class ProfessorDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = Professor
    template_name = 'professores/professor_confirm_delete.html'
    success_url = reverse_lazy('professores:professor_list')
    success_message = "Professor excluído com sucesso!"
    
    def test_func(self):
        # Apenas staff pode excluir professores
        return self.request.user.is_staff
