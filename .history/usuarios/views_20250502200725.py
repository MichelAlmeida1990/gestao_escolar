# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required
def perfil_view(request):
    # Aqui você pode adicionar lógica para exibir e editar o perfil do usuário
    return render(request, 'usuarios/perfil.html')

@login_required
def alterar_senha_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Importante para manter o usuário logado
            messages.success(request, 'Sua senha foi alterada com sucesso!')
            return redirect('usuarios:perfil')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'usuarios/alterar_senha.html', {'form': form})
