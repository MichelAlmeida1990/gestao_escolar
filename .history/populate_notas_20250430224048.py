# populate_notas.py
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurar ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from faker import Faker
from notas.models import Disciplina, Avaliacao, Nota
from alunos.models import Aluno

fake = Faker('pt_BR')

def verificar_modelos():
    """Verifica os campos disponíveis em cada modelo"""
    print("Verificando campos dos modelos:")
    
    print("\nCampos do modelo Disciplina:")
    print([field.name for field in Disciplina._meta.fields])
    
    print("\nCampos do modelo Avaliacao:")
    print([field.name for field in Avaliacao._meta.fields])
    
    print("\nCampos do modelo Nota:")
    print([field.name for field in Nota._meta.fields])
    
    print("\nVerificando se existem alunos cadastrados:")
    alunos_count = Aluno.objects.count()
    print(f"Total de alunos: {alunos_count}")
    
    return True

# [Restante do script como mostrado anteriormente]

if __name__ == '__main__':
    print("Populando o banco de dados do app de notas...")
    
    # Verificar modelos antes de prosseguir
    if verificar_modelos():
        popular_notas()
    else:
        print("Verifique os modelos antes de continuar.")
    
    print("Processo finalizado!")
