from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Turma
from alunos.models import Aluno
from .forms import TurmaForm, AlunoTurmaForm

class TurmaListView(ListView):
    model = Turma
    template_name = 'turmas/turma_list.html'
    context_object_name = 'turmas'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(serie__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context

class TurmaDetailView(DetailView):
    model = Turma
    template_name = 'turmas/turma_detail.html'
    context_object_name = 'turma'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turma = self.get_object()
        context['alunos'] = turma.alunos.all()
        context['professores'] = turma.professor_set.all()
        return context

class TurmaCreateView(CreateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'turmas/turma_form.html'
    success_url = reverse_lazy('turma_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Turma cadastrada com sucesso!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Cadastrar Nova Turma'
        context['botao'] = 'Cadastrar'
        return context

class TurmaUpdateView(UpdateView):
    model = Turma
    form_class = TurmaForm
    template_name = 'turmas/turma_form.html'
    success_url = reverse_lazy('turma_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Turma atualizada com sucesso!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Turma'
        context['botao'] = 'Atualizar'
        return context

class TurmaDeleteView(DeleteView):
    model = Turma
    template_name = 'turmas/turma_confirm_delete.html'
    success_url = reverse_lazy('turma_list')
    context_object_name = 'turma'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Turma excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

def adicionar_alunos(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    
    if request.method == 'POST':
        form = AlunoTurmaForm(request.POST)
        if form.is_valid():
            alunos = form.cleaned_data['alunos']
            for aluno in alunos:
                turma.alunos.add(aluno)
            messages.success(request, f'{len(alunos)} aluno(s) adicionado(s) à turma com sucesso!')
            return redirect('turma_detail', pk=turma.id)
    else:
        # Excluir alunos que já estão na turma
        alunos_disponiveis = Aluno.objects.exclude(turma=turma)
        form = AlunoTurmaForm()
        form.fields['alunos'].queryset = alunos_disponiveis
    
    return render(request, 'turmas/adicionar_alunos.html', {
        'form': form,
        'turma': turma
    })

def remover_aluno(request, turma_id, aluno_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    if request.method == 'POST':
        turma.alunos.remove(aluno)
        messages.success(request, f'Aluno {aluno.nome} removido da turma com sucesso!')
    
    return redirect('turma_detail', pk=turma.id)
