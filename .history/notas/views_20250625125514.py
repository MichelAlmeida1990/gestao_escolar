from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required

from .models import Disciplina, Avaliacao, Nota
from alunos.models import Aluno
from turmas.models import Turma
from .forms import NotaForm, AlunoSelecionarForm, TurmaSelecionarForm
from responsaveis.models import Responsavel, ResponsavelAluno

class StaffOrProfessorMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff ou professor"""
    
    def test_func(self):
        return self.request.user.is_staff or hasattr(self.request.user, 'professor')

class StaffOrFilteredByResponsavelMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é staff, professor ou responsável e filtrar adequadamente"""
    
    def test_func(self):
        # Sempre permite acesso, mas o queryset será filtrado em get_queryset
        return True

# Views para Disciplina
class DisciplinaListView(LoginRequiredMixin, StaffOrFilteredByResponsavelMixin, ListView):
    model = Disciplina
    context_object_name = 'disciplinas'
    template_name = 'notas/disciplina_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se for staff, retorna todas as disciplinas
        if self.request.user.is_staff:
            return queryset
            
        # Se for professor, retorna apenas suas disciplinas
        # Como não há relacionamento direto entre professor e disciplina,
        # esta funcionalidade precisa ser implementada de acordo com a estrutura do projeto
        if hasattr(self.request.user, 'professor'):
            return queryset
            
        # Se for responsável, filtra pelas disciplinas dos alunos vinculados
        try:
            responsavel = Responsavel.objects.get(usuario=self.request.user)
            
            # Obtém IDs dos alunos vinculados ao responsável
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            # Obtém as turmas desses alunos através de TurmaAluno
            from turmas.models import TurmaAluno
            turmas_ids = TurmaAluno.objects.filter(
                aluno_id__in=alunos_ids, ativo=True
            ).values_list('turma_id', flat=True)
            
            # Retorna apenas disciplinas dessas turmas
            return queryset.filter(avaliacoes__turma_id__in=turmas_ids).distinct()
            
        except Responsavel.DoesNotExist:
            # Se não for responsável nem staff nem professor, não mostra nenhuma disciplina
            return queryset.none()

class DisciplinaCreateView(LoginRequiredMixin, StaffOrProfessorMixin, SuccessMessageMixin, CreateView):
    model = Disciplina
    template_name = 'notas/disciplina_form.html'
    fields = ['nome', 'codigo', 'carga_horaria', 'ementa']
    success_url = reverse_lazy('notas:disciplina_list')
    success_message = "Disciplina cadastrada com sucesso!"

class DisciplinaUpdateView(LoginRequiredMixin, StaffOrProfessorMixin, SuccessMessageMixin, UpdateView):
    model = Disciplina
    template_name = 'notas/disciplina_form.html'
    fields = ['nome', 'codigo', 'carga_horaria', 'ementa']
    success_url = reverse_lazy('notas:disciplina_list')
    success_message = "Disciplina atualizada com sucesso!"

class DisciplinaDeleteView(LoginRequiredMixin, StaffOrProfessorMixin, SuccessMessageMixin, DeleteView):
    model = Disciplina
    template_name = 'notas/disciplina_confirm_delete.html'
    success_url = reverse_lazy('notas:disciplina_list')
    success_message = "Disciplina excluída com sucesso!"

# Views para Avaliação
class AvaliacaoListView(LoginRequiredMixin, StaffOrFilteredByResponsavelMixin, ListView):
    model = Avaliacao
    context_object_name = 'avaliacoes'
    template_name = 'notas/avaliacao_list.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Se for staff, retorna todas as avaliações
        if self.request.user.is_staff:
            return queryset
            
        # Se for professor, retorna apenas avaliações de suas disciplinas
        # Como não há relacionamento direto entre professor e disciplina,
        # esta funcionalidade precisa ser implementada de acordo com a estrutura do projeto
        if hasattr(self.request.user, 'professor'):
            return queryset
            
        # Se for responsável, filtra pelas avaliações dos alunos vinculados
        try:
            responsavel = Responsavel.objects.get(usuario=self.request.user)
            
            # Obtém IDs dos alunos vinculados ao responsável
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            # Obtém as turmas desses alunos através de TurmaAluno
            from turmas.models import TurmaAluno
            turmas_ids = TurmaAluno.objects.filter(
                aluno_id__in=alunos_ids, ativo=True
            ).values_list('turma_id', flat=True)
            
            # Retorna apenas avaliações dessas turmas
            return queryset.filter(turma_id__in=turmas_ids)
            
        except Responsavel.DoesNotExist:
            # Se não for responsável nem staff nem professor, não mostra nenhuma avaliação
            return queryset.none()

