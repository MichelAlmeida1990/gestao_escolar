from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import MatriculaOnline, DocumentoMatricula, ConfiguracaoMatricula
import re

class MatriculaOnlineForm(forms.ModelForm):
    """Formulário principal de matrícula online"""
    
    # Campos adicionais para validação
    confirmar_email = forms.EmailField(
        label="Confirmar E-mail",
        help_text="Digite novamente o e-mail para confirmação"
    )
    confirmar_responsavel_email = forms.EmailField(
        label="Confirmar E-mail do Responsável",
        help_text="Digite novamente o e-mail do responsável"
    )
    
    class Meta:
        model = MatriculaOnline
        fields = [
            'nome_completo', 'data_nascimento', 'cpf', 'rg',
            'telefone', 'email', 'endereco', 'bairro', 'cidade', 'estado', 'cep',
            'serie_desejada', 'turno_desejado', 'escola_anterior',
            'responsavel_nome', 'responsavel_cpf', 'responsavel_telefone', 'responsavel_email',
            'observacoes'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do aluno'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do RG'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, número, complemento'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da cidade'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Selecione o estado'),
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
                ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'),
                ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
                ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'),
                ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
                ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
                ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'),
                ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
                ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
                ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
            ]),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000'
            }),
            'serie_desejada': forms.Select(attrs={
                'class': 'form-control'
            }),
            'turno_desejado': forms.Select(attrs={
                'class': 'form-control'
            }),
            'escola_anterior': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da escola anterior (se aplicável)'
            }),
            'responsavel_nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do responsável'
            }),
            'responsavel_cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'responsavel_telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999'
            }),
            'responsavel_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Carregar configurações para popular as opções
        try:
            config = ConfiguracaoMatricula.get_config()
            self.fields['serie_desejada'].choices = [
                ('', 'Selecione a série desejada')
            ] + [(serie, serie) for serie in config.series_disponiveis]
            
            self.fields['turno_desejado'].choices = [
                ('', 'Selecione o turno desejado')
            ] + [(turno, dict(MatriculaOnline.TURNO_CHOICES)[turno]) 
                 for turno in config.turnos_disponiveis]
        except:
            # Fallback se não conseguir carregar configurações
            self.fields['serie_desejada'].choices = [
                ('', 'Selecione a série desejada'),
                ('Educação Infantil - Maternal', 'Educação Infantil - Maternal'),
                ('Educação Infantil - Jardim I', 'Educação Infantil - Jardim I'),
                ('Educação Infantil - Jardim II', 'Educação Infantil - Jardim II'),
                ('1º Ano do Ensino Fundamental', '1º Ano do Ensino Fundamental'),
                ('2º Ano do Ensino Fundamental', '2º Ano do Ensino Fundamental'),
                ('3º Ano do Ensino Fundamental', '3º Ano do Ensino Fundamental'),
                ('4º Ano do Ensino Fundamental', '4º Ano do Ensino Fundamental'),
                ('5º Ano do Ensino Fundamental', '5º Ano do Ensino Fundamental'),
                ('6º Ano do Ensino Fundamental', '6º Ano do Ensino Fundamental'),
                ('7º Ano do Ensino Fundamental', '7º Ano do Ensino Fundamental'),
                ('8º Ano do Ensino Fundamental', '8º Ano do Ensino Fundamental'),
                ('9º Ano do Ensino Fundamental', '9º Ano do Ensino Fundamental'),
            ]
    
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
                telefone = telefone_numeros
        return telefone
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if cep:
            # Remove caracteres não numéricos
            cep_numeros = re.sub(r'\D', '', cep)
            # Formata para o padrão brasileiro
            if len(cep_numeros) == 8:
                cep = f"{cep_numeros[:5]}-{cep_numeros[5:]}"
            else:
                cep = cep_numeros
        return cep
    
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get('data_nascimento')
        if data_nascimento:
            # Verificar se a data não é no futuro
            if data_nascimento > timezone.now().date():
                raise ValidationError("A data de nascimento não pode ser no futuro.")
            
            # Verificar se a pessoa tem pelo menos 1 ano
            idade = timezone.now().date().year - data_nascimento.year
            if idade < 1:
                raise ValidationError("A data de nascimento parece estar incorreta.")
        
        return data_nascimento
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirmar_email = cleaned_data.get('confirmar_email')
        responsavel_email = cleaned_data.get('responsavel_email')
        confirmar_responsavel_email = cleaned_data.get('confirmar_responsavel_email')
        
        # Validar confirmação de email
        if email and confirmar_email and email != confirmar_email:
            raise ValidationError("Os e-mails não coincidem.")
        
        # Validar confirmação de email do responsável
        if responsavel_email and confirmar_responsavel_email and responsavel_email != confirmar_responsavel_email:
            raise ValidationError("Os e-mails do responsável não coincidem.")
        
        # Verificar se as matrículas estão ativas
        try:
            config = ConfiguracaoMatricula.get_config()
            if not config.matricula_ativa:
                raise ValidationError("As matrículas online estão temporariamente desativadas.")
            
            hoje = timezone.now().date()
            if hoje < config.data_inicio_matriculas or hoje > config.data_fim_matriculas:
                raise ValidationError(
                    f"As matrículas estão abertas apenas entre {config.data_inicio_matriculas.strftime('%d/%m/%Y')} "
                    f"e {config.data_fim_matriculas.strftime('%d/%m/%Y')}."
                )
        except:
            pass
        
        return cleaned_data

