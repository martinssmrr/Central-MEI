#!/usr/bin/env python
"""
Teste do checkout transparente via API
"""
import requests
import json
import urllib3

# Desabilitar warnings SSL para desenvolvimento
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_checkout_transparente():
    """Testa o checkout transparente via API"""
    
    print("=== TESTE CHECKOUT TRANSPARENTE ===")
    
    # ID do pagamento criado anteriormente
    pagamento_id = "988751bc-8686-443c-9475-840c5a004ac3"
    
    # URL base (HTTP para desenvolvimento)
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Testar acesso à página de checkout
        print("1. Testando acesso ao checkout...")
        checkout_url = f"{base_url}/pagamentos/checkout/{pagamento_id}/"
        
        response = requests.get(checkout_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Checkout acessível via HTTPS!")
            print(f"Tamanho da resposta: {len(response.content)} bytes")
            
            # Verificar se contém elementos do Mercado Pago
            if "MercadoPago" in response.text:
                print("✅ SDK do Mercado Pago encontrado na página!")
            else:
                print("⚠️ SDK do Mercado Pago não encontrado")
                
            if "mercadopago_public_key" in response.text:
                print("✅ Chave pública do MP encontrada!")
            else:
                print("⚠️ Chave pública do MP não encontrada")
            
        else:
            print(f"❌ Erro ao acessar checkout: {response.status_code}")
            return
            
        # 2. Simular dados de teste do cartão
        print("\n2. Simulando processamento de cartão...")
        
        # Dados de teste para cartão (dados fictícios para teste)
        card_data = {
            "token": "test_token_12345",  # Token fictício
            "pagamento_id": pagamento_id,
            "cardholderEmail": "teste@example.com",
            "cardholderName": "João Teste",
            "identificationType": "CPF",
            "identificationNumber": "12345678901"
        }
        
        # URL para processamento do cartão
        process_url = f"{base_url}/pagamentos/pagamento-cartao/"
        
        # Headers necessários
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TestScript/1.0'
        }
        
        # Primeiro, precisamos obter o CSRF token
        csrf_response = requests.get(checkout_url)
        if 'csrftoken' in csrf_response.cookies:
            csrf_token = csrf_response.cookies['csrftoken']
            headers['X-CSRFToken'] = csrf_token
            print(f"✅ CSRF Token obtido: {csrf_token[:10]}...")
        
        print(f"Enviando dados para: {process_url}")
        print(f"Dados: {json.dumps(card_data, indent=2)}")
        
        # response = requests.post(process_url, 
        #                         json=card_data, 
        #                         headers=headers,
        #                         verify=False, 
        #                         timeout=30)
        
        # print(f"Status da resposta: {response.status_code}")
        # print(f"Resposta: {response.text}")
        
        print("\n⚠️ Teste de pagamento comentado - use apenas para verificar se o checkout carrega")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
        print("Verifique se o servidor HTTPS está rodando")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_checkout_transparente()