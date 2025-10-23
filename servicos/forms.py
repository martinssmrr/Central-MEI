from django import forms
from django.core.validators import RegexValidator
import re
from .models import SolicitacaoBaixaMEI

ESTADO_CHOICES = [
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]

ORGAO_EXPEDIDOR_CHOICES = [
    ('', 'Selecione o órgão expedidor'),
    ('SSP', 'SSP - Secretaria de Segurança Pública'),
    ('IFP', 'IFP - Instituto Felix Pacheco'),
    ('IFF', 'IFF - Instituto de Identificação Forense'),
    ('IGP', 'IGP - Instituto Geral de Perícias'),
    ('PC', 'PC - Polícia Civil'),
    ('DETRAN', 'DETRAN - Departamento Estadual de Trânsito'),
    ('EB', 'EB - Exército Brasileiro'),
    ('FAB', 'FAB - Força Aérea Brasileira'),
    ('MB', 'MB - Marinha do Brasil'),
    ('PF', 'PF - Polícia Federal'),
    ('PRF', 'PRF - Polícia Rodoviária Federal'),
]

ESTADO_CHOICES = [
    ('', 'Selecione o estado'),
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]

CNAE_CHOICES = [
    # Comércio
    ('4711302', 'Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios - minimercados, mercearias e armazéns'),
    ('4712100', 'Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios - supermercados'),
    ('4713002', 'Lojas de departamentos ou magazines'),
    ('4721102', 'Padaria e confeitaria com predominância de revenda'),
    ('4722901', 'Comércio varejista de carnes - açougues'),
    ('4723700', 'Comércio varejista de bebidas'),
    ('4724500', 'Comércio varejista de hortifrutigranjeiros'),
    ('4729699', 'Comércio varejista de produtos alimentícios em geral ou especializado em produtos alimentícios não especificados anteriormente'),
    ('4751201', 'Comércio varejista especializado de equipamentos e suprimentos de informática'),
    ('4752100', 'Comércio varejista especializado de equipamentos de telefonia e comunicação'),
    ('4753900', 'Comércio varejista especializado de eletrodomésticos e equipamentos de áudio e vídeo'),
    ('4754701', 'Comércio varejista de móveis'),
    ('4755501', 'Comércio varejista de tecidos'),
    ('4756300', 'Comércio varejista especializado de instrumentos musicais e acessórios'),
    ('4757100', 'Comércio varejista especializado de peças e acessórios para veículos automotores'),
    ('4759801', 'Comércio varejista de artigos do vestuário e acessórios'),
    ('4771701', 'Comércio varejista de produtos farmacêuticos sem manipulação de fórmulas'),
    ('4772500', 'Comércio varejista de cosméticos, produtos de perfumaria e de higiene pessoal'),
    ('4773300', 'Comércio varejista de artigos médicos e ortopédicos'),
    ('4774100', 'Comércio varejista de artigos de óptica'),
    ('4781400', 'Comércio varejista de artigos do vestuário e acessórios'),
    ('4782201', 'Comércio varejista de calçados'),
    ('4783101', 'Comércio varejista de artigos de viagem'),
    ('4784901', 'Comércio varejista de brinquedos e artigos recreativos'),
    ('4785703', 'Comércio varejista de artigos usados'),
    
    # Serviços
    ('9602501', 'Cabeleireiros, manicure e pedicure'),
    ('9603301', 'Gestão e manutenção de cemitérios'),
    ('9609208', 'Outras atividades de serviços pessoais'),
    ('8299701', 'Serviços de organização de feiras, congressos, exposições e festas'),
    ('8230001', 'Serviços de organização de feiras, congressos, exposições e festas'),
    ('7500100', 'Atividades veterinárias'),
    ('7319002', 'Promoção de vendas'),
    ('7311400', 'Agências de publicidade'),
    ('6910200', 'Atividades jurídicas'),
    ('6920601', 'Atividades de consultoria e auditoria contábil e tributária'),
    ('8640205', 'Atividade médica ambulatorial com recursos para realização de procedimentos cirúrgicos'),
    ('8630501', 'Atividade médica ambulatorial restrita a consultas'),
    ('8650001', 'Atividades de psicologia e psicanálise'),
    ('8660700', 'Atividades de apoio à gestão de saúde'),
    ('8690901', 'Atividades de práticas integrativas e complementares em saúde humana'),
    ('8712300', 'Atividades de fornecimento de infraestrutura de apoio e assistência a paciente no domicílio'),
    ('8720401', 'Atividades de centros de assistência psicossocial'),
    ('8730101', 'Atividades de cuidados residenciais para idosos'),
    ('8800600', 'Serviços de assistência social sem alojamento'),
    
    # Indústria
    ('1091101', 'Fabricação de produtos de padaria, confeitaria e pastelaria'),
    ('1099601', 'Fabricação de fermentos e leveduras'),
    ('1411801', 'Confecção de roupas íntimas'),
    ('1412601', 'Confecção de peças do vestuário, exceto roupas íntimas e confecção de roupas profissionais'),
    ('1413401', 'Confecção de roupas profissionais'),
    ('1531901', 'Fabricação de calçados de couro'),
    ('1540800', 'Fabricação de partes para calçados, de qualquer material'),
    ('1610201', 'Serrarias com desdobramento de madeira'),
    ('1621800', 'Fabricação de madeira laminada e de chapas de madeira compensada, prensada e aglomerada'),
    ('1622600', 'Fabricação de casas de madeira pré-fabricadas'),
    ('1629301', 'Fabricação de artefatos diversos de madeira, exceto móveis'),
    ('1813001', 'Impressão de jornais'),
    ('1813099', 'Impressão de material para outros usos'),
    ('2219600', 'Fabricação de artefatos de borracha não especificados anteriormente'),
    ('2229301', 'Fabricação de artefatos diversos de material plástico'),
    ('2312500', 'Fabricação de vidro plano e de segurança'),
    ('2319200', 'Fabricação de artigos de vidro'),
    ('2330301', 'Fabricação de artefatos de concreto, cimento, fibrocimento, gesso e materiais semelhantes'),
]

