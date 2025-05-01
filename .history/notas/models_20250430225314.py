from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from alunos.models import Aluno
from turmas.models import Turma

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    carga_horaria = models.PositiveIntegerField(default=60)
    ementa = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['nome']

class Avaliacao(models.Model):
    TIPO_CHOICES = [
        ('prova', 'Prova'),
        ('trabalho', 'Trabalho'),
        ('projeto', 'Projeto'),
        ('participacao', 'Participação'),
        ('outro', 'Outro')
    ]
    
    PERIODO_CHOICES = [
        ('1', '1º Bimestre'),
        ('2', '2º Bimestre'),
        ('3', '3º Bimestre'),
        ('4', '4º Bimestre'),
        ('rec', 'Recuperação')
    ]
    
    nome = models.CharField(max_length=100)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='avaliacoes')
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='avaliacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data = models.DateField()
    periodo = models.CharField(max_length=3, choices=PERIODO_CHOICES)
    peso = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.nome} - {self.disciplina} ({self.get_periodo_display()})"
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['data']

class Nota(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notas')
    avaliacao = models.ForeignKey(Avaliacao, on_delete=models.CASCADE, related_name='notas')
    valor = models.DecimalField(
        max_digits=4, 
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    observacao = models.TextField(blank=True)
    data_lancamento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.aluno} - {self.avaliacao} - {self.valor}"
    
    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = ['aluno', 'avaliacao']
