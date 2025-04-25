from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

def home(request):
    # Importações locais para evitar dependências circulares
    from alunos.models import Aluno
    
    # Contagem de registros
    alunos_count = Aluno.objects.count()
    professores_count = 0  # Será implementado quando criarmos o modelo de Professor
    turmas_count = 0       # Será implementado quando criarmos o modelo de Turma
    
    context = {
        'alunos_count': alunos_count,
        'professores_count': professores_count,
        'turmas_count': turmas_count,
    }
    
    return render(request, 'core/home.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('home')
