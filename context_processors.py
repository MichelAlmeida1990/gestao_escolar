def menu_permissions(request):
    """
    Adiciona permissões de menu ao contexto para controlar o que é exibido no menu
    """
    # Verificar se o usuário está autenticado
    is_authenticated = request.user.is_authenticated
    is_staff = request.user.is_staff if is_authenticated else False
    
    # Valores padrão
    context = {
        # Permissões gerais
        'is_staff': is_staff,
        'is_professor': False,
        'is_responsavel': False,
        
        # Permissões específicas de visualização
        'can_view_all_alunos': is_staff,
        'can_view_all_professores': is_staff,
        'can_view_all_turmas': is_staff,
        'can_view_all_disciplinas': is_staff,
        'can_view_all_avaliacoes': is_staff,
        'can_view_all_notas': is_staff,
        'can_view_all_frequencias': is_staff,
        'can_view_all_eventos': is_staff,
        'can_view_all_comunicados': is_staff,
        
        # Permissões específicas de edição
        'can_edit_alunos': is_staff,
        'can_edit_professores': is_staff,
        'can_edit_turmas': is_staff,
        'can_edit_disciplinas': is_staff,
        'can_edit_avaliacoes': is_staff,
        'can_edit_notas': is_staff,
        'can_edit_frequencias': is_staff,
        'can_edit_eventos': is_staff,
        'can_edit_comunicados': is_staff,
    }
    
    # Se o usuário não estiver autenticado, retorna apenas os valores padrão
    if not is_authenticated:
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
