from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from alunos.models import Aluno
from professores.models import Professor
from turmas.models import Turma, TurmaAluno
from matriculas.models import MatriculaOnline
from financeiro.models import Mensalidade
from notas.models import Disciplina, Avaliacao
from frequencia.models import RegistroFrequencia
from comunicados.models import Comunicado
from biblioteca.models import Emprestimo, Reserva

class Command(BaseCommand):
    help = 'Remove dados fake/artificiais do sistema, mantendo apenas dados essenciais.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a remoção dos dados fake',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'ATENÇÃO: Este comando irá remover dados fake do sistema!\n'
                    'Execute com --confirm para prosseguir.'
                )
            )
            return

        self.stdout.write('Iniciando limpeza de dados fake...')

        # Contadores
        removidos = {
            'alunos': 0,
            'professores': 0,
            'turmas': 0,
            'matriculas': 0,
            'mensalidades': 0,
            'disciplinas': 0,
            'avaliacoes': 0,
            'frequencias': 0,
            'comunicados': 0,
            'emprestimos': 0,
            'reservas': 0,
        }

        # Remover dados relacionados
        try:
            # Empréstimos e reservas
            emprestimos = Emprestimo.objects.all()
            removidos['emprestimos'] = emprestimos.count()
            emprestimos.delete()

            reservas = Reserva.objects.all()
            removidos['reservas'] = reservas.count()
            reservas.delete()

            # Avaliações
            avaliacoes = Avaliacao.objects.all()
            removidos['avaliacoes'] = avaliacoes.count()
            avaliacoes.delete()

            # Disciplinas
            disciplinas = Disciplina.objects.all()
            removidos['disciplinas'] = disciplinas.count()
            disciplinas.delete()

            # Frequências
            frequencias = RegistroFrequencia.objects.all()
            removidos['frequencias'] = frequencias.count()
            frequencias.delete()

            # Mensalidades
            mensalidades = Mensalidade.objects.all()
            removidos['mensalidades'] = mensalidades.count()
            mensalidades.delete()

            # Matrículas online
            matriculas = MatriculaOnline.objects.all()
            removidos['matriculas'] = matriculas.count()
            matriculas.delete()

            # TurmaAluno (relacionamentos)
            turma_alunos = TurmaAluno.objects.all()
            turma_alunos.delete()

            # Comunicados
            comunicados = Comunicado.objects.all()
            removidos['comunicados'] = comunicados.count()
            comunicados.delete()

            # Alunos (remover todos)
            alunos = Aluno.objects.all()
            removidos['alunos'] = alunos.count()
            alunos.delete()

            # Professores (exceto admin)
            professores = Professor.objects.exclude(usuario__username='admin')
            removidos['professores'] = professores.count()
            professores.delete()

            # Turmas
            turmas = Turma.objects.all()
            removidos['turmas'] = turmas.count()
            turmas.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Limpeza concluída!\n'
                    f'Removidos:\n'
                    f'- {removidos["alunos"]} alunos\n'
                    f'- {removidos["professores"]} professores\n'
                    f'- {removidos["turmas"]} turmas\n'
                    f'- {removidos["matriculas"]} matrículas\n'
                    f'- {removidos["mensalidades"]} mensalidades\n'
                    f'- {removidos["disciplinas"]} disciplinas\n'
                    f'- {removidos["avaliacoes"]} avaliações\n'
                    f'- {removidos["frequencias"]} registros de frequência\n'
                    f'- {removidos["comunicados"]} comunicados\n'
                    f'- {removidos["emprestimos"]} empréstimos\n'
                    f'- {removidos["reservas"]} reservas\n'
                    f'\nDados essenciais (usuários admin, livros reais) foram mantidos.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a limpeza: {str(e)}')
            ) 