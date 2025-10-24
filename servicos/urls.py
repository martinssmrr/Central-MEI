from django.urls import path
from . import views

app_name = 'servicos'

urlpatterns = [
    path('', views.ServicoListView.as_view(), name='lista'),
    path('abrir-mei/', views.abrir_mei, name='abrir_mei'),
    path('abrir-mei/info/', views.abrir_mei_info, name='abrir_mei_info'),
    path('abrir-mei/passo-1/', views.abrir_mei_passo1, name='abrir_mei_passo1'),
    path('abrir-mei/passo-2/', views.abrir_mei_passo2, name='abrir_mei_passo2'),
    path('abrir-mei/passo1/', views.abrir_mei_passo1, name='abrir_mei_passo1_alt'),
    path('abrir-mei/passo2/', views.abrir_mei_passo2, name='abrir_mei_passo2_alt'),
    path('abrir-mei/sucesso/<int:protocolo>/', views.abrir_mei_sucesso, name='abrir_mei_sucesso'),
    path('abrir-mei/voltar/', views.abrir_mei_voltar_passo1, name='abrir_mei_voltar'),
    path('regularizar-mei/', views.regularizar_mei_passo_1, name='regularizar_mei'),
    path('regularizar-mei/passo-1/', views.regularizar_mei_passo_1, name='regularizar_mei_passo_1'),
    path('regularizar-mei/passo-2/', views.regularizar_mei_passo_2, name='regularizar_mei_passo_2'),
    path('regularizar-mei/passo1/', views.regularizar_mei_passo_1, name='regularizar_mei_passo1'),
    path('regularizar-mei/passo2/', views.regularizar_mei_passo_2, name='regularizar_mei_passo2'),
    path('regularizar-mei/sucesso/<int:pk>/', views.regularizar_mei_sucesso, name='regularizar_mei_sucesso'),
    path('declaracao-mei/', views.declaracao_mei_passo_1, name='declaracao_mei'),
    path('declaracao-mei/passo-1/', views.declaracao_mei_passo_1, name='declaracao_mei_passo_1'),
    path('declaracao-mei/passo-2/', views.declaracao_mei_passo_2, name='declaracao_mei_passo_2'),
    path('declaracao-anual-mei/passo1/', views.declaracao_mei_passo_1, name='declaracao_anual_mei_passo1'),
    path('declaracao-anual-mei/passo2/', views.declaracao_mei_passo_2, name='declaracao_anual_mei_passo2'),
    path('declaracao-mei/sucesso/<int:protocolo>/', views.declaracao_mei_sucesso, name='declaracao_mei_sucesso'),
    path('baixar-mei/', views.baixar_mei_passo_1, name='baixar_mei'),
    path('baixar-mei/passo-1/', views.baixar_mei_passo_1, name='baixar_mei_passo_1'),
    path('baixar-mei/passo-2/', views.baixar_mei_passo_2, name='baixar_mei_passo_2'),
    path('baixar-mei/passo1/', views.baixar_mei_passo_1, name='baixar_mei_passo1'),
    path('baixar-mei/passo2/', views.baixar_mei_passo_2, name='baixar_mei_passo2'),
    path('baixar-mei/sucesso/<int:pk>/', views.baixar_mei_sucesso, name='baixar_mei_sucesso'),
    path('<slug:slug>/', views.ServicoDetailView.as_view(), name='detalhe'),
    path('<slug:slug>/solicitar/', views.SolicitarServicoView.as_view(), name='solicitar'),
]