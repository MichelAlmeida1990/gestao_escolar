from django.db import models
from django.contrib.auth.models import User
from turmas.models import Turma

class Professor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    formacao = models.CharField(max_length=100)
    disciplina = models.CharField(max_length=100)
    turmas = models.ManyToManyField(Turma, related_name='professores_diretos', blank=True)
    
    def __str__(self):
        return f"{self.nome} - {self.disciplina}"
