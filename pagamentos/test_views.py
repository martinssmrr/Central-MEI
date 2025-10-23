from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import mercadopago

def test_mercadopago(request):
    """
    View para testar conexão com Mercado Pago
    """
    context = {}
    
    try:
        # Verificar se as chaves estão configuradas
        access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
        public_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', None)
        
        context['access_token_set'] = bool(access_token)
        context['public_key_set'] = bool(public_key)
        context['access_token_preview'] = access_token[:20] + '...' if access_token else 'NÃO CONFIGURADO'
        context['public_key_preview'] = public_key[:20] + '...' if public_key else 'NÃO CONFIGURADO'
        
        if not access_token:
            context['error'] = 'Access Token não configurado'
            return render(request, 'pagamentos/test_mp.html', context)
        
        # Testar conexão
        sdk = mercadopago.SDK(access_token)
        
        # Testar criação de preferência simples
        preference_data = {
            "items": [
                {
                    "title": "Teste de Integração",
                    "quantity": 1,
                    "unit_price": 1.0,
                }
            ]
        }
        
        response = sdk.preference().create(preference_data)
        
        context['mp_response_status'] = response.get('status')
        context['success'] = response.get('status') == 201
        
        if response.get('status') == 201:
            preference = response.get('response', {})
            context['preference_id'] = preference.get('id')
            context['init_point'] = preference.get('init_point')
            context['message'] = 'Integração com Mercado Pago funcionando corretamente!'
        else:
            context['error'] = f"Erro na resposta do MP: {response.get('message', 'Erro desconhecido')}"
        
    except Exception as e:
        context['error'] = f"Erro ao testar Mercado Pago: {str(e)}"
    
    return render(request, 'pagamentos/test_mp.html', context)