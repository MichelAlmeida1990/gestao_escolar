from django.db import models
from django.contrib.auth.models import User
from alunos.models import Aluno  # Ajuste o import conforme o nome do seu app de alunos

class Responsavel(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='responsavel')
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=15)
    celular = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    endereco = models.CharField(max_length=255)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)
    profissao = models.CharField(max_length=100)
    local_trabalho = models.CharField(max_length=200, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_completo

    class Meta:
        verbose_name = 'Responsável'
        verbose_name_plural = 'Responsáveis'
        ordering = ['nome_completo']


class RelacaoAlunoResponsavel(models.Model):
    TIPO_PARENTESCO_CHOICES = [
        ('PAI', 'Pai'),
        ('MAE', 'Mãe'),
        ('AVO', 'Avô/Avó'),
        ('TIO', 'Tio/Tia'),
        ('IRMAO', 'Irmão/Irmã'),
        ('TUTOR', 'Tutor Legal'),
        ('OUTRO', 'Outro'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='relacoes_responsaveis')
    responsavel = models.ForeignKey(Responsavel, on_delete=models.CASCADE, related_name='relacoes_alunos')
    tipo_parentesco = models.CharField(max_length=10, choices=TIPO_PARENTESCO_CHOICES)
    responsavel_financeiro = models.BooleanField(default=False)
    autorizado_buscar = models.BooleanField(default=True)
    data_inicio = models.DateField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.responsavel.nome_completo} - {self.get_tipo_parentesco_display()} de {self.aluno.nome_completo}"

    class Meta:
        verbose_name = 'Relação Aluno-Responsável'
        verbose_name_plural = 'Relações Aluno-Responsável'
        unique_together = ('aluno', 'responsavel')
