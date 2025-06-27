from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from alunos.models import Aluno
from professores.models import Professor
from datetime import datetime, timedelta

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    cor = models.CharField(max_length=7, default="#007bff", verbose_name="Cor (Hex)", help_text="Cor para identificação visual")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Editora(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome da Editora")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    site = models.URLField(blank=True, null=True, verbose_name="Site")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Editora"
        verbose_name_plural = "Editoras"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Autor(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Autor")
    nacionalidade = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nacionalidade")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    biografia = models.TextField(blank=True, null=True, verbose_name="Biografia")
    foto = models.ImageField(upload_to='autores/', blank=True, null=True, verbose_name="Foto")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome

class Livro(models.Model):
    TIPO_CHOICES = [
        ('livro', 'Livro'),
        ('revista', 'Revista'),
        ('jornal', 'Jornal'),
        ('manual', 'Manual'),
        ('apostila', 'Apostila'),
        ('dvd', 'DVD'),
        ('cd', 'CD'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('disponivel', 'Disponível'),
        ('emprestado', 'Emprestado'),
        ('reservado', 'Reservado'),
        ('manutencao', 'Manutenção'),
        ('perdido', 'Perdido'),
        ('danificado', 'Danificado'),
    ]
    
    # Informações básicas
    titulo = models.CharField(max_length=200, verbose_name="Título")
    subtitulo = models.CharField(max_length=200, blank=True, null=True, verbose_name="Subtítulo")
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="ISBN")
    codigo_barras = models.CharField(max_length=50, unique=True, verbose_name="Código de Barras")
    
    # Classificação
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, verbose_name="Categoria")
    autores = models.ManyToManyField(Autor, verbose_name="Autores")
    editora = models.ForeignKey(Editora, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Editora")
    
    # Detalhes da publicação
    ano_publicacao = models.IntegerField(validators=[MinValueValidator(1000), MaxValueValidator(2100)], verbose_name="Ano de Publicação")
    edicao = models.CharField(max_length=50, blank=True, null=True, verbose_name="Edição")
    idioma = models.CharField(max_length=50, default="Português", verbose_name="Idioma")
    paginas = models.IntegerField(blank=True, null=True, verbose_name="Número de Páginas")
    
    # Informações do acervo
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='livro', verbose_name="Tipo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel', verbose_name="Status")
    localizacao = models.CharField(max_length=100, verbose_name="Localização", help_text="Ex: Estante A, Prateleira 3")
    
    # Controle
    exemplares_total = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Total de Exemplares")
    exemplares_disponiveis = models.IntegerField(default=1, validators=[MinValueValidator(0)], verbose_name="Exemplares Disponíveis")
    valor_livro = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valor do Livro")
    
    # Descrição e observações
    sinopse = models.TextField(blank=True, null=True, verbose_name="Sinopse")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    capa = models.ImageField(upload_to='livros/capas/', blank=True, null=True, verbose_name="Capa")
    
    # Metadados
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"
        ordering = ['titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.codigo_barras})"
    
    @property
    def esta_disponivel(self):
        return self.exemplares_disponiveis > 0 and self.status == 'disponivel'
    
    @property
    def autores_lista(self):
        return ", ".join([autor.nome for autor in self.autores.all()])

class Emprestimo(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('devolvido', 'Devolvido'),
        ('atrasado', 'Atrasado'),
        ('perdido', 'Perdido'),
        ('renovado', 'Renovado'),
    ]
    
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]
    
    # Informações do empréstimo
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, verbose_name="Livro")
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, verbose_name="Tipo de Usuário")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Aluno")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Professor")
    
    # Datas
    data_emprestimo = models.DateTimeField(default=timezone.now, verbose_name="Data do Empréstimo")
    data_prevista_devolucao = models.DateField(verbose_name="Data Prevista para Devolução")
    data_devolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data da Devolução")
    
    # Status e controle
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ativo', verbose_name="Status")
    renovacoes = models.IntegerField(default=0, verbose_name="Número de Renovações")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Multa
    valor_multa = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor da Multa")
    multa_paga = models.BooleanField(default=False, verbose_name="Multa Paga")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        ordering = ['-data_emprestimo']
    
    def __str__(self):
        usuario = self.aluno.nome if self.aluno else self.professor.nome
        return f"{self.livro.titulo} - {usuario} ({self.data_emprestimo.strftime('%d/%m/%Y')})"
    
    @property
    def usuario(self):
        return self.aluno if self.aluno else self.professor
    
    @property
    def nome_usuario(self):
        return self.usuario.nome if self.usuario else "Usuário não identificado"
    
    @property
    def esta_atrasado(self):
        if self.status == 'devolvido':
            return False
        return timezone.now().date() > self.data_prevista_devolucao
    
    @property
    def dias_atraso(self):
        if not self.esta_atrasado:
            return 0
        return (timezone.now().date() - self.data_prevista_devolucao).days
    
    def calcular_multa(self, valor_por_dia=1.00):
        """Calcula a multa baseada nos dias de atraso"""
        if not self.esta_atrasado:
            return 0
        return self.dias_atraso * valor_por_dia
    
    def pode_renovar(self, max_renovacoes=2):
        """Verifica se o empréstimo pode ser renovado"""
        return (self.status == 'ativo' and 
                self.renovacoes < max_renovacoes and 
                not self.esta_atrasado)