FORMA_ATUACAO_CHOICES = [
    ('fixo', 'Estabelecimento Fixo'),
    ('internet', 'Internet'),
    ('televenda', 'Televenda'),
    ('porta_porta', 'Porta a Porta'),
    ('correio', 'Correio'),
    ('fixo_fora', 'Em local fixo fora da loja'),
    ('maquinas', 'Máquinas automáticas'),
]

class AbrirMeiPasso1Form(forms.Form):
    """Formulário do Passo 1: Dados básicos de contato"""
    nome_completo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome completo',
            'required': True
        }),
        label='Nome Completo'
    )
    
    telefone = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
                message='Digite um telefone válido no formato (00) 00000-0000'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
            'data-mask': '(00) 00000-0000',
            'required': True
        }),
        label='Telefone'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'required': True
        }),
        label='E-mail'
    )

class AbrirMeiPasso2Form(forms.Form):
    """Formulário do Passo 2: Dados de identificação + dados empresariais"""
    
    # Campos de identificação (movidos do Passo 1)
    cpf = forms.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='Digite um CPF válido no formato 000.000.000-00'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'data-mask': '000.000.000-00',
            'required': True
        }),
        label='CPF'
    )
    
    rg = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu RG',
            'required': True
        }),
        label='RG'
    )
    
    orgao_expedidor = forms.ChoiceField(
        choices=ORGAO_EXPEDIDOR_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': True
        }),
        label='Órgão Expedidor'
    )
    
    estado_expedidor = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': True
        }),
        label='Estado do Órgão Expedidor'
    )
    
    # Campos empresariais (já existentes no DadosEmpresariaisForm)
    cnae_primario = forms.ChoiceField(
        choices=CNAE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='CNAE Primário (Atividade Principal)'
    )
    
    cnae_secundario = forms.ChoiceField(
        choices=[('', 'Nenhuma atividade secundária')] + CNAE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        label='CNAE Secundário (Atividade Complementar)'
    )
    
    forma_atuacao = forms.ChoiceField(
        choices=FORMA_ATUACAO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Forma de Atuação'
    )
    
    capital_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0,00',
            'step': '0.01',
            'min': '0',
            'required': True
        }),
        label='Capital Inicial (R$)'
    )
    
    # Dados de endereço
    cep = forms.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='Digite um CEP válido no formato 00000-000'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000',
            'data-mask': '00000-000',
            'required': True
        }),
        label='CEP'
    )
    
    cidade = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da cidade',
            'required': True
        }),
        label='Cidade'
    )
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Estado'
    )
    
    rua = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da rua/avenida',
            'required': True
        }),
        label='Rua/Avenida'
    )
    
    numero = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número',
            'required': True
        }),
        label='Número'
    )
    
    bairro = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do bairro',
            'required': True
        }),
        label='Bairro'
    )
    
    complemento = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartamento, sala, etc. (opcional)'
        }),
        label='Complemento'
    )

