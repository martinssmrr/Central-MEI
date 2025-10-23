from django.urls import path
from . import views
from . import test_views
from . import test_pagamento

app_name = 'pagamentos'

urlpatterns = [
    # Processar pagamento
    path('processar/', views.ProcessarPagamentoView.as_view(), name='processar'),
    path('pagamento-cartao/', views.processar_pagamento_cartao, name='pagamento_cartao'),
    
    # Checkout
    path('checkout/<uuid:pagamento_id>/', views.checkout_view, name='checkout'),
    
    # Páginas de retorno
    path('sucesso/', views.pagamento_sucesso, name='sucesso'),
    path('erro/', views.pagamento_erro, name='erro'),
    path('pendente/', views.pagamento_pendente, name='pendente'),
    
    # Webhook
    path('webhook/', views.webhook_mercadopago, name='webhook'),
    
    # Test views
    path('test-mp/', test_views.test_mercadopago, name='test_mp'),
    path('test-pagamento/', test_pagamento.ProcessarPagamentoTestView.as_view(), name='test_pagamento'),
]