class DocumentoMatriculaForm(forms.ModelForm):
    """Formulário para upload de documentos"""
    
    class Meta:
        model = DocumentoMatricula
        fields = ['tipo', 'arquivo', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observações sobre o documento (opcional)'
            }),
        }
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            # Verificar tamanho do arquivo
            try:
                config = ConfiguracaoMatricula.get_config()
                tamanho_max = config.tamanho_max_arquivo
            except:
                tamanho_max = 10 * 1024 * 1024  # 10MB padrão
            
            if arquivo.size > tamanho_max:
                raise ValidationError(f"O arquivo não pode ter mais de {tamanho_max // (1024*1024)}MB.")
            
            # Verificar extensão
            extensoes_permitidas = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            import os
            nome, extensao = os.path.splitext(arquivo.name)
            if extensao.lower() not in extensoes_permitidas:
                raise ValidationError(f"Tipo de arquivo não permitido. Use: {', '.join(extensoes_permitidas)}")
        
        return arquivo

class ConsultaMatriculaForm(forms.Form):
    """Formulário para consultar status da matrícula"""
    
    codigo_matricula = forms.CharField(
        max_length=20,
        label="Código da Matrícula",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: MAT20240001'
        })
    )
    email = forms.EmailField(
        label="E-mail",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@exemplo.com'
        })
    )

class ConfiguracaoMatriculaForm(forms.ModelForm):
    """Formulário para configurações de matrícula"""
    
    class Meta:
        model = ConfiguracaoMatricula
        fields = [
            'data_inicio_matriculas', 'data_fim_matriculas',
            'series_disponiveis', 'turnos_disponiveis', 'documentos_obrigatorios',
            'email_confirmacao_ativa', 'email_aprovacao_ativa', 'email_rejeicao_ativa',
            'matricula_ativa', 'max_documentos_por_matricula', 'tamanho_max_arquivo'
        ]
        widgets = {
            'data_inicio_matriculas': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'data_fim_matriculas': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'series_disponiveis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Digite uma série por linha'
            }),
            'turnos_disponiveis': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'documentos_obrigatorios': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'email_confirmacao_ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_aprovacao_ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_rejeicao_ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'matricula_ativa': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'max_documentos_por_matricula': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
            'tamanho_max_arquivo': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1024000,  # 1MB
                'max': 52428800,  # 50MB
                'step': 1024000
            }),
        }
    
    def clean_series_disponiveis(self):
        series = self.cleaned_data.get('series_disponiveis')
        if isinstance(series, str):
            # Converter string em lista (uma série por linha)
            series = [serie.strip() for serie in series.split('\n') if serie.strip()]
        return series
    
    def clean_turnos_disponiveis(self):
        turnos = self.cleaned_data.get('turnos_disponiveis')
        if isinstance(turnos, list):
            return turnos
        return []
    
    def clean_documentos_obrigatorios(self):
        documentos = self.cleaned_data.get('documentos_obrigatorios')
        if isinstance(documentos, list):
            return documentos
        return [] 