from django.db import models

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    serie = models.CharField(max_length=50)
    turno = models.CharField(max_length=20)
    ano_letivo = models.IntegerField()
    capacidade = models.IntegerField()
    
    def __str__(self):
        return self.nome
    # Adicione ao final do arquivo turmas/models.py
class TurmaAluno(models.Model):
    turma = models.ForeignKey('Turma', on_delete=models.CASCADE, related_name='alunos_matriculados')
    aluno = models.ForeignKey('alunos.Aluno', on_delete=models.CASCADE, related_name='turmas_matriculadas')
    data_matricula = models.DateField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Matrícula de Aluno'
        verbose_name_plural = 'Matrículas de Alunos'
        unique_together = ['turma', 'aluno']

    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome}"

