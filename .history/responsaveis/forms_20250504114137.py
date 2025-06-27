from django import forms
from .models import Responsavel, RelacaoAlunoResponsavel

class ResponsavelForm(forms.ModelForm):
    class Meta:
        model = Responsavel
        exclude = ['usuario', 'data_cadastro']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['ativo'].widget.attrs.update({'class': 'form-check-input'})

class RelacaoAlunoResponsavelForm(forms.ModelForm):
    class Meta:
        model = RelacaoAlunoResponsavel
        exclude = ['responsavel', 'data_inicio']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['responsavel_financeiro', 'autorizado_buscar']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['responsavel_financeiro'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['autorizado_buscar'].widget.attrs.update({'class': 'form-check-input'})
