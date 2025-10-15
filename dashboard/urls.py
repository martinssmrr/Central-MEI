from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_home, name='home'),
    
    # Vendas
    path('vendas/', views.vendas_list, name='vendas_list'),
    path('vendas/nova/', views.venda_create, name='venda_create'),
    
    # Movimentações Financeiras
    path('movimentacoes/', views.movimentacoes_list, name='movimentacoes_list'),
    path('movimentacoes/nova/', views.movimentacao_create, name='movimentacao_create'),
    path('movimentacoes/<int:pk>/editar/', views.movimentacao_update, name='movimentacao_update'),
    path('movimentacoes/<int:pk>/excluir/', views.movimentacao_delete, name='movimentacao_delete'),
    
    # Plano de Contas
    path('plano-contas/', views.plano_contas, name='plano_contas'),
    
    # Relatórios
    path('relatorios/', views.relatorios, name='relatorios'),
    path('relatorios/pdf/', views.relatorio_pdf, name='relatorio_pdf'),
    
    # Categorias
    path('categorias/nova/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/excluir/', views.categoria_delete, name='categoria_delete'),
    
    # Subcategorias
    path('subcategorias/nova/', views.subcategoria_create, name='subcategoria_create'),
    path('subcategorias/<int:pk>/editar/', views.subcategoria_update, name='subcategoria_update'),
    path('subcategorias/<int:pk>/excluir/', views.subcategoria_delete, name='subcategoria_delete'),
    
    # AJAX
    path('ajax/subcategorias/', views.get_subcategorias, name='get_subcategorias'),
    path('ajax/categorias-por-tipo/', views.get_categorias_por_tipo, name='get_categorias_por_tipo'),
]