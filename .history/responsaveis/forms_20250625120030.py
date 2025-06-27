from django import forms
from .models import Responsavel, ResponsavelAluno
import re

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
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if telefone:
            # Remove todos os caracteres não numéricos
            telefone_numeros = re.sub(r'\D', '', telefone)
            # Formata automaticamente para o padrão brasileiro
            if len(telefone_numeros) == 11:
                telefone = f"({telefone_numeros[:2]}) {telefone_numeros[2:7]}-{telefone_numeros[7:]}"
            elif len(telefone_numeros) == 10:
                telefone = f"({telefone_numeros[:2]}) {telefone_numeros[2:6]}-{telefone_numeros[6:]}"
            elif telefone_numeros:
                # Se não tem 10 ou 11 dígitos, mantém os números apenas
                telefone = telefone_numeros
        return telefone

class ResponsavelAlunoForm(forms.ModelForm):
    class Meta:
        model = ResponsavelAluno
        fields = ['aluno', 'tipo_relacao']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
