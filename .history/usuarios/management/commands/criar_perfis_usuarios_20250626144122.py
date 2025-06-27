from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, TipoUsuario

class Command(BaseCommand):
    help = 'Cria perfis para usuários existentes que não possuem perfil'

    def handle(self, *args, **options):
        usuarios_sem_perfil = []
        
        for user in User.objects.all():
            try:
                # Tentar acessar o perfil
                perfil = user.perfil
                self.stdout.write(f'✓ Usuário {user.username} já possui perfil')
            except PerfilUsuario.DoesNotExist:
                # Criar perfil para usuário sem perfil
                tipo_usuario = TipoUsuario.ADMIN if user.is_staff else TipoUsuario.FUNCIONARIO
                
                perfil = PerfilUsuario.objects.create(
                    user=user,
                    tipo_usuario=tipo_usuario,
                    session_timeout=3600,  # 1 hora padrão
                    max_sessions=3,
                    force_password_change=False
                )
                
                usuarios_sem_perfil.append(user.username)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Perfil criado para usuário: {user.username} (tipo: {tipo_usuario})'
                    )
                )
        
        if usuarios_sem_perfil:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nCriados {len(usuarios_sem_perfil)} perfis de usuário:'
                )
            )
            for username in usuarios_sem_perfil:
                self.stdout.write(f'  - {username}')
        else:
            self.stdout.write(
                self.style.WARNING('Todos os usuários já possuem perfis.')
            ) 