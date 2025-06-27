from django.db import models
from alunos.models import Aluno

class Responsavel(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    endereco = models.CharField(max_length=200)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    alunos = models.ManyToManyField(Aluno, through='ResponsavelAluno')
    
    def __str__(self):
        return self.nome
    
    class Meta:
        verbose_name = 'ResponsÃ¡vel'
        verbose_name_plural = 'ResponsÃ¡veis'
        ordering = ['nome']


class ResponsavelAluno(models.Model):
    TIPO_RELACAO_CHOICES = [
        ('mae', 'MÃ£e'),
        ('pai', 'Pai'),
        ('avoa', 'AvÃ³'),
        ('avo', 'AvÃ´'),
        ('tia', 'Tia'),
        ('tio', 'Tio'),
        ('irma', 'IrmÃ£'),
        ('irmao', 'IrmÃ£o'),
        ('responsavel_legal', 'ResponsÃ¡vel Legal'),
        ('outro', 'Outro'),
    ]
    
    responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    tipo_relacao = models.CharField(max_length=20, choices=TIPO_RELACAO_CHOICES)
    data_vinculo = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.responsavel.nome} - {self.aluno.nome} ({self.get_tipo_relacao_display()})"
    
    class Meta:
        verbose_name = 'VÃ­nculo ResponsÃ¡vel-Aluno'
        verbose_name_plural = 'VÃ­nculos ResponsÃ¡vel-Aluno'
        unique_together = ['responsavel', 'aluno']

