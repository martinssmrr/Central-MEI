import mercadopago
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

class MercadoPagoService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    
    def create_payment_preference(self, items, payer_email="", external_reference=""):
        """
        Cria uma preferência de pagamento no Mercado Pago
        
        Args:
            items: Lista de itens a serem cobrados
            payer_email: Email do pagador
            external_reference: Referência externa para identificar o pagamento
        """
        preference_data = {
            "items": items,
            "payer": {
                "email": payer_email
            },
            "back_urls": {
                "success": settings.MERCADOPAGO_SUCCESS_URL,
                "failure": settings.MERCADOPAGO_FAILURE_URL,
                "pending": settings.MERCADOPAGO_PENDING_URL
            },
            "auto_return": "approved",
            "external_reference": external_reference,
        }
        
        preference_response = self.sdk.preference().create(preference_data)
        return preference_response
    
    def get_payment(self, payment_id):
        """
        Consulta informações de um pagamento específico
        """
        payment_response = self.sdk.payment().get(payment_id)
        return payment_response


@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhookView(View):
    """
    Webhook para receber notificações do Mercado Pago
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Verificar se é uma notificação de pagamento
            if data.get('type') == 'payment':
                payment_id = data['data']['id']
                
                # Consultar detalhes do pagamento
                mp_service = MercadoPagoService()
                payment_info = mp_service.get_payment(payment_id)
                
                if payment_info["status"] == 200:
                    payment = payment_info["response"]
                    
                    # Processar o pagamento conforme o status
                    status = payment.get('status')
                    external_reference = payment.get('external_reference')
                    
                    # Aqui você pode atualizar o status do pedido no seu banco de dados
                    # com base no external_reference e status do pagamento
                    
                    if status == 'approved':
                        # Pagamento aprovado
                        pass
                    elif status == 'pending':
                        # Pagamento pendente
                        pass
                    elif status == 'rejected':
                        # Pagamento rejeitado
                        pass
            
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)


def create_service_payment(servico, user_email):
    """
    Cria um pagamento para um serviço específico
    """
    mp_service = MercadoPagoService()
    
    items = [{
        "title": servico.nome,
        "description": servico.descricao,
        "quantity": 1,
        "currency_id": "BRL",
        "unit_price": float(servico.preco)
    }]
    
    preference = mp_service.create_payment_preference(
        items=items,
        payer_email=user_email,
        external_reference=f"servico_{servico.id}"
    )
    
    return preference