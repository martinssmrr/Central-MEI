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
    
    def get(self, request, *args, **kwargs):
        # Aceitar parâmetros via GET também
        return self._processar_pagamento(request)
    
    def post(self, request, *args, **kwargs):
        # Manter compatibilidade com POST
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
                messages.error(request, 'Solicitação não encontrada.')
                return redirect('core:home')
            
            try:
                solicitacao = SolicitacaoMEI.objects.get(id=solicitacao_id)
            except SolicitacaoMEI.DoesNotExist:
                messages.error(request, 'Solicitação não encontrada.')
                return redirect('core:home')
            
            # Verificar se já existe pagamento
            pagamento_existente = Pagamento.objects.filter(
                usuario=request.user,
                solicitacao_mei=solicitacao
            ).first()
            
            if pagamento_existente:
                return redirect('pagamentos:checkout', pagamento_id=pagamento_existente.id)
            
            # Gerar referência externa única
            external_reference = f"CMEI-{uuid.uuid4().hex[:12].upper()}"
            
            # Criar novo pagamento
            pagamento = Pagamento.objects.create(
                usuario=request.user,
                solicitacao_mei=solicitacao,
                tipo_servico=tipo_servico or 'abrir_mei',
                valor=Decimal('50.00'),
                status='pending',
                nome_cliente=request.user.get_full_name() or request.user.username,
                email_cliente=request.user.email,
                telefone_cliente=getattr(request.user, 'telefone', '11999999999'),
                mp_external_reference=external_reference
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
        
        # Criar preferência no Mercado Pago
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
            "external_reference": pagamento.mp_external_reference,
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
            error_info = response.get("response", {})
            error_msg = error_info.get("message", "Erro desconhecido ao criar preferência")
            messages.error(request, f"Erro no pagamento: {error_msg}")
            return redirect('core:home')
            
    except Exception as e:
        messages.error(request, f'Erro ao processar pagamento: {str(e)}')
        return redirect('core:home')


def processar_pagamento_cartao(request):
    """
    Processar pagamento com cartão
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"DEBUG: Dados recebidos: {data}")
            
            pagamento_id = data.get('pagamento_id')
            token = data.get('token')
            
            if not pagamento_id or not token:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Dados obrigatórios não fornecidos'
                })
            
            pagamento = get_object_or_404(Pagamento, id=pagamento_id)
            print(f"DEBUG: Pagamento encontrado: {pagamento.id}")
            
            # Configurar SDK
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            payment_data = {
                "transaction_amount": float(pagamento.valor),
                "token": token,
                "description": f"Central MEI - {pagamento.get_tipo_servico_display()}",
                "installments": 1,
                "payment_method_id": data.get('payment_method_id', 'visa'),
                "issuer_id": data.get('issuer_id', ''),
                "payer": {
                    "email": data.get('cardholderEmail', pagamento.email_cliente),
                    "identification": {
                        "type": data.get('identificationType', 'CPF'),
                        "number": data.get('identificationNumber', '00000000000')
                    }
                },
                "external_reference": pagamento.mp_external_reference
            }
            
            print(f"DEBUG: Dados do pagamento MP: {payment_data}")
            
            response = sdk.payment().create(payment_data)
            print(f"DEBUG: Resposta MP: {response}")
            
            if response["status"] in [200, 201]:
                payment = response["response"]
                pagamento.mp_payment_id = payment["id"] 
                pagamento.status = payment["status"]
                pagamento.save()
                
                print(f"DEBUG: Pagamento processado - Status: {payment['status']}")
                
                return JsonResponse({
                    'status': payment["status"],
                    'payment_id': payment["id"],
                    'status_detail': payment.get("status_detail"),
                    'redirect_url': reverse('pagamentos:sucesso')
                })
            else:
                error_msg = response.get("message", "Erro desconhecido")
                print(f"DEBUG: Erro no pagamento: {error_msg}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao processar pagamento: {error_msg}'
                })
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"DEBUG: Exception ao processar cartão: {error_details}")
            return JsonResponse({
                'status': 'error',
                'message': f'Erro interno: {str(e)}'
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