class DadosPessoaisForm(forms.Form):
    nome_completo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome completo',
            'required': True
        }),
        label='Nome Completo'
    )
    
    cpf = forms.CharField(
        max_length=14,
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='Digite um CPF válido no formato 000.000.000-00'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'data-mask': '000.000.000-00',
            'required': True
        }),
        label='CPF'
    )
    
    rg = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu RG',
            'required': True
        }),
        label='RG'
    )
    
    orgao_expedidor = forms.ChoiceField(
        choices=ORGAO_EXPEDIDOR_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': True
        }),
        label='Órgão Expedidor'
    )
    
    estado_expedidor = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'required': True
        }),
        label='Estado do Órgão Expedidor'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'required': True
        }),
        label='E-mail'
    )
    
    telefone = forms.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\(\d{2}\)\s\d{4,5}-\d{4}$',
                message='Digite um telefone válido no formato (00) 00000-0000'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000',
            'data-mask': '(00) 00000-0000',
            'required': True
        }),
        label='Telefone'
    )

class DadosEmpresariaisForm(forms.Form):
    cnae_primario = forms.ChoiceField(
        choices=CNAE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='CNAE Primário (Atividade Principal)'
    )
    
    cnae_secundario = forms.ChoiceField(
        choices=[('', 'Nenhuma atividade secundária')] + CNAE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        label='CNAE Secundário (Atividade Complementar)'
    )
    
    forma_atuacao = forms.ChoiceField(
        choices=FORMA_ATUACAO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Forma de Atuação'
    )
    
    capital_inicial = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0,00',
            'step': '0.01',
            'min': '0',
            'required': True
        }),
        label='Capital Inicial (R$)'
    )
    
    # Endereço Residencial
    cep = forms.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='Digite um CEP válido no formato 00000-000'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000',
            'data-mask': '00000-000',
            'required': True
        }),
        label='CEP'
    )
    
    cidade = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a cidade',
            'required': True
        }),
        label='Cidade'
    )
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label='Estado'
    )
    
    rua = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome da rua',
            'required': True
        }),
        label='Rua/Logradouro'
    )
    
    numero = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nº',
            'required': True
        }),
        label='Número'
    )
    
    bairro = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o bairro',
            'required': True
        }),
        label='Bairro'
    )
    
    complemento = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apartamento, casa, etc. (opcional)'
        }),
        required=False,
        label='Complemento'
    )


