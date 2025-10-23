from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from decimal import Decimal
import mercadopago
import json
import uuid
import traceback

from servicos.models import SolicitacaoMEI
from .models import Pagamento


class ProcessarPagamentoView(LoginRequiredMixin, View):
    """
    View simplificada para processar pagamentos
    """
    
    def post(self, request, *args, **kwargs):
        try:
            solicitacao_id = request.POST.get('solicitacao_id')
            if not solicitacao_id:
                messages.error(request, 'Solicitação não encontrada.')
                return redirect('core:home')
            
            solicitacao = get_object_or_404(SolicitacaoMEI, id=solicitacao_id)
            
            # Verificar se já existe pagamento
            pagamento_existente = Pagamento.objects.filter(
                usuario=request.user,
                solicitacao_mei=solicitacao
            ).first()
            
            if pagamento_existente:
                return redirect('pagamentos:checkout', pagamento_id=pagamento_existente.id)
            
            # Criar novo pagamento
            pagamento = Pagamento.objects.create(
                usuario=request.user,
                solicitacao_mei=solicitacao,
                tipo_servico=solicitacao.tipo_mei,
                valor=Decimal('50.00'),
                status='pendente',
                nome_cliente=request.user.get_full_name() or request.user.username,
                email_cliente=request.user.email,
                telefone_cliente=getattr(request.user, 'telefone', '11999999999')
            )
            
            return redirect('pagamentos:checkout', pagamento_id=pagamento.id)
            
        except Exception as e:
            print(f"Erro ao processar pagamento: {e}")
            messages.error(request, 'Erro ao processar pagamento. Tente novamente.')
            return redirect('core:home')


def checkout_view(request, pagamento_id):
    """
    View para exibir a página de checkout
    """
    try:
        pagamento = get_object_or_404(Pagamento, id=pagamento_id)
        
        # Se já tem preferência, usar ela
        if pagamento.mp_preference_id:
            return render(request, 'pagamentos/checkout.html', {
                'pagamento': pagamento,
                'mercadopago_public_key': settings.MERCADOPAGO_PUBLIC_KEY,
                'preference_id': pagamento.mp_preference_id
            })
        
        # Criar preferência
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        preference_data = {
            "items": [
                {
                    "title": f"Central MEI - {pagamento.get_tipo_servico_display()}",
                    "quantity": 1,
                    "unit_price": float(pagamento.valor),
                }
            ],
            "payer": {
                "name": pagamento.nome_cliente,
                "email": pagamento.email_cliente,
            },
            "back_urls": {
                "success": request.build_absolute_uri(reverse('pagamentos:sucesso')),
                "failure": request.build_absolute_uri(reverse('pagamentos:erro')),
                "pending": request.build_absolute_uri(reverse('pagamentos:pendente')),
            },
            "auto_return": "approved",
            "external_reference": str(pagamento.id),
        }
        
        response = sdk.preference().create(preference_data)
        
        if response["status"] == 201:
            preference = response["response"]
            pagamento.mp_preference_id = preference["id"]
            pagamento.save()
            
            return render(request, 'pagamentos/checkout.html', {
                'pagamento': pagamento,
                'mercadopago_public_key': settings.MERCADOPAGO_PUBLIC_KEY,
                'preference_id': preference["id"]
            })
        else:
            messages.error(request, 'Erro ao criar preferência de pagamento.')
            return redirect('core:home')
            
    except Exception as e:
        print(f"Erro no checkout: {e}")
        messages.error(request, 'Erro ao carregar checkout.')
        return redirect('core:home')


def processar_pagamento_cartao(request):
    """
    Processar pagamento com cartão
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            pagamento_id = data.get('pagamento_id')
            token = data.get('token')
            
            pagamento = get_object_or_404(Pagamento, id=pagamento_id)
            
            # Configurar SDK
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            payment_data = {
                "transaction_amount": float(pagamento.valor),
                "token": token,
                "description": f"Central MEI - {pagamento.get_tipo_servico_display()}",
                "installments": 1,
                "payment_method_id": data.get('payment_method_id'),
                "issuer_id": data.get('issuer_id', ''),
                "payer": {
                    "email": pagamento.email_cliente,
                    "identification": {
                        "type": data.get('doc_type', 'CPF'),
                        "number": data.get('doc_number', '00000000000')
                    }
                },
                "external_reference": str(pagamento.id)
            }
            
            response = sdk.payment().create(payment_data)
            
            if response["status"] in [200, 201]:
                payment = response["response"]
                pagamento.mp_payment_id = payment["id"] 
                pagamento.status = payment["status"]
                pagamento.save()
                
                return JsonResponse({
                    'status': 'success',
                    'payment_id': payment["id"],
                    'status_detail': payment.get("status_detail"),
                    'redirect_url': reverse('pagamentos:sucesso')
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erro ao processar pagamento'
                })
                
        except Exception as e:
            print(f"Erro ao processar cartão: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Erro interno'
            })
    
    return JsonResponse({'status': 'invalid_method'})


# Views das páginas de status
def pagamento_sucesso(request):
    return render(request, 'pagamentos/sucesso.html')

def pagamento_erro(request):
    return render(request, 'pagamentos/erro.html')

def pagamento_pendente(request):
    return render(request, 'pagamentos/pendente.html')


@csrf_exempt
def webhook_mercadopago(request):
    """
    Webhook para receber notificações do Mercado Pago
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if data.get('type') == 'payment':
                payment_id = data['data']['id']
                
                # Buscar informações do pagamento
                sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                response = sdk.payment().get(payment_id)
                
                if response["status"] == 200:
                    payment_data = response["response"]
                    external_reference = payment_data.get("external_reference")
                    
                    if external_reference:
                        try:
                            pagamento = Pagamento.objects.get(id=external_reference)
                            pagamento.status = payment_data["status"]
                            pagamento.mp_payment_id = payment_id
                            pagamento.save()
                        except Pagamento.DoesNotExist:
                            pass
            
            return HttpResponse(status=200)
            
        except Exception as e:
            print(f"Erro no webhook: {e}")
            return HttpResponse(status=400)
    
    return HttpResponse(status=405)