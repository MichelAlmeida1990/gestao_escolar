from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import uuid

class MatriculaOnline(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ]
    
    TURNO_CHOICES = [
        ('manha', 'Manhã'),
        ('tarde', 'Tarde'),
        ('noite', 'Noite'),
        ('integral', 'Integral'),
    ]
    
    # Informações básicas
    codigo_matricula = models.CharField(max_length=20, unique=True, verbose_name="Código da Matrícula")
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    cpf = models.CharField(
        max_length=14, 
        verbose_name="CPF",
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message="CPF deve estar no formato 000.000.000-00"
        )]
    )
    rg = models.CharField(max_length=20, verbose_name="RG")
    
    # Contato
    telefone = models.CharField(max_length=15, verbose_name="Telefone")
    email = models.EmailField(verbose_name="E-mail")
    
    # Endereço
    endereco = models.CharField(max_length=200, verbose_name="Endereço")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    cidade = models.CharField(max_length=100, verbose_name="Cidade")
    estado = models.CharField(max_length=2, verbose_name="Estado")
    cep = models.CharField(max_length=9, verbose_name="CEP")
    
    # Informações escolares
    serie_desejada = models.CharField(max_length=50, verbose_name="Série Desejada")
    turno_desejado = models.CharField(max_length=20, choices=TURNO_CHOICES, verbose_name="Turno Desejado")
    escola_anterior = models.CharField(max_length=200, blank=True, null=True, verbose_name="Escola Anterior")
    ano_letivo = models.IntegerField(default=timezone.now().year, verbose_name="Ano Letivo")
    
    # Responsável
    responsavel_nome = models.CharField(max_length=200, verbose_name="Nome do Responsável")
    responsavel_cpf = models.CharField(
        max_length=14, 
        verbose_name="CPF do Responsável",
        validators=[RegexValidator(
            regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            message="CPF deve estar no formato 000.000.000-00"
        )]
    )
    responsavel_telefone = models.CharField(max_length=15, verbose_name="Telefone do Responsável")
    responsavel_email = models.EmailField(verbose_name="E-mail do Responsável")
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Validação e aprovação
    aprovado_por = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Aprovado por"
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    motivo_rejeicao = models.TextField(blank=True, null=True, verbose_name="Motivo da Rejeição")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    token_confirmacao = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Token de Confirmação")
    
    class Meta:
        verbose_name = "Matrícula Online"
        verbose_name_plural = "Matrículas Online"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome_completo} - {self.codigo_matricula}"
    
    def save(self, *args, **kwargs):
        if not self.codigo_matricula:
            # Gerar código único de matrícula
            ano = timezone.now().year
            ultima_matricula = MatriculaOnline.objects.filter(
                codigo_matricula__startswith=f"MAT{ano}"
            ).order_by('-codigo_matricula').first()
            
            if ultima_matricula:
                ultimo_numero = int(ultima_matricula.codigo_matricula[-4:])
                novo_numero = ultimo_numero + 1
            else:
                novo_numero = 1
            
            self.codigo_matricula = f"MAT{ano}{novo_numero:04d}"
        
        super().save(*args, **kwargs)
    
    def aprovar(self, usuario_aprovador):
        """Aprova a matrícula"""
        self.status = 'aprovada'
        self.aprovado_por = usuario_aprovador
        self.data_aprovacao = timezone.now()
        self.save()
    
    def rejeitar(self, motivo, usuario_aprovador):
        """Rejeita a matrícula"""
        self.status = 'rejeitada'
        self.motivo_rejeicao = motivo
        self.aprovado_por = usuario_aprovador
        self.data_aprovacao = timezone.now()
        self.save()
    
    def cancelar(self):
        """Cancela a matrícula"""
        self.status = 'cancelada'
        self.save()