class AvaliacaoCreateView(LoginRequiredMixin, StaffOrProfessorMixin, SuccessMessageMixin, CreateView):
    model = Avaliacao
    template_name = 'notas/avaliacao_form.html'
    fields = ['nome', 'disciplina', 'turma', 'tipo', 'data', 'periodo', 'peso']
    success_url = reverse_lazy('notas:avaliacao_list')
    success_message = "Avaliação cadastrada com sucesso!"

class AvaliacaoUpdateView(LoginRequiredMixin, StaffOrProfessorMixin, SuccessMessageMixin, UpdateView):
    model = Avaliacao
    template_name = 'notas/avaliacao_form.html'
    fields = ['nome', 'disciplina', 'turma', 'tipo', 'data', 'periodo', 'peso']
    success_url = reverse_lazy('notas:avaliacao_list')
    success_message = "Avaliação atualizada com sucesso!"

class AvaliacaoDeleteView(LoginRequiredMixin, StaffOrProfessorMixin, SuccessMessageMixin, DeleteView):
    model = Avaliacao
    template_name = 'notas/avaliacao_confirm_delete.html'
    success_url = reverse_lazy('notas:avaliacao_list')
    success_message = "Avaliação excluída com sucesso!"

# Lançamento de notas
@login_required
def lancar_notas(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, pk=avaliacao_id)
    
    # Verificar permissões
    if not request.user.is_staff and not (
        hasattr(request.user, 'professor') and 
        avaliacao.disciplina.professor == request.user.professor
    ):
        raise Http404("Você não tem permissão para lançar notas para esta avaliação.")
    
    # Obter alunos da turma através de TurmaAluno
    from turmas.models import TurmaAluno
    alunos = Aluno.objects.filter(
        turmas_matriculadas__turma=avaliacao.turma,
        turmas_matriculadas__ativo=True
    )
    
    # Dicionário para armazenar as notas existentes
    notas = {}
    for nota in Nota.objects.filter(avaliacao=avaliacao):
        notas[nota.aluno.id] = nota.valor
    
    if request.method == 'POST':
        for aluno in alunos:
            nota_valor = request.POST.get(f'aluno_{aluno.id}')
            if nota_valor and nota_valor.strip():
                try:
                    nota_valor = float(nota_valor)
                    if 0 <= nota_valor <= 10:  # Validação do valor da nota
                        Nota.objects.update_or_create(
                            aluno=aluno,
                            avaliacao=avaliacao,
                            defaults={'valor': nota_valor}
                        )
                except ValueError:
                    pass  # Ignorar valores inválidos
        
        messages.success(request, "Notas lançadas com sucesso!")
        return redirect('notas:avaliacao_list')
    
    context = {
        'avaliacao': avaliacao,
        'alunos': alunos,
        'notas': notas,
    }
    
    return render(request, 'notas/lancar_notas.html', context)

# Boletim
@login_required
def selecionar_aluno_boletim(request):
    # Se for responsável, mostrar apenas seus alunos vinculados
    if not request.user.is_staff and not hasattr(request.user, 'professor'):
        try:
            responsavel = Responsavel.objects.get(usuario=request.user)
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            # Se o responsável tem apenas um aluno, redirecionar direto para o boletim
            if len(alunos_ids) == 1:
                return redirect('notas:boletim_aluno', aluno_id=alunos_ids[0])
                
            # Limitar o queryset do form apenas aos alunos do responsável
            if request.method == 'POST':
                form = AlunoSelecionarForm(request.POST)
                form.fields['aluno'].queryset = Aluno.objects.filter(id__in=alunos_ids)
                if form.is_valid():
                    aluno_id = form.cleaned_data['aluno'].id
                    return redirect('notas:boletim_aluno', aluno_id=aluno_id)
            else:
                form = AlunoSelecionarForm()
                form.fields['aluno'].queryset = Aluno.objects.filter(id__in=alunos_ids)
        except Responsavel.DoesNotExist:
            raise Http404("Você não tem permissão para acessar esta página.")
    else:
        # Para staff e professores, mostrar o formulário normal
        if request.method == 'POST':
            form = AlunoSelecionarForm(request.POST)
            if form.is_valid():
                aluno_id = form.cleaned_data['aluno'].id
                return redirect('notas:boletim_aluno', aluno_id=aluno_id)
        else:
            form = AlunoSelecionarForm()
    
    return render(request, 'notas/selecionar_aluno_boletim.html', {'form': form})

