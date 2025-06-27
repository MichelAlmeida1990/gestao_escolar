from django.db import models
from django.contrib.auth.models import User
from alunos.models import Aluno
from turmas.models import Turma

class Comunicado(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comunicados')
    
    # Destinatários possíveis (podem ser específicos ou gerais)
    para_todos = models.BooleanField(default=False)
    turmas = models.ManyToManyField(Turma, blank=True, related_name='comunicados')
    alunos = models.ManyToManyField(Aluno, blank=True, related_name='comunicados')
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Comunicado'
        verbose_name_plural = 'Comunicados'
    
    def __str__(self):
        return self.titulo
