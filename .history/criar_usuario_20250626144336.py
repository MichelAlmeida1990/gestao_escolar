#!/usr/bin/env python
"""
Script para criar usuários rapidamente
Uso: python criar_usuario.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, TipoUsuario

def criar_usuario():
    print("=== CADASTRO DE NOVO USUÁRIO ===")
    
    # Dados básicos
    username = input("Nome de usuário: ")
    email = input("Email: ")
    first_name = input("Primeiro nome: ")
    last_name = input("Sobrenome: ")
    password = input("Senha: ")
    
    # Tipo de usuário
    print("\nTipos de usuário disponíveis:")
    print("1 - Administrador")
    print("2 - Professor") 
    print("3 - Responsável")
    print("4 - Funcionário")
    
    tipo_choice = input("Escolha o tipo (1-4): ")
    tipo_map = {
        '1': TipoUsuario.ADMIN,
        '2': TipoUsuario.PROFESSOR,
        '3': TipoUsuario.RESPONSAVEL, 
        '4': TipoUsuario.FUNCIONARIO
    }
    
    tipo_usuario = tipo_map.get(tipo_choice, TipoUsuario.FUNCIONARIO)
    
    try:
        # Criar usuário
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        # Se for admin, marcar como staff
        if tipo_usuario == TipoUsuario.ADMIN:
            user.is_staff = True
            user.is_superuser = True
            user.save()
        
        # Criar/atualizar perfil
        try:
            perfil = user.perfil
            perfil.tipo_usuario = tipo_usuario
            perfil.save()
        except PerfilUsuario.DoesNotExist:
            PerfilUsuario.objects.create(
                user=user,
                tipo_usuario=tipo_usuario
            )
        
        print(f"\n✅ Usuário criado com sucesso!")
        print(f"👤 Usuário: {username}")
        print(f"📧 Email: {email}")
        print(f"🎭 Tipo: {tipo_usuario}")
        print(f"🔗 Login: http://127.0.0.1:8000/usuarios/login/")
        
    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}")

if __name__ == "__main__":
    criar_usuario() 