class Reserva(models.Model):
    STATUS_CHOICES = [
        ('ativa', 'Ativa'),
        ('atendida', 'Atendida'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]
    
    TIPO_USUARIO_CHOICES = [
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
    ]
    
    # Informações da reserva
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, verbose_name="Livro")
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES, verbose_name="Tipo de Usuário")
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Aluno")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Professor")
    
    # Controle
    data_reserva = models.DateTimeField(auto_now_add=True, verbose_name="Data da Reserva")
    data_expiracao = models.DateTimeField(verbose_name="Data de Expiração")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ativa', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Metadados
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-data_reserva']
        unique_together = ['livro', 'aluno', 'professor', 'status']
    
    def __str__(self):
        usuario = self.aluno.nome if self.aluno else self.professor.nome
        return f"Reserva: {self.livro.titulo} - {usuario}"
    
    @property
    def usuario(self):
        return self.aluno if self.aluno else self.professor
    
    @property
    def nome_usuario(self):
        return self.usuario.nome if self.usuario else "Usuário não identificado"
    
    @property
    def esta_expirada(self):
        return timezone.now() > self.data_expiracao
    
    def save(self, *args, **kwargs):
        if not self.data_expiracao:
            # Reserva expira em 3 dias
            self.data_expiracao = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

class ConfiguracaoBiblioteca(models.Model):
    # Configurações de empréstimo
    dias_emprestimo_aluno = models.IntegerField(default=7, verbose_name="Dias de Empréstimo - Aluno")
    dias_emprestimo_professor = models.IntegerField(default=14, verbose_name="Dias de Empréstimo - Professor")
    max_renovacoes = models.IntegerField(default=2, verbose_name="Máximo de Renovações")
    max_livros_aluno = models.IntegerField(default=3, verbose_name="Máximo de Livros por Aluno")
    max_livros_professor = models.IntegerField(default=5, verbose_name="Máximo de Livros por Professor")
    
    # Multas
    valor_multa_dia = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name="Valor da Multa por Dia")
    
    # Reservas
    dias_reserva = models.IntegerField(default=3, verbose_name="Dias de Validade da Reserva")
    
    # Informações da biblioteca
    nome_biblioteca = models.CharField(max_length=200, default="Biblioteca Escolar", verbose_name="Nome da Biblioteca")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    horario_funcionamento = models.TextField(blank=True, null=True, verbose_name="Horário de Funcionamento")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    
    class Meta:
        verbose_name = "Configuração da Biblioteca"
        verbose_name_plural = "Configurações da Biblioteca"
    
    def __str__(self):
        return f"Configurações - {self.nome_biblioteca}"
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração única ou cria uma nova"""
        config, created = cls.objects.get_or_create(id=1)
        return config
