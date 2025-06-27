import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User

print("=== TESTE DO TEMPLATE RELATÓRIOS ===")

try:
    # Testar carregamento do template
    template = get_template('financeiro/relatorios.html')
    print("✓ Template carregado com sucesso")
    
    # Criar contexto de teste
    context = {
        'dados_anuais': [
            {
                'ano': 2025,
                'valor_total': 10000.00,
                'valor_pago': 8000.00,
                'percentual_pagamento': 80.0
            }
        ],
        'dados_mensais': [
            {
                'mes': 1,
                'valor_total': 1000.00,
                'valor_pago': 800.00,
                'valor_pendente': 200.00,
                'percentual_pagamento': 80.0
            },
            {
                'mes': 6,
                'valor_total': 1200.00,
                'valor_pago': 1000.00,
                'valor_pendente': 200.00,
                'percentual_pagamento': 83.3
            }
        ],
        'ano_atual': 2025,
    }
    
    # Tentar renderizar o template
    html = template.render(context)
    print("✓ Template renderizado com sucesso")
    
    # Verificar se o HTML contém elementos esperados
    if 'Janeiro' in html:
        print("✓ Nomes dos meses estão sendo exibidos corretamente")
    if 'R$' in html:
        print("✓ Valores monetários estão sendo exibidos")
    if 'Chart.js' in html:
        print("✓ Scripts de gráficos incluídos")
    
    print("\n=== TEMPLATE FUNCIONANDO CORRETAMENTE ===")
    
except Exception as e:
    print(f"❌ Erro ao processar template: {str(e)}")
    import traceback
    traceback.print_exc() 