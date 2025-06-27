from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def lista_frequencia(request):
    return render(request, 'frequencia/lista_frequencia.html')

@login_required
def registrar_frequencia(request):
    return render(request, 'frequencia/registrar_frequencia.html')
