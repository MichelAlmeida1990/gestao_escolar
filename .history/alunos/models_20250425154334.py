from django.db import models
from django.contrib.auth.models import User
from turmas.models import Turma

class Aluno(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    endereco = models.TextField()
    responsavel = models.CharField(max_length=100)
    telefone_responsavel = models.CharField(max_length=20)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, related_name='alunos')
    
    def __str__(self):
        return self.nome
