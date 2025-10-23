#!/usr/bin/env python
"""
Teste de integração com Mercado Pago
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'central_mei.settings')
django.setup()

import mercadopago
from django.conf import settings
from pagamentos.models import Pagamento
from servicos.models import SolicitacaoMEI
from django.contrib.auth.models import User
import uuid

def test_mercadopago_preference():
    """Testa a criação de uma preferência no Mercado Pago"""
    
    print("=== TESTE MERCADO PAGO ===")
    
    # Verificar credenciais
    print(f"Access Token: {settings.MERCADOPAGO_ACCESS_TOKEN[:20]}...")
    print(f"Public Key: {settings.MERCADOPAGO_PUBLIC_KEY[:20]}...")
    
    # Inicializar SDK
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    print("SDK inicializado com sucesso!")
    
    # Criar dados de teste
    preference_data = {
        "items": [
            {
                "title": "Central MEI - Abertura de MEI",
                "quantity": 1,
                "unit_price": 50.00,
            }
        ],
        "payer": {
            "name": "João Silva",
            "email": "joao.teste@example.com",
        },
        "back_urls": {
            "success": "http://localhost:8000/pagamentos/sucesso/",
            "failure": "http://localhost:8000/pagamentos/erro/",
            "pending": "http://localhost:8000/pagamentos/pendente/",
        },
        "external_reference": str(uuid.uuid4()),
    }
    
    print("\n=== DADOS DA PREFERÊNCIA ===")
    print(f"Items: {preference_data['items']}")
    print(f"Payer: {preference_data['payer']}")
    print(f"External Reference: {preference_data['external_reference']}")
    
    try:
        print("\n=== CRIANDO PREFERÊNCIA ===")
        response = sdk.preference().create(preference_data)
        
        print(f"Status: {response.get('status')}")
        print(f"Response keys: {list(response.keys())}")
        
        if response["status"] == 201:
            preference = response["response"]
            print("✅ Preferência criada com sucesso!")
            print(f"ID: {preference['id']}")
            print(f"Init Point: {preference.get('init_point', 'N/A')}")
            print(f"Sandbox Init Point: {preference.get('sandbox_init_point', 'N/A')}")
        else:
            print("❌ Erro na criação da preferência:")
            print(f"Message: {response.get('message', 'N/A')}")
            print(f"Cause: {response.get('cause', 'N/A')}")
            print(f"Full Response: {response}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mercadopago_preference()