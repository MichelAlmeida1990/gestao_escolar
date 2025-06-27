from django import forms
from .models import Aluno
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
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
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'data-max-size': '5242880'  # 5MB em bytes
            }),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        
        if foto:
            # Validar tamanho do arquivo (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError('O arquivo é muito grande. Tamanho máximo permitido: 5MB.')
            
            # Validar tipo de arquivo
            if not foto.content_type.startswith('image/'):
                raise ValidationError('Por favor, envie apenas arquivos de imagem (JPG, PNG, GIF).')
            
            # Validar dimensões da imagem
            try:
                w, h = get_image_dimensions(foto)
                if w and h:
                    # Limitar dimensões máximas (opcional)
                    if w > 2000 or h > 2000:
                        raise ValidationError('A imagem é muito grande. Dimensões máximas: 2000x2000 pixels.')
                    
                    # Garantir dimensões mínimas
                    if w < 50 or h < 50:
                        raise ValidationError('A imagem é muito pequena. Dimensões mínimas: 50x50 pixels.')
            except Exception:
                raise ValidationError('Arquivo de imagem inválido.')
        
        return foto
    
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
    
    def clean_responsavel_telefone(self):
        telefone = self.cleaned_data.get('responsavel_telefone')
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
