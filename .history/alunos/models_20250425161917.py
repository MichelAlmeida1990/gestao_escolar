from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class Aluno(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('transferido', 'Transferido'),
    ]
    
    # Informações básicas
    nome = models.CharField(max_length=100, verbose_name="Nome completo")
    data_nascimento = models.DateField(verbose_name="Data de nascimento")
    matricula = models.CharField(max_length=20, unique=True, verbose_name="Número de matrícula")
    
    # Documentos
    cpf = models.CharField(
        max_length=14, 
        verbose_name="CPF",
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message="CPF deve estar no formato 000.000.000-00"
        )],
        unique=True,
        null=True,
        blank=True
    )
    rg = models.CharField(max_length=20, verbose_name="RG", null=True, blank=True)
    
    # Contato
    telefone = models.CharField(
        max_length=15, 
        verbose_name="Telefone",
        validators=[RegexValidator(
            regex=r'^\(\d{2}\) \d{5}-\d{4}$',
            message="Telefone deve estar no formato (00) 00000-0000"
        )],
        null=True,
        blank=True
    )
    email = models.EmailField(verbose_name="E-mail", null=True, blank=True)
    
    # Endereço
    endereco = models.CharField(max_length=200, verbose_name="Endereço", null=True, blank=True)
    bairro = models.CharField(max_length=100, verbose_name="Bairro", null=True, blank=True)
    cidade = models.CharField(max_length=100, verbose_name="Cidade", null=True, blank=True)
    estado = models.CharField(max_length=2, verbose_name="Estado", null=True, blank=True)
    cep = models.CharField(max_length=9, verbose_name="CEP", null=True, blank=True)
    
    # Responsável
    responsavel_nome = models.CharField(max_length=100, verbose_name="Nome do responsável", null=True, blank=True)
    responsavel_telefone = models.CharField(
        max_length=15, 
        verbose_name="Telefone do responsável",
        validators=[RegexValidator(
            regex=r'^\(\d{2}\) \d{5}-\d{4}$',
            message="Telefone deve estar no formato (00) 00000-0000"
        )],
        null=True,
        blank=True
    )
    
    # Informações escolares
    data_ingresso = models.DateField(verbose_name="Data de ingresso", default=timezone.now)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ativo', verbose_name="Status")
    foto = models.ImageField(upload_to='alunos/', verbose_name="Foto", null=True, blank=True)
    observacoes = models.TextField(verbose_name="Observações", null=True, blank=True)
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} (Matrícula: {self.matricula})"
    
    def idade(self):
        hoje = timezone.now().date()
        idade = hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
        return idade
