from django.db import models
from django.utils import timezone
from alunos.models import Aluno
from turmas.models import Turma
from professores.models import Professor
from notas.models import Disciplina

class RegistroFrequencia(models.Model):
    STATUS_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('atrasado', 'Atrasado'),
        ('justificado', 'Justificado'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name="Aluno")
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="Professor")
    data = models.DateField(verbose_name="Data", default=timezone.now)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='presente', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")
    
    class Meta:
        verbose_name = "Registro de Frequência"
        verbose_name_plural = "Registros de Frequência"
        unique_together = ['aluno', 'turma', 'disciplina', 'data']
        ordering = ['-data', 'turma', 'aluno__nome']
    
    def __str__(self):
        return f"{self.aluno.nome} - {self.disciplina.nome} - {self.data} - {self.get_status_display()}"

class RelatorioFrequencia(models.Model):
    PERIODO_CHOICES = [
        ('diario', 'Diário'),
        ('semanal', 'Semanal'),
        ('mensal', 'Mensal'),
        ('bimestral', 'Bimestral'),
        ('anual', 'Anual'),
    ]
    
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, verbose_name="Turma")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, verbose_name="Disciplina", null=True, blank=True)
    periodo = models.CharField(max_length=15, choices=PERIODO_CHOICES, verbose_name="Período")
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim")
    total_aulas = models.IntegerField(verbose_name="Total de Aulas", default=0)
    total_presencas = models.IntegerField(verbose_name="Total de Presenças", default=0)
    total_faltas = models.IntegerField(verbose_name="Total de Faltas", default=0)
    percentual_presenca = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="% Presença", default=0)
    
    # Metadados
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    
    class Meta:
        verbose_name = "Relatório de Frequência"
        verbose_name_plural = "Relatórios de Frequência"
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Relatório {self.turma.nome} - {self.get_periodo_display()} - {self.data_inicio} a {self.data_fim}"

class JustificativaFalta(models.Model):
    registro_frequencia = models.OneToOneField(RegistroFrequencia, on_delete=models.CASCADE, verbose_name="Registro de Frequência")
    motivo = models.TextField(verbose_name="Motivo da Justificativa")
    documento = models.FileField(upload_to='justificativas/', blank=True, null=True, verbose_name="Documento Comprobatório")
    aprovado = models.BooleanField(default=False, verbose_name="Aprovado")
    data_justificativa = models.DateTimeField(auto_now_add=True, verbose_name="Data da Justificativa")
    aprovado_por = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True, blank=True, related_name='justificativas_aprovadas', verbose_name="Aprovado por")
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Aprovação")
    
    class Meta:
        verbose_name = "Justificativa de Falta"
        verbose_name_plural = "Justificativas de Faltas"
        ordering = ['-data_justificativa']
    
    def __str__(self):
        return f"Justificativa - {self.registro_frequencia.aluno.nome} - {self.registro_frequencia.data}"
