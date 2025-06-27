from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comunicado
from .forms import ComunicadoForm
from responsaveis.models import Responsavel

@login_required
def comunicado_list(request):
    if request.user.is_staff:
        comunicados = Comunicado.objects.all()
    else:
        comunicados = Comunicado.objects.filter(para_todos=True)
    return render(request, 'comunicados/comunicado_list.html', {'comunicados': comunicados})

@login_required
def comunicado_create(request):
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para criar comunicados.")
        return redirect('comunicados:comunicado_list')
    
    if request.method == 'POST':
        form = ComunicadoForm(request.POST)
        if form.is_valid():
            comunicado = form.save(commit=False)
            comunicado.autor = request.user
            comunicado.save()
            form.save_m2m()  # Salva relações ManyToMany
            messages.success(request, "Comunicado criado com sucesso!")
            return redirect('comunicados:comunicado_list')
    else:
        form = ComunicadoForm()
    
    return render(request, 'comunicados/comunicado_form.html', {'form': form})

@login_required
def meus_comunicados(request):
    # Verifica se o usuário é um responsável
    try:
        responsavel = Responsavel.objects.get(usuario=request.user)
        alunos = responsavel.alunos.all()
        
        # Busca comunicados para os alunos do responsável
        comunicados_alunos = Comunicado.objects.filter(alunos__in=alunos).distinct()
        
        # Busca comunicados para as turmas dos alunos do responsável
        turmas = [aluno.turma for aluno in alunos if aluno.turma]
        comunicados_turmas = Comunicado.objects.filter(turmas__in=turmas).distinct()
        
        # Busca comunicados para todos
        comunicados_gerais = Comunicado.objects.filter(para_todos=True)
        
        # Combina todos os comunicados sem duplicatas
        comunicados = comunicados_alunos.union(comunicados_turmas, comunicados_gerais)
        
        return render(request, 'comunicados/meus_comunicados.html', {'comunicados': comunicados})
    except Responsavel.DoesNotExist:
        messages.error(request, "Você não está registrado como responsável.")
        return redirect('home')
