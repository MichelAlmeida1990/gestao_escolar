from django import forms
from .models import Professor

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
