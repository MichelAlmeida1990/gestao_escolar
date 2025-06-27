from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, TipoUsuario

class Command(BaseCommand):
    help = 'Cria um novo usuário no sistema'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nome de usuário')
        parser.add_argument('email', type=str, help='Email do usuário')
        parser.add_argument('password', type=str, help='Senha do usuário')
        parser.add_argument(
            '--first-name',
            type=str,
            help='Primeiro nome'
        )
        parser.add_argument(
            '--last-name', 
            type=str,
            help='Sobrenome'
        )
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['admin', 'professor', 'responsavel', 'funcionario'],
            default='funcionario',
            help='Tipo de usuário (padrão: funcionario)'
        )
        parser.add_argument(
            '--staff',
            action='store_true',
            help='Marcar como staff (acesso ao admin)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options.get('first_name', '')
        last_name = options.get('last_name', '')
        tipo = options['tipo']
        is_staff = options['staff']

        # Mapear tipo para o enum
        tipo_map = {
            'admin': TipoUsuario.ADMIN,
            'professor': TipoUsuario.PROFESSOR,
            'responsavel': TipoUsuario.RESPONSAVEL,
            'funcionario': TipoUsuario.FUNCIONARIO
        }
        tipo_usuario = tipo_map[tipo]

        # Verificar se usuário já existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'❌ Usuário "{username}" já existe!')
            )
            return

        try:
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            # Configurar permissões de admin
            if tipo == 'admin' or is_staff:
                user.is_staff = True
                if tipo == 'admin':
                    user.is_superuser = True
                user.save()

            # Criar perfil
            try:
                perfil = user.perfil
                perfil.tipo_usuario = tipo_usuario
                perfil.save()
            except PerfilUsuario.DoesNotExist:
                PerfilUsuario.objects.create(
                    user=user,
                    tipo_usuario=tipo_usuario
                )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuário criado com sucesso!')
            )
            self.stdout.write(f'👤 Usuário: {username}')
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'🎭 Tipo: {tipo_usuario}')
            self.stdout.write(f'🔧 Staff: {"Sim" if user.is_staff else "Não"}')
            self.stdout.write(f'🔗 Login: http://127.0.0.1:8000/usuarios/login/')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao criar usuário: {e}')
            ) 