from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random
from faker import Faker

from usuarios.models import PerfilUsuario, TipoUsuario
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma, TurmaAluno, TurmaProfessor
from notas.models import Disciplina, Avaliacao, Nota
from financeiro.models import Mensalidade
from responsaveis.models import Responsavel
from matriculas.models import MatriculaOnline

fake = Faker('pt_BR')

class Command(BaseCommand):
    help = 'Popula o sistema completo com dados realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpando dados existentes...')
            self.clear_data()

        self.stdout.write('Iniciando população do sistema...')
        
        # 1. Criar professores
        self.stdout.write('Criando professores...')
        professores = self.criar_professores()
        
        # 2. Criar disciplinas
        self.stdout.write('Criando disciplinas...')
        disciplinas = self.criar_disciplinas()
        
        # 3. Criar turmas
        self.stdout.write('Criando turmas...')
        turmas = self.criar_turmas(professores)
        
        # 4. Criar responsáveis
        self.stdout.write('Criando responsáveis...')
        responsaveis = self.criar_responsaveis()
        
        # 5. Criar alunos
        self.stdout.write('Criando alunos...')
        alunos = self.criar_alunos(responsaveis)
        
        # 6. Matricular alunos nas turmas
        self.stdout.write('Matriculando alunos...')
        self.matricular_alunos(alunos, turmas)
        
        # 7. Associar professores às disciplinas
        self.stdout.write('Associando professores às disciplinas...')
        self.associar_professores_disciplinas(professores, disciplinas, turmas)
        
        # 8. Criar avaliações e notas
        self.stdout.write('Criando avaliações e notas...')
        self.criar_avaliacoes_notas(disciplinas, turmas, alunos)
        
        # 9. Gerar mensalidades
        self.stdout.write('Gerando mensalidades...')
        self.gerar_mensalidades(alunos)
        
        # 10. Criar matrículas online
        self.stdout.write('Criando matrículas online...')
        self.criar_matriculas_online()
        
        self.stdout.write(
            self.style.SUCCESS('Sistema populado com sucesso!')
        )

    def clear_data(self):
        """Remove dados existentes preservando admin"""
        # Preservar usuário admin
        admin_users = User.objects.filter(is_superuser=True)
        
        # Deletar dados relacionados
        Nota.objects.all().delete()
        Avaliacao.objects.all().delete()
        TurmaProfessor.objects.all().delete()
        TurmaAluno.objects.all().delete()
        Mensalidade.objects.all().delete()
        MatriculaOnline.objects.all().delete()
        
        # Deletar modelos principais (exceto admin)
        Aluno.objects.all().delete()
        Professor.objects.all().delete()
        Responsavel.objects.all().delete()
        Turma.objects.all().delete()
        Disciplina.objects.all().delete()
        
        # Deletar usuários não-admin
        User.objects.exclude(is_superuser=True).delete()

    def criar_professores(self):
        """Cria professores com usuários"""
        professores = []
        nomes_professores = [
            'Ana Maria Silva', 'Carlos Roberto Santos', 'Maria José Oliveira',
            'João Pedro Lima', 'Fernanda Costa', 'Ricardo Almeida',
            'Juliana Ferreira', 'Paulo Henrique', 'Carla Rodrigues',
            'André Luiz Souza', 'Patrícia Gomes', 'Felipe Martins',
            'Luciana Barbosa', 'Rafael Torres', 'Cristina Pereira'
        ]
        
        disciplinas_professores = [
            'Matemática', 'Português', 'História', 'Geografia',
            'Ciências', 'Educação Física', 'Inglês', 'Artes',
            'Física', 'Química', 'Biologia', 'Filosofia',
            'Sociologia', 'Matemática', 'Português'
        ]
        
        for i, nome in enumerate(nomes_professores):
            # Criar usuário
            username = f'prof{i+1:02d}'
            user = User.objects.create_user(
                username=username,
                email=f'{username}@escola.com',
                password='123456',
                first_name=nome.split()[0],
                last_name=' '.join(nome.split()[1:])
            )
            
            # Obter ou criar perfil (signal já cria automaticamente)
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={'tipo_usuario': TipoUsuario.PROFESSOR}
            )
            if not created:
                perfil.tipo_usuario = TipoUsuario.PROFESSOR
                perfil.save()
            
            # Criar professor
            professor = Professor.objects.create(
                nome=nome,
                email=f'{username}@escola.com',
                telefone=fake.phone_number(),
                formacao=random.choice([
                    'Licenciatura em Matemática',
                    'Licenciatura em Português',
                    'Licenciatura em História',
                    'Licenciatura em Geografia',
                    'Licenciatura em Ciências',
                    'Licenciatura em Educação Física',
                    'Licenciatura em Inglês',
                    'Licenciatura em Artes'
                ]),
                disciplina=disciplinas_professores[i],
                usuario=user
            )
            professores.append(professor)
            
        return professores

    def criar_disciplinas(self):
        """Cria disciplinas básicas"""
        disciplinas_data = [
            ('Matemática', 'MAT'),
            ('Português', 'POR'),
            ('História', 'HIS'),
            ('Geografia', 'GEO'),
            ('Ciências', 'CIE'),
            ('Educação Física', 'EDF'),
            ('Inglês', 'ING'),
            ('Artes', 'ART'),
            ('Física', 'FIS'),
            ('Química', 'QUI'),
            ('Biologia', 'BIO'),
            ('Filosofia', 'FIL'),
            ('Sociologia', 'SOC')
        ]
        
        disciplinas = []
        for nome, codigo in disciplinas_data:
            disciplina, created = Disciplina.objects.get_or_create(
                nome=nome,
                defaults={
                    'codigo': codigo,
                    'carga_horaria': random.choice([40, 60, 80]),
                    'ementa': f'Ementa da disciplina {nome}',
                }
            )
            disciplinas.append(disciplina)
            
        return disciplinas

    def criar_turmas(self, professores):
        """Cria turmas para diferentes séries"""
        turmas = []
        series = ['1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano', '6º Ano', '7º Ano', '8º Ano', '9º Ano']
        turnos = ['Matutino', 'Vespertino']
        
        for serie in series:
            for turno in turnos:
                for turma_letra in ['A', 'B']:
                    nome = f'{serie} {turma_letra}'
                    
                    turma = Turma.objects.create(
                        nome=nome,
                        serie=serie,
                        turno=turno,
                        ano_letivo=timezone.now().year,
                        capacidade=random.randint(25, 35)
                    )
                    
                    # Associar professor regente aleatório
                    professor_regente = random.choice(professores)
                    TurmaProfessor.objects.create(
                        turma=turma,
                        professor=professor_regente,
                        disciplina=professor_regente.disciplina
                    )
                    
                    turmas.append(turma)
                    
        return turmas

    def criar_responsaveis(self):
        """Cria responsáveis com usuários"""
        responsaveis = []
        
        for i in range(50):  # Criar 50 responsáveis
            nome = fake.name()
            username = f'resp{i+1:03d}'
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=f'{username}@email.com',
                password='123456',
                first_name=nome.split()[0],
                last_name=' '.join(nome.split()[1:])
            )
            
            # Obter ou criar perfil (signal já cria automaticamente)
            perfil, created = PerfilUsuario.objects.get_or_create(
                user=user,
                defaults={'tipo_usuario': TipoUsuario.RESPONSAVEL}
            )
            if not created:
                perfil.tipo_usuario = TipoUsuario.RESPONSAVEL
                perfil.save()
            
            # Criar responsável
            responsavel = Responsavel.objects.create(
                nome=nome,
                cpf=fake.cpf(),
                rg=fake.rg(),
                data_nascimento=fake.date_between(start_date='-60y', end_date='-25y'),
                telefone=fake.phone_number(),
                email=f'{username}@email.com',
                endereco=fake.address()[:200],  # Limitar tamanho
                bairro=fake.neighborhood()[:100],
                cidade=fake.city()[:100],
                estado=fake.state_abbr(),
                cep=fake.postcode()
            )
            responsaveis.append(responsavel)
            
        return responsaveis

    def criar_alunos(self, responsaveis):
        """Cria alunos e associa aos responsáveis"""
        alunos = []
        
        for i in range(150):  # Criar 150 alunos
            nome = fake.name()
            username = f'aluno{i+1:03d}'
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=f'{username}@aluno.escola.com',
                password='123456',
                first_name=nome.split()[0],
                last_name=' '.join(nome.split()[1:])
            )
            
            # Obter perfil criado pelo signal
            perfil = PerfilUsuario.objects.get(user=user)
            perfil.tipo_usuario = TipoUsuario.FUNCIONARIO  # Usar como padrão pois não há tipo aluno
            perfil.save()
            
            # Criar aluno
            aluno = Aluno.objects.create(
                nome=nome,
                data_nascimento=fake.date_between(start_date='-18y', end_date='-6y'),
                matricula=f'2025{i+1:03d}',
                cpf=fake.cpf(),
                rg=fake.rg(),
                telefone=fake.phone_number(),
                email=f'{username}@aluno.escola.com',
                endereco=fake.address()[:200],
                bairro=fake.neighborhood()[:100] if hasattr(fake, 'neighborhood') else fake.city()[:100],
                cidade=fake.city()[:100],
                estado=fake.state_abbr(),
                cep=fake.postcode(),
                responsavel_nome=fake.name(),
                responsavel_telefone=fake.phone_number(),
                observacoes=fake.text(max_nb_chars=100) if random.choice([True, False]) else '',
                status='ativo'
            )
            
            # Associar responsável aleatório
            responsavel = random.choice(responsaveis)
            from responsaveis.models import ResponsavelAluno
            ResponsavelAluno.objects.create(
                responsavel=responsavel,
                aluno=aluno,
                tipo_relacao=random.choice(['mae', 'pai', 'responsavel_legal'])
            )
            
            alunos.append(aluno)
            
        return alunos

    def matricular_alunos(self, alunos, turmas):
        """Matricula alunos nas turmas"""
        for aluno in alunos:
            # Escolher turma baseada na idade do aluno
            idade = (timezone.now().date() - aluno.data_nascimento).days // 365
            
            if idade <= 7:
                turmas_adequadas = [t for t in turmas if '1º Ano' in t.nome or '2º Ano' in t.nome]
            elif idade <= 9:
                turmas_adequadas = [t for t in turmas if '3º Ano' in t.nome or '4º Ano' in t.nome]
            elif idade <= 11:
                turmas_adequadas = [t for t in turmas if '5º Ano' in t.nome or '6º Ano' in t.nome]
            else:
                turmas_adequadas = [t for t in turmas if '7º Ano' in t.nome or '8º Ano' in t.nome or '9º Ano' in t.nome]
            
            if turmas_adequadas:
                turma = random.choice(turmas_adequadas)
                # Verificar se a turma não está lotada
                if turma.alunos_matriculados.count() < turma.capacidade:
                    TurmaAluno.objects.create(
                        turma=turma,
                        aluno=aluno,
                        ativo=True
                    )

    def associar_professores_disciplinas(self, professores, disciplinas, turmas):
        """Associa professores às disciplinas nas turmas"""
        for turma in turmas:
            # Escolher disciplinas adequadas para a série
            if any(ano in turma.serie for ano in ['1º', '2º', '3º', '4º', '5º']):
                # Ensino fundamental I - menos disciplinas
                disciplinas_turma = [d for d in disciplinas if d.nome in [
                    'Português', 'Matemática', 'Ciências', 'História', 'Geografia', 'Educação Física', 'Artes'
                ]]
            else:
                # Ensino fundamental II - mais disciplinas
                disciplinas_turma = disciplinas
            
            for disciplina in disciplinas_turma:
                # Encontrar professor especialista na disciplina
                professores_especialistas = [p for p in professores if p.disciplina == disciplina.nome]
                if not professores_especialistas:
                    professores_especialistas = professores
                
                professor = random.choice(professores_especialistas)
                
                # Verificar se já não existe essa associação
                if not TurmaProfessor.objects.filter(turma=turma, professor=professor, disciplina=disciplina.nome).exists():
                    TurmaProfessor.objects.create(
                        turma=turma,
                        professor=professor,
                        disciplina=disciplina.nome
                    )

    def criar_avaliacoes_notas(self, disciplinas, turmas, alunos):
        """Cria avaliações e notas para as disciplinas"""
        tipos_avaliacao = ['prova', 'trabalho', 'projeto', 'participacao']
        periodos = ['1', '2', '3', '4']
        
        for turma in turmas:
            # Obter disciplinas da turma
            professores_turma = TurmaProfessor.objects.filter(turma=turma)
            alunos_turma = TurmaAluno.objects.filter(turma=turma, ativo=True)
            
            for tp in professores_turma:
                professor = tp.professor
                # Usar a disciplina da associação TurmaProfessor
                disciplina_nome = tp.disciplina
                if disciplina_nome:
                    disciplinas_professor = [d for d in disciplinas if d.nome == disciplina_nome]
                else:
                    disciplinas_professor = [d for d in disciplinas if d.nome == professor.disciplina]
                
                if not disciplinas_professor:
                    disciplinas_professor = disciplinas[:3]  # Pegar algumas disciplinas
                
                for disciplina in disciplinas_professor:
                    # Criar 4 avaliações por disciplina (uma por bimestre)
                    for periodo in periodos:
                        avaliacao = Avaliacao.objects.create(
                            nome=f'{random.choice(tipos_avaliacao).title()} {periodo}º Bimestre',
                            disciplina=disciplina,
                            turma=turma,
                            tipo=random.choice(tipos_avaliacao),
                            data=fake.date_between(start_date='-3m', end_date='today'),
                            periodo=periodo,
                            peso=random.randint(1, 3)
                        )
                        
                        # Criar notas para cada aluno da turma
                        for ta in alunos_turma:
                            aluno = ta.aluno
                            nota_valor = round(random.uniform(5.0, 10.0), 1)
                            
                            Nota.objects.create(
                                avaliacao=avaliacao,
                                aluno=aluno,
                                valor=nota_valor,
                                observacao=fake.text(max_nb_chars=50) if random.choice([True, False, False]) else ''
                            )

    def gerar_mensalidades(self, alunos):
        """Gera mensalidades para os alunos"""
        ano_atual = timezone.now().year
        valores_mensalidade = [350.00, 400.00, 450.00, 500.00]
        
        for aluno in alunos:
            valor_base = random.choice(valores_mensalidade)
            
            # Gerar mensalidades do ano inteiro (12 meses)
            for mes in range(1, 13):
                # Data de vencimento: dia 10 de cada mês
                data_vencimento = datetime(ano_atual, mes, 10).date()
                
                # Determinar status baseado na data
                if data_vencimento < timezone.now().date():
                    # Mensalidades passadas - 80% pagas, 20% pendentes/vencidas
                    if random.random() < 0.8:
                        status = 'pago'
                        data_pagamento = data_vencimento + timedelta(days=random.randint(-5, 15))
                    else:
                        status = 'vencido'
                        data_pagamento = None
                else:
                    # Mensalidades futuras - pendentes
                    status = 'pendente'
                    data_pagamento = None
                
                Mensalidade.objects.create(
                    aluno=aluno,
                    mes_referencia=mes,
                    ano_referencia=ano_atual,
                    valor_total=valor_base,
                    data_vencimento=data_vencimento,
                    data_pagamento=data_pagamento,
                    status=status,
                    observacoes=fake.text(max_nb_chars=50) if random.choice([True, False, False, False]) else ''
                )

    def criar_matriculas_online(self):
        """Cria algumas matrículas online pendentes"""
        for i in range(10):
            MatriculaOnline.objects.create(
                nome_aluno=fake.name(),
                data_nascimento=fake.date_between(start_date='-12y', end_date='-6y'),
                nome_responsavel=fake.name(),
                telefone_responsavel=fake.phone_number(),
                email_responsavel=fake.email(),
                serie_pretendida=random.choice([
                    '1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano',
                    '6º Ano', '7º Ano', '8º Ano', '9º Ano'
                ]),
                turno_preferido=random.choice(['Matutino', 'Vespertino']),
                observacoes=fake.text(max_nb_chars=100) if random.choice([True, False]) else '',
                status=random.choice(['pendente', 'analisando', 'aprovada', 'rejeitada']),
                data_solicitacao=fake.date_time_between(start_date='-1m', end_date='now', tzinfo=timezone.get_current_timezone())
            ) 