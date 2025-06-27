from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from alunos.models import Aluno
from turmas.models import Turma

class PlanoContas(models.Model):
    TIPO_CHOICES = [
        ('receita', 'Receita'),
        ('despesa', 'Despesa'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Código")
    nome = models.CharField(max_length=150, verbose_name="Nome")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Plano de Contas"
        verbose_name_plural = "Planos de Contas"
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nome}"

class CategoriaFinanceira(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    cor = models.CharField(max_length=7, default="#007bff", verbose_name="Cor (Hex)")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Categoria Financeira"
        verbose_name_plural = "Categorias Financeiras"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Mensalidade(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    DESCONTO_TIPO_CHOICES = [
        ('valor', 'Valor Fixo'),
        ('percentual', 'Percentual'),
    ]
    
    # Informações básicas
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    
    # Período
    mes_referencia = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="Mês de Referência")
    ano_referencia = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)], verbose_name="Ano de Referência")
    
    # Valores
    valor_base = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Base")
    valor_desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor do Desconto")
    tipo_desconto = models.CharField(max_length=10, choices=DESCONTO_TIPO_CHOICES, default='valor', verbose_name="Tipo de Desconto")
    valor_juros = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor dos Juros")
    valor_multa = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor da Multa")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total")
    
    # Datas
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Data do Pagamento")
    
    # Status e controle
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    descricao_desconto = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descrição do Desconto")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Mensalidade"
        verbose_name_plural = "Mensalidades"
        unique_together = ['aluno', 'mes_referencia', 'ano_referencia']
        ordering = ['-ano_referencia', '-mes_referencia', 'aluno__nome']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.mes_referencia:02d}/{self.ano_referencia} - R$ {self.valor_total}"
    
    @property
    def esta_vencida(self):
        if self.status == 'pago':
            return False
        return timezone.now().date() > self.data_vencimento
    
    @property
    def dias_atraso(self):
        if not self.esta_vencida:
            return 0
        return (timezone.now().date() - self.data_vencimento).days

class ConfiguracaoFinanceira(models.Model):
    # Configurações de mensalidade
    valor_padrao_mensalidade = models.DecimalField(max_digits=10, decimal_places=2, default=150.00, verbose_name="Valor Padrão da Mensalidade")
    dia_vencimento_mensalidade = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)], default=5, verbose_name="Dia de Vencimento da Mensalidade")
    
    # Juros e multas
    percentual_juros_mes = models.DecimalField(max_digits=5, decimal_places=2, default=1.00, verbose_name="Juros ao Mês (%)")
    valor_multa_atraso = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, verbose_name="Multa por Atraso (R$)")
    dias_carencia_juros = models.IntegerField(default=5, verbose_name="Dias de Carência para Juros")
    
    # Descontos
    percentual_desconto_pontualidade = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, verbose_name="Desconto por Pontualidade (%)")
    percentual_desconto_irmao = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, verbose_name="Desconto para Irmãos (%)")
    
    # Informações da escola
    nome_escola = models.CharField(max_length=200, default="Escola", verbose_name="Nome da Escola")
    cnpj_escola = models.CharField(max_length=20, blank=True, null=True, verbose_name="CNPJ da Escola")
    endereco_escola = models.TextField(blank=True, null=True, verbose_name="Endereço da Escola")
    
    class Meta:
        verbose_name = "Configuração Financeira"
        verbose_name_plural = "Configurações Financeiras"
    
    def __str__(self):
        return f"Configurações Financeiras - {self.nome_escola}"
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração única ou cria uma nova"""
        config, created = cls.objects.get_or_create(id=1)
        return config 