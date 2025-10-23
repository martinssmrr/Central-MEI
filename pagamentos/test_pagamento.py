from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
import mercadopago
import traceback
import uuid

from servicos.models import SolicitacaoMEI
from pagamentos.models import Pagamento


class ProcessarPagamentoTestView(View):
    """
    View de teste para processar pagamentos (sem LoginRequired)
    """
    
    def get(self, request, *args, **kwargs):
        return self._processar_pagamento(request)
    
    def post(self, request, *args, **kwargs):
        return self._processar_pagamento(request)
    
    def _processar_pagamento(self, request):
        try:
            # Buscar solicitacao_id em GET ou POST
            solicitacao_id = (request.GET.get('solicitacao_id') or 
                            request.POST.get('solicitacao_id'))
            
            # Buscar tipo_servico em GET ou POST
            tipo_servico = (request.GET.get('tipo_servico') or 
                          request.POST.get('tipo_servico'))
            
            if not solicitacao_id:
                return JsonResponse({
                    'error': 'Solicitação não encontrada.',
                    'solicitacao_id': solicitacao_id,
                    'tipo_servico': tipo_servico
                })
            
            try:
                solicitacao = SolicitacaoMEI.objects.get(id=solicitacao_id)
            except SolicitacaoMEI.DoesNotExist:
                return JsonResponse({
                    'error': 'Solicitação não existe no banco de dados.',
                    'solicitacao_id': solicitacao_id
                })
            
            # Verificar se já existe pagamento
            pagamento_existente = Pagamento.objects.filter(
                solicitacao_mei=solicitacao
            ).first()
            
            if pagamento_existente:
                return JsonResponse({
                    'status': 'pagamento_existente',
                    'pagamento_id': str(pagamento_existente.id),
                    'checkout_url': reverse('pagamentos:checkout', kwargs={'pagamento_id': pagamento_existente.id})
                })
            
            # Gerar referência externa única
            external_reference = f"CMEI-TEST-{uuid.uuid4().hex[:12].upper()}"
            
            # Criar novo pagamento
            pagamento = Pagamento.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                solicitacao_mei=solicitacao,
                tipo_servico=tipo_servico or 'abrir_mei',
                valor=Decimal('50.00'),
                status='pending',
                nome_cliente=solicitacao.nome_completo,
                email_cliente=solicitacao.email,
                telefone_cliente=solicitacao.telefone,
                mp_external_reference=external_reference
            )
            
            return JsonResponse({
                'status': 'pagamento_criado',
                'pagamento_id': str(pagamento.id),
                'solicitacao': {
                    'id': solicitacao.id,
                    'nome': solicitacao.nome_completo,
                    'cpf': solicitacao.cpf,
                    'email': solicitacao.email
                },
                'checkout_url': reverse('pagamentos:checkout', kwargs={'pagamento_id': pagamento.id})
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'traceback': traceback.format_exc()
            })