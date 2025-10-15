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
