import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Testar a página de relatórios financeiros
print("=== TESTE DO MÓDULO FINANCEIRO ===")

# Configurar cliente de teste
client = Client()

# Buscar usuário admin
admin_user = User.objects.filter(is_staff=True).first()
if not admin_user:
    print("❌ Nenhum usuário admin encontrado")
    exit(1)

print(f"✓ Usuário admin encontrado: {admin_user.username}")

# Fazer login
client.force_login(admin_user)
print("✓ Login realizado")

# Testar URLs do financeiro
urls_to_test = [
    ('/financeiro/', 'Dashboard Financeiro'),
    ('/financeiro/mensalidades/', 'Lista de Mensalidades'),
    ('/financeiro/relatorios/', 'Relatórios Financeiros'),
    ('/financeiro/configuracoes/', 'Configurações'),
    ('/financeiro/mensalidades/gerar/', 'Gerar Mensalidades'),
]

for url, description in urls_to_test:
    try:
        response = client.get(url)
        if response.status_code == 200:
            print(f"✓ {description}: OK (200)")
        else:
            print(f"⚠ {description}: {response.status_code}")
    except Exception as e:
        print(f"❌ {description}: Erro - {str(e)}")

print("\n=== TESTE CONCLUÍDO ===") 