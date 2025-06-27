from django import forms
from .models import Responsavel, ResponsavelAluno

class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        fields = ['nome', 'cpf', 'rg', 'data_nascimento', 'telefone', 
                 'email', 'endereco', 'bairro', 'cidade', 'estado', 'cep']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ResponsavelAlunoForm(forms.ModelForm):
    class Meta:
        model = ResponsavelAluno
        fields = ['aluno', 'tipo_relacao']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
