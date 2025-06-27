from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma

def home(request):
    # Contar os registros
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    # Passar os dados para o template
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
    }
    
    return render(request, 'core/home.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('core:home')
