from django.core.management.base import BaseCommand
from django.utils import timezone
from matriculas.models import MatriculaOnline, ConfiguracaoMatricula
import random

class Command(BaseCommand):
    help = 'Popula o sistema com matrículas de teste e cria configuração padrão se necessário.'

    def handle(self, *args, **options):
        # Garantir configuração
        config = ConfiguracaoMatricula.get_config()
        self.stdout.write(self.style.SUCCESS('Configuração de matrícula garantida.'))

        # Dados de exemplo
        nomes = [
            'Ana Silva', 'Bruno Souza', 'Carla Oliveira', 'Daniel Santos', 'Eduarda Lima',
            'Felipe Costa', 'Gabriela Rocha', 'Henrique Alves', 'Isabela Martins', 'João Pedro'
        ]
        cpfs = [
            '111.111.111-11', '222.222.222-22', '333.333.333-33', '444.444.444-44', '555.555.555-55',
            '666.666.666-66', '777.777.777-77', '888.888.888-88', '999.999.999-99', '000.000.000-00'
        ]
        emails = [
            'ana@email.com', 'bruno@email.com', 'carla@email.com', 'daniel@email.com', 'eduarda@email.com',
            'felipe@email.com', 'gabriela@email.com', 'henrique@email.com', 'isabela@email.com', 'joao@email.com'
        ]
        
        for i in range(10):
            MatriculaOnline.objects.create(
                nome_completo=nomes[i],
                data_nascimento=timezone.now().date().replace(year=2010+i),
                cpf=cpfs[i],
                rg=f'RG{i+1000}',
                telefone=f'(11) 9{i}000-000{i}',
                email=emails[i],
                endereco=f'Rua Exemplo, {i+1}',
                bairro='Centro',
                cidade='Cidade Exemplo',
                estado='SP',
                cep='01000-000',
                serie_desejada=random.choice(config.series_disponiveis),
                turno_desejado=random.choice(config.turnos_disponiveis),
                escola_anterior='Escola Anterior',
                ano_letivo=timezone.now().year,
                responsavel_nome=f'Resp. {nomes[i]}',
                responsavel_cpf=cpfs[i],
                responsavel_telefone=f'(11) 9{i}111-111{i}',
                responsavel_email=emails[i],
                status='pendente',
            )
        self.stdout.write(self.style.SUCCESS('10 matrículas de teste criadas com sucesso!')) 