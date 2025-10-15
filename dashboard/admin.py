from django.contrib import admin
from .models import (
    CategoriaPlanoContas, 
    SubcategoriaPlanoContas, 
    Produto, 
    Venda, 
    MovimentacaoCaixa, 
    SaldoCaixa
)

@admin.register(CategoriaPlanoContas)
class CategoriaPlanoContasAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'ativo', 'criado_em']
    list_filter = ['tipo', 'ativo', 'criado_em']
    search_fields = ['nome']
    list_editable = ['ativo']

@admin.register(SubcategoriaPlanoContas)
class SubcategoriaPlanoContasAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'ativo', 'criado_em']
    list_filter = ['categoria__tipo', 'categoria', 'ativo']
    search_fields = ['nome', 'categoria__nome']
    list_editable = ['ativo']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'categoria', 'ativo', 'criado_em']
    list_filter = ['categoria__categoria__tipo', 'categoria', 'ativo']
    search_fields = ['nome', 'descricao']
    list_editable = ['preco', 'ativo']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente_nome', 'produto', 'valor_final', 'status', 'vendedor', 'data_venda']
    list_filter = ['status', 'forma_pagamento', 'produto', 'vendedor', 'data_venda']
    search_fields = ['cliente_nome', 'cliente_email', 'cliente_cpf_cnpj', 'produto__nome']
    readonly_fields = ['valor_total', 'valor_final', 'data_venda']
    list_editable = ['status']
    date_hierarchy = 'data_venda'

@admin.register(MovimentacaoCaixa)
class MovimentacaoCaixaAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'tipo', 'subcategoria', 'valor', 'data_movimentacao', 'usuario']
    list_filter = ['tipo', 'subcategoria__categoria__tipo', 'subcategoria', 'data_movimentacao']
    search_fields = ['descricao', 'observacoes']
    date_hierarchy = 'data_movimentacao'

@admin.register(SaldoCaixa)
class SaldoCaixaAdmin(admin.ModelAdmin):
    list_display = ['data', 'saldo_inicial', 'total_entradas', 'total_saidas', 'saldo_final']
    readonly_fields = ['atualizado_em']
    date_hierarchy = 'data'
