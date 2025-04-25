from django.db import models

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    serie = models.CharField(max_length=50)
    turno = models.CharField(max_length=20)
    ano_letivo = models.IntegerField()
    capacidade = models.IntegerField()
    
    def __str__(self):
        return self.nome