class SolicitacaoBaixaMEIForm(forms.ModelForm):
    """
    Formulário para solicitação de baixa do MEI.
    
    Inclui validações customizadas e formatação adequada
    para todos os campos necessários.
    """
    
    class Meta:
        model = SolicitacaoBaixaMEI
        fields = [
            'cnpj_mei', 'nome_fantasia', 'nome_completo', 'cpf', 
            'data_nascimento', 'rg', 'orgao_emissor', 'nome_mae', 
            'telefone', 'email', 'cep', 'rua', 'numero', 'complemento', 
            'bairro', 'cidade', 'estado', 'observacoes'
        ]
        widgets = {
            'cnpj_mei': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000/0001-00',
                'maxlength': '18'
            }),
            'nome_fantasia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome fantasia ou razão social do MEI'
            }),
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do titular do MEI'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00',
                'maxlength': '14'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00.000.000-0'
            }),
            'orgao_emissor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: SSP, DETRAN, PC'
            }),
            'nome_mae': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo da mãe'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(11) 99999-9999',
                'maxlength': '15'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seuemail@exemplo.com'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'maxlength': '9'
            }),
            'rua': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da rua, avenida, etc.'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número do endereço'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartamento, sala, bloco, etc. (opcional)'
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
                'class': 'form-select'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Informações adicionais sobre a solicitação (opcional)'
            }),
        }
        labels = {
            'cnpj_mei': 'CNPJ do MEI',
            'nome_fantasia': 'Nome Fantasia',
            'nome_completo': 'Nome Completo',
            'cpf': 'CPF',
            'data_nascimento': 'Data de Nascimento',
            'rg': 'RG',
            'orgao_emissor': 'Órgão Emissor',
            'nome_mae': 'Nome da Mãe',
            'telefone': 'Telefone',
            'email': 'E-mail',
            'cep': 'CEP',
            'rua': 'Rua/Logradouro',
            'numero': 'Número',
            'complemento': 'Complemento',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'estado': 'Estado',
            'observacoes': 'Observações',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar opção vazia para estado
        self.fields['estado'].choices = [('', 'Selecione o estado')] + list(self.fields['estado'].choices)
        
        # Marcar campos obrigatórios
        required_fields = [
            'cnpj_mei', 'nome_fantasia', 'nome_completo', 'cpf', 
            'data_nascimento', 'rg', 'orgao_emissor', 'nome_mae', 
            'telefone', 'email', 'cep', 'rua', 'numero', 'bairro', 
            'cidade', 'estado'
        ]
        
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                self.fields[field_name].widget.attrs['required'] = True
    
    def clean_cnpj_mei(self):
        """Validação customizada para CNPJ."""
        cnpj = self.cleaned_data.get('cnpj_mei', '')
        
        # Remover caracteres especiais
        cnpj_digits = re.sub(r'[^0-9]', '', cnpj)
        
        # Validar formato básico
        if len(cnpj_digits) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos.')
        
        # Validar se não é uma sequência repetida
        if cnpj_digits == cnpj_digits[0] * 14:
            raise forms.ValidationError('CNPJ inválido.')
        
        # Retornar formatado
        return f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/{cnpj_digits[8:12]}-{cnpj_digits[12:14]}"
    
    def clean_cpf(self):
        """Validação customizada para CPF."""
        cpf = self.cleaned_data.get('cpf', '')
        
        # Remover caracteres especiais
        cpf_digits = re.sub(r'[^0-9]', '', cpf)
        
        # Validar formato básico
        if len(cpf_digits) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        
        # Validar se não é uma sequência repetida
        if cpf_digits == cpf_digits[0] * 11:
            raise forms.ValidationError('CPF inválido.')
        
        # Retornar formatado
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:11]}"
    
    def clean_telefone(self):
        """Validação customizada para telefone."""
        telefone = self.cleaned_data.get('telefone', '')
        
        # Remover caracteres especiais
        telefone_digits = re.sub(r'[^0-9]', '', telefone)
        
        # Validar formato básico (10 ou 11 dígitos)
        if len(telefone_digits) not in [10, 11]:
            raise forms.ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        
        # Retornar formatado
        if len(telefone_digits) == 11:
            return f"({telefone_digits[:2]}) {telefone_digits[2:7]}-{telefone_digits[7:11]}"
        else:
            return f"({telefone_digits[:2]}) {telefone_digits[2:6]}-{telefone_digits[6:10]}"
    
    def clean_cep(self):
        """Validação customizada para CEP."""
        cep = self.cleaned_data.get('cep', '')
        
        # Remover caracteres especiais
        cep_digits = re.sub(r'[^0-9]', '', cep)
        
        # Validar formato básico
        if len(cep_digits) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos.')
        
        # Retornar formatado
        return f"{cep_digits[:5]}-{cep_digits[5:8]}"
    
    def clean_email(self):
        """Validação customizada para e-mail."""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if not email:
            raise forms.ValidationError('E-mail é obrigatório.')
        
        return email


