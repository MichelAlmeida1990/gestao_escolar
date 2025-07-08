from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma
from matriculas.models import MatriculaOnline
from django.utils import timezone

def home(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    from datetime import datetime
    return render(request, 'landing.html', {'year': datetime.now().year})

def dashboard_view(request):
    ano_atual = timezone.now().year
    total_alunos = Aluno.objects.filter(status='ativo').count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.filter(ano_letivo=ano_atual).count()
    matriculas_pendentes = MatriculaOnline.objects.filter(status='pendente', ano_letivo=ano_atual).count()
    context = {
        'total_alunos': total_alunos,
        'total_professores': total_professores,
        'total_turmas': total_turmas,
        'matriculas_pendentes': matriculas_pendentes,
    }
    return render(request, 'core/dashboard.html', context)

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('usuarios:login')
