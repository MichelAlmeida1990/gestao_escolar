# populate_notas.py
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from faker import Faker
from notas.models import Disciplina, Avaliacao, Nota
from alunos.models import Aluno

fake = Faker('pt_BR')

def verificar_modelos():
    """Verifica os campos disponíveis em cada modelo"""
    print("Verificando campos dos modelos:")
    
    print("\nCampos do modelo Disciplina:")
    print([field.name for field in Disciplina._meta.fields])
    
    print("\nCampos do modelo Avaliacao:")
    print([field.name for field in Avaliacao._meta.fields])
    
    print("\nCampos do modelo Nota:")
    print([field.name for field in Nota._meta.fields])
    
    print("\nVerificando se existem alunos cadastrados:")
    alunos_count = Aluno.objects.count()
    print(f"Total de alunos: {alunos_count}")
    
    return True

def criar_disciplinas():
    """Cria disciplinas básicas do currículo escolar"""
    disciplinas_base = [
        "Português", "Matemática", "História", "Geografia", "Ciências", 
        "Física", "Química", "Biologia", "Educação Física", "Artes",
        "Inglês", "Espanhol", "Filosofia", "Sociologia", "Literatura"
    ]
    
    disciplinas_criadas = []
    
    for i, nome_disciplina in enumerate(disciplinas_base):
        # Criar código único para cada disciplina
        codigo = f"DISC{i+1:03d}"
        
        # Criar ementa fictícia para a disciplina
        ementa = fake.paragraph(nb_sentences=3)
        
        disciplina = Disciplina.objects.create(
            nome=nome_disciplina,
            codigo=codigo,
            carga_horaria=random.choice([40, 60, 80, 100]),
            ementa=ementa
        )
        
        disciplinas_criadas.append(disciplina)
        print(f"Disciplina criada: {disciplina.nome} - Código: {disciplina.codigo}")
    
    return disciplinas_criadas

def criar_avaliacoes(disciplinas):
    """Cria avaliações para as disciplinas"""
    tipos_avaliacao = ["Prova", "Trabalho", "Projeto", "Seminário", "Exercício", "Participação"]
    avaliacoes_criadas = []
    
    turmas = ["A", "B", "C"]
    periodos = ["Manhã", "Tarde", "Noite"]
    
    for disciplina in disciplinas:
        # Cria entre 3 e 5 avaliações por disciplina
        num_avaliacoes = random.randint(3, 5)
        
        for i in range(num_avaliacoes):
            tipo = random.choice(tipos_avaliacao)
            data_base = datetime.now()
            data_avaliacao = data_base + timedelta(days=random.randint(-30, 30))
            
            avaliacao = Avaliacao.objects.create(
                nome=f"{tipo} de {disciplina.nome}",
                disciplina=disciplina,
                turma=random.choice(turmas),
                tipo=tipo,
                data=data_avaliacao.date(),
                periodo=random.choice(periodos),
                peso=random.choice([1, 2, 3])
            )
            
            avaliacoes_criadas.append(avaliacao)
            print(f"Avaliação criada: {avaliacao.nome} - {avaliacao.tipo} - Disciplina: {avaliacao.disciplina.nome}")
    
    return avaliacoes_criadas

def lancar_notas(avaliacoes):
    """Lança notas para os alunos nas avaliações"""
    notas_criadas = []
    
    # Obter todos os alunos
    alunos = list(Aluno.objects.all())
    if not alunos:
        print("Não há alunos cadastrados no sistema.")
        return []
    
    for avaliacao in avaliacoes:
        # Para cada avaliação, atribuir notas a todos os alunos
        for aluno in alunos:
            # Gera uma nota entre 0 e 10, com uma casa decimal
            valor_nota = round(random.uniform(0, 10), 1)
            
            nota = Nota.objects.create(
                aluno=aluno,
                avaliacao=avaliacao,
                valor=Decimal(str(valor_nota)),
                observacao=fake.sentence(nb_words=10) if random.random() > 0.7 else "",
                data_lancamento=datetime.now().date()
            )
            
            notas_criadas.append(nota)
            print(f"Nota lançada: Aluno: {aluno.nome} - Avaliação: {avaliacao.nome} - Valor: {nota.valor}")
    
    return notas_criadas

def popular_notas():
    """Função principal para popular o app de notas"""
    print("Iniciando população do app de notas...")
    
    # Verifica se já existem dados para evitar duplicação
    if Disciplina.objects.exists():
        print("Já existem disciplinas no banco de dados. Limpando dados existentes...")
        Nota.objects.all().delete()
        Avaliacao.objects.all().delete()
        Disciplina.objects.all().delete()
    
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
    
    # Verificar modelos antes de prosseguir
    if verificar_modelos():
        popular_notas()
    else:
        print("Verifique os modelos antes de continuar.")
    
    print("Processo finalizado!")
