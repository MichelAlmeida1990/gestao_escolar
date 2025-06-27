def menu_permissions(request):
    """
    Adiciona permissões de menu ao contexto para controlar o que é exibido no menu
    """
    # Valores padrão
    context = {
        # Permissões gerais
        'is_staff': request.user.is_staff,
        'is_professor': False,
        'is_responsavel': False,
        
        # Permissões específicas de visualização
        'can_view_all_alunos': request.user.is_staff,
        'can_view_all_professores': request.user.is_staff,
        'can_view_all_turmas': request.user.is_staff,
        'can_view_all_disciplinas': request.user.is_staff,
        'can_view_all_avaliacoes': request.user.is_staff,
        'can_view_all_notas': request.user.is_staff,
        'can_view_all_frequencias': request.user.is_staff,
        'can_view_all_eventos': request.user.is_staff,
        'can_view_all_comunicados': request.user.is_staff,
        
        # Permissões específicas de edição
        'can_edit_alunos': request.user.is_staff,
        'can_edit_professores': request.user.is_staff,
        'can_edit_turmas': request.user.is_staff,
        'can_edit_disciplinas': request.user.is_staff,
        'can_edit_avaliacoes': request.user.is_staff,
        'can_edit_notas': request.user.is_staff,
        'can_edit_frequencias': request.user.is_staff,
        'can_edit_eventos': request.user.is_staff,
        'can_edit_comunicados': request.user.is_staff,
    }
    
    # Se o usuário não estiver autenticado, retorna apenas os valores padrão
    if not request.user.is_authenticated:
        return context
    
    # Verifica se o usuário é um professor
    if hasattr(request.user, 'professor'):
        context['is_professor'] = True
        
        # Professores podem ver e editar suas próprias disciplinas, turmas, avaliações e notas
        context['can_view_all_disciplinas'] = True
        context['can_view_all_turmas'] = True
        context['can_view_all_avaliacoes'] = True
        context['can_view_all_notas'] = True
        context['can_view_all_alunos'] = True
        context['can_view_all_frequencias'] = True
        
        context['can_edit_disciplinas'] = True
        context['can_edit_avaliacoes'] = True
        context['can_edit_notas'] = True
        context['can_edit_frequencias'] = True
    
    # Verifica se o usuário é um responsável
    if hasattr(request.user, 'responsavel'):
        context['is_responsavel'] = True
        
        # Responsáveis podem ver informações relacionadas aos seus alunos
        context['can_view_all_alunos'] = True  # Filtrado para mostrar apenas seus alunos
        context['can_view_all_professores'] = True  # Filtrado para mostrar apenas professores de seus alunos
        context['can_view_all_turmas'] = True  # Filtrado para mostrar apenas turmas de seus alunos
        context['can_view_all_disciplinas'] = True  # Filtrado para mostrar apenas disciplinas de seus alunos
        context['can_view_all_avaliacoes'] = True  # Filtrado para mostrar apenas avaliações de seus alunos
        context['can_view_all_notas'] = True  # Filtrado para mostrar apenas notas de seus alunos
        context['can_view_all_frequencias'] = True  # Filtrado para mostrar apenas frequências de seus alunos
        context['can_view_all_eventos'] = True  # Todos podem ver eventos
        context['can_view_all_comunicados'] = True  # Todos podem ver comunicados
    
    return context
