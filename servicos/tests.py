"""
Testes para automação entre Solicitações MEI e Painel Financeiro

Este módulo testa a funcionalidade de criação automática de vendas
quando uma solicitação de abertura MEI é marcada como concluída.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from servicos.models import SolicitacaoMEI
from dashboard.models import Venda, Produto, CategoriaPlanoContas, SubcategoriaPlanoContas, MovimentacaoCaixa


class AutomacaoMEIFinanceiroTest(TestCase):
    """Testes para automação MEI → Financeiro."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar usuário administrador
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
    
    def test_criacao_venda_automatica_ao_concluir_mei(self):
        """
        Testa se uma venda é criada automaticamente quando
        uma solicitação MEI é marcada como concluída.
        """
        # Criar solicitação MEI
        solicitacao = SolicitacaoMEI.objects.create(
            nome_completo='João Silva',
            cpf='123.456.789-00',
            rg='12345678',
            orgao_expedidor='SSP',
            estado_expedidor='SP',
            email='joao@example.com',
            telefone='(11) 99999-9999',
            cnae_primario='5611-2/01',
            forma_atuacao='fixo',
            capital_inicial=Decimal('1000.00'),
            cep='01234-567',
            cidade='São Paulo',
            estado='SP',
            rua='Rua Exemplo',
            numero='123',
            bairro='Centro',
            usuario=self.user,
            status='pendente',
            valor_servico=Decimal('97.00')
        )
        
        # Verificar que não há venda inicialmente
        self.assertFalse(solicitacao.venda_criada)
        self.assertEqual(Venda.objects.count(), 0)
        
        # Marcar como concluída
        solicitacao.status = 'concluido'
        solicitacao.save()
        
        # Recarregar do banco de dados
        solicitacao.refresh_from_db()
        
        # Verificar que a venda foi criada
        self.assertTrue(solicitacao.venda_criada)
        self.assertEqual(Venda.objects.count(), 1)
        
        # Verificar dados da venda
        venda = Venda.objects.first()
        self.assertEqual(venda.cliente_nome, 'João Silva')
        self.assertEqual(venda.cliente_cpf_cnpj, '123.456.789-00')
        self.assertEqual(venda.cliente_email, 'joao@example.com')
        self.assertEqual(venda.valor_final, Decimal('97.00'))
        self.assertEqual(venda.status, 'pago')
        self.assertIn('solicitação MEI #', venda.observacoes)
    
    def test_nao_duplicar_venda_ao_salvar_novamente(self):
        """
        Testa se não são criadas vendas duplicadas quando
        uma solicitação já concluída é salva novamente.
        """
        # Criar solicitação como pendente primeiro
        solicitacao = SolicitacaoMEI.objects.create(
            nome_completo='Maria Oliveira',
            cpf='987.654.321-00',
            rg='87654321',
            orgao_expedidor='SSP',
            estado_expedidor='RJ',
            email='maria@example.com',
            telefone='(21) 88888-8888',
            cnae_primario='5611-2/01',
            forma_atuacao='internet',
            capital_inicial=Decimal('500.00'),
            cep='20000-000',
            cidade='Rio de Janeiro',
            estado='RJ',
            rua='Av. Brasil',
            numero='456',
            bairro='Centro',
            usuario=self.user,
            status='pendente',  # Criar como pendente
            valor_servico=Decimal('120.00')
        )
        
        # Alterar para concluído para ativar o signal
        solicitacao.status = 'concluido'
        solicitacao.save()
        
        # Recarregar e verificar que uma venda foi criada
        solicitacao.refresh_from_db()
        self.assertEqual(Venda.objects.count(), 1)
        self.assertTrue(solicitacao.venda_criada)
        
        # Salvar novamente (simular edição no admin)
        solicitacao.observacoes = 'Solicitação editada'
        solicitacao.save()
        
        # Verificar que não foi criada venda duplicada
        self.assertEqual(Venda.objects.count(), 1)
    
    def test_mudanca_status_de_processando_para_concluido(self):
        """
        Testa mudança de status específica: processando → concluído.
        """
        # Criar solicitação em processamento
        solicitacao = SolicitacaoMEI.objects.create(
            nome_completo='Carlos Ferreira',
            cpf='444.555.666-77',
            rg='44556677',
            orgao_expedidor='EB',
            estado_expedidor='DF',
            email='carlos@example.com',
            telefone='(61) 55555-5555',
            cnae_primario='5611-2/01',
            forma_atuacao='internet',
            capital_inicial=Decimal('700.00'),
            cep='70000-000',
            cidade='Brasília',
            estado='DF',
            rua='SQN 123',
            numero='Bloco A',
            bairro='Asa Norte',
            usuario=self.user,
            status='processando',  # Iniciar como processando
            valor_servico=Decimal('110.00')
        )
        
        # Verificar que não há venda inicialmente
        self.assertEqual(Venda.objects.count(), 0)
        self.assertFalse(solicitacao.venda_criada)
        
        # Mudar para concluído
        solicitacao.status = 'concluido'
        solicitacao.save()
        
        # Recarregar e verificar
        solicitacao.refresh_from_db()
        self.assertTrue(solicitacao.venda_criada)
        self.assertEqual(Venda.objects.count(), 1)
        
        venda = Venda.objects.first()
        self.assertEqual(venda.valor_final, Decimal('110.00'))
