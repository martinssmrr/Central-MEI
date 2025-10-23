#!/usr/bin/env python
"""
Criar solicitação MEI de teste para testar o fluxo completo
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'central_mei.settings')
django.setup()

from servicos.models import SolicitacaoMEI
from django.contrib.auth.models import User
from django.utils import timezone

def criar_solicitacao_teste():
    """Cria uma solicitação MEI de teste"""
    
    # Obter ou criar usuário de teste
    user, created = User.objects.get_or_create(
        username='teste',
        defaults={
            'email': 'teste@example.com',
            'first_name': 'João',
            'last_name': 'Silva'
        }
    )
    
    # Criar solicitação
    solicitacao = SolicitacaoMEI.objects.create(
        usuario=user,
        nome_completo="João da Silva Teste",
        cpf="123.456.789-01",
        rg="12.345.678-9",
        orgao_expedidor="SSP",
        estado_expedidor="SP",
        telefone="(11) 99999-9999",
        email="joao.teste@example.com",
        cep="01234-567",
        rua="Rua Teste",
        numero="123",
        bairro="Centro",
        cidade="São Paulo",
        estado="SP",
        cnae_primario="6201-5/00",
        forma_atuacao="fixo",
        capital_inicial=100.00,
        status="pendente"
    )
    
    print(f"✅ Solicitação criada com ID: {solicitacao.id}")
    print(f"📋 Status: {solicitacao.status}")
    print(f"👤 Cliente: {solicitacao.nome_completo}")
    print(f"📧 Email: {solicitacao.email}")
    
    return solicitacao

if __name__ == "__main__":
    solicitacao = criar_solicitacao_teste()
    print(f"\n🔗 Acesse: http://127.0.0.1:8000/pagamentos/processar/?solicitacao_id={solicitacao.id}&tipo_servico=abrir_mei")