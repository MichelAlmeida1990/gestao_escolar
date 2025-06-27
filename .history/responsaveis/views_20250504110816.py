from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count
from .models import Responsavel, RelacaoAlunoResponsavel
from alunos.models import Aluno
from notas.models import Nota
from turmas.models import Turma

@login_required
def dashboard_responsavel(request):
    """
    Dashboard principal para o responsável visualizar informações gerais
    sobre seus dependentes (alunos).
    """
    try:
        responsavel = request.user.responsavel
        relacoes = RelacaoAlunoResponsavel.objects.filter(responsavel=responsavel)
        alunos = [relacao.aluno for relacao in relacoes]
        
        # Dados para o dashboard
        dados_alunos = []
        for aluno in alunos:
            notas_recentes = Nota.objects.filter(aluno=aluno).order_by('-data_lancamento')[:5]
            media_geral = Nota.objects.filter(aluno=aluno).aggregate(media=Avg('valor'))['media'] or 0
            
            dados_alunos.append({
                'aluno': aluno,
                'turma': aluno.turma_atual,
                'notas_recentes': notas_recentes,
                'media_geral': round(media_geral, 1),
                'faltas': aluno.total_faltas() if hasattr(aluno, 'total_faltas') else 0,
            })
        
        context = {
            'responsavel': responsavel,
            'dados_alunos': dados_alunos,
        }
        
        return render(request, 'responsaveis/dashboard.html', context)
    
    except Responsavel.DoesNotExist:
        messages.error(request, 'Você não está registrado como responsável no sistema.')
        return redirect('home')

@login_required
def boletim_aluno(request, aluno_id):
    """
    Exibe o boletim completo de um aluno específico.
    """
    try:
        responsavel = request.user.responsavel
        aluno = get_object_or_404(Aluno, id=aluno_id)
        
        # Verificar se o responsável tem permissão para ver este aluno
        if not RelacaoAlunoResponsavel.objects.filter(responsavel=responsavel, aluno=aluno).exists():
            messages.error(request, 'Você não tem permissão para acessar o boletim deste aluno.')
            return redirect('dashboard_responsavel')
        
        # Buscar todas as notas do aluno, agrupadas por disciplina
        notas_por_disciplina = {}
        todas_notas = Nota.objects.filter(aluno=aluno).order_by('disciplina__nome', 'bimestre')
        
        for nota in todas_notas:
            if nota.disciplina not in notas_por_disciplina:
                notas_por_disciplina[nota.disciplina] = {
                    'notas': [],
                    'media': 0
                }
            notas_por_disciplina[nota.disciplina]['notas'].append(nota)
        
        # Calcular médias por disciplina
        for disciplina, dados in notas_por_disciplina.items():
            media = sum(nota.valor for nota in dados['notas']) / len(dados['notas']) if dados['notas'] else 0
            notas_por_disciplina[disciplina]['media'] = round(media, 1)
        
        context = {
            'responsavel': responsavel,
            'aluno': aluno,
            'notas_por_disciplina': notas_por_disciplina,
            'turma': aluno.turma_atual,
        }
        
        return render(request, 'responsaveis/boletim.html', context)
    
    except Responsavel.DoesNotExist:
        messages.error(request, 'Você não está registrado como responsável no sistema.')
        return redirect('home')

@login_required
def perfil_responsavel(request):
    """
    Exibe e permite edição do perfil do responsável.
    """
    try:
        responsavel = request.user.responsavel
        relacoes = RelacaoAlunoResponsavel.objects.filter(responsavel=responsavel)
        
        context = {
            'responsavel': responsavel,
            'relacoes': relacoes,
        }
        
        return render(request, 'responsaveis/perfil.html', context)
    
    except Responsavel.DoesNotExist:
        messages.error(request, 'Você não está registrado como responsável no sistema.')
        return redirect('home')

@login_required
@user_passes_test(lambda u: u.is_staff)
def responsavel_list(request):
    """
    Lista todos os responsáveis cadastrados no sistema.
    Acesso restrito a funcionários da escola (is_staff=True).
    """
    responsaveis = Responsavel.objects.all().order_by('user__first_name')
    
    # Adicionar informações sobre os dependentes de cada responsável
    for responsavel in responsaveis:
        responsavel.dependentes = RelacaoAlunoResponsavel.objects.filter(responsavel=responsavel)
        responsavel.num_dependentes = responsavel.dependentes.count()
    
    context = {
        'responsaveis': responsaveis,
        'total_responsaveis': responsaveis.count(),
        'titulo': 'Responsáveis Cadastrados',
        'subtitulo': 'Listagem de todos os responsáveis no sistema'
    }
    
    return render(request, 'responsaveis/responsavel_list.html', context)
