#!/usr/bin/env python
"""
Script para criar os serviços iniciais no sistema
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'central_mei.settings')
django.setup()

from servicos.models import Servico
from decimal import Decimal

# Dados dos serviços
servicos_data = [
    {
        'nome': 'Abrir MEI',
        'slug': 'abrir-mei',
        'tipo': 'abrir_mei',
        'descricao': 'Abertura completa do seu MEI com toda documentação necessária. Processo rápido e seguro, com acompanhamento até a conclusão.',
        'preco': Decimal('129.90'),
        'tempo_estimado': '2-3 dias úteis',
        'ativo': True,
        'ordem': 1
    },
    {
        'nome': 'Regularizar MEI',
        'slug': 'regularizar-mei',
        'tipo': 'regularizar_mei',
        'descricao': 'Regularização completa do seu MEI em atraso. Quitação de débitos e colocação da documentação em dia.',
        'preco': Decimal('129.90'),
        'tempo_estimado': '3-5 dias úteis',
        'ativo': True,
        'ordem': 2
    },
    {
        'nome': 'Declaração Anual MEI',
        'slug': 'declaracao-anual-mei',
        'tipo': 'declaracao_anual_mei',
        'descricao': 'Declaração anual simplificada (DASN-SIMEI). Evite multas e mantenha seu MEI regular com nossa ajuda especializada.',
        'preco': Decimal('129.90'),
        'tempo_estimado': '1-2 dias úteis',
        'ativo': True,
        'ordem': 3
    },
    {
        'nome': 'Baixar MEI',
        'slug': 'baixar-mei',
        'tipo': 'baixar_mei',
        'descricao': 'Encerramento completo das atividades do MEI com quitação de todas as pendências. Processo seguro e definitivo.',
        'preco': Decimal('129.90'),
        'tempo_estimado': '5-7 dias úteis',
        'ativo': True,
        'ordem': 4
    }
]

def criar_servicos():
    """Criar os serviços no banco de dados"""
    print("Criando serviços iniciais...")
    
    for servico_data in servicos_data:
        servico, created = Servico.objects.get_or_create(
            slug=servico_data['slug'],
            defaults=servico_data
        )
        
        if created:
            print(f"✅ Serviço '{servico.nome}' criado com sucesso!")
        else:
            print(f"⚠️  Serviço '{servico.nome}' já existe")
            # Atualizar preço se necessário
            if servico.preco != servico_data['preco']:
                servico.preco = servico_data['preco']
                servico.save()
                print(f"   Preço atualizado para R$ {servico_data['preco']}")

    print(f"\n📊 Total de serviços ativos: {Servico.objects.filter(ativo=True).count()}")
    print("\n🎉 Configuração inicial concluída!")

if __name__ == '__main__':
    criar_servicos()