# Formulários para Declaração MEI em dois passos
class DeclaracaoMeiPasso1Form(forms.Form):
    """Formulário para o primeiro passo da Declaração MEI: dados de contato."""
    
    nome_completo = forms.CharField(
        max_length=200,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu nome completo',
            'required': True
        })
    )
    
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
            'required': True
        })
    )
    
    telefone = forms.CharField(
        max_length=15,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(11) 99999-9999',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^\([0-9]{2}\)\s[0-9]{4,5}-[0-9]{4}$',
                message='Telefone deve estar no formato (11) 99999-9999 ou (11) 9999-9999'
            )
        ]
    )
    
    def clean_nome_completo(self):
        """Validação customizada para nome completo."""
        nome = self.cleaned_data.get('nome_completo', '').strip()
        
        if len(nome) < 5:
            raise forms.ValidationError('Nome deve ter pelo menos 5 caracteres.')
        
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', nome):
            raise forms.ValidationError('Nome deve conter apenas letras e espaços.')
        
        return nome.title()
    
    def clean_telefone(self):
        """Validação customizada para telefone."""
        telefone = self.cleaned_data.get('telefone', '')
        
        # Remover caracteres especiais
        telefone_digits = re.sub(r'[^0-9]', '', telefone)
        
        # Validar quantidade de dígitos
        if len(telefone_digits) not in [10, 11]:
            raise forms.ValidationError('Telefone deve ter 10 ou 11 dígitos.')
        
        # Retornar formatado
        if len(telefone_digits) == 11:
            return f"({telefone_digits[:2]}) {telefone_digits[2:7]}-{telefone_digits[7:11]}"
        else:
            return f"({telefone_digits[:2]}) {telefone_digits[2:6]}-{telefone_digits[6:10]}"
    
    def clean_email(self):
        """Validação customizada para e-mail."""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if not email:
            raise forms.ValidationError('E-mail é obrigatório.')
        
        return email


class DeclaracaoMeiPasso2Form(forms.Form):
    """Formulário para o segundo passo da Declaração MEI: CNPJ, CPF e endereço."""
    
    cnpj = forms.CharField(
        max_length=18,
        label='CNPJ do MEI',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00.000.000/0001-00',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
                message='CNPJ deve estar no formato 00.000.000/0001-00'
            )
        ]
    )
    
    cpf = forms.CharField(
        max_length=14,
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato 000.000.000-00'
            )
        ]
    )
    
    cep = forms.CharField(
        max_length=9,
        label='CEP',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000',
            'required': True
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{5}-\d{3}$',
                message='CEP deve estar no formato 00000-000'
            )
        ]
    )
    
    rua = forms.CharField(
        max_length=200,
        label='Rua/Logradouro',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da rua, avenida, etc.',
            'required': True
        })
    )
    
    numero = forms.CharField(
        max_length=10,
        label='Número',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123',
            'required': True
        })
    )
    
    complemento = forms.CharField(
        max_length=100,
        label='Complemento',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apto, sala, bloco (opcional)'
        })
    )
    
    bairro = forms.CharField(
        max_length=100,
        label='Bairro',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do bairro',
            'required': True
        })
    )
    
    cidade = forms.CharField(
        max_length=100,
        label='Cidade',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome da cidade',
            'required': True
        })
    )
    
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        })
    )
    
    def clean_cnpj(self):
        """Validação customizada para CNPJ."""
        cnpj = self.cleaned_data.get('cnpj', '')
        
        # Remover caracteres especiais para validação
        cnpj_digits = re.sub(r'[^0-9]', '', cnpj)
        
        if len(cnpj_digits) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos.')
        
        # Retornar formatado
        return f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/{cnpj_digits[8:12]}-{cnpj_digits[12:14]}"
    
    def clean_cpf(self):
        """Validação customizada para CPF."""
        cpf = self.cleaned_data.get('cpf', '')
        
        # Remover caracteres especiais para validação
        cpf_digits = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf_digits) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        
        # Verificar se todos os dígitos são iguais
        if len(set(cpf_digits)) == 1:
            raise forms.ValidationError('CPF inválido.')
        
        # Retornar formatado
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:11]}"
    
    def clean_cep(self):
        """Validação customizada para CEP."""
        cep = self.cleaned_data.get('cep', '')
        
        # Remover caracteres especiais
        cep_digits = re.sub(r'[^0-9]', '', cep)
        
        # Validar formato básico
        if len(cep_digits) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos.')
        
        # Retornar formatado
        return f"{cep_digits[:5]}-{cep_digits[5:8]}"


