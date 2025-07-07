#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def criar_usuario_demo():
    """Cria um usuário de demonstração com acesso total"""
    
    # Dados do usuário de demonstração
    username = 'demo'
    email = 'demo@escola.com'
    password = 'demo123456'
    first_name = 'Usuário'
    last_name = 'Demonstração'
    
    # Verificar se o usuário já existe
    if User.objects.filter(username=username).exists():
        print(f"Usuário '{username}' já existe!")
        user = User.objects.get(username=username)
        print(f"ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Superuser: {user.is_superuser}")
        print(f"Staff: {user.is_staff}")
        return user
    
    # Criar o usuário
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,  # Acesso total
            is_staff=True,      # Acesso ao admin
            is_active=True
        )
        
        print("✅ Usuário de demonstração criado com sucesso!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Senha: {password}")
        print(f"Superuser: {user.is_superuser}")
        print(f"Staff: {user.is_staff}")
        print("\n🔑 Credenciais de acesso:")
        print(f"Login: {username}")
        print(f"Senha: {password}")
        print(f"URL: https://michel1990.pythonanywhere.com/usuarios/login/")
        
        return user
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return None

def listar_usuarios():
    """Lista todos os usuários existentes"""
    print("\n📋 Usuários existentes no sistema:")
    print("-" * 50)
    
    users = User.objects.all().order_by('id')
    for user in users:
        status = "🟢 Ativo" if user.is_active else "🔴 Inativo"
        superuser = "👑 Superuser" if user.is_superuser else "👤 Usuário"
        staff = "🔧 Staff" if user.is_staff else "📚 Normal"
        
        print(f"ID: {user.id} | {user.username} | {user.email}")
        print(f"    Nome: {user.first_name} {user.last_name}")
        print(f"    Status: {status} | {superuser} | {staff}")
        print("-" * 50)

if __name__ == "__main__":
    print("🎓 Sistema de Gestão Escolar - Criador de Usuário Demo")
    print("=" * 60)
    
    # Listar usuários existentes
    listar_usuarios()
    
    # Criar usuário demo
    print("\n🚀 Criando usuário de demonstração...")
    user = criar_usuario_demo()
    
    if user:
        print("\n🎉 Usuário de demonstração pronto para uso!")
        print("💡 Use as credenciais acima para fazer login no sistema.")
    else:
        print("\n❌ Falha ao criar usuário de demonstração.") 