from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
import mercadopago
import json
import uuid
from decimal import Decimal
from .models import Pagamento
from servicos.models import SolicitacaoMEI

class ProcessarPagamentoView(View):
    """
    View para processar pagamento após o cliente finalizar a solicitação
    """
    
    def get(self, request):
        return self.processar_pagamento(request)
    
    def post(self, request):
        return self.processar_pagamento(request)
    
    def processar_pagamento(self, request):
        try:
            # Recuperar dados da sessão, POST ou GET
            solicitacao_id = (request.POST.get('solicitacao_id') or 
                            request.GET.get('solicitacao_id'))
            tipo_servico = (request.POST.get('tipo_servico') or 
                          request.GET.get('tipo_servico'))
            
            print(f"DEBUG - Processando pagamento:")
            print(f"  solicitacao_id: {solicitacao_id}")
            print(f"  tipo_servico: {tipo_servico}")
            print(f"  Method: {request.method}")
            print(f"  GET: {dict(request.GET)}")
            print(f"  POST: {dict(request.POST)}")
            
            # Definir valores dos serviços
            precos_servicos = {
                'abrir_mei': Decimal('97.00'),
                'regularizar_mei': Decimal('87.00'),
                'declaracao_mei': Decimal('47.00'),
                'baixar_mei': Decimal('67.00'),
            }
            
            valor = precos_servicos.get(tipo_servico, Decimal('97.00'))
            
            # Obter dados do cliente
            if solicitacao_id:
                try:
                    solicitacao = SolicitacaoMEI.objects.get(id=solicitacao_id)
                    nome_cliente = solicitacao.nome_completo
                    email_cliente = solicitacao.email
                    telefone_cliente = solicitacao.telefone
                except SolicitacaoMEI.DoesNotExist:
                    # Fallback para dados da sessão ou POST
                    nome_cliente = request.POST.get('nome_completo', 'Cliente')
                    email_cliente = request.POST.get('email', 'cliente@exemplo.com')
                    telefone_cliente = request.POST.get('telefone', '11999999999')
            else:
                nome_cliente = (request.POST.get('nome_completo') or 
                              request.GET.get('nome_completo') or 'Cliente')
                email_cliente = (request.POST.get('email') or 
                               request.GET.get('email') or 'cliente@exemplo.com')
                telefone_cliente = (request.POST.get('telefone') or 
                                  request.GET.get('telefone') or '11999999999')
            
            # Criar referência externa única
            external_reference = f"CMEI-{uuid.uuid4().hex[:8].upper()}"
            
            # Criar pagamento
            pagamento = Pagamento.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                solicitacao_mei_id=solicitacao_id if solicitacao_id else None,
                tipo_servico=tipo_servico,
                valor=valor,
                nome_cliente=nome_cliente,
                email_cliente=email_cliente,
                telefone_cliente=telefone_cliente,
                mp_external_reference=external_reference,
                dados_extras={
                    'solicitacao_id': solicitacao_id,
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                    'ip': request.META.get('REMOTE_ADDR', ''),
                }
            )
            
            # Configurar Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            # Criar preferência de pagamento
            preference_data = {
                "items": [
                    {
                        "title": f"Central MEI - {dict(Pagamento.TIPO_SERVICO_CHOICES)[tipo_servico]}",
                        "quantity": 1,
                        "unit_price": float(valor),
                    }
                ],
                "payer": {
                    "name": nome_cliente,
                    "email": email_cliente,
                    "phone": {
                        "number": telefone_cliente
                    }
                },
                "back_urls": {
                    "success": settings.MERCADOPAGO_SUCCESS_URL,
                    "failure": settings.MERCADOPAGO_FAILURE_URL,
                    "pending": settings.MERCADOPAGO_PENDING_URL
                },
                "auto_return": "approved",
                "external_reference": external_reference,
                "notification_url": request.build_absolute_uri('/pagamentos/webhook/'),
                "statement_descriptor": "CENTRAL MEI",
            }
            
            preference_response = sdk.preference().create(preference_data)
            
            print(f"DEBUG - Preference response status: {preference_response['status']}")
            
            if preference_response["status"] == 201:
                # Salvar ID da preferência
                pagamento.mp_preference_id = preference_response["response"]["id"]
                pagamento.save()
                
                print(f"DEBUG - Pagamento criado com sucesso: {pagamento.id}")
                print(f"DEBUG - Preference ID: {pagamento.mp_preference_id}")
                
                # Redirecionar para checkout
                return redirect('pagamentos:checkout', pagamento_id=pagamento.id)
            else:
                print(f"DEBUG - Erro na preferência: {preference_response}")
                messages.error(request, f'Erro ao criar preferência de pagamento: {preference_response}')
                return redirect('core:home')
                
        except Exception as e:
            print(f"DEBUG - Erro completo ao processar pagamento:")
            print(f"  Erro: {e}")
            print(f"  Tipo: {type(e)}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
            messages.error(request, f'Erro ao processar pagamento: {str(e)}')
            return redirect('core:home')

def checkout_view(request, pagamento_id):
    """
    View para exibir o checkout transparente
    """
    try:
        pagamento = get_object_or_404(Pagamento, id=pagamento_id)
        
        context = {
            'pagamento': pagamento,
            'mercadopago_public_key': settings.MERCADOPAGO_PUBLIC_KEY,
            'preference_id': pagamento.mp_preference_id,
        }
        
        return render(request, 'pagamentos/checkout.html', context)
        
    except Exception as e:
        messages.error(request, f'Erro ao carregar checkout: {str(e)}')
        return redirect('core:home')

def pagamento_sucesso(request):
    """
    Página de sucesso do pagamento
    """
    collection_id = request.GET.get('collection_id')
    external_reference = request.GET.get('external_reference')
    
    context = {
        'collection_id': collection_id,
        'external_reference': external_reference,
    }
    
    return render(request, 'pagamentos/sucesso.html', context)

def pagamento_erro(request):
    """
    Página de erro do pagamento
    """
    return render(request, 'pagamentos/erro.html')

def pagamento_pendente(request):
    """
    Página de pagamento pendente
    """
    return render(request, 'pagamentos/pendente.html')

@csrf_exempt
@require_POST  
def processar_pagamento_cartao(request):
    """
    Processa pagamento com cartão de crédito
    """
    try:
        data = json.loads(request.body)
        token = data.get('token')
        pagamento_id = data.get('pagamento_id')
        
        # Buscar pagamento
        pagamento = get_object_or_404(Pagamento, id=pagamento_id)
        
        # Configurar SDK
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        # Criar dados do pagamento
        payment_data = {
            "transaction_amount": float(pagamento.valor),
            "token": token,
            "description": f"Central MEI - {pagamento.get_tipo_servico_display()}",
            "installments": 1,
            "payment_method_id": data.get('payment_method_id', 'visa'),
            "issuer_id": data.get('issuer_id'),
            "payer": {
                "email": data.get('cardholderEmail', pagamento.email_cliente),
                "identification": {
                    "type": data.get('identificationType', 'CPF'),
                    "number": data.get('identificationNumber')
                }
            },
            "external_reference": pagamento.mp_external_reference,
            "notification_url": request.build_absolute_uri('/pagamentos/webhook/'),
        }
        
        # Processar pagamento
        payment_response = sdk.payment().create(payment_data)
        
        if payment_response["status"] == 201:
            payment_result = payment_response["response"]
            
            # Atualizar pagamento
            pagamento.mp_payment_id = str(payment_result['id'])
            pagamento.status = payment_result.get('status', 'pending')
            pagamento.save()
            
            # Se aprovado, atualizar solicitação
            if pagamento.status == 'approved' and pagamento.solicitacao_mei:
                pagamento.solicitacao_mei.status = 'processando'
                pagamento.solicitacao_mei.save()
            
            return JsonResponse({
                'status': payment_result.get('status'),
                'payment_id': payment_result.get('id'),
                'external_reference': pagamento.mp_external_reference
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Erro ao processar pagamento'
            }, status=400)
            
    except Exception as e:
        print(f"Erro ao processar pagamento: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
@require_POST
def webhook_mercadopago(request):
    """
    Webhook for Mercado Pago notifications
    """
    try:
        data = json.loads(request.body)
        
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if payment_id:
                # Configurar SDK
                sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                
                # Obter informações do pagamento
                payment_info = sdk.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment_data = payment_info["response"]
                    external_reference = payment_data.get("external_reference")
                    
                    if external_reference:
                        try:
                            pagamento = Pagamento.objects.get(mp_external_reference=external_reference)
                            pagamento.mp_payment_id = str(payment_id)
                            pagamento.status = payment_data.get("status", "pending")
                            pagamento.save()
                            
                            # Se aprovado, atualizar solicitação
                            if pagamento.status == 'approved' and pagamento.solicitacao_mei:
                                pagamento.solicitacao_mei.status = 'processando'
                                pagamento.solicitacao_mei.save()
                                
                        except Pagamento.DoesNotExist:
                            pass
        
        return HttpResponse(status=200)
        
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return HttpResponse(status=500)
