from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages

def home(request):
    # Seu código existente para a view home
    return render(request, 'core/home.html')

def custom_logout(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso!')
    return redirect('home')
