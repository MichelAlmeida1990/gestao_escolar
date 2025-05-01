# populate_notas.py
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  # Altere para o nome correto do seu módulo
django.setup()

from faker import Faker
from notas.models import Disciplina, Avaliacao, Nota
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma

fake = Faker('pt_BR')

def criar_disciplinas():
    """Cria disciplinas básicas do currículo escolar"""
    disciplinas_base = [
        "Português", "Matemática", "História", "Geografia", "Ciências", 
        "Física", "Química", "Biologia", "Educação Física", "Artes",
        "Inglês", "Espanhol", "Filosofia", "Sociologia", "Literatura"
    ]
    
    disciplinas_criadas = []
    professores = list(Professor.objects.all())
    turmas = list(Turma.objects.all())
    
    if not professores or not turmas:
        print("É necessário ter professores e turmas cadastrados antes de criar disciplinas.")
        return []
    
    for nome_disciplina in disciplinas_base:
        # Seleciona aleatoriamente um professor e uma turma
        professor = random.choice(professores)
        turma = random.choice(turmas)
        
        disciplina = Disciplina.objects.create(
            nome=nome_disciplina,
            professor=professor,
            turma=turma,
            carga_horaria=random.choice([40, 60, 80, 100]),
            periodo=random.choice(['1º Bimestre', '2º Bimestre', '3º Bimestre', '4º Bimestre'])
        )
        disciplinas_criadas.append(disciplina)
        print(f"Disciplina criada: {disciplina.nome} - Professor: {disciplina.professor.nome} - Turma: {disciplina.turma.nome}")
    
    return disciplinas_criadas

def criar_avaliacoes(disciplinas):
    """Cria avaliações para as disciplinas"""
    tipos_avaliacao = ["Prova", "Trabalho", "Projeto", "Seminário", "Exercício", "Participação"]
    avaliacoes_criadas = []
    
    for disciplina in disciplinas:
        # Cria entre 3 e 5 avaliações por disciplina
        num_avaliacoes = random.randint(3, 5)
        
        for i in range(num_avaliacoes):
            tipo = random.choice(tipos_avaliacao)
            data_base = datetime.now()
            data_avaliacao = data_base + timedelta(days=random.randint(-30, 30))
            
            avaliacao = Avaliacao.objects.create(
                disciplina=disciplina,
                tipo=tipo,
                descricao=f"{tipo} sobre {fake.sentence(nb_words=6)}",
                data=data_avaliacao.date(),
                peso=random.choice([1, 2, 3])
            )
            avaliacoes_criadas.append(avaliacao)
            print(f"Avaliação criada: {avaliacao.tipo} - {avaliacao.descricao} - Disciplina: {avaliacao.disciplina.nome}")
    
    return avaliacoes_criadas

def lancar_notas(avaliacoes):
    """Lança notas para os alunos nas avaliações"""
    notas_criadas = []
    
    for avaliacao in avaliacoes:
        # Obtém todos os alunos da turma associada à disciplina da avaliação
        alunos_turma = Aluno.objects.filter(turma=avaliacao.disciplina.turma)
        
        for aluno in alunos_turma:
            # Gera uma nota entre 0 e 10, com uma casa decimal
            valor_nota = round(random.uniform(0, 10), 1)
            
            nota = Nota.objects.create(
                aluno=aluno,
                avaliacao=avaliacao,
                valor=Decimal(str(valor_nota))
            )
            notas_criadas.append(nota)
            print(f"Nota lançada: Aluno: {aluno.nome} - Avaliação: {avaliacao.tipo} - Valor: {nota.valor}")
    
    return notas_criadas

def popular_notas():
    """Função principal para popular o app de notas"""
    print("Iniciando população do app de notas...")
    
    # Verifica se já existem dados para evitar duplicação
    if Disciplina.objects.exists():
        print("Já existem disciplinas no banco de dados. Deseja continuar e adicionar mais? (s/n)")
        resposta = input().lower()
        if resposta != 's':
            return
    
    # Cria os dados em sequência
    disciplinas = criar_disciplinas()
    avaliacoes = criar_avaliacoes(disciplinas)
    notas = lancar_notas(avaliacoes)
    
    print(f"\nPopulação concluída com sucesso!")
    print(f"Foram criadas {len(disciplinas)} disciplinas")
    print(f"Foram criadas {len(avaliacoes)} avaliações")
    print(f"Foram lançadas {len(notas)} notas")

if __name__ == '__main__':
    print("Populando o banco de dados do app de notas...")
    popular_notas()
    print("Processo finalizado!")
