from django import forms
from .models import Nota
from alunos.models import Aluno
from turmas.models import Turma

class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['valor']

class AlunoSelecionarForm(forms.Form):
    aluno = forms.ModelChoiceField(
        queryset=Aluno.objects.all(),
        label="Selecione o aluno",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class TurmaSelecionarForm(forms.Form):
    turma = forms.ModelChoiceField(
        queryset=Turma.objects.all(),
        label="Selecione a turma",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
