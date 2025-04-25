import os
import django
import random
from datetime import date, timedelta

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importar depois de configurar o ambiente
from faker import Faker
from django.contrib.auth.models import User
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma
from django.db import transaction

fake = Faker('pt_BR')

# Configurações
NUM_ALUNOS = 50
NUM_PROFESSORES = 10
NUM_TURMAS = 5
SERIES = ['1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano', '6º Ano', '7º Ano', '8º Ano', '9º Ano', '1º EM', '2º EM', '3º EM']
TURNOS = ['Manhã', 'Tarde', 'Noite']
DISCIPLINAS = ['Matemática', 'Português', 'História', 'Geografia', 'Ciências', 'Física', 'Química', 'Biologia', 'Educação Física', 'Artes', 'Inglês', 'Espanhol']

def gerar_data_nascimento(min_idade=6, max_idade=18):
    """Gera uma data de nascimento aleatória para idades entre min_idade e max_idade"""
    hoje = date.today()
    idade = random.randint(min_idade, max_idade)
    dias_aleatorios = random.randint(0, 365)
    data_nascimento = hoje - timedelta(days=(idade * 365) + dias_aleatorios)
    return data_nascimento

@transaction.atomic
def criar_turmas():
    """Cria turmas aleatórias"""
    turmas = []
    for _ in range(NUM_TURMAS):
        serie = random.choice(SERIES)
        letra = chr(random.randint(65, 70))  # A a F
        turno = random.choice(TURNOS)
        ano_letivo = random.randint(2023, 2025)
        
        nome = f"{serie} {letra} - {turno}"
        
        turma = Turma.objects.create(
            nome=nome,
            serie=serie,
            turno=turno,
            ano_letivo=ano_letivo,
            capacidade=random.randint(20, 40)
        )
        turmas.append(turma)
    return turmas

@transaction.atomic
def criar_professores(turmas):
    """Cria professores aleatórios e associa a turmas"""
    professores = []
    for i in range(NUM_PROFESSORES):
        nome = fake.name()
        email = fake.email()
        telefone = fake.phone_number()
        formacao = random.choice(['Licenciatura', 'Bacharelado', 'Mestrado', 'Doutorado'])
        disciplina = random.choice(DISCIPLINAS)
        
        # Cria um usuário para o professor
        username = f"prof_{i+1}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password="senha123",
            first_name=nome.split()[0],
            last_name=" ".join(nome.split()[1:])
        )
        
        professor = Professor.objects.create(
            usuario=user,
            nome=nome,
            email=email,
            telefone=telefone,
            formacao=formacao,
            disciplina=disciplina
        )
        
        # Associa o professor a algumas turmas aleatórias
        num_turmas = random.randint(1, 3)
        turmas_aleatorias = random.sample(turmas, min(num_turmas, len(turmas)))
        for turma in turmas_aleatorias:
            professor.turmas.add(turma)
        
        professores.append(professor)
    return professores

@transaction.atomic
def criar_alunos(turmas):
    """Cria alunos aleatórios e associa a turmas"""
    for i in range(NUM_ALUNOS):
        nome = fake.name()
        data_nascimento = gerar_data_nascimento()
        email = fake.email()
        telefone = fake.phone_number()
        endereco = fake.address()
        responsavel = fake.name()
        telefone_responsavel = fake.phone_number()
        
        # Cria um usuário para o aluno
        username = f"aluno_{i+1}"
        user = User.objects.create_user(
            username=username,
            email=email,
            password="senha123",
            first_name=nome.split()[0],
            last_name=" ".join(nome.split()[1:])
        )
        
        # Escolhe uma turma aleatória
        turma = random.choice(turmas)
        
        aluno = Aluno.objects.create(
            usuario=user,
            nome=nome,
            data_nascimento=data_nascimento,
            email=email,
            telefone=telefone,
            endereco=endereco,
            responsavel=responsavel,
            telefone_responsavel=telefone_responsavel,
            turma=turma
        )

def limpar_banco():
    """Limpa os dados existentes"""
    print("Limpando banco de dados...")
    Aluno.objects.all().delete()
    Professor.objects.all().delete()
    Turma.objects.all().delete()
    # Não exclui superusuários
    User.objects.filter(is_superuser=False).delete()

def popular_banco():
    """Popula o banco de dados com dados falsos"""
    print("Populando banco de dados...")
    print("Criando turmas...")
    turmas = criar_turmas()
    print(f"{len(turmas)} turmas criadas!")
    
    print("Criando professores...")
    professores = criar_professores(turmas)
    print(f"{len(professores)} professores criados!")
    
    print("Criando alunos...")
    criar_alunos(turmas)
    print(f"{NUM_ALUNOS} alunos criados!")
    
    print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    limpar_banco()
    popular_banco()
