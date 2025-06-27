from django import forms
from .models import Comunicado

class ComunicadoForm(forms.ModelForm):
    class Meta:
        model = Comunicado
        fields = ['titulo', 'conteudo', 'para_todos', 'turmas', 'alunos']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 5}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'alunos': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }
