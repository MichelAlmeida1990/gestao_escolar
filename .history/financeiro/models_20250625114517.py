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
    
    def calcular_total(self):
        """Calcula o valor total considerando descontos, juros e multas"""
        total = self.valor_base
        
        # Aplicar desconto
        if self.valor_desconto > 0:
            if self.tipo_desconto == 'percentual':
                desconto = total * (self.valor_desconto / 100)
            else:
                desconto = self.valor_desconto
            total -= desconto
        
        # Adicionar juros e multa
        total += self.valor_juros + self.valor_multa
        
        return total
    
    def save(self, *args, **kwargs):
        # Calcular valor total antes de salvar
        self.valor_total = self.calcular_total()
        
        # Atualizar status se vencida
        if self.esta_vencida and self.status == 'pendente':
            self.status = 'vencido'
        
        super().save(*args, **kwargs)

class Receita(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('recebido', 'Recebido'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
        ('cheque', 'Cheque'),
    ]
    
    # Informações básicas
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    categoria = models.ForeignKey(CategoriaFinanceira, on_delete=models.SET_NULL, null=True, verbose_name="Categoria")
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.SET_NULL, null=True, limit_choices_to={'tipo': 'receita'}, verbose_name="Plano de Contas")
    
    # Valores
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    
    # Datas
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_recebimento = models.DateTimeField(null=True, blank=True, verbose_name="Data do Recebimento")
    
    # Forma de pagamento
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True, verbose_name="Forma de Pagamento")
    
    # Relacionamentos opcionais
    aluno = models.ForeignKey(Aluno, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Aluno")
    mensalidade = models.ForeignKey(Mensalidade, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mensalidade")
    
    # Status e controle
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    comprovante = models.FileField(upload_to='comprovantes/receitas/', blank=True, null=True, verbose_name="Comprovante")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"
        ordering = ['-data_vencimento']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.get_status_display()})"
    
    @property
    def esta_vencida(self):
        if self.status == 'recebido':
            return False
        return timezone.now().date() > self.data_vencimento

class Despesa(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência'),
        ('boleto', 'Boleto'),
        ('cheque', 'Cheque'),
    ]
    
    # Informações básicas
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    categoria = models.ForeignKey(CategoriaFinanceira, on_delete=models.SET_NULL, null=True, verbose_name="Categoria")
    plano_contas = models.ForeignKey(PlanoContas, on_delete=models.SET_NULL, null=True, limit_choices_to={'tipo': 'despesa'}, verbose_name="Plano de Contas")
    
    # Fornecedor/Beneficiário
    fornecedor = models.CharField(max_length=200, verbose_name="Fornecedor/Beneficiário")
    documento_fornecedor = models.CharField(max_length=20, blank=True, null=True, verbose_name="CPF/CNPJ do Fornecedor")
    
    # Valores
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    
    # Datas
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateTimeField(null=True, blank=True, verbose_name="Data do Pagamento")
    
    # Forma de pagamento
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True, null=True, verbose_name="Forma de Pagamento")
    
    # Status e controle
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    comprovante = models.FileField(upload_to='comprovantes/despesas/', blank=True, null=True, verbose_name="Comprovante")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ['-data_vencimento']
    
    def __str__(self):
        return f"{self.descricao} - {self.fornecedor} - R$ {self.valor} ({self.get_status_display()})"
    
    @property
    def esta_vencida(self):
        if self.status == 'pago':
            return False
        return timezone.now().date() > self.data_vencimento

class FluxoCaixa(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    # Informações básicas
    data = models.DateField(verbose_name="Data")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, verbose_name="Tipo")
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    
    # Relacionamentos
    receita = models.ForeignKey(Receita, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Receita")
    despesa = models.ForeignKey(Despesa, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Despesa")
    categoria = models.ForeignKey(CategoriaFinanceira, on_delete=models.SET_NULL, null=True, verbose_name="Categoria")
    
    # Saldo
    saldo_anterior = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Saldo Anterior")
    saldo_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Saldo Atual")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Fluxo de Caixa"
        verbose_name_plural = "Fluxo de Caixa"
        ordering = ['-data', '-data_criacao']
    
    def __str__(self):
        sinal = "+" if self.tipo == 'entrada' else "-"
        return f"{self.data.strftime('%d/%m/%Y')} - {self.descricao} - {sinal}R$ {self.valor}"
    
    def save(self, *args, **kwargs):
        # Calcular saldo atual
        if self.tipo == 'entrada':
            self.saldo_atual = self.saldo_anterior + self.valor
        else:
            self.saldo_atual = self.saldo_anterior - self.valor
        
        super().save(*args, **kwargs)

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
    
    # Banco para boletos
    banco_codigo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Código do Banco")
    banco_agencia = models.CharField(max_length=10, blank=True, null=True, verbose_name="Agência")
    banco_conta = models.CharField(max_length=20, blank=True, null=True, verbose_name="Conta")
    banco_carteira = models.CharField(max_length=10, blank=True, null=True, verbose_name="Carteira")
    
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

class RelatorioFinanceiro(models.Model):
    TIPO_CHOICES = [
        ('mensal', 'Mensal'),
        ('anual', 'Anual'),
        ('periodo', 'Período'),
        ('inadimplencia', 'Inadimplência'),
        ('fluxo_caixa', 'Fluxo de Caixa'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo de Relatório")
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim")
    
    # Totalizadores
    total_receitas = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total de Receitas")
    total_despesas = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total de Despesas")
    saldo_periodo = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Saldo do Período")
    
    # Detalhes
    total_mensalidades_pagas = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Mensalidades Pagas")
    total_mensalidades_pendentes = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Mensalidades Pendentes")
    quantidade_alunos_inadimplentes = models.IntegerField(default=0, verbose_name="Quantidade de Alunos Inadimplentes")
    
    # Arquivo do relatório
    arquivo_pdf = models.FileField(upload_to='relatorios/financeiro/', blank=True, null=True, verbose_name="Arquivo PDF")
    
    # Metadados
    data_geracao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Geração")
    gerado_por = models.CharField(max_length=150, verbose_name="Gerado por")
    
    class Meta:
        verbose_name = "Relatório Financeiro"
        verbose_name_plural = "Relatórios Financeiros"
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"Relatório {self.get_tipo_display()} - {self.data_inicio} a {self.data_fim}"
