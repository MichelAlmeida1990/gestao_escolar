#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_aluno_detail():
    """Testa se a página de detalhes do aluno está funcionando"""
    client = Client()
    
    # Fazer login com o usuário michas
    try:
        user = User.objects.get(username='michas')
        client.force_login(user)
        
        # Tentar acessar a página de detalhes do aluno
        response = client.get('/alunos/72/')
        print(f"Status da página /alunos/72/: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Página de detalhes do aluno funcionando corretamente!")
        else:
            print(f"❌ Erro na página: Status {response.status_code}")
            if hasattr(response, 'content'):
                print("Conteúdo do erro:")
                print(response.content.decode('utf-8')[:500])
        
        # Testar também a lista de alunos
        response = client.get('/alunos/')
        print(f"Status da página /alunos/: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Lista de alunos funcionando corretamente!")
        else:
            print(f"❌ Erro na lista de alunos: Status {response.status_code}")
            
    except User.DoesNotExist:
        print("❌ Usuário 'michas' não encontrado")
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")

if __name__ == "__main__":
    test_aluno_detail() 