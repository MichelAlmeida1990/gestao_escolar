from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.forms import formset_factory, modelformset_factory

from .models import Disciplina, Avaliacao, Nota
from alunos.models import Aluno
from turmas.models import Turma
from .forms import NotaForm, AlunoSelecionarForm, TurmaSelecionarForm

# Views para Disciplina
class DisciplinaListView(ListView):
    model = Disciplina
    context_object_name = 'disciplinas'
    template_name = 'notas/disciplina_list.html'

class DisciplinaCreateView(SuccessMessageMixin, CreateView):
    model = Disciplina
    template_name = 'notas/disciplina_form.html'
    fields = ['nome', 'descricao', 'carga_horaria', 'professor']
    success_url = reverse_lazy('notas:disciplina_list')
    success_message = "Disciplina cadastrada com sucesso!"

class DisciplinaUpdateView(SuccessMessageMixin, UpdateView):
    model = Disciplina
    template_name = 'notas/disciplina_form.html'
    fields = ['nome', 'descricao', 'carga_horaria', 'professor']
    success_url = reverse_lazy('notas:disciplina_list')
    success_message = "Disciplina atualizada com sucesso!"

class DisciplinaDeleteView(SuccessMessageMixin, DeleteView):
    model = Disciplina
    template_name = 'notas/disciplina_confirm_delete.html'
    success_url = reverse_lazy('notas:disciplina_list')
    success_message = "Disciplina excluída com sucesso!"

# Views para Avaliação
class AvaliacaoListView(ListView):
    model = Avaliacao
    context_object_name = 'avaliacoes'
    template_name = 'notas/avaliacao_list.html'

class AvaliacaoCreateView(SuccessMessageMixin, CreateView):
    model = Avaliacao
    template_name = 'notas/avaliacao_form.html'
    fields = ['titulo', 'descricao', 'data', 'peso', 'disciplina', 'turma']
    success_url = reverse_lazy('notas:avaliacao_list')
    success_message = "Avaliação cadastrada com sucesso!"

class AvaliacaoUpdateView(SuccessMessageMixin, UpdateView):
    model = Avaliacao
    template_name = 'notas/avaliacao_form.html'
    fields = ['titulo', 'descricao', 'data', 'peso', 'disciplina', 'turma']
    success_url = reverse_lazy('notas:avaliacao_list')
    success_message = "Avaliação atualizada com sucesso!"

class AvaliacaoDeleteView(SuccessMessageMixin, DeleteView):
    model = Avaliacao
    template_name = 'notas/avaliacao_confirm_delete.html'
    success_url = reverse_lazy('notas:avaliacao_list')
    success_message = "Avaliação excluída com sucesso!"

# Lançamento de notas
def lancar_notas(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    alunos = Aluno.objects.filter(turma=avaliacao.turma)
    
    # Verificar se já existem notas lançadas e criar ou atualizar
    if request.method == 'POST':
        for aluno in alunos:
            valor_nota = request.POST.get(f'nota_{aluno.id}')
            if valor_nota:
                nota, created = Nota.objects.update_or_create(
                    aluno=aluno,
                    avaliacao=avaliacao,
                    defaults={'valor': float(valor_nota)}
                )
        messages.success(request, "Notas lançadas com sucesso!")
        return redirect('notas:avaliacao_list')
    
    # Preparar notas existentes para exibição
    notas_dict = {}
    notas_existentes = Nota.objects.filter(avaliacao=avaliacao)
    for nota in notas_existentes:
        notas_dict[nota.aluno.id] = nota.valor
    
    context = {
        'avaliacao': avaliacao,
        'alunos': alunos,
        'notas_dict': notas_dict,
    }
    return render(request, 'notas/lancar_notas.html', context)

# Boletim
def selecionar_aluno_boletim(request):
    if request.method == 'POST':
        form = AlunoSelecionarForm(request.POST)
        if form.is_valid():
            aluno_id = form.cleaned_data['aluno'].id
            return redirect('notas:boletim_aluno', aluno_id=aluno_id)
    else:
        form = AlunoSelecionarForm()
    
    return render(request, 'notas/selecionar_aluno_boletim.html', {'form': form})

def boletim_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    # Agrupar notas por disciplina
    disciplinas = Disciplina.objects.filter(avaliacao__nota__aluno=aluno).distinct()
    boletim = []
    
    for disciplina in disciplinas:
        avaliacoes = Avaliacao.objects.filter(disciplina=disciplina, nota__aluno=aluno)
        notas = Nota.objects.filter(avaliacao__disciplina=disciplina, aluno=aluno)
        media = notas.aggregate(Avg('valor'))['valor__avg']
        
        item_boletim = {
            'disciplina': disciplina,
            'notas': notas,
            'media': media,
        }
        boletim.append(item_boletim)
    
    context = {
        'aluno': aluno,
        'boletim': boletim,
    }
    return render(request, 'notas/boletim_aluno.html', context)

# Desempenho da turma
def selecionar_turma_desempenho(request):
    if request.method == 'POST':
        form = TurmaSelecionarForm(request.POST)
        if form.is_valid():
            turma_id = form.cleaned_data['turma'].id
            return redirect('notas:desempenho_turma', turma_id=turma_id)
    else:
        form = TurmaSelecionarForm()
    
    return render(request, 'notas/selecionar_turma_desempenho.html', {'form': form})

def desempenho_turma(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    alunos = Aluno.objects.filter(turma=turma)
    disciplinas = Disciplina.objects.filter(avaliacao__turma=turma).distinct()
    
    desempenho = []
    
    for disciplina in disciplinas:
        # Média geral da turma na disciplina
        media_turma = Nota.objects.filter(
            avaliacao__disciplina=disciplina,
            aluno__turma=turma
        ).aggregate(Avg('valor'))['valor__avg']
        
        # Contagem de aprovações (média >= 6)
        aprovados = 0
        for aluno in alunos:
            media_aluno = Nota.objects.filter(
                avaliacao__disciplina=disciplina,
                aluno=aluno
            ).aggregate(Avg('valor'))['valor__avg']
            
            if media_aluno and media_aluno >= 6.0:
                aprovados += 1
        
        taxa_aprovacao = (aprovados / alunos.count()) * 100 if alunos.count() > 0 else 0
        
        item_desempenho = {
            'disciplina': disciplina,
            'media_turma': media_turma,
            'aprovados': aprovados,
            'total_alunos': alunos.count(),
            'taxa_aprovacao': taxa_aprovacao,
        }
        desempenho.append(item_desempenho)
    
    context = {
        'turma': turma,
        'desempenho': desempenho,
    }
    return render(request, 'notas/desempenho_turma.html', context)