@login_required
def boletim_aluno(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    # Verificar permissões
    if not request.user.is_staff and not hasattr(request.user, 'professor'):
        try:
            responsavel = Responsavel.objects.get(usuario=request.user)
            if not ResponsavelAluno.objects.filter(
                responsavel=responsavel, 
                aluno_id=aluno_id
            ).exists():
                raise Http404("Você não tem permissão para visualizar o boletim deste aluno.")
        except Responsavel.DoesNotExist:
            raise Http404("Você não tem permissão para visualizar o boletim deste aluno.")
    
    # Estrutura para armazenar dados do boletim
    disciplinas = {}
    
    # Obter todas as disciplinas que o aluno tem avaliações
    disciplinas_aluno = Disciplina.objects.filter(
        avaliacoes__nota__aluno=aluno
    ).distinct()
    
    for disciplina in disciplinas_aluno:
        # Obter turmas do aluno através de TurmaAluno
        from turmas.models import TurmaAluno
        turmas_aluno = TurmaAluno.objects.filter(aluno=aluno, ativo=True).values_list('turma', flat=True)
        
        avaliacoes = Avaliacao.objects.filter(
            disciplina=disciplina,
            turma__in=turmas_aluno
        ).order_by('data')
        
        # Preparar dados de avaliações com notas
        avaliacoes_com_notas = []
        for avaliacao in avaliacoes:
            try:
                nota = Nota.objects.get(aluno=aluno, avaliacao=avaliacao)
                valor_nota = nota.valor
            except Nota.DoesNotExist:
                valor_nota = None
                
            avaliacoes_com_notas.append({
                'nome': avaliacao.nome,
                'data': avaliacao.data,
                'peso': avaliacao.peso,
                'nota': valor_nota
            })
        
        # Calcular média
        notas_disciplina = Nota.objects.filter(
            aluno=aluno, 
            avaliacao__disciplina=disciplina
        )
        media = notas_disciplina.aggregate(Avg('valor'))['valor__avg']
        
        # Adicionar informações da disciplina ao dicionário
        disciplinas[disciplina.nome] = {
            'avaliacoes': avaliacoes_com_notas,
            'media': media
        }
    
    context = {
        'aluno': aluno,
        'disciplinas': disciplinas
    }
    return render(request, 'notas/boletim_aluno.html', context)

# Desempenho da turma
@login_required
def selecionar_turma_desempenho(request):
    # Se for responsável, mostrar apenas turmas de seus alunos
    if not request.user.is_staff and not hasattr(request.user, 'professor'):
        try:
            responsavel = Responsavel.objects.get(usuario=request.user)
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            # Obter turmas através de TurmaAluno
            from turmas.models import TurmaAluno
            turmas_ids = TurmaAluno.objects.filter(
                aluno_id__in=alunos_ids, ativo=True
            ).values_list('turma_id', flat=True).distinct()
            
            # Se o responsável tem alunos em apenas uma turma, redirecionar direto
            if len(turmas_ids) == 1:
                return redirect('notas:desempenho_turma', turma_id=turmas_ids[0])
                
            # Limitar o queryset do form apenas às turmas dos alunos do responsável
            if request.method == 'POST':
                form = TurmaSelecionarForm(request.POST)
                form.fields['turma'].queryset = Turma.objects.filter(id__in=turmas_ids)
                if form.is_valid():
                    turma_id = form.cleaned_data['turma'].id
                    return redirect('notas:desempenho_turma', turma_id=turma_id)
            else:
                form = TurmaSelecionarForm()
                form.fields['turma'].queryset = Turma.objects.filter(id__in=turmas_ids)
        except Responsavel.DoesNotExist:
            raise Http404("Você não tem permissão para acessar esta página.")
    else:
        # Para staff e professores, mostrar o formulário normal
        if request.method == 'POST':
            form = TurmaSelecionarForm(request.POST)
            if form.is_valid():
                turma_id = form.cleaned_data['turma'].id
                return redirect('notas:desempenho_turma', turma_id=turma_id)
        else:
            form = TurmaSelecionarForm()
            # Se for professor, mostrar apenas suas turmas
            if hasattr(request.user, 'professor'):
                professor = request.user.professor
                # Como não há relacionamento direto entre professor e disciplina,
                # mostrar todas as turmas para professores
                form.fields['turma'].queryset = Turma.objects.all()
    
    return render(request, 'notas/selecionar_turma_desempenho.html', {'form': form})

@login_required
def desempenho_turma(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    
    # Verificar permissões
    if not request.user.is_staff and not hasattr(request.user, 'professor'):
        try:
            responsavel = Responsavel.objects.get(usuario=request.user)
            alunos_ids = ResponsavelAluno.objects.filter(
                responsavel=responsavel
            ).values_list('aluno_id', flat=True)
            
            if not Aluno.objects.filter(
                id__in=alunos_ids, 
                turma=turma
            ).exists():
                raise Http404("Você não tem permissão para visualizar o desempenho desta turma.")
        except Responsavel.DoesNotExist:
            raise Http404("Você não tem permissão para visualizar o desempenho desta turma.")
    
    alunos = Aluno.objects.filter(turma=turma)
    disciplinas = Disciplina.objects.filter(avaliacoes__turma=turma).distinct()
    
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
