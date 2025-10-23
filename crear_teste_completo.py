#!/usr/bin/env python
"""
Teste completo do fluxo de pagamento
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'central_mei.settings')
django.setup()

from django.contrib.auth.models import User
from servicos.models import SolicitacaoMEI
from pagamentos.models import Pagamento
import uuid

def criar_pagamento_teste():
    """Cria um pagamento de teste completo"""
    
    print("=== CRIANDO PAGAMENTO TESTE ===")
    
    # Criar ou buscar usuário
    user, created = User.objects.get_or_create(
        username='teste@example.com',
        defaults={
            'email': 'teste@example.com',
            'first_name': 'João',
            'last_name': 'Teste'
        }
    )
    
    if created:
        user.set_password('123456')
        user.save()
        print(f"✅ Usuário criado: {user.username}")
    else:
        print(f"✅ Usuário encontrado: {user.username}")
    
    # Criar solicitação MEI
    solicitacao = SolicitacaoMEI.objects.create(
        usuario=user,
        nome_completo="João da Silva Teste",
        cpf="98765432100",
        rg="123456789",
        orgao_expedidor="SSP",
        estado_expedidor="SP",
        email="teste@example.com",
        telefone="11999999999",
        cnae_primario="6201-5/00",
        forma_atuacao="fixo",
        capital_inicial=1000.00,
        cep="01001000",
        cidade="São Paulo",
        estado="SP",
        rua="Praça da Sé",
        numero="123",
        bairro="Sé",
        complemento="Apto 1",
        status='pendente'
    )
    
    print(f"✅ Solicitação MEI criada: {solicitacao.id}")
    
    # Criar pagamento
    pagamento = Pagamento.objects.create(
        solicitacao_mei=solicitacao,
        tipo_servico='abrir_mei',
        valor=50.00,
        nome_cliente=solicitacao.nome_completo,
        email_cliente=solicitacao.email,
        status='pendente'
    )
    
    print(f"✅ Pagamento criado: {pagamento.id}")
    print(f"🔗 URL de checkout: http://127.0.0.1:8000/pagamentos/checkout/{pagamento.id}/")
    
    return pagamento

if __name__ == "__main__":
    pagamento = criar_pagamento_teste()