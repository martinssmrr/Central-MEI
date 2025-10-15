from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

class CategoriaPlanoContas(models.Model):
    """Categoria principal do plano de contas (Entrada/Saída)"""
    TIPOS_CATEGORIA = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPOS_CATEGORIA)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoria do Plano de Contas"
        verbose_name_plural = "Categorias do Plano de Contas"
        ordering = ['tipo', 'nome']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"

class SubcategoriaPlanoContas(models.Model):
    """Subcategoria do plano de contas"""
    categoria = models.ForeignKey(CategoriaPlanoContas, on_delete=models.CASCADE, related_name='subcategorias')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Subcategoria do Plano de Contas"
        verbose_name_plural = "Subcategorias do Plano de Contas"
        ordering = ['categoria', 'nome']
    
    def __str__(self):
        return f"{self.categoria.nome} - {self.nome}"

class Produto(models.Model):
    """Produtos/Serviços oferecidos"""
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    ativo = models.BooleanField(default=True)
    categoria = models.ForeignKey(SubcategoriaPlanoContas, on_delete=models.CASCADE, related_name='produtos')
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Produto/Serviço"
        verbose_name_plural = "Produtos/Serviços"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.preco}"

class Venda(models.Model):
    """Registro de vendas realizadas"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('cancelado', 'Cancelado'),
    ]
    
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('transferencia', 'Transferência Bancária'),
        ('boleto', 'Boleto'),
    ]
    
    cliente_nome = models.CharField(max_length=200)
    cliente_email = models.EmailField(blank=True)
    cliente_telefone = models.CharField(max_length=20, blank=True)
    cliente_cpf_cnpj = models.CharField(max_length=18, blank=True)
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='vendas')
    quantidade = models.PositiveIntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_final = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True)
    
    observacoes = models.TextField(blank=True)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendas_realizadas')
    
    data_venda = models.DateTimeField(auto_now_add=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-data_venda']
    
    def __str__(self):
        return f"Venda #{self.id} - {self.cliente_nome} - {self.produto.nome}"
    
    def save(self, *args, **kwargs):
        # Calcula valor total e final automaticamente
        self.valor_total = self.quantidade * self.valor_unitario
        self.valor_final = self.valor_total - self.desconto
        super().save(*args, **kwargs)

class MovimentacaoCaixa(models.Model):
    """Movimentações do caixa (entradas e saídas)"""
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(CategoriaPlanoContas, on_delete=models.CASCADE, related_name='movimentacoes', null=True, blank=True)
    subcategoria = models.ForeignKey(SubcategoriaPlanoContas, on_delete=models.CASCADE, related_name='movimentacoes', null=True, blank=True)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # Referência opcional à venda (para entradas automáticas)
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, null=True, blank=True, related_name='movimentacoes')
    
    data_movimentacao = models.DateTimeField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movimentacoes_criadas')
    observacoes = models.TextField(blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Movimentação de Caixa"
        verbose_name_plural = "Movimentações de Caixa"
        ordering = ['-data_movimentacao']
    
    def __str__(self):
        sinal = "+" if self.tipo == 'entrada' else "-"
        return f"{sinal} R$ {self.valor} - {self.descricao}"

class SaldoCaixa(models.Model):
    """Controle de saldo do caixa por data"""
    data = models.DateField(unique=True)
    saldo_inicial = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_entradas = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_saidas = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Saldo do Caixa"
        verbose_name_plural = "Saldos do Caixa"
        ordering = ['-data']
    
    def __str__(self):
        return f"Saldo {self.data} - R$ {self.saldo_final}"
    
    def calcular_saldo(self):
        """Recalcula o saldo baseado nas movimentações"""
        self.saldo_final = self.saldo_inicial + self.total_entradas - self.total_saidas
        return self.saldo_final
