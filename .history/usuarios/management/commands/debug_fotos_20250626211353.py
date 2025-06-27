from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Debug das fotos de perfil dos usuários'

    def handle(self, *args, **options):
        self.stdout.write('=== DEBUG DAS FOTOS DE PERFIL ===\n')
        
        # Verificar configurações de media
        self.stdout.write(f'MEDIA_ROOT: {settings.MEDIA_ROOT}')
        self.stdout.write(f'MEDIA_URL: {settings.MEDIA_URL}')
        
        # Verificar se a pasta existe
        perfis_path = os.path.join(settings.MEDIA_ROOT, 'perfis')
        self.stdout.write(f'Pasta perfis existe: {os.path.exists(perfis_path)}')
        
        if os.path.exists(perfis_path):
            arquivos = os.listdir(perfis_path)
            self.stdout.write(f'Arquivos na pasta perfis: {arquivos}')
        
        self.stdout.write('\n=== USUÁRIOS E FOTOS ===')
        
        for user in User.objects.all():
            self.stdout.write(f'\nUsuário: {user.username}')
            
            if hasattr(user, 'perfil'):
                perfil = user.perfil
                self.stdout.write(f'  Perfil existe: Sim')
                self.stdout.write(f'  Foto campo: {perfil.foto}')
                
                if perfil.foto:
                    self.stdout.write(f'  Foto nome: {perfil.foto.name}')
                    self.stdout.write(f'  Foto URL: {perfil.foto.url}')
                    
                    # Verificar se o arquivo existe fisicamente
                    foto_path = perfil.foto.path
                    self.stdout.write(f'  Arquivo existe: {os.path.exists(foto_path)}')
                    self.stdout.write(f'  Caminho completo: {foto_path}')
                else:
                    self.stdout.write('  Foto: Não definida')
            else:
                self.stdout.write('  Perfil existe: Não')
        
        self.stdout.write('\n=== FIM DO DEBUG ===') 