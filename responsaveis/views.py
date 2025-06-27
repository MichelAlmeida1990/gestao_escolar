from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db import transaction
from .models import Responsavel, ResponsavelAluno
from .forms import ResponsavelForm, ResponsavelAlunoForm
from alunos.models import Aluno

@login_required
def responsavel_list(request):
    """Lista todos os responsÃ¡veis cadastrados no sistema."""
    responsaveis = Responsavel.objects.all()
    return render(request, 'responsaveis/responsavel_list.html', {'responsaveis': responsaveis})

@login_required
def responsavel_detail(request, pk):
    """Exibe detalhes de um responsÃ¡vel especÃ­fico."""
    responsavel = get_object_or_404(Responsavel, pk=pk)
    relacoes = ResponsavelAluno.objects.filter(responsavel=responsavel)
    return render(request, 'responsaveis/responsavel_detail.html', {
        'responsavel': responsavel,
        'relacoes': relacoes
    })

@login_required
@transaction.atomic
def responsavel_create(request):
    """Cria um novo responsÃ¡vel e seu usuÃ¡rio associado."""
    if request.method == 'POST':
        form = ResponsavelForm(request.POST)
        if form.is_valid():
            # Criar usuÃ¡rio
            username = form.cleaned_data['cpf']
            email = form.cleaned_data['email']
            password = User.objects.make_random_password()
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=form.cleaned_data['nome_completo'].split()[0],
                last_name=' '.join(form.cleaned_data['nome_completo'].split()[1:]) if len(form.cleaned_data['nome_completo'].split()) > 1 else ''
            )
            
            # Adicionar ao grupo de responsÃ¡veis
            grupo_responsaveis, created = Group.objects.get_or_create(name='ResponsÃ¡veis')
            user.groups.add(grupo_responsaveis)
            
            # Criar responsÃ¡vel
            responsavel = form.save(commit=False)
            responsavel.usuario = user
            responsavel.save()
            
            messages.success(request, 'ResponsÃ¡vel cadastrado com sucesso! Uma senha temporÃ¡ria foi gerada.')
            return redirect('responsavel_detail', pk=responsavel.pk)
    else:
        form = ResponsavelForm()
    
    return render(request, 'responsaveis/responsavel_form.html', {'form': form})

@login_required
def responsavel_update(request, pk):
    """Atualiza os dados de um responsÃ¡vel existente."""
    responsavel = get_object_or_404(Responsavel, pk=pk)
    
    if request.method == 'POST':
        form = ResponsavelForm(request.POST, instance=responsavel)
        if form.is_valid():
            # Atualizar dados do usuÃ¡rio tambÃ©m
            user = responsavel.usuario
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['nome_completo'].split()[0]
            user.last_name = ' '.join(form.cleaned_data['nome_completo'].split()[1:]) if len(form.cleaned_data['nome_completo'].split()) > 1 else ''
            user.save()
            
            form.save()
            messages.success(request, 'Dados do responsÃ¡vel atualizados com sucesso!')
            return redirect('responsavel_detail', pk=responsavel.pk)
    else:
        form = ResponsavelForm(instance=responsavel)
    
    return render(request, 'responsaveis/responsavel_form.html', {'form': form, 'responsavel': responsavel})

@login_required
def responsavel_delete(request, pk):
    """Remove um responsÃ¡vel do sistema."""
    responsavel = get_object_or_404(Responsavel, pk=pk)
    
    if request.method == 'POST':
        usuario = responsavel.usuario
        responsavel.delete()
        usuario.delete()
        messages.success(request, 'ResponsÃ¡vel removido com sucesso!')
        return redirect('responsavel_list')
    
    return render(request, 'responsaveis/responsavel_confirm_delete.html', {'responsavel': responsavel})

@login_required
def vincular_aluno(request, responsavel_id):
    """Vincula um aluno a um responsÃ¡vel."""
    responsavel = get_object_or_404(Responsavel, pk=responsavel_id)
    
    if request.method == 'POST':
        form = ResponsavelAlunoForm(request.POST)
        if form.is_valid():
            relacao = form.save(commit=False)
            relacao.responsavel = responsavel
            relacao.save()
            messages.success(request, 'Aluno vinculado ao responsÃ¡vel com sucesso!')
            return redirect('responsavel_detail', pk=responsavel.pk)
    else:
        # Filtra alunos que ainda nÃ£o estÃ£o vinculados a este responsÃ¡vel
        alunos_vinculados = ResponsavelAluno.objects.filter(responsavel=responsavel).values_list('aluno_id', flat=True)
        form = ResponsavelAlunoForm()
        form.fields['aluno'].queryset = Aluno.objects.exclude(id__in=alunos_vinculados)
    
    return render(request, 'responsaveis/vincular_aluno.html', {'form': form, 'responsavel': responsavel})

@login_required
def desvincular_aluno(request, relacao_id):
    """Remove o vÃ­nculo entre um aluno e um responsÃ¡vel."""
    relacao = get_object_or_404(ResponsavelAluno, pk=relacao_id)
    responsavel_id = relacao.responsavel.id
    
    if request.method == 'POST':
        relacao.delete()
        messages.success(request, 'VÃ­nculo com aluno removido com sucesso!')
        return redirect('responsavel_detail', pk=responsavel_id)
    
    return render(request, 'responsaveis/desvincular_aluno_confirm.html', {'relacao': relacao})

