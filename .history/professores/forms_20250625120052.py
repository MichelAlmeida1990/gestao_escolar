from django import forms
from .models import Professor
import re

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = ['nome', 'email', 'telefone', 'formacao', 'disciplina', 'turmas']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'formacao': forms.TextInput(attrs={'class': 'form-control'}),
            'disciplina': forms.TextInput(attrs={'class': 'form-control'}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
    
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