class BaixarMeiPasso1Form(forms.Form):
    """
    Formulário para o primeiro passo da solicitação de baixa do MEI.
    Coleta dados de contato: Nome Completo, E-mail e Telefone.
    """
    nome_completo = forms.CharField(
        max_length=200,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite seu nome completo',
            'required': True
        }),
        help_text='Nome completo do titular do MEI'
    )
    
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'exemplo@email.com',
            'required': True
        }),
        help_text='E-mail para contato e envio de documentos'
    )
    
    telefone = forms.CharField(
        max_length=15,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '(00) 00000-0000',
            'required': True
        }),
        help_text='Telefone para contato (com DDD)'
    )
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone:
            return telefone
        
        # Remover caracteres não numéricos
        telefone_digits = re.sub(r'\D', '', telefone)
        
        # Validar se tem pelo menos 10 dígitos (DDD + número)
        if len(telefone_digits) < 10:
            raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos (DDD + número).')
        
        if len(telefone_digits) > 11:
            raise forms.ValidationError('Telefone deve ter no máximo 11 dígitos.')
        
        # Formatar telefone
        if len(telefone_digits) == 10:
            return f"({telefone_digits[:2]}) {telefone_digits[2:6]}-{telefone_digits[6:]}"
        else:
            return f"({telefone_digits[:2]}) {telefone_digits[2:7]}-{telefone_digits[7:]}"


