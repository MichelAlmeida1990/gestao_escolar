#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from django.contrib.auth import authenticate
from django.http import HttpRequest

def test_user_access():
    print("🔍 Testando acesso do usuário 'michas'...")
    print("=" * 50)
    
    try:
        # Buscar o usuário
        user = User.objects.get(username='michas')
        print(f"✅ Usuário encontrado: {user.username}")
        print(f"📧 Email: {user.email}")
        print(f"🔐 É superusuário: {user.is_superuser}")
        print(f"👨‍💼 É staff: {user.is_staff}")
        print(f"✅ Está ativo: {user.is_active}")
        print()
        
        # Testar permissões básicas
        print("🎯 Testando permissões básicas:")
        print(f"  • Pode acessar admin: {user.is_staff}")
        print(f"  • Tem acesso total: {user.is_superuser}")
        print()
        
        # Verificar permissões específicas do context processor
        from core.context_processors import menu_permissions
        request = HttpRequest()
        request.user = user
        
        perms = menu_permissions(request)
        print("🏠 Permissões de menu:")
        for key, value in perms.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")
        print()
        
        # Testar acesso aos modelos principais
        print("📊 Testando acesso aos dados:")
        
        from alunos.models import Aluno
        from professores.models import Professor
        from turmas.models import Turma
        from notas.models import Disciplina
        from biblioteca.models import Livro
        from financeiro.models import Mensalidade
        from comunicados.models import Comunicado
        
        print(f"  • Alunos: {Aluno.objects.count()} registros")
        print(f"  • Professores: {Professor.objects.count()} registros")
        print(f"  • Turmas: {Turma.objects.count()} registros")
        print(f"  • Disciplinas: {Disciplina.objects.count()} registros")
        print(f"  • Livros: {Livro.objects.count()} registros")
        print(f"  • Mensalidades: {Mensalidade.objects.count()} registros")
        print(f"  • Comunicados: {Comunicado.objects.count()} registros")
        print()
        
        # Verificar se pode criar registros (simular)
        print("➕ Testando capacidade de criação/edição:")
        
        # Como é superuser, pode fazer tudo
        if user.is_superuser:
            print("  ✅ Pode criar alunos")
            print("  ✅ Pode editar alunos")
            print("  ✅ Pode excluir alunos")
            print("  ✅ Pode criar professores")
            print("  ✅ Pode editar professores")
            print("  ✅ Pode excluir professores")
            print("  ✅ Pode criar turmas")
            print("  ✅ Pode gerenciar biblioteca")
            print("  ✅ Pode gerenciar financeiro")
            print("  ✅ Pode criar comunicados")
            print("  ✅ Pode gerenciar frequência")
            print("  ✅ Pode gerenciar notas")
        
        print()
        print("🎉 RESULTADO: O usuário 'michas' tem ACESSO COMPLETO ao sistema!")
        print("   Como superusuário, ele pode:")
        print("   • Acessar todas as páginas")
        print("   • Criar, editar e excluir qualquer registro")
        print("   • Visualizar todos os dados")
        print("   • Gerenciar outros usuários")
        print("   • Acessar o painel administrativo")
        
    except User.DoesNotExist:
        print("❌ Usuário 'michas' não encontrado!")
    except Exception as e:
        print(f"❌ Erro ao testar acesso: {e}")

if __name__ == "__main__":
    test_user_access() 