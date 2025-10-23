from django.db import models
from django.contrib.auth.models import User
from servicos.models import SolicitacaoMEI
import uuid

class Pagamento(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
        ('cancelled', 'Cancelado'),
        ('in_process', 'Em Processamento'),
    ]
    
    TIPO_SERVICO_CHOICES = [
        ('abrir_mei', 'Abrir MEI'),
        ('regularizar_mei', 'Regularizar MEI'),
        ('declaracao_mei', 'Declaração Anual MEI'),
        ('baixar_mei', 'Baixar MEI'),
    ]
    
    # Identificação única
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relacionamentos
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    solicitacao_mei = models.ForeignKey(SolicitacaoMEI, on_delete=models.CASCADE, null=True, blank=True)
    
    # Dados do pagamento
    tipo_servico = models.CharField(max_length=50, choices=TIPO_SERVICO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dados do cliente
    nome_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefone_cliente = models.CharField(max_length=20)
    
    # Mercado Pago
    mp_payment_id = models.CharField(max_length=50, null=True, blank=True)
    mp_preference_id = models.CharField(max_length=100, null=True, blank=True)
    mp_external_reference = models.CharField(max_length=100, unique=True)
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Dados adicionais
    dados_extras = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
    
    def __str__(self):
        return f"Pagamento {self.mp_external_reference} - {self.nome_cliente}"
    
    @property
    def valor_formatado(self):
        return f"R$ {self.valor:.2f}".replace('.', ',')
    
    def get_status_display_color(self):
        cores = {
            'pending': 'warning',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary',
            'in_process': 'info',
        }
        return cores.get(self.status, 'secondary')
