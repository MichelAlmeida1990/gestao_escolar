from django import forms
from .models import Responsavel, RelacaoAlunoResponsavel
from django.contrib.auth.models import User

class ResponsavelForm(forms.ModelForm):
    """
    Formulário para criação e edição de responsáveis
    """
    class Meta:
        model = Responsavel
        exclude = ['usuario', 'data_cadastro', 'ativo']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
            'cpf': forms.TextInput(attrs={'class': 'cpf-mask'}),
            'telefone': forms.TextInput(attrs={'class': 'phone-mask'}),
            'celular': forms.TextInput(attrs={'class': 'phone-mask'}),
            'cep': forms.TextInput(attrs={'class': 'cep-mask'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class RelacaoAlunoResponsavelForm(forms.ModelForm):
    """
    Formulário para estabelecer relação entre aluno e responsável
    """
    class Meta:
        model = RelacaoAlunoResponsavel
        exclude = ['data_inicio']
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição de dados básicos do usuário
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
