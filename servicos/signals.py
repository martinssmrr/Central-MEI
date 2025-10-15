"""
Signals para automação entre Solicitações MEI e Painel Financeiro

Este módulo implementa a automação que cria automaticamente uma venda
no painel financeiro quando uma solicitação de abertura MEI é concluída.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import logging

from .models import SolicitacaoMEI
from dashboard.models import Venda, Produto, CategoriaPlanoContas, SubcategoriaPlanoContas

# Configurar logging para rastrear as operações
logger = logging.getLogger(__name__)

# Cache para evitar múltiplas criações de vendas
_solicitacao_previous_status = {}

@receiver(pre_save, sender=SolicitacaoMEI)
def store_previous_status(sender, instance, **kwargs):
    """
    Armazena o status anterior da solicitação antes de salvar.
    
    Usado para detectar mudanças de status e evitar criação 
    duplicada de vendas.
    """
    if instance.pk:
        try:
            previous = SolicitacaoMEI.objects.get(pk=instance.pk)
            _solicitacao_previous_status[instance.pk] = previous.status
        except SolicitacaoMEI.DoesNotExist:
            _solicitacao_previous_status[instance.pk] = None
    else:
        _solicitacao_previous_status[instance.pk] = None

@receiver(post_save, sender=SolicitacaoMEI)
def criar_venda_automatica(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma venda quando uma solicitação MEI é concluída.
    
    Args:
        sender: Model class (SolicitacaoMEI)
        instance: Instância da solicitação salva
        created: Boolean indicando se foi criação ou atualização
        **kwargs: Argumentos adicionais
        
    Comportamento:
        - Verifica se o status mudou de qualquer coisa para 'concluido'
        - Evita duplicação de vendas
        - Cria produto/serviço se não existir
        - Registra a venda com dados da solicitação
        - Cria movimentação de caixa automaticamente
    """
    # Obter status anterior
    previous_status = _solicitacao_previous_status.get(instance.pk)
    current_status = instance.status
    
    # Verificar se houve mudança para 'concluido'
    if current_status == 'concluido' and previous_status != 'concluido':
        
        logger.info(f"Processando conclusão da solicitação MEI #{instance.pk} - {instance.nome_completo}")
        
        try:
            # Verificar se já foi criada uma venda para esta solicitação
            if instance.venda_criada:
                logger.warning(f"Venda já foi criada para solicitação #{instance.pk}")
                return
            
            # Verificar dupla segurança por CPF e produto
            venda_existente = Venda.objects.filter(
                cliente_cpf_cnpj=instance.cpf,
                produto__nome__icontains='Abertura de MEI',
                observacoes__icontains=f'solicitação MEI #{instance.pk}'
            ).first()
            
            if venda_existente:
                logger.warning(f"Venda já existe para solicitação #{instance.pk} - Venda #{venda_existente.pk}")
                # Marcar como criada para evitar futuras tentativas
                SolicitacaoMEI.objects.filter(pk=instance.pk).update(venda_criada=True)
                return
            
            # Obter ou criar categoria e subcategoria para serviços MEI
            categoria_entrada, _ = CategoriaPlanoContas.objects.get_or_create(
                nome='Serviços MEI',
                tipo='entrada',
                defaults={'ativo': True}
            )
            
            subcategoria_mei, _ = SubcategoriaPlanoContas.objects.get_or_create(
                categoria=categoria_entrada,
                nome='Abertura de MEI',
                defaults={
                    'descricao': 'Serviços de abertura de MEI',
                    'ativo': True
                }
            )
            
            # Obter ou criar produto/serviço "Abertura de MEI"
            produto_mei, created_produto = Produto.objects.get_or_create(
                nome='Abertura de MEI',
                categoria=subcategoria_mei,
                defaults={
                    'descricao': 'Serviço completo de abertura de MEI',
                    'preco': instance.valor_servico,  # Usar valor da solicitação
                    'ativo': True
                }
            )
            
            if created_produto:
                logger.info(f"Produto 'Abertura de MEI' criado automaticamente")
            
            # Obter usuário para vincular à venda (usuário administrativo ou da solicitação)
            vendedor = instance.usuario
            if not vendedor:
                # Se não há usuário vinculado à solicitação, usar o primeiro superuser
                vendedor = User.objects.filter(is_superuser=True).first()
                if not vendedor:
                    # Se não há superuser, usar qualquer usuário staff
                    vendedor = User.objects.filter(is_staff=True).first()
            
            if not vendedor:
                logger.error("Nenhum usuário encontrado para vincular à venda")
                return
            
            # Criar a venda
            venda = Venda.objects.create(
                cliente_nome=instance.nome_completo,
                cliente_email=instance.email,
                cliente_telefone=instance.telefone,
                cliente_cpf_cnpj=instance.cpf,
                
                produto=produto_mei,
                quantidade=1,
                valor_unitario=instance.valor_servico,  # Usar valor da solicitação
                desconto=Decimal('0.00'),
                
                status='pago',  # Assumindo que o pagamento foi processado
                forma_pagamento='pix',  # Forma padrão, pode ser ajustada
                
                observacoes=f'Venda gerada automaticamente pela conclusão da solicitação MEI #{instance.pk} - {instance.nome_completo}',
                vendedor=vendedor,
                data_pagamento=timezone.now(),
            )
            
            # Marcar solicitação como tendo venda criada
            SolicitacaoMEI.objects.filter(pk=instance.pk).update(venda_criada=True)
            
            logger.info(f"Venda #{venda.pk} criada automaticamente para solicitação #{instance.pk}")
            
            # A movimentação de caixa será criada por outro signal do modelo Venda
            
        except Exception as e:
            logger.error(f"Erro ao criar venda automática para solicitação #{instance.pk}: {str(e)}")
            
        finally:
            # Limpar cache do status anterior
            if instance.pk in _solicitacao_previous_status:
                del _solicitacao_previous_status[instance.pk]
    
    else:
        # Limpar cache se não precisou processar
        if instance.pk in _solicitacao_previous_status:
            del _solicitacao_previous_status[instance.pk]


@receiver(post_save, sender=Venda)
def criar_movimentacao_caixa_venda(sender, instance, created, **kwargs):
    """
    Cria movimentação de caixa automaticamente quando uma venda é paga.
    
    Args:
        sender: Model class (Venda)
        instance: Instância da venda
        created: Boolean indicando se foi criação
        **kwargs: Argumentos adicionais
    """
    from dashboard.models import MovimentacaoCaixa
    
    # Verificar se a venda está paga e não tem movimentação
    if instance.status == 'pago' and instance.data_pagamento:
        
        # Verificar se já existe movimentação para esta venda
        movimentacao_existente = MovimentacaoCaixa.objects.filter(venda=instance).first()
        
        if not movimentacao_existente:
            try:
                # Criar movimentação de entrada
                MovimentacaoCaixa.objects.create(
                    tipo='entrada',
                    categoria=instance.produto.categoria.categoria,  # Categoria principal
                    subcategoria=instance.produto.categoria,  # Subcategoria
                    descricao=f'Venda #{instance.pk} - {instance.produto.nome}',
                    valor=instance.valor_final,
                    venda=instance,
                    data_movimentacao=instance.data_pagamento,
                    usuario=instance.vendedor,
                    observacoes=f'Movimentação automática - Venda para {instance.cliente_nome}'
                )
                
                logger.info(f"Movimentação de caixa criada para venda #{instance.pk}")
                
            except Exception as e:
                logger.error(f"Erro ao criar movimentação de caixa para venda #{instance.pk}: {str(e)}")