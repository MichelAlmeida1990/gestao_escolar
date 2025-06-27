import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker

# Importar todos os modelos
from alunos.models import Aluno
from responsaveis.models import Responsavel, ResponsavelAluno
from professores.models import Professor
from turmas.models import Turma
from notas.models import Disciplina, Avaliacao, Nota
from biblioteca.models import Autor, Categoria, Editora, Livro, Emprestimo, Reserva, ConfiguracaoBiblioteca
from financeiro.models import Mensalidade, PlanoContas, CategoriaFinanceira, ConfiguracaoFinanceira
from frequencia.models import RegistroFrequencia, RelatorioFrequencia, JustificativaFalta
from comunicados.models import Comunicado


class Command(BaseCommand):
    help = 'Popula todo o sistema escolar com dados realistas'

    def __init__(self):
        super().__init__()
        self.fake = Faker('pt_BR')

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa todos os dados antes de popular',
        )
        parser.add_argument(
            '--alunos',
            type=int,
            default=30,
            help='Número de alunos a criar (padrão: 30)',
        )

    def handle(self, *args, **options):
        if options['limpar']:
            self.limpar_dados()
        
        self.stdout.write(self.style.SUCCESS('🎓 Iniciando população do sistema escolar...'))
        
        with transaction.atomic():
            # 1. Criar configurações básicas
            self.criar_configuracoes()
            
            # 2. Criar dados acadêmicos básicos
            disciplinas = self.criar_disciplinas()
            turmas = self.criar_turmas()
            
            # 3. Criar usuários e pessoas
            responsaveis = self.criar_responsaveis(30)
            professores = self.criar_professores(10, disciplinas, turmas)
            alunos = self.criar_alunos(options['alunos'], turmas, responsaveis)
            
            # 4. Criar dados de biblioteca
            autores, editoras, categorias = self.criar_dados_biblioteca()
            livros = self.criar_livros(autores, editoras, categorias, 50)
            self.criar_emprestimos_reservas(livros, alunos, professores)
            
            # 5. Criar dados financeiros
            self.criar_dados_financeiros(alunos)
            
            # 6. Criar dados de frequência
            self.criar_dados_frequencia(alunos, turmas)
            
            # 7. Criar dados de avaliações e notas
            avaliacoes = self.criar_avaliacoes(disciplinas, turmas, professores)
            self.criar_notas(avaliacoes, alunos)
            
            # 8. Criar comunicados
            self.criar_comunicados(professores, turmas)
        
        self.stdout.write(self.style.SUCCESS('✅ Sistema populado com sucesso!'))

    def limpar_dados(self):
        """Limpa todos os dados do sistema (exceto superusuários)"""
        self.stdout.write('🧹 Limpando dados existentes...')
        
        # Ordem de exclusão baseada nas dependências
        RegistroFrequencia.objects.all().delete()
        RelatorioFrequencia.objects.all().delete()
        JustificativaFalta.objects.all().delete()
        
        Nota.objects.all().delete()
        Avaliacao.objects.all().delete()
        
        Emprestimo.objects.all().delete()
        Reserva.objects.all().delete()
        Livro.objects.all().delete()
        Autor.objects.all().delete()
        Editora.objects.all().delete()
        Categoria.objects.all().delete()
        
        Mensalidade.objects.all().delete()
        PlanoContas.objects.all().delete()
        CategoriaFinanceira.objects.all().delete()
        
        Comunicado.objects.all().delete()
        
        ResponsavelAluno.objects.all().delete()
        Aluno.objects.all().delete()
        Responsavel.objects.all().delete()
        Professor.objects.all().delete()
        
        Disciplina.objects.all().delete()
        Turma.objects.all().delete()
        
        # Excluir usuários não-superusuários
        User.objects.filter(is_superuser=False).delete()

    def criar_configuracoes(self):
        """Cria configurações básicas do sistema"""
        self.stdout.write('⚙️ Criando configurações...')
        
        # Configuração da biblioteca
        ConfiguracaoBiblioteca.objects.get_or_create(
            prazo_emprestimo_dias=15,
            renovacoes_maximas=2,
            multa_por_dia=Decimal('2.00'),
            livros_por_pessoa=3
        )
        
        # Configuração financeira
        ConfiguracaoFinanceira.objects.get_or_create(
            valor_mensalidade_padrao=Decimal('350.00'),
            dia_vencimento=10,
            juros_por_dia=Decimal('0.10'),
            desconto_pontualidade=Decimal('5.00')
        )

    def criar_disciplinas(self):
        """Cria disciplinas do currículo"""
        self.stdout.write('📚 Criando disciplinas...')
        
        disciplinas_data = [
            ('Português', 'PORT001', 120, 'Língua Portuguesa e Literatura'),
            ('Matemática', 'MAT001', 120, 'Matemática Fundamental e Aplicada'),
            ('História', 'HIS001', 80, 'História Geral e do Brasil'),
            ('Geografia', 'GEO001', 80, 'Geografia Física e Humana'),
            ('Ciências', 'CIE001', 100, 'Ciências Naturais'),
            ('Física', 'FIS001', 100, 'Física Básica e Aplicada'),
            ('Química', 'QUI001', 100, 'Química Geral e Orgânica'),
            ('Biologia', 'BIO001', 100, 'Biologia Geral e Molecular'),
            ('Educação Física', 'EDF001', 80, 'Educação Física e Esportes'),
            ('Artes', 'ART001', 60, 'Artes Visuais e História da Arte'),
            ('Inglês', 'ING001', 80, 'Língua Inglesa'),
            ('Filosofia', 'FIL001', 60, 'Filosofia e Ética'),
            ('Sociologia', 'SOC001', 60, 'Sociologia e Cidadania'),
        ]
        
        disciplinas = []
        for nome, codigo, carga, ementa in disciplinas_data:
            disciplina, created = Disciplina.objects.get_or_create(
                codigo=codigo,
                defaults={'nome': nome, 'carga_horaria': carga, 'ementa': ementa}
            )
            disciplinas.append(disciplina)
        
        return disciplinas

    def criar_turmas(self):
        """Cria turmas por série e turno"""
        self.stdout.write('🏫 Criando turmas...')
        
        series = [
            ('1º Ano EF', '1EF'), ('2º Ano EF', '2EF'), ('3º Ano EF', '3EF'),
            ('4º Ano EF', '4EF'), ('5º Ano EF', '5EF'), ('6º Ano EF', '6EF'),
            ('7º Ano EF', '7EF'), ('8º Ano EF', '8EF'), ('9º Ano EF', '9EF'),
            ('1º Ano EM', '1EM'), ('2º Ano EM', '2EM'), ('3º Ano EM', '3EM'),
        ]
        
        turnos = ['Manhã', 'Tarde', 'Noite']
        letras = ['A', 'B']
        
        turmas = []
        for serie_nome, serie_codigo in series:
            for turno in turnos:
                for letra in letras:
                    # Não criar todas as combinações, apenas algumas
                    if random.random() > 0.7:  # 30% de chance de criar
                        continue
                        
                    nome = f"{serie_nome} {letra} - {turno}"
                    turma = Turma.objects.create(
                        nome=nome,
                        serie=serie_nome,
                        turno=turno,
                        ano_letivo=2025,
                        capacidade=random.randint(25, 35)
                    )
                    turmas.append(turma)
        
        self.stdout.write(f'✅ {len(turmas)} turmas criadas')
        return turmas

    def criar_responsaveis(self, quantidade):
        """Cria responsáveis realistas"""
        self.stdout.write(f'👨‍👩‍👧‍👦 Criando {quantidade} responsáveis...')
        
        responsaveis = []
        for i in range(quantidade):
            nome = self.fake.name()
            username = f"resp_{i+1:03d}"
            email = self.fake.email()
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password='senha123',
                first_name=nome.split()[0],
                last_name=' '.join(nome.split()[1:])
            )
            
            # Gerar telefone no formato correto
            telefone = f"(11) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
            
            responsavel = Responsavel.objects.create(
                usuario=user,
                nome=nome,
                email=email,
                telefone=telefone,
                endereco=self.fake.address(),
                cpf=self.fake.cpf(),
                rg=self.fake.rg(),
                profissao=self.fake.job(),
                renda_familiar=Decimal(random.randint(2000, 15000))
            )
            responsaveis.append(responsavel)
        
        return responsaveis

    def criar_professores(self, quantidade, disciplinas, turmas):
        """Cria professores e associa a disciplinas e turmas"""
        self.stdout.write(f'👨‍🏫 Criando {quantidade} professores...')
        
        formacoes = ['Licenciatura', 'Bacharelado', 'Especialização', 'Mestrado', 'Doutorado']
        professores = []
        
        for i in range(quantidade):
            nome = self.fake.name()
            username = f"prof_{i+1:03d}"
            email = self.fake.email()
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password='senha123',
                first_name=nome.split()[0],
                last_name=' '.join(nome.split()[1:]),
                is_staff=True  # Professores são staff
            )
            
            telefone = f"(11) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
            disciplina_principal = random.choice(disciplinas)
            
            professor = Professor.objects.create(
                usuario=user,
                nome=nome,
                email=email,
                telefone=telefone,
                formacao=random.choice(formacoes),
                disciplina=disciplina_principal.nome,
                data_admissao=self.fake.date_between(start_date='-10y', end_date='today'),
                salario=Decimal(random.randint(3000, 8000))
            )
            
            # Associar a turmas aleatórias
            num_turmas = random.randint(2, min(5, len(turmas)))
            turmas_escolhidas = random.sample(turmas, num_turmas)
            professor.turmas.set(turmas_escolhidas)
            
            professores.append(professor)
        
        return professores

    def criar_alunos(self, quantidade, turmas, responsaveis):
        """Cria alunos e associa a responsáveis e turmas"""
        self.stdout.write(f'👨‍🎓 Criando {quantidade} alunos...')
        
        status_choices = ['ativo', 'inativo', 'transferido', 'formado']
        alunos = []
        
        for i in range(quantidade):
            nome = self.fake.name()
            username = f"aluno_{i+1:03d}"
            email = self.fake.email()
            
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password='senha123',
                first_name=nome.split()[0],
                last_name=' '.join(nome.split()[1:])
            )
            
            # Data de nascimento entre 6 e 18 anos
            idade = random.randint(6, 18)
            data_nascimento = date.today() - timedelta(days=idade * 365 + random.randint(0, 365))
            
            telefone = f"(11) {random.randint(90000, 99999)}-{random.randint(1000, 9999)}"
            turma = random.choice(turmas)
            
            aluno = Aluno.objects.create(
                usuario=user,
                nome=nome,
                data_nascimento=data_nascimento,
                email=email,
                telefone=telefone,
                endereco=self.fake.address(),
                matricula=f"MAT{2025}{i+1:04d}",
                turma=turma,
                status=random.choice(status_choices) if random.random() > 0.8 else 'ativo',
                data_matricula=self.fake.date_between(start_date='-2y', end_date='today')
            )
            
            # Associar a 1-2 responsáveis
            num_responsaveis = random.choice([1, 1, 1, 2])  # Mais provável ter 1 responsável
            responsaveis_escolhidos = random.sample(responsaveis, num_responsaveis)
            
            for j, responsavel in enumerate(responsaveis_escolhidos):
                parentesco = 'pai' if j == 0 else random.choice(['mãe', 'avô', 'avó', 'tio', 'tia'])
                ResponsavelAluno.objects.create(
                    responsavel=responsavel,
                    aluno=aluno,
                    parentesco=parentesco,
                    autorizado_buscar=True
                )
            
            alunos.append(aluno)
        
        return alunos

    def criar_dados_biblioteca(self):
        """Cria autores, editoras e categorias para a biblioteca"""
        self.stdout.write('📖 Criando dados da biblioteca...')
        
        # Autores famosos
        autores_data = [
            'Machado de Assis', 'José de Alencar', 'Lima Barreto', 'Clarice Lispector',
            'Guimarães Rosa', 'Rachel de Queiroz', 'Jorge Amado', 'Érico Veríssimo',
            'Monteiro Lobato', 'Cecília Meireles', 'Carlos Drummond de Andrade',
            'Vinícius de Moraes', 'William Shakespeare', 'Charles Dickens',
            'Gabriel García Márquez', 'Paulo Coelho', 'Agatha Christie'
        ]
        
        autores = []
        for nome in autores_data:
            autor = Autor.objects.create(
                nome=nome,
                biografia=self.fake.paragraph(nb_sentences=3),
                data_nascimento=self.fake.date_between(start_date='-150y', end_date='-20y')
            )
            autores.append(autor)
        
        # Editoras
        editoras_data = [
            'Editora Ática', 'Saraiva', 'FTD', 'Moderna', 'Scipione',
            'Companhia das Letras', 'Record', 'Globo Livros', 'Planeta',
            'Rocco', 'Intrínseca', 'Penguin Classics'
        ]
        
        editoras = []
        for nome in editoras_data:
            editora = Editora.objects.create(
                nome=nome,
                endereco=self.fake.address(),
                telefone=f"(11) {random.randint(3000, 3999)}-{random.randint(1000, 9999)}",
                email=f"contato@{nome.lower().replace(' ', '')}.com.br"
            )
            editoras.append(editora)
        
        # Categorias
        categorias_data = [
            'Literatura Brasileira', 'Literatura Estrangeira', 'Didáticos',
            'Paradidáticos', 'Ficção Científica', 'Romance', 'Biografia',
            'História', 'Geografia', 'Ciências', 'Matemática', 'Filosofia',
            'Sociologia', 'Arte', 'Educação Física', 'Idiomas'
        ]
        
        categorias = []
        for nome in categorias_data:
            categoria = Categoria.objects.create(
                nome=nome,
                descricao=f"Livros da categoria {nome}"
            )
            categorias.append(categoria)
        
        return autores, editoras, categorias

    def criar_livros(self, autores, editoras, categorias, quantidade):
        """Cria livros para a biblioteca"""
        self.stdout.write(f'📚 Criando {quantidade} livros...')
        
        livros = []
        for i in range(quantidade):
            titulo = self.fake.sentence(nb_words=random.randint(2, 6)).rstrip('.')
            autor = random.choice(autores)
            editora = random.choice(editoras)
            categoria = random.choice(categorias)
            
            # ISBN simulado
            isbn = f"978-{random.randint(10, 99)}-{random.randint(1000, 9999)}-{random.randint(100, 999)}-{random.randint(0, 9)}"
            
            livro = Livro.objects.create(
                titulo=titulo,
                autor=autor,
                editora=editora,
                categoria=categoria,
                isbn=isbn,
                ano_publicacao=random.randint(1950, 2025),
                numero_paginas=random.randint(50, 800),
                exemplares_total=random.randint(1, 5),
                exemplares_disponiveis=random.randint(0, 5),
                localizacao=f"Estante {random.randint(1, 20)}, Prateleira {random.choice(['A', 'B', 'C', 'D'])}",
                sinopse=self.fake.paragraph(nb_sentences=4)
            )
            livros.append(livro)
        
        return livros

    def criar_emprestimos_reservas(self, livros, alunos, professores):
        """Cria empréstimos e reservas na biblioteca"""
        self.stdout.write('📋 Criando empréstimos e reservas...')
        
        usuarios = alunos + professores
        
        # Empréstimos
        for _ in range(20):
            usuario = random.choice(usuarios)
            livro = random.choice(livros)
            
            if livro.exemplares_disponiveis > 0:
                data_emprestimo = self.fake.date_between(start_date='-30d', end_date='today')
                data_prevista = data_emprestimo + timedelta(days=15)
                
                emprestimo = Emprestimo.objects.create(
                    usuario=usuario.usuario,
                    livro=livro,
                    data_emprestimo=data_emprestimo,
                    data_prevista_devolucao=data_prevista,
                    status=random.choice(['ativo', 'devolvido', 'atrasado']),
                    renovacoes=random.randint(0, 2)
                )
                
                if emprestimo.status == 'devolvido':
                    emprestimo.data_devolucao = self.fake.date_between(
                        start_date=data_emprestimo,
                        end_date=data_prevista + timedelta(days=5)
                    )
                    emprestimo.save()
                else:
                    livro.exemplares_disponiveis -= 1
                    livro.save()
        
        # Reservas
        for _ in range(10):
            usuario = random.choice(usuarios)
            livro = random.choice([l for l in livros if l.exemplares_disponiveis == 0])
            
            if livro:
                Reserva.objects.create(
                    usuario=usuario.usuario,
                    livro=livro,
                    data_reserva=self.fake.date_between(start_date='-15d', end_date='today'),
                    status=random.choice(['ativa', 'cancelada', 'atendida'])
                )

    def criar_dados_financeiros(self, alunos):
        """Cria dados financeiros do sistema"""
        self.stdout.write('💰 Criando dados financeiros...')
        
        # Categorias financeiras
        categorias_data = [
            ('Mensalidades', 'receita', 'Receitas com mensalidades escolares'),
            ('Material Escolar', 'receita', 'Receitas com material escolar'),
            ('Atividades Extras', 'receita', 'Receitas com atividades extracurriculares'),
            ('Salários', 'despesa', 'Pagamento de salários'),
            ('Manutenção', 'despesa', 'Despesas com manutenção'),
            ('Material de Escritório', 'despesa', 'Compra de material de escritório'),
        ]
        
        for nome, tipo, descricao in categorias_data:
            CategoriaFinanceira.objects.get_or_create(
                nome=nome,
                defaults={'tipo': tipo, 'descricao': descricao}
            )
        
        # Plano de contas
        contas_data = [
            ('1.1.01', 'Caixa', 'ativo'),
            ('1.1.02', 'Banco', 'ativo'),
            ('1.2.01', 'Mensalidades a Receber', 'ativo'),
            ('2.1.01', 'Fornecedores', 'passivo'),
            ('2.1.02', 'Salários a Pagar', 'passivo'),
            ('3.1.01', 'Capital Social', 'patrimonio'),
            ('4.1.01', 'Receitas de Mensalidades', 'receita'),
            ('5.1.01', 'Despesas com Salários', 'despesa'),
        ]
        
        for codigo, nome, tipo in contas_data:
            PlanoContas.objects.get_or_create(
                codigo=codigo,
                defaults={'nome': nome, 'tipo': tipo}
            )
        
        # Mensalidades para alunos
        config = ConfiguracaoFinanceira.objects.first()
        if config:
            for aluno in alunos[:20]:  # Apenas 20 para não sobrecarregar
                # Criar mensalidades dos últimos 6 meses
                for mes in range(6):
                    data_base = date.today().replace(day=1) - timedelta(days=30*mes)
                    vencimento = data_base.replace(day=config.dia_vencimento)
                    
                    valor = config.valor_mensalidade_padrao + Decimal(random.randint(-50, 100))
                    
                    Mensalidade.objects.create(
                        aluno=aluno,
                        mes_referencia=data_base.month,
                        ano_referencia=data_base.year,
                        valor=valor,
                        data_vencimento=vencimento,
                        status=random.choice(['pendente', 'pago', 'atrasado']),
                        data_pagamento=self.fake.date_between(start_date=vencimento, end_date='today') if random.random() > 0.3 else None
                    )

    def criar_dados_frequencia(self, alunos, turmas):
        """Cria registros de frequência"""
        self.stdout.write('📅 Criando dados de frequência...')
        
        # Registros de frequência dos últimos 30 dias
        for dia in range(30):
            data = date.today() - timedelta(days=dia)
            
            # Pular fins de semana
            if data.weekday() >= 5:
                continue
            
            for turma in turmas[:5]:  # Apenas 5 turmas para não sobrecarregar
                alunos_turma = [a for a in alunos if a.turma == turma]
                
                for aluno in alunos_turma[:10]:  # Máximo 10 alunos por turma
                    # 90% de chance de estar presente
                    presente = random.random() > 0.1
                    
                    registro = RegistroFrequencia.objects.create(
                        aluno=aluno,
                        turma=turma,
                        data=data,
                        periodo=random.choice(['Manhã', 'Tarde', 'Noite']),
                        presente=presente,
                        atraso=random.randint(0, 30) if presente and random.random() > 0.8 else 0,
                        observacoes=self.fake.sentence() if random.random() > 0.9 else ''
                    )
                    
                    # Criar justificativa para faltas
                    if not presente and random.random() > 0.5:
                        JustificativaFalta.objects.create(
                            registro_frequencia=registro,
                            motivo=random.choice(['doença', 'médico', 'família', 'outro']),
                            descricao=self.fake.sentence(),
                            data_justificativa=data + timedelta(days=random.randint(1, 3)),
                            aprovada=random.choice([True, False, None])
                        )

    def criar_avaliacoes(self, disciplinas, turmas, professores):
        """Cria avaliações para as disciplinas"""
        self.stdout.write('📝 Criando avaliações...')
        
        tipos = ['Prova', 'Trabalho', 'Projeto', 'Seminário', 'Exercício']
        avaliacoes = []
        
        for turma in turmas[:5]:  # Apenas 5 turmas
            for disciplina in disciplinas[:5]:  # Apenas 5 disciplinas
                professor = random.choice(professores)
                
                # 2 avaliações por disciplina/turma
                for i in range(2):
                    data_avaliacao = self.fake.date_between(start_date='-60d', end_date='+30d')
                    
                    avaliacao = Avaliacao.objects.create(
                        nome=f"{random.choice(tipos)} - {disciplina.nome}",
                        disciplina=disciplina,
                        turma=turma,
                        professor=professor,
                        tipo=random.choice(tipos),
                        data=data_avaliacao,
                        valor_total=Decimal('10.00'),
                        peso=random.randint(1, 3),
                        descricao=self.fake.paragraph(),
                        periodo=random.choice(['Manhã', 'Tarde', 'Noite'])
                    )
                    avaliacoes.append(avaliacao)
        
        return avaliacoes

    def criar_notas(self, avaliacoes, alunos):
        """Cria notas para as avaliações"""
        self.stdout.write('🎯 Criando notas...')
        
        for avaliacao in avaliacoes:
            # Alunos da turma da avaliação
            alunos_turma = [a for a in alunos if a.turma == avaliacao.turma]
            
            for aluno in alunos_turma:
                # 95% dos alunos têm nota
                if random.random() > 0.05:
                    # Gerar nota realista (distribuição normal em torno de 7.0)
                    nota_base = random.gauss(7.0, 1.5)
                    nota = max(0, min(10, round(nota_base, 1)))
                    
                    Nota.objects.create(
                        aluno=aluno,
                        avaliacao=avaliacao,
                        valor=Decimal(str(nota)),
                        data_lancamento=avaliacao.data + timedelta(days=random.randint(1, 7)),
                        observacao=self.fake.sentence() if random.random() > 0.8 else ''
                    )

    def criar_comunicados(self, professores, turmas):
        """Cria comunicados escolares"""
        self.stdout.write('📢 Criando comunicados...')
        
        tipos = ['geral', 'turma', 'urgente', 'evento']
        
        for _ in range(15):
            autor = random.choice(professores)
            tipo = random.choice(tipos)
            
            data_publicacao = self.fake.date_between(start_date='-30d', end_date='today')
            data_evento = self.fake.date_between(start_date='today', end_date='+60d') if tipo == 'evento' else None
            
            comunicado = Comunicado.objects.create(
                titulo=self.fake.sentence(nb_words=6).rstrip('.'),
                conteudo=self.fake.paragraph(nb_sentences=5),
                autor=autor,
                tipo=tipo,
                data_publicacao=data_publicacao,
                data_evento=data_evento,
                ativo=random.choice([True, False]) if random.random() > 0.8 else True,
                prioridade=random.choice(['baixa', 'media', 'alta'])
            )
            
            # Associar a turmas se for comunicado específico
            if tipo == 'turma':
                turmas_escolhidas = random.sample(turmas, random.randint(1, 3))
                comunicado.turmas.set(turmas_escolhidas)

        self.stdout.write(self.style.SUCCESS('🎉 Todos os dados foram criados com sucesso!'))
        self.stdout.write('')
        self.stdout.write('📊 Resumo dos dados criados:')
        self.stdout.write(f'• {User.objects.filter(is_superuser=False).count()} usuários')
        self.stdout.write(f'• {Aluno.objects.count()} alunos')
        self.stdout.write(f'• {Responsavel.objects.count()} responsáveis')
        self.stdout.write(f'• {Professor.objects.count()} professores')
        self.stdout.write(f'• {Turma.objects.count()} turmas')
        self.stdout.write(f'• {Disciplina.objects.count()} disciplinas')
        self.stdout.write(f'• {Livro.objects.count()} livros')
        self.stdout.write(f'• {Emprestimo.objects.count()} empréstimos')
        self.stdout.write(f'• {Mensalidade.objects.count()} mensalidades')
        self.stdout.write(f'• {RegistroFrequencia.objects.count()} registros de frequência')
        self.stdout.write(f'• {Avaliacao.objects.count()} avaliações')
        self.stdout.write(f'• {Nota.objects.count()} notas')
        self.stdout.write(f'• {Comunicado.objects.count()} comunicados')
        self.stdout.write('')
        self.stdout.write('🔑 Credenciais de acesso:')
        self.stdout.write('• Alunos: aluno_001 a aluno_030 (senha: senha123)')
        self.stdout.write('• Responsáveis: resp_001 a resp_030 (senha: senha123)')
        self.stdout.write('• Professores: prof_001 a prof_010 (senha: senha123)') 