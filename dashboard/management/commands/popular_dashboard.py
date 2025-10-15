from django.core.management.base import BaseCommand
from dashboard.models import (
    CategoriaPlanoContas, 
    SubcategoriaPlanoContas, 
    Produto
)

class Command(BaseCommand):
    help = 'Popula o banco de dados com dados iniciais do dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Criando categorias e produtos iniciais...')

        # Criar categorias de entrada
        cat_entrada, created = CategoriaPlanoContas.objects.get_or_create(
            nome='Receitas',
            tipo='entrada'
        )
        if created:
            self.stdout.write(f'Categoria criada: {cat_entrada}')

        # Criar categorias de saída
        cat_saida, created = CategoriaPlanoContas.objects.get_or_create(
            nome='Despesas Operacionais',
            tipo='saida'
        )
        if created:
            self.stdout.write(f'Categoria criada: {cat_saida}')

        # Subcategorias de entrada (vendas)
        subcats_entrada = [
            ('Abertura de MEI', 'Serviços de abertura de MEI'),
            ('Regularização de MEI', 'Serviços de regularização'),
            ('Declaração Anual MEI', 'DASN-SIMEI'),
            ('Contabilidade MEI', 'Serviços contábeis mensais'),
        ]

        for nome, desc in subcats_entrada:
            subcat, created = SubcategoriaPlanoContas.objects.get_or_create(
                categoria=cat_entrada,
                nome=nome,
                defaults={'descricao': desc}
            )
            if created:
                self.stdout.write(f'Subcategoria criada: {subcat}')

        # Subcategorias de saída (despesas)
        subcats_saida = [
            ('Salários e Encargos', 'Folha de pagamento dos colaboradores'),
            ('Marketing Digital', 'Google Ads, Facebook Ads, etc.'),
            ('Infraestrutura TI', 'Hosting, domínios, ferramentas'),
            ('Despesas Administrativas', 'Materiais de escritório, telefone, etc.'),
        ]

        for nome, desc in subcats_saida:
            subcat, created = SubcategoriaPlanoContas.objects.get_or_create(
                categoria=cat_saida,
                nome=nome,
                defaults={'descricao': desc}
            )
            if created:
                self.stdout.write(f'Subcategoria criada: {subcat}')

        # Criar produtos
        produtos_data = [
            ('Abertura de MEI', 'Abertura completa de MEI com documentos', 147.00, 'Abertura de MEI'),
            ('Regularização de MEI', 'Regularização de MEI em atraso', 147.00, 'Regularização de MEI'),
            ('Declaração Anual MEI', 'DASN-SIMEI - Declaração anual', 147.00, 'Declaração Anual MEI'),
            ('Contabilidade MEI Mensal', 'Acompanhamento contábil mensal', 97.00, 'Contabilidade MEI'),
        ]

        for nome, desc, preco, subcat_nome in produtos_data:
            try:
                subcategoria = SubcategoriaPlanoContas.objects.get(
                    categoria=cat_entrada,
                    nome=subcat_nome
                )
                produto, created = Produto.objects.get_or_create(
                    nome=nome,
                    defaults={
                        'descricao': desc,
                        'preco': preco,
                        'categoria': subcategoria
                    }
                )
                if created:
                    self.stdout.write(f'Produto criado: {produto}')
            except SubcategoriaPlanoContas.DoesNotExist:
                self.stdout.write(f'Subcategoria não encontrada: {subcat_nome}')

        self.stdout.write(
            self.style.SUCCESS('Dados iniciais criados com sucesso!')
        )