class DocumentoMatricula(models.Model):
    TIPO_CHOICES = [
        ('certidao_nascimento', 'Certidão de Nascimento'),
        ('rg', 'RG'),
        ('cpf', 'CPF'),
        ('comprovante_residencia', 'Comprovante de Residência'),
        ('historico_escolar', 'Histórico Escolar'),
        ('declaracao_transferencia', 'Declaração de Transferência'),
        ('carteira_vacinacao', 'Carteira de Vacinação'),
        ('foto', 'Foto 3x4'),
        ('outro', 'Outro'),
    ]
    
    matricula = models.ForeignKey(MatriculaOnline, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo de Documento")
    arquivo = models.FileField(upload_to='documentos_matricula/', verbose_name="Arquivo")
    nome_arquivo = models.CharField(max_length=255, verbose_name="Nome do Arquivo")
    tamanho_arquivo = models.IntegerField(verbose_name="Tamanho do Arquivo (bytes)")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data do Upload")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Documento da Matrícula"
        verbose_name_plural = "Documentos da Matrícula"
        ordering = ['tipo', 'data_upload']
    
    def __str__(self):
        return f"{self.matricula.nome_completo} - {self.get_tipo_display()}"
    
    def clean(self):
        # Validar tamanho do arquivo (máximo 10MB)
        if self.arquivo and self.arquivo.size > 10 * 1024 * 1024:
            raise ValidationError("O arquivo não pode ter mais de 10MB.")
        
        # Validar tipo de arquivo
        extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        if self.arquivo:
            import os
            nome, extensao = os.path.splitext(self.arquivo.name)
            if extensao.lower() not in extensoes_permitidas:
                raise ValidationError(f"Tipo de arquivo não permitido. Use: {', '.join(extensoes_permitidas)}")

class ConfiguracaoMatricula(models.Model):
    """Configurações do sistema de matrículas online"""
    
    # Período de matrículas
    data_inicio_matriculas = models.DateField(verbose_name="Data de Início das Matrículas")
    data_fim_matriculas = models.DateField(verbose_name="Data de Fim das Matrículas")
    
    # Séries disponíveis
    series_disponiveis = models.JSONField(default=list, verbose_name="Séries Disponíveis")
    
    # Turnos disponíveis
    turnos_disponiveis = models.JSONField(default=list, verbose_name="Turnos Disponíveis")
    
    # Documentos obrigatórios
    documentos_obrigatorios = models.JSONField(default=list, verbose_name="Documentos Obrigatórios")
    
    # Configurações de email
    email_confirmacao_ativa = models.BooleanField(default=True, verbose_name="Enviar Email de Confirmação")
    email_aprovacao_ativa = models.BooleanField(default=True, verbose_name="Enviar Email de Aprovação")
    email_rejeicao_ativa = models.BooleanField(default=True, verbose_name="Enviar Email de Rejeição")
    
    # Configurações gerais
    matricula_ativa = models.BooleanField(default=True, verbose_name="Matrículas Ativas")
    max_documentos_por_matricula = models.IntegerField(default=10, verbose_name="Máximo de Documentos por Matrícula")
    tamanho_max_arquivo = models.IntegerField(default=10485760, verbose_name="Tamanho Máximo de Arquivo (bytes)")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última Atualização")
    
    class Meta:
        verbose_name = "Configuração de Matrícula"
        verbose_name_plural = "Configurações de Matrícula"
    
    def __str__(self):
        return f"Configuração de Matrículas - {self.data_inicio_matriculas.year}"
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração única ou cria uma nova"""
        config, created = cls.objects.get_or_create(id=1)
        if created:
            # Configurações padrão
            config.data_inicio_matriculas = timezone.now().date()
            config.data_fim_matriculas = timezone.now().date().replace(month=12, day=31)
            config.series_disponiveis = [
                'Educação Infantil - Maternal',
                'Educação Infantil - Jardim I',
                'Educação Infantil - Jardim II',
                '1º Ano do Ensino Fundamental',
                '2º Ano do Ensino Fundamental',
                '3º Ano do Ensino Fundamental',
                '4º Ano do Ensino Fundamental',
                '5º Ano do Ensino Fundamental',
                '6º Ano do Ensino Fundamental',
                '7º Ano do Ensino Fundamental',
                '8º Ano do Ensino Fundamental',
                '9º Ano do Ensino Fundamental',
            ]
            config.turnos_disponiveis = ['manha', 'tarde', 'noite', 'integral']
            config.documentos_obrigatorios = [
                'certidao_nascimento',
                'rg',
                'cpf',
                'comprovante_residencia',
                'historico_escolar',
                'carteira_vacinacao',
                'foto'
            ]
            config.save()
        return config
