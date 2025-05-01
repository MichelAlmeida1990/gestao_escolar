# populate_notas.py
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal
import inspect

# Configurar ambiente Django com o nome correto do módulo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from faker import Faker
from notas.models import Disciplina, Avaliacao, Nota
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma

fake = Faker('pt_BR')

def verificar_campos_modelo(modelo):
    """Verifica quais campos estão disponíveis no modelo"""
    return [field.name for field in modelo._meta.fields]

def criar_disciplinas():
    """Cria disciplinas básicas do currículo escolar"""
    disciplinas_base = [
        "Português", "Matemática", "História", "Geografia", "Ciências", 
        "Física", "Química", "Biologia", "Educação Física", "Artes",
        "Inglês", "Espanhol", "Filosofia", "Sociologia", "Literatura"
    ]
    
    disciplinas_criadas = []
    
    # Verificar campos disponíveis no modelo Disciplina
    campos_disciplina = verificar_campos_modelo(Disciplina)
    print(f"Campos disponíveis no modelo Disciplina: {campos_disciplina}")
    
    # Preparar dados básicos para todas as disciplinas
    dados_base = {'nome': None, 'carga_horaria': None}
    
    # Verificar se campos adicionais existem e adicionar à estrutura de dados
    if 'professor' in campos_disciplina:
        professores = list(Professor.objects.all())
        if not professores:
            print("Não há professores cadastrados no sistema.")
            return []
    
    if 'turma' in campos_disciplina:
        turmas = list(Turma.objects.all())
        if not turmas:
            print("Não há turmas cadastradas no sistema.")
            return []
    
    for nome_disciplina in disciplinas_base:
        # Preparar dados específicos para esta disciplina
        dados_disciplina = dados_base.copy()
        dados_disciplina['nome'] = nome_disciplina
        dados_disciplina['carga_horaria'] = random.choice([40, 60, 80, 100])
        
        # Adicionar campos opcionais se existirem no modelo
        if 'professor' in campos_disciplina:
            dados_disciplina['professor'] = random.choice(professores)
        
        if 'turma' in campos_disciplina:
            dados_disciplina['turma'] = random.choice(turmas)
        
        if 'periodo' in campos_disciplina:
            dados_disciplina['periodo'] = random.choice(['1º Bimestre', '2º Bimestre', '3º Bimestre', '4º Bimestre'])
        
        # Criar a disciplina com os campos disponíveis
        disciplina = Disciplina.objects.create(**dados_disciplina)
        disciplinas_criadas.append(disciplina)
        
        # Construir mensagem de log com base nos campos disponíveis
        msg = f"Disciplina criada: {disciplina.nome}"
        if 'professor' in campos_disciplina:
            msg += f" - Professor: {disciplina.professor.nome}"
        if 'turma' in campos_disciplina:
            msg += f" - Turma: {disciplina.turma.nome}"
        print(msg)
    
    return disciplinas_criadas

def criar_avaliacoes(disciplinas):
    """Cria avaliações para as disciplinas"""
    tipos_avaliacao = ["Prova", "Trabalho", "Projeto", "Seminário", "Exercício", "Participação"]
    avaliacoes_criadas = []
    
    # Verificar campos disponíveis no modelo Avaliacao
    campos_avaliacao = verificar_campos_modelo(Avaliacao)
    print(f"Campos disponíveis no modelo Avaliacao: {campos_avaliacao}")
    
    for disciplina in disciplinas:
        # Cria entre 3 e 5 avaliações por disciplina
        num_avaliacoes = random.randint(3, 5)
        
        for i in range(num_avaliacoes):
            tipo = random.choice(tipos_avaliacao)
            data_base = datetime.now()
            data_avaliacao = data_base + timedelta(days=random.randint(-30, 30))
            
            # Preparar dados com base nos campos disponíveis
            dados_avaliacao = {
                'disciplina': disciplina,
                'tipo': tipo,
                'descricao': f"{tipo} sobre {fake.sentence(nb_words=6)}",
            }
            
            if 'data' in campos_avaliacao:
                dados_avaliacao['data'] = data_avaliacao.date()
            
            if 'peso' in campos_avaliacao:
                dados_avaliacao['peso'] = random.choice([1, 2, 3])
            
            avaliacao = Avaliacao.objects.create(**dados_avaliacao)
            avaliacoes_criadas.append(avaliacao)
            print(f"Avaliação criada: {avaliacao.tipo} - {avaliacao.descricao} - Disciplina: {avaliacao.disciplina.nome}")
    
    return avaliacoes_criadas

def lancar_notas(avaliacoes):
    """Lança notas para os alunos nas avaliações"""
    notas_criadas = []
    
    # Verificar campos disponíveis no modelo Nota
    campos_nota = verificar_campos_modelo(Nota)
    print(f"Campos disponíveis no modelo Nota: {campos_nota}")
    
    for avaliacao in avaliacoes:
        # Verificar se o modelo Disciplina tem o campo turma
        campos_disciplina = verificar_campos_modelo(Disciplina)
        
        if 'turma' in campos_disciplina:
            # Obtém todos os alunos da turma associada à disciplina da avaliação
            alunos_turma = Aluno.objects.filter(turma=avaliacao.disciplina.turma)
        else:
            # Se não houver campo turma, pegar todos os alunos
            alunos_turma = Aluno.objects.all()
            if not alunos_turma:
                print("Não há alunos cadastrados no sistema.")
                return []
        
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
    if disciplinas:
        avaliacoes = criar_avaliacoes(disciplinas)
        if avaliacoes:
            notas = lancar_notas(avaliacoes)
            
            print(f"\nPopulação concluída com sucesso!")
            print(f"Foram criadas {len(disciplinas)} disciplinas")
            print(f"Foram criadas {len(avaliacoes)} avaliações")
            print(f"Foram lançadas {len(notas)} notas")
        else:
            print("Não foi possível criar avaliações.")
    else:
        print("Não foi possível criar disciplinas.")

if __name__ == '__main__':
    print("Populando o banco de dados do app de notas...")
    popular_notas()
    print("Processo finalizado!")
