# notas/models.py
from django.db import models
from alunos.models import Aluno
from turmas.models import Turma

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nome

class Avaliacao(models.Model):
    TIPOS_AVALIACAO = (
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('projeto', 'Projeto'),
        ('participacao', 'Participação'),
        ('outro', 'Outro'),
    )
    
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='avaliacoes')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='avaliacoes')
    nome = models.CharField(max_length=100)
    data = models.DateField()
    valor_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    peso = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    tipo = models.CharField(max_length=20, choices=TIPOS_AVALIACAO, default='prova')
    
    def __str__(self):
        return f"{self.nome} - {self.disciplina} ({self.turma})"
    
    class Meta:
        ordering = ['data']

class Nota(models.Model):
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='notas')
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notas')
    valor = models.DecimalField(max_digits=5, decimal_places=2)
    observacao = models.TextField(blank=True, null=True)
    data_lancamento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.aluno} - {self.avaliacao}: {self.valor}"
    
    class Meta:
        unique_together = ['avaliacao', 'aluno']
        ordering = ['avaliacao__data', 'aluno__nome']
