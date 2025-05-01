from django import forms
from .models import Turma
from alunos.models import Aluno

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = '__all__'
        exclude = ['alunos']

class AlunoTurmaForm(forms.Form):
    alunos = forms.ModelMultipleChoiceField(
        queryset=Aluno.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
