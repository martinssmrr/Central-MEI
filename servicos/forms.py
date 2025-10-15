from django import forms
from django.core.validators import RegexValidator
import re

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