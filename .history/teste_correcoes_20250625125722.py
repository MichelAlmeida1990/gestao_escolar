#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse

def test_correcoes():
    print("🔧 Testando correções dos erros...")
    print("=" * 50)
    
    # Criar cliente de teste
    client = Client()
    
    # Fazer login como superusuário michas
    user = User.objects.get(username='michas')
    client.force_login(user)
    
    print("✅ Login realizado como 'michas'")
    print()
    
    # Testar URLs que estavam com problema
    urls_teste = [
        ('/alunos/', 'Lista de Alunos'),
        ('/professores/', 'Lista de Professores'), 
        ('/turmas/', 'Lista de Turmas'),
        ('/notas/disciplinas/', 'Lista de Disciplinas'),
        ('/notas/avaliacoes/', 'Lista de Avaliações'),
    ]
    
    print("🌐 Testando URLs principais:")
    for url, nome in urls_teste:
        try:
            response = client.get(url)
            if response.status_code == 200:
                print(f"  ✅ {nome}: OK (200)")
            else:
                print(f"  ❌ {nome}: Erro {response.status_code}")
        except Exception as e:
            print(f"  ❌ {nome}: Exceção - {e}")
    
    print()
    
    # Testar se os dados estão sendo exibidos
    from alunos.models import Aluno
    from professores.models import Professor
    from turmas.models import Turma
    from notas.models import Disciplina, Avaliacao
    
    print("📊 Verificando dados no banco:")
    print(f"  • Alunos: {Aluno.objects.count()}")
    print(f"  • Professores: {Professor.objects.count()}")
    print(f"  • Turmas: {Turma.objects.count()}")
    print(f"  • Disciplinas: {Disciplina.objects.count()}")
    print(f"  • Avaliações: {Avaliacao.objects.count()}")
    
    # Testar relacionamentos específicos que foram corrigidos
    print()
    print("🔗 Testando relacionamentos corrigidos:")
    
    # Testar TurmaAluno
    from turmas.models import TurmaAluno
    total_matriculas = TurmaAluno.objects.filter(ativo=True).count()
    print(f"  • Matrículas ativas (TurmaAluno): {total_matriculas}")
    
    # Testar se conseguimos obter alunos de uma turma
    primeira_turma = Turma.objects.first()
    if primeira_turma:
        alunos_turma = Aluno.objects.filter(
            turmas_matriculadas__turma=primeira_turma,
            turmas_matriculadas__ativo=True
        ).count()
        print(f"  • Alunos na turma '{primeira_turma.nome}': {alunos_turma}")
    
    # Testar disciplinas com avaliações
    disciplinas_com_avaliacoes = Disciplina.objects.filter(
        avaliacoes__isnull=False
    ).distinct().count()
    print(f"  • Disciplinas com avaliações: {disciplinas_com_avaliacoes}")
    
    print()
    print("🎉 Teste de correções concluído!")
    
    # Testar URLs específicas que estavam com erro
    print()
    print("🧪 Testando URLs específicas que causavam erro:")
    
    # Tentar acessar detail de uma turma
    if Turma.objects.exists():
        turma = Turma.objects.first()
        try:
            response = client.get(f'/turmas/{turma.id}/')
            if response.status_code == 200:
                print(f"  ✅ Detalhe da turma {turma.id}: OK")
            else:
                print(f"  ❌ Detalhe da turma {turma.id}: Erro {response.status_code}")
        except Exception as e:
            print(f"  ❌ Detalhe da turma {turma.id}: Exceção - {e}")
    
    # Tentar acessar edição de disciplina
    if Disciplina.objects.exists():
        disciplina = Disciplina.objects.first()
        try:
            response = client.get(f'/notas/disciplinas/{disciplina.id}/editar/')
            if response.status_code == 200:
                print(f"  ✅ Editar disciplina {disciplina.id}: OK")
            else:
                print(f"  ❌ Editar disciplina {disciplina.id}: Erro {response.status_code}")
        except Exception as e:
            print(f"  ❌ Editar disciplina {disciplina.id}: Exceção - {e}")
    
    # Tentar criar nova avaliação
    try:
        response = client.get('/notas/avaliacoes/nova/')
        if response.status_code == 200:
            print(f"  ✅ Nova avaliação: OK")
        else:
            print(f"  ❌ Nova avaliação: Erro {response.status_code}")
    except Exception as e:
        print(f"  ❌ Nova avaliação: Exceção - {e}")

if __name__ == "__main__":
    test_correcoes() 