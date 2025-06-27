from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, TipoUsuario
from django.db import transaction

class Command(BaseCommand):
    help = 'Cria usuários de teste com diferentes perfis'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Remove usuários existentes antes de criar novos'
        )
    
    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write('Removendo usuários de teste existentes...')
            User.objects.filter(username__in=[
                'admin_teste', 'prof_teste', 'resp_teste', 'func_teste'
            ]).delete()
        
        with transaction.atomic():
            # Criar usuário administrador
            admin_user, created = User.objects.get_or_create(
                username='admin_teste',
                defaults={
                    'email': 'admin@escola.com',
                    'first_name': 'Admin',
                    'last_name': 'Sistema',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                admin_user.perfil.tipo_usuario = TipoUsuario.ADMIN
                admin_user.perfil.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Usuário administrador criado: {admin_user.username}')
                )
            
            # Criar usuário professor
            prof_user, created = User.objects.get_or_create(
                username='prof_teste',
                defaults={
                    'email': 'professor@escola.com',
                    'first_name': 'Professor',
                    'last_name': 'Teste',
                    'is_staff': False
                }
            )
            if created:
                prof_user.set_password('prof123')
                prof_user.save()
                prof_user.perfil.tipo_usuario = TipoUsuario.PROFESSOR
                prof_user.perfil.telefone = '(11) 99999-1111'
                prof_user.perfil.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Usuário professor criado: {prof_user.username}')
                )
            
            # Criar usuário responsável
            resp_user, created = User.objects.get_or_create(
                username='resp_teste',
                defaults={
                    'email': 'responsavel@email.com',
                    'first_name': 'Responsável',
                    'last_name': 'Teste',
                    'is_staff': False
                }
            )
            if created:
                resp_user.set_password('resp123')
                resp_user.save()
                resp_user.perfil.tipo_usuario = TipoUsuario.RESPONSAVEL
                resp_user.perfil.telefone = '(11) 99999-2222'
                resp_user.perfil.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Usuário responsável criado: {resp_user.username}')
                )
            
            # Criar usuário funcionário
            func_user, created = User.objects.get_or_create(
                username='func_teste',
                defaults={
                    'email': 'funcionario@escola.com',
                    'first_name': 'Funcionário',
                    'last_name': 'Teste',
                    'is_staff': False
                }
            )
            if created:
                func_user.set_password('func123')
                func_user.save()
                func_user.perfil.tipo_usuario = TipoUsuario.FUNCIONARIO
                func_user.perfil.telefone = '(11) 99999-3333'
                func_user.perfil.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Usuário funcionário criado: {func_user.username}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('USUÁRIOS DE TESTE CRIADOS COM SUCESSO!'))
        self.stdout.write('='*50)
        self.stdout.write('\nCredenciais para teste:')
        self.stdout.write('👑 Admin: admin_teste / admin123')
        self.stdout.write('👨‍🏫 Professor: prof_teste / prof123')
        self.stdout.write('👨‍👩‍👧‍👦 Responsável: resp_teste / resp123')
        self.stdout.write('👷 Funcionário: func_teste / func123')
        self.stdout.write('\nAcesse: http://localhost:8000/auth/login/')
        self.stdout.write('='*50) 