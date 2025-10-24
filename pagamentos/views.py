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


@method_decorator(csrf_exempt, name='dispatch')
class ProcessarPagamentoView(View):
    """
    View simplificada para processar pagamentos
    """
    
    def get(self, request, *args, **kwargs):
        # Aceitar parâmetros via GET também
        return self._processar_pagamento(request)
    
    def post(self, request, *args, **kwargs):
        # Se for requisição JSON (Payment Brick), processar via API
        if request.content_type == 'application/json':
            return self._processar_pagamento_brick(request)
        # Senão, manter compatibilidade com POST tradicional
        return self._processar_pagamento(request)
    
    def _processar_pagamento_brick(self, request):
        """Processar pagamento via Payment Brick do Mercado Pago"""
        try:
            import json
            from django.http import JsonResponse
            
            # Parse dos dados JSON
            data = json.loads(request.body)
            
            # Obter o pagamento_id dos dados
            pagamento_id = data.get('pagamento_id')
            if not pagamento_id:
                return JsonResponse({'error': 'pagamento_id é obrigatório'}, status=400)
            
            # Buscar o pagamento
            try:
                pagamento = Pagamento.objects.get(id=pagamento_id)
            except Pagamento.DoesNotExist:
                return JsonResponse({'error': 'Pagamento não encontrado'}, status=404)
            
            # Criar pagamento no Mercado Pago
            import mercadopago
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            payment_data = {
                "transaction_amount": float(pagamento.valor),
                "token": data.get('token'),
                "description": f"Central MEI - {pagamento.get_tipo_servico_display()}",
                "installments": data.get('installments', 1),
                "payment_method_id": data.get('payment_method_id'),
                "issuer_id": data.get('issuer_id'),
                "payer": {
                    "email": data.get('payer', {}).get('email', pagamento.email_cliente),
                    "identification": {
                        "type": data.get('payer', {}).get('identification', {}).get('type'),
                        "number": data.get('payer', {}).get('identification', {}).get('number')
                    }
                },
                "external_reference": pagamento.mp_external_reference
            }
            
            # Criar o pagamento
            payment_response = sdk.payment().create(payment_data)
            
            if payment_response["status"] == 201:
                payment = payment_response["response"]
                
                # Atualizar o pagamento no banco
                pagamento.mp_payment_id = payment["id"]
                pagamento.status = payment["status"]
                pagamento.save()
                
                return JsonResponse({
                    'status': payment["status"],
                    'payment_id': payment["id"],
                    'external_reference': payment["external_reference"]
                })
            else:
                return JsonResponse({'error': 'Erro ao processar pagamento'}, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados JSON inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
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
    # Limpar dados da sessão após sucesso no pagamento
    session_keys_to_clear = [
        'servico_dados_completos',
        'dados_passo1',
        'dados_passo2',
        'regularizar_mei_step1_data',
        'declaracao_mei_dados',
        'baixar_mei_dados'
    ]
    
    for key in session_keys_to_clear:
        if key in request.session:
            del request.session[key]
    
    return render(request, 'pagamentos/sucesso.html')

def pagamento_erro(request):
    return render(request, 'pagamentos/erro.html')

def pagamento_pendente(request):
    return render(request, 'pagamentos/pendente.html')


@csrf_exempt
def webhook_mercadopago(request):
    """
    Webhook para receber notificações do Mercado Pago com validação de segurança
    """
    if request.method == 'POST':
        try:
            import hashlib
            import hmac
            
            # Validar assinatura do webhook para segurança
            webhook_secret = settings.MERCADOPAGO_WEBHOOK_SECRET
            if webhook_secret:
                # Obter headers necessários para validação
                x_signature = request.headers.get('x-signature', '')
                x_request_id = request.headers.get('x-request-id', '')
                
                if x_signature and x_request_id:
                    # Extrair timestamp e hash da assinatura
                    signature_parts = {}
                    for part in x_signature.split(','):
                        if '=' in part:
                            key, value = part.strip().split('=', 1)
                            signature_parts[key] = value
                    
                    ts = signature_parts.get('ts', '')
                    v1 = signature_parts.get('v1', '')
                    
                    if ts and v1:
                        # Criar payload para validação
                        payload = f"id:{request.body.decode('utf-8')};request-id:{x_request_id};ts:{ts};"
                        
                        # Calcular hash esperado
                        expected_hash = hmac.new(
                            webhook_secret.encode('utf-8'),
                            payload.encode('utf-8'),
                            hashlib.sha256
                        ).hexdigest()
                        
                        # Validar assinatura
                        if not hmac.compare_digest(v1, expected_hash):
                            print("Webhook rejeitado: assinatura inválida")
                            return HttpResponse(status=401)
            
            # Processar dados do webhook
            data = json.loads(request.body)
            print(f"Webhook recebido: {data}")
            
            # Processar diferentes tipos de notificação
            if data.get('type') == 'payment' and data.get('action') in ['payment.created', 'payment.updated']:
                payment_id = data['data']['id']
                
                # Buscar informações detalhadas do pagamento
                sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                response = sdk.payment().get(payment_id)
                
                if response["status"] == 200:
                    payment_data = response["response"]
                    external_reference = payment_data.get("external_reference")
                    payment_status = payment_data.get("status")
                    payment_method = payment_data.get("payment_method_id")
                    transaction_amount = payment_data.get("transaction_amount")
                    
                    print(f"Pagamento {payment_id}: status={payment_status}, external_ref={external_reference}")
                    
                    if external_reference:
                        try:
                            # Buscar pagamento pelo external_reference
                            pagamento = Pagamento.objects.get(mp_external_reference=external_reference)
                            
                            # Mapear status do Mercado Pago para nossos status
                            status_mapping = {
                                'approved': 'aprovado',
                                'pending': 'pendente', 
                                'in_process': 'processando',
                                'rejected': 'rejeitado',
                                'cancelled': 'cancelado',
                                'refunded': 'estornado',
                                'charged_back': 'contestado'
                            }
                            
                            # Atualizar status do pagamento
                            pagamento.status = status_mapping.get(payment_status, payment_status)
                            pagamento.mp_payment_id = str(payment_id)
                            
                            # Adicionar informações extras se disponível
                            if payment_method:
                                pagamento.forma_pagamento = payment_method
                            
                            pagamento.save()
                            
                            # Se aprovado, criar solicitação específica do serviço
                            if payment_status == 'approved':
                                try:
                                    _criar_solicitacao_servico_aprovado(pagamento, payment_id, transaction_amount)
                                except Exception as e:
                                    print(f"Erro ao criar solicitação de serviço: {e}")
                            
                            print(f"Pagamento {external_reference} atualizado para status: {pagamento.status}")
                            
                        except Pagamento.DoesNotExist:
                            print(f"Pagamento com external_reference {external_reference} não encontrado")
                        except Exception as e:
                            print(f"Erro ao processar pagamento {external_reference}: {e}")
                            return HttpResponse(status=500)
                else:
                    print(f"Erro ao buscar pagamento {payment_id}: {response}")
                    return HttpResponse(status=400)
            
            return HttpResponse(status=200)
            
        except json.JSONDecodeError:
            print("Webhook rejeitado: JSON inválido")
            return HttpResponse(status=400)
        except Exception as e:
            print(f"Erro no webhook: {e}")
            print(traceback.format_exc())
            return HttpResponse(status=500)
    
    return HttpResponse(status=405)


def _criar_solicitacao_servico_aprovado(pagamento, payment_id, transaction_amount):
    """
    Função auxiliar para criar solicitações específicas de serviço após pagamento aprovado.
    Como o webhook não tem acesso à sessão do usuário, tentamos identificar o tipo de serviço
    pelo valor do pagamento e dados disponíveis.
    """
    from servicos.models import (
        Servico, SolicitacaoServico, SolicitacaoMEI, 
        RegularizacaoMEI, SolicitacaoDeclaracaoMEI, SolicitacaoBaixaMEI
    )
    from decimal import Decimal
    
    try:
        # Buscar o serviço pelo preço
        servico = Servico.objects.filter(
            preco=Decimal(str(transaction_amount)),
            ativo=True
        ).first()
        
        if not servico:
            print(f"Nenhum serviço encontrado com preço R$ {transaction_amount}")
            return
        
        # Verificar se já existe uma solicitação para este pagamento
        existing_solicitacao = SolicitacaoServico.objects.filter(
            usuario=pagamento.usuario,
            servico=servico,
            observacoes__contains=f'Pagamento {payment_id}'
        ).first()
        
        if existing_solicitacao:
            print(f"Solicitação já existe para pagamento {payment_id}")
            return
            
        # Criar solicitação genérica de serviço
        solicitacao = SolicitacaoServico.objects.create(
            usuario=pagamento.usuario,
            servico=servico,
            status='em_andamento',
            observacoes=f'Pagamento aprovado via Mercado Pago. ID: {payment_id}. '
                       f'Dados do cliente: {pagamento.nome_cliente} - {pagamento.email_cliente}'
        )
        
        print(f"Solicitação de serviço #{solicitacao.id} criada para pagamento {payment_id}")
        
        # Nota: Para implementação completa, seria ideal armazenar os dados
        # do formulário em um modelo temporário vinculado ao pagamento,
        # em vez de depender apenas da sessão do usuário.
        
    except Exception as e:
        print(f"Erro detalhado ao criar solicitação: {e}")
        import traceback
        print(traceback.format_exc())


class CheckoutServicoView(View):
    """
    View para checkout de serviços dinâmicos - requer dados na sessão
    """
    
    def get(self, request, servico_slug):
        try:
            from servicos.models import Servico
            
            # Verificar se os dados completos do serviço estão na sessão
            dados_servico = request.session.get('servico_dados_completos')
            if not dados_servico or dados_servico.get('servico_slug') != servico_slug:
                messages.warning(request, 'Para continuar com o pagamento, você precisa primeiro preencher os dados do serviço.')
                return redirect(f'/servicos/{servico_slug}/passo1/')
            
            # Busca o serviço pelo slug
            servico = get_object_or_404(Servico, slug=servico_slug, ativo=True)
            
            # Verificar se já existe um pagamento pendente para este usuário e serviço
            pagamento_existente = None
            if request.user.is_authenticated:
                pagamento_existente = Pagamento.objects.filter(
                    usuario=request.user,
                    valor=servico.preco,
                    status='pendente'
                ).first()
            
            if pagamento_existente and pagamento_existente.mp_preference_id:
                return render(request, 'pagamentos/checkout.html', {
                    'servico': servico,
                    'pagamento': pagamento_existente,
                    'mercadopago_public_key': settings.MERCADOPAGO_PUBLIC_KEY,
                    'preference_id': pagamento_existente.mp_preference_id
                })
            
            # Usar dados da sessão para criar o pagamento
            nome_cliente = dados_servico.get('nome_completo', '')
            if not nome_cliente and request.user.is_authenticated:
                nome_cliente = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
            
            email_cliente = dados_servico.get('email', '')
            if not email_cliente and request.user.is_authenticated:
                email_cliente = request.user.email
            
            # Criar novo pagamento
            pagamento = Pagamento.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                valor=servico.preco,
                nome_cliente=nome_cliente,
                email_cliente=email_cliente,
                status='pendente',
                mp_external_reference=str(uuid.uuid4())
            )
            
            # Associar pagamento aos dados do serviço na sessão
            dados_servico['pagamento_id'] = str(pagamento.id)
            request.session['servico_dados_completos'] = dados_servico
            
            # Criar preferência no Mercado Pago
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            # Para desenvolvimento local, usar URLs fictícias que o MP aceite
            base_url = "https://centralmei.com.br"  # URL fictícia para desenvolvimento
            if settings.DEBUG:
                preference_data = {
                    "items": [
                        {
                            "title": f"Central MEI - {servico.nome}",
                            "description": servico.descricao[:250],  # Mercado Pago tem limite de caracteres
                            "quantity": 1,
                            "unit_price": float(servico.preco),
                        }
                    ],
                    "payer": {
                        "name": nome_cliente,
                        "email": email_cliente,
                    },
                    "external_reference": pagamento.mp_external_reference,
                }
            else:
                preference_data = {
                    "items": [
                        {
                            "title": f"Central MEI - {servico.nome}",
                            "description": servico.descricao[:250],  # Mercado Pago tem limite de caracteres
                            "quantity": 1,
                            "unit_price": float(servico.preco),
                        }
                    ],
                    "payer": {
                        "name": nome_cliente,
                        "email": email_cliente,
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
                    'servico': servico,
                    'pagamento': pagamento,
                    'mercadopago_public_key': settings.MERCADOPAGO_PUBLIC_KEY,
                    'preference_id': preference["id"]
                })
            else:
                error_info = response.get("response", {})
                error_msg = error_info.get("message", "Erro desconhecido ao criar preferência")
                messages.error(request, f"Erro ao processar pagamento: {error_msg}")
                return redirect('servicos:lista')
                
        except Exception as e:
            messages.error(request, "Erro interno do servidor. Tente novamente.")
            print(f"Erro no checkout: {str(e)}")
            print(traceback.format_exc())
            return redirect('servicos:lista')