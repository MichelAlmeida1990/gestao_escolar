from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, TipoUsuario

class Command(BaseCommand):
    help = 'Cria perfis para usuários que não possuem'

    def handle(self, *args, **options):
        usuarios_sem_perfil = User.objects.filter(perfil__isnull=True)
        
        if not usuarios_sem_perfil.exists():
            self.stdout.write(
                self.style.SUCCESS('Todos os usuários já possuem perfis.')
            )
            return

        perfis_criados = 0
        
        for user in usuarios_sem_perfil:
            # Determinar tipo de usuário baseado em is_staff
            tipo_usuario = TipoUsuario.ADMIN if user.is_staff else TipoUsuario.FUNCIONARIO
            
            perfil = PerfilUsuario.objects.create(
                user=user,
                tipo_usuario=tipo_usuario,
                session_timeout=3600,  # 1 hora padrão
                max_sessions=3,
                force_password_change=False
            )
            
            perfis_criados += 1
            self.stdout.write(f'Perfil criado para {user.username} ({perfil.get_tipo_usuario_display()})')

        self.stdout.write(
            self.style.SUCCESS(f'Foram criados {perfis_criados} perfis de usuário.')
        ) 