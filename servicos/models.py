from django.db import models
from django.contrib.auth.models import User

SERVICOS_CHOICES = [
    ('abrir_mei', 'Abrir MEI'),
    ('regularizar_mei', 'Regularizar MEI'),
    ('declaracao_anual_mei', 'Declaração Anual MEI'),
    ('baixar_mei', 'Baixar MEI'),
    ('alteracao_mei', 'Alteração MEI'),
    ('inscricao_estadual', 'Inscrição Estadual'),
    ('parcelamento_mei', 'Parcelamento MEI'),
    ('certificado_mei', 'Certificado MEI - CCMEI'),
    ('desenquadramento_mei', 'Desenquadramento MEI'),
    ('reenquadramento_mei', 'Reenquadramento MEI'),
    ('nota_fiscal', 'Nota Fiscal'),
    ('buscar_mei_cpf', 'Buscar MEI pelo CPF'),
    ('certidao_negativa_debitos', 'Certidão Negativa de Débitos'),
    ('situacao_mei', 'Situação MEI'),
    ('alvara_funcionamento', 'Alvará de Funcionamento'),
    ('dividas_mei', 'Dívidas MEI'),
    ('licenca_maternidade', 'Licença Maternidade'),
    ('extrato_cnpj_mei', 'Extrato CNPJ MEI'),
    ('certidao_negativa_fgts', 'Certidão Negativa de FGTS'),
    ('certidao_negativa_trabalhistas', 'Certidão Negativa de Débitos Trabalhistas'),
    ('certidao_inss', 'Certidão de INSS'),
    ('aposentadoria_mei', 'Aposentadoria MEI'),
    ('certificado_digital', 'Certificado Digital'),
]

class Servico(models.Model):
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    tipo = models.CharField(max_length=50, choices=SERVICOS_CHOICES)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    tempo_estimado = models.CharField(max_length=100, help_text="Ex: 2-3 dias úteis")
    ativo = models.BooleanField(default=True)
    ordem = models.IntegerField(default=0, help_text="Ordem de exibição")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'nome']
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return self.nome


class SolicitacaoServico(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando_cliente', 'Aguardando Cliente'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Solicitação de Serviço'
        verbose_name_plural = 'Solicitações de Serviços'

    def __str__(self):
        return f"{self.servico.nome} - {self.usuario.username}"

class SolicitacaoMEI(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Em Processamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
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
    
    # Dados Pessoais
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=15)
    orgao_expedidor = models.CharField(max_length=10)
    estado_expedidor = models.CharField(max_length=2, default='')
    email = models.EmailField()
    telefone = models.CharField(max_length=15)
    
    # Dados Empresariais
    cnae_primario = models.CharField(max_length=20)
    cnaes_secundarios = models.TextField(blank=True, help_text="CNAE secundário opcional")
    forma_atuacao = models.CharField(max_length=20, choices=FORMA_ATUACAO_CHOICES)
    capital_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Endereço
    cep = models.CharField(max_length=9)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    complemento = models.CharField(max_length=100, blank=True)
    
    # Controle
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    valor_servico = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=97.00,
        help_text="Valor cobrado pelo serviço de abertura MEI"
    )
    venda_criada = models.BooleanField(
        default=False,
        help_text="Indica se a venda foi criada automaticamente no painel financeiro"
    )
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"MEI - {self.nome_completo} ({self.cpf})"
    
    def get_cnaes_secundarios_list(self):
        if self.cnaes_secundarios:
            return [cnae.strip() for cnae in self.cnaes_secundarios.split(',')]
        return []
    
    class Meta:
        verbose_name = 'Solicitação de Abertura MEI'
        verbose_name_plural = 'Solicitações de Abertura MEI'
        ordering = ['-criado_em']


