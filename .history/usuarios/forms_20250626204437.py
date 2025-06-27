from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .models import PerfilUsuario

class LoginCustomForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome de usuário ou email',
            'id': 'id_username'
        }),
        label='Usuário'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Senha',
            'id': 'id_password'
        }),
        label='Senha'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Lembrar-me'
    )

class RecuperacaoSenhaForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu email',
            'id': 'id_email'
        }),
        label='Email',
        help_text='Digite o email associado à sua conta.'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Não revelar se o email existe ou não por questões de segurança
        return email

class RedefinirSenhaForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nova senha',
            'id': 'id_new_password1'
        }),
        label='Nova senha',
        help_text='Sua senha deve ter pelo menos 8 caracteres.'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha',
            'id': 'id_new_password2'
        }),
        label='Confirmar nova senha'
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if password:
            validate_password(password, self.user)
        return password

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = [
            'telefone', 'foto', 'data_nascimento', 'endereco',
            'session_timeout', 'max_sessions'
        ]
        widgets = {
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço completo'
            }),
            'session_timeout': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 300,
                'max': 86400,
                'step': 300
            }),
            'max_sessions': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5
            }),
        }
        labels = {
            'telefone': 'Telefone',
            'foto': 'Foto do perfil',
            'data_nascimento': 'Data de nascimento',
            'endereco': 'Endereço',
            'session_timeout': 'Timeout da sessão (segundos)',
            'max_sessions': 'Máximo de sessões simultâneas'
        }
        help_texts = {
            'session_timeout': 'Tempo em segundos para expirar a sessão por inatividade (300s = 5min)',
            'max_sessions': 'Número máximo de sessões simultâneas permitidas'
        }
    
    def clean_foto(self):
        foto = self.cleaned_data.get('foto')
        if foto:
            # Validar tamanho do arquivo (máximo 5MB)
            if foto.size > 5 * 1024 * 1024:
                raise ValidationError('A foto deve ter no máximo 5MB.')
            
            # Validar tipo de arquivo
            if not foto.content_type.startswith('image/'):
                raise ValidationError('Apenas arquivos de imagem são permitidos.')
            
            # Validar extensão
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(foto.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError('Apenas arquivos JPG, PNG e GIF são permitidos.')
        
        return foto

class AlterarTipoUsuarioForm(forms.ModelForm):
    """Formulário para administradores alterarem tipo de usuário"""
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_usuario']
        widgets = {
            'tipo_usuario': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apenas staff pode ver todas as opções
        if not hasattr(self, 'request') or not self.request.user.is_staff:
            self.fields['tipo_usuario'].widget = forms.HiddenInput()

class ConfiguracaoSegurancaForm(forms.ModelForm):
    """Formulário para configurações de segurança"""
    class Meta:
        model = PerfilUsuario
        fields = [
            'force_password_change',
            'dois_fatores_ativo',
            'session_timeout',
            'max_sessions'
        ]
        widgets = {
            'force_password_change': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'dois_fatores_ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'session_timeout': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 300,
                'max': 86400
            }),
            'max_sessions': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
        }
        labels = {
            'force_password_change': 'Forçar mudança de senha no próximo login',
            'dois_fatores_ativo': 'Autenticação de dois fatores',
            'session_timeout': 'Timeout da sessão (segundos)',
            'max_sessions': 'Máximo de sessões simultâneas'
        } 