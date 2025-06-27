from django import forms
from .models import Aluno
from django.core.exceptions import ValidationError
import re

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = '__all__'
        exclude = ['data_criacao', 'data_atualizacao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_nome': forms.TextInput(attrs={'class': 'form-control'}),
            'responsavel_telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'data_ingresso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Verifica se o CPF está no formato correto
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
                raise ValidationError('CPF deve estar no formato 000.000.000-00')
            
            # Verifica se já existe outro aluno com este CPF (exceto o atual em caso de edição)
            if Aluno.objects.filter(cpf=cpf).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
                raise ValidationError('Este CPF já está cadastrado para outro aluno')
        return cpf
    
    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula')
        if matricula:
            # Verifica se já existe outro aluno com esta matrícula (exceto o atual em caso de edição)
            if Aluno.objects.filter(matricula=matricula).exclude(pk=self.instance.pk if self.instance.pk else None).exists():
                raise ValidationError('Este número de matrícula já está em uso')
        return matricula
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone and not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone):
            raise ValidationError('Telefone deve estar no formato (00) 00000-0000')
        return telefone
    
    def clean_responsavel_telefone(self):
        telefone = self.cleaned_data.get('responsavel_telefone')
        if telefone and not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', telefone):
            raise ValidationError('Telefone deve estar no formato (00) 00000-0000')
        return telefone