class SolicitacaoBaixaMEI(models.Model):
    """
    Modelo para solicitações de baixa do MEI.
    
    Armazena todas as informações necessárias para processar
    a solicitação de baixa de um Microempreendedor Individual.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Em Processamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
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
    
    # Dados do MEI
    cnpj_mei = models.CharField(
        max_length=18,
        verbose_name='CNPJ do MEI',
        help_text='Formato: 00.000.000/0001-00'
    )
    nome_fantasia = models.CharField(
        max_length=200,
        verbose_name='Nome Fantasia',
        help_text='Razão social ou nome fantasia do MEI'
    )
    
    # Dados do Titular
    nome_completo = models.CharField(
        max_length=200,
        verbose_name='Nome Completo do Titular'
    )
    cpf = models.CharField(
        max_length=14,
        verbose_name='CPF do Titular',
        help_text='Formato: 000.000.000-00'
    )
    rg = models.CharField(
        max_length=15,
        verbose_name='RG'
    )
    orgao_emissor = models.CharField(
        max_length=10,
        verbose_name='Órgão Emissor',
        help_text='Ex: SSP, DETRAN, PC'
    )
    data_nascimento = models.DateField(
        verbose_name='Data de Nascimento'
    )
    nome_mae = models.CharField(
        max_length=200,
        verbose_name='Nome Completo da Mãe'
    )
    
    # Contato
    email = models.EmailField(
        verbose_name='E-mail'
    )
    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        help_text='Formato: (00) 00000-0000'
    )
    
    # Endereço Comercial
    cep = models.CharField(
        max_length=9,
        verbose_name='CEP',
        help_text='Formato: 00000-000'
    )
    rua = models.CharField(
        max_length=200,
        verbose_name='Rua/Logradouro'
    )
    numero = models.CharField(
        max_length=10,
        verbose_name='Número'
    )
    complemento = models.CharField(
        max_length=100,
        verbose_name='Complemento',
        blank=True,
        help_text='Apartamento, sala, bloco, etc. (opcional)'
    )
    bairro = models.CharField(
        max_length=100,
        verbose_name='Bairro'
    )
    cidade = models.CharField(
        max_length=100,
        verbose_name='Cidade'
    )
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        verbose_name='Estado'
    )
    
    # Controle
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuário Solicitante'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Informações adicionais sobre a solicitação'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Solicitação'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Solicitação de Baixa MEI'
        verbose_name_plural = 'Solicitações de Baixa MEI'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Baixa MEI - {self.nome_completo} ({self.cnpj_mei})"
    
    def get_status_display_class(self):
        """Retorna classe CSS baseada no status."""
        status_classes = {
            'pendente': 'status-pendente',
            'processando': 'status-processando',
            'concluido': 'status-concluido',
            'cancelado': 'status-cancelado',
        }
        return status_classes.get(self.status, 'status-pendente')


class SolicitacaoDeclaracaoMEI(models.Model):
    """
    Modelo para solicitações de Declaração Anual MEI (DASN-SIMEI).
    
    Armazena todas as informações necessárias para processar
    a declaração anual do Microempreendedor Individual.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Em Processamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
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
    
    # Dados de Contato (Passo 1)
    nome_completo = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    email = models.EmailField(
        verbose_name='E-mail'
    )
    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        help_text='Formato: (00) 00000-0000'
    )
    
    # Dados do MEI (Passo 2)
    cnpj = models.CharField(
        max_length=18,
        verbose_name='CNPJ do MEI',
        help_text='Formato: 00.000.000/0001-00'
    )
    cpf = models.CharField(
        max_length=14,
        verbose_name='CPF',
        help_text='Formato: 000.000.000-00'
    )
    
    # Endereço
    cep = models.CharField(
        max_length=9,
        verbose_name='CEP',
        help_text='Formato: 00000-000'
    )
    rua = models.CharField(
        max_length=200,
        verbose_name='Rua/Logradouro'
    )
    numero = models.CharField(
        max_length=10,
        verbose_name='Número'
    )
    complemento = models.CharField(
        max_length=100,
        verbose_name='Complemento',
        blank=True,
        help_text='Apartamento, sala, bloco, etc. (opcional)'
    )
    bairro = models.CharField(
        max_length=100,
        verbose_name='Bairro'
    )
    cidade = models.CharField(
        max_length=100,
        verbose_name='Cidade'
    )
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        verbose_name='Estado'
    )
    
    # Controle
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuário Solicitante'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    valor_servico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=67.00,
        help_text="Valor cobrado pelo serviço de declaração MEI"
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Informações adicionais sobre a solicitação'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Solicitação'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Solicitação de Declaração MEI'
        verbose_name_plural = 'Solicitações de Declaração MEI'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Declaração MEI - {self.nome_completo} ({self.cnpj})"
    
    def get_status_display_class(self):
        """Retorna classe CSS baseada no status."""
        status_classes = {
            'pendente': 'status-pendente',
            'processando': 'status-processando',
            'concluido': 'status-concluido',
            'cancelado': 'status-cancelado',
        }
        return status_classes.get(self.status, 'status-pendente')


class RegularizacaoMEI(models.Model):
    """
    Modelo para solicitações de regularização do MEI.
    
    Armazena todas as informações necessárias para processar
    a regularização de um Microempreendedor Individual.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Em Processamento'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ]
    
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
    
    # Dados de Contato (Passo 1)
    nome_completo = models.CharField(
        max_length=200,
        verbose_name='Nome Completo'
    )
    email = models.EmailField(
        verbose_name='E-mail'
    )
    telefone = models.CharField(
        max_length=15,
        verbose_name='Telefone',
        help_text='Formato: (00) 00000-0000'
    )
    
    # Dados do MEI (Passo 2)
    cpf = models.CharField(
        max_length=14,
        verbose_name='CPF',
        help_text='Formato: 000.000.000-00'
    )
    rg = models.CharField(
        max_length=15,
        verbose_name='RG'
    )
    cnpj = models.CharField(
        max_length=18,
        verbose_name='CNPJ do MEI',
        help_text='Formato: 00.000.000/0001-00'
    )
    
    # Endereço
    cep = models.CharField(
        max_length=9,
        verbose_name='CEP',
        help_text='Formato: 00000-000'
    )
    rua = models.CharField(
        max_length=200,
        verbose_name='Rua/Logradouro'
    )
    numero = models.CharField(
        max_length=10,
        verbose_name='Número'
    )
    complemento = models.CharField(
        max_length=100,
        verbose_name='Complemento',
        blank=True,
        help_text='Apartamento, sala, bloco, etc. (opcional)'
    )
    bairro = models.CharField(
        max_length=100,
        verbose_name='Bairro'
    )
    cidade = models.CharField(
        max_length=100,
        verbose_name='Cidade'
    )
    estado = models.CharField(
        max_length=2,
        choices=ESTADO_CHOICES,
        verbose_name='Estado'
    )
    
    # Controle
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuário Solicitante'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        verbose_name='Status'
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações',
        help_text='Informações adicionais sobre a regularização'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data da Solicitação'
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Regularização MEI'
        verbose_name_plural = 'Regularizações MEI'
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Regularização MEI - {self.nome_completo} ({self.cnpj})"
    
    def get_status_display_class(self):
        """Retorna classe CSS baseada no status."""
        status_classes = {
            'pendente': 'status-pendente',
            'processando': 'status-processando',
            'concluido': 'status-concluido',
            'cancelado': 'status-cancelado',
        }
        return status_classes.get(self.status, 'status-pendente')