class BaixarMeiPasso2Form(forms.Form):
    """
    Formulário para o segundo passo da solicitação de baixa do MEI.
    Coleta CNPJ, Nome Fantasia, CPF, RG, Data de Nascimento, Nome da Mãe e Endereço.
    """
    cnpj_mei = forms.CharField(
        max_length=18,
        label='CNPJ do MEI',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '00.000.000/0001-00',
            'required': True
        }),
        help_text='CNPJ do Microempreendedor Individual'
    )
    
    nome_fantasia = forms.CharField(
        max_length=200,
        label='Nome Fantasia',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome fantasia ou razão social',
            'required': True
        }),
        help_text='Razão social ou nome fantasia do MEI'
    )
    
    cpf = forms.CharField(
        max_length=14,
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '000.000.000-00',
            'required': True
        }),
        help_text='CPF do titular do MEI'
    )
    
    rg = forms.CharField(
        max_length=15,
        label='RG',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '00.000.000-0',
            'required': True
        }),
        help_text='Registro Geral (RG)'
    )
    
    orgao_emissor = forms.CharField(
        max_length=10,
        label='Órgão Emissor',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ex: SSP, DETRAN, PC',
            'required': True
        }),
        help_text='Órgão que emitiu o RG'
    )
    
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-lg',
            'type': 'date',
            'required': True
        }),
        help_text='Data de nascimento do titular'
    )
    
    nome_mae = forms.CharField(
        max_length=200,
        label='Nome da Mãe',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome completo da mãe',
            'required': True
        }),
        help_text='Nome completo da mãe do titular'
    )
    
    # Campos de Endereço
    cep = forms.CharField(
        max_length=9,
        label='CEP',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '00000-000',
            'required': True
        }),
        help_text='CEP do endereço comercial'
    )
    
    rua = forms.CharField(
        max_length=200,
        label='Rua/Logradouro',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome da rua, avenida',
            'required': True
        }),
        help_text='Logradouro do endereço comercial'
    )
    
    numero = forms.CharField(
        max_length=10,
        label='Número',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '123',
            'required': True
        }),
        help_text='Número do endereço'
    )
    
    complemento = forms.CharField(
        max_length=100,
        label='Complemento',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Apto, sala, bloco (opcional)'
        }),
        help_text='Complemento do endereço (opcional)'
    )
    
    bairro = forms.CharField(
        max_length=100,
        label='Bairro',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome do bairro',
            'required': True
        }),
        help_text='Bairro do endereço'
    )
    
    cidade = forms.CharField(
        max_length=100,
        label='Cidade',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome da cidade',
            'required': True
        }),
        help_text='Cidade do endereço'
    )
    
    estado = forms.ChoiceField(
        choices=[
            ('', 'Selecione o estado'),
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        ],
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'required': True
        }),
        help_text='Estado do endereço'
    )
    
    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Observações adicionais (opcional)'
        }),
        label='Observações',
        required=False,
        help_text='Informações adicionais sobre a solicitação (opcional)'
    )
    
    def clean_cnpj_mei(self):
        cnpj = self.cleaned_data.get('cnpj_mei')
        if not cnpj:
            return cnpj
        
        # Remover caracteres não numéricos
        cnpj_digits = re.sub(r'\D', '', cnpj)
        
        # Validar se tem 14 dígitos
        if len(cnpj_digits) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos.')
        
        # Formatar CNPJ
        return f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/{cnpj_digits[8:12]}-{cnpj_digits[12:14]}"
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            return cpf
        
        # Remover caracteres não numéricos
        cpf_digits = re.sub(r'\D', '', cpf)
        
        # Validar se tem 11 dígitos
        if len(cpf_digits) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        
        # Formatar CPF
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:11]}"
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if not cep:
            return cep
        
        # Remover caracteres não numéricos
        cep_digits = re.sub(r'\D', '', cep)
        
        # Validar se tem 8 dígitos
        if len(cep_digits) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos.')
        
        # Formatar CEP
        return f"{cep_digits[:5]}-{cep_digits[5:8]}"


class RegularizarMeiPasso1Form(forms.Form):
    """
    Formulário para o primeiro passo da regularização do MEI.
    Coleta dados de contato: Nome Completo, E-mail e Telefone.
    """
    nome_completo = forms.CharField(
        max_length=200,
        label='Nome Completo',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Digite seu nome completo',
            'required': True
        }),
        help_text='Nome completo do titular do MEI'
    )
    
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'exemplo@email.com',
            'required': True
        }),
        help_text='E-mail para contato e envio de documentos'
    )
    
    telefone = forms.CharField(
        max_length=15,
        label='Telefone',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '(00) 00000-0000',
            'required': True
        }),
        help_text='Telefone para contato (com DDD)'
    )
    
    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        if not telefone:
            return telefone
        
        # Remover caracteres não numéricos
        telefone_digits = re.sub(r'\D', '', telefone)
        
        # Validar se tem pelo menos 10 dígitos (DDD + número)
        if len(telefone_digits) < 10:
            raise forms.ValidationError('Telefone deve ter pelo menos 10 dígitos (DDD + número).')
        
        if len(telefone_digits) > 11:
            raise forms.ValidationError('Telefone deve ter no máximo 11 dígitos.')
        
        # Formatar telefone
        if len(telefone_digits) == 10:
            return f"({telefone_digits[:2]}) {telefone_digits[2:6]}-{telefone_digits[6:]}"
        else:
            return f"({telefone_digits[:2]}) {telefone_digits[2:7]}-{telefone_digits[7:]}"


