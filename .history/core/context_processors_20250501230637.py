def menu_permissions(request):
    """
    Context processor para adicionar permissões de menu ao contexto de todas as templates.
    """
    # Exemplo básico - você pode personalizar conforme necessário
    context = {
        'user_permissions': {
            'can_view_alunos': request.user.is_authenticated,
            'can_view_professores': request.user.is_authenticated,
            'can_view_turmas': request.user.is_authenticated,
            'can_view_notas': request.user.is_authenticated,
            'can_view_responsaveis': request.user.is_authenticated,
            # Adicione mais permissões conforme necessário
        }
    }
    return context
