#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from frequencia.models import RegistroFrequencia
from alunos.models import Aluno
from turmas.models import Turma
from notas.models import Disciplina
from professores.models import Professor

def criar_dados_teste():
    """Cria dados de teste para verificar o cálculo de frequência"""
    
    # Buscar uma turma existente
    turma = Turma.objects.first()
    if not turma:
        print("Nenhuma turma encontrada!")
        return
    
    # Buscar uma disciplina existente
    disciplina = Disciplina.objects.first()
    if not disciplina:
        print("Nenhuma disciplina encontrada!")
        return
        
    # Buscar um professor existente
    professor = Professor.objects.first()
    if not professor:
        print("Nenhum professor encontrado!")
        return
    
    # Buscar alunos da turma
    alunos = Aluno.objects.filter(turmas_matriculadas__turma=turma, turmas_matriculadas__ativo=True)
    if not alunos:
        print("Nenhum aluno encontrado na turma!")
        return
    
    print(f"Criando dados de teste para:")
    print(f"- Turma: {turma.nome}")
    print(f"- Disciplina: {disciplina.nome}")
    print(f"- Professor: {professor.nome}")
    print(f"- Alunos: {alunos.count()}")
    
    # Definir período de teste (últimos 7 dias úteis)
    hoje = datetime.now().date()
    inicio_periodo = hoje - timedelta(days=10)
    
    # Criar registros de frequência para teste
    dias_criados = 0
    for i in range(10):
        data_aula = inicio_periodo + timedelta(days=i)
        
        # Só criar registros para dias úteis (segunda a sexta)
        if data_aula.weekday() < 5:  # 0=segunda, 4=sexta
            dias_criados += 1
            
            for j, aluno in enumerate(alunos[:5]):  # Pegar só 5 alunos para teste
                # Simular diferentes cenários:
                if j == 0:  # Aluno sempre presente
                    status = 'presente'
                elif j == 1:  # Aluno com algumas faltas
                    status = 'ausente' if i % 3 == 0 else 'presente'
                elif j == 2:  # Aluno com atrasos
                    status = 'atrasado' if i % 2 == 0 else 'presente'
                elif j == 3:  # Aluno com faltas justificadas
                    status = 'justificado' if i % 4 == 0 else 'presente'
                else:  # Aluno com muitas faltas
                    status = 'presente' if i % 3 == 0 else 'ausente'
                
                # Criar ou atualizar registro
                registro, created = RegistroFrequencia.objects.get_or_create(
                    aluno=aluno,
                    turma=turma,
                    disciplina=disciplina,
                    data=data_aula,
                    defaults={
                        'professor': professor,
                        'status': status,
                        'observacoes': f'Teste - {status}'
                    }
                )
                
                if not created:
                    registro.status = status
                    registro.save()
    
    print(f"\nDados criados para {dias_criados} dias letivos")
    print(f"Período: {inicio_periodo} a {hoje}")
    
    # Mostrar estatísticas
    registros = RegistroFrequencia.objects.filter(
        turma=turma,
        disciplina=disciplina,
        data__range=[inicio_periodo, hoje]
    )
    
    print(f"\nEstatísticas criadas:")
    print(f"- Total de registros: {registros.count()}")
    print(f"- Presenças: {registros.filter(status='presente').count()}")
    print(f"- Faltas: {registros.filter(status='ausente').count()}")
    print(f"- Atrasos: {registros.filter(status='atrasado').count()}")
    print(f"- Justificados: {registros.filter(status='justificado').count()}")
    
    return turma.id, disciplina.id, inicio_periodo, hoje

if __name__ == "__main__":
    resultado = criar_dados_teste()
    if resultado:
        turma_id, disciplina_id, data_inicio, data_fim = resultado
        print(f"\nPara testar o relatório, use:")
        print(f"- Turma ID: {turma_id}")
        print(f"- Disciplina ID: {disciplina_id}")
        print(f"- Data início: {data_inicio}")
        print(f"- Data fim: {data_fim}") 