class RegularizarMeiPasso2Form(forms.Form):
    """
    Formulário para o segundo passo da regularização do MEI.
    Coleta CPF, RG, CNPJ e endereço completo.
    """
    cpf = forms.CharField(
        max_length=14,
        label='CPF',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '000.000.000-00',
            'required': True
        }),
        help_text='CPF do titular do MEI'
    )
    
    rg = forms.CharField(
        max_length=15,
        label='RG',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '00.000.000-0',
            'required': True
        }),
        help_text='Registro Geral (RG)'
    )
    
    cnpj = forms.CharField(
        max_length=18,
        label='CNPJ do MEI',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '00.000.000/0001-00',
            'required': True
        }),
        help_text='CNPJ do Microempreendedor Individual'
    )
    
    # Campos de Endereço
    cep = forms.CharField(
        max_length=9,
        label='CEP',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '00000-000',
            'required': True
        }),
        help_text='CEP do endereço'
    )
    
    rua = forms.CharField(
        max_length=200,
        label='Rua/Logradouro',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome da rua, avenida',
            'required': True
        }),
        help_text='Logradouro do endereço'
    )
    
    numero = forms.CharField(
        max_length=10,
        label='Número',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '123',
            'required': True
        }),
        help_text='Número do endereço'
    )
    
    complemento = forms.CharField(
        max_length=100,
        label='Complemento',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Apto, sala, bloco (opcional)'
        }),
        help_text='Complemento do endereço (opcional)'
    )
    
    bairro = forms.CharField(
        max_length=100,
        label='Bairro',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome do bairro',
            'required': True
        }),
        help_text='Bairro do endereço'
    )
    
    cidade = forms.CharField(
        max_length=100,
        label='Cidade',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Nome da cidade',
            'required': True
        }),
        help_text='Cidade do endereço'
    )
    
    estado = forms.ChoiceField(
        choices=[
            ('', 'Selecione o estado'),
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        ],
        label='Estado',
        widget=forms.Select(attrs={
            'class': 'form-control form-control-lg',
            'required': True
        }),
        help_text='Estado do endereço'
    )
    
    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Observações adicionais sobre a regularização (opcional)'
        }),
        label='Observações',
        required=False,
        help_text='Informações adicionais sobre a regularização (opcional)'
    )
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            return cpf
        
        # Remover caracteres não numéricos
        cpf_digits = re.sub(r'\D', '', cpf)
        
        # Validar se tem 11 dígitos
        if len(cpf_digits) != 11:
            raise forms.ValidationError('CPF deve ter 11 dígitos.')
        
        # Formatar CPF
        return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:11]}"
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if not cnpj:
            return cnpj
        
        # Remover caracteres não numéricos
        cnpj_digits = re.sub(r'\D', '', cnpj)
        
        # Validar se tem 14 dígitos
        if len(cnpj_digits) != 14:
            raise forms.ValidationError('CNPJ deve ter 14 dígitos.')
        
        # Formatar CNPJ
        return f"{cnpj_digits[:2]}.{cnpj_digits[2:5]}.{cnpj_digits[5:8]}/{cnpj_digits[8:12]}-{cnpj_digits[12:14]}"
    
    def clean_cep(self):
        cep = self.cleaned_data.get('cep')
        if not cep:
            return cep
        
        # Remover caracteres não numéricos
        cep_digits = re.sub(r'\D', '', cep)
        
        # Validar se tem 8 dígitos
        if len(cep_digits) != 8:
            raise forms.ValidationError('CEP deve ter 8 dígitos.')
        
        # Formatar CEP
        return f"{cep_digits[:5]}-{cep_digits[5:8]}"