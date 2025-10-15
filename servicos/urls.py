from django.urls import path
from . import views

app_name = 'servicos'

urlpatterns = [
    path('', views.ServicoListView.as_view(), name='lista'),
    path('abrir-mei/', views.abrir_mei, name='abrir_mei'),
    path('abrir-mei/info/', views.abrir_mei_info, name='abrir_mei_info'),
    path('abrir-mei/passo-1/', views.abrir_mei_passo1, name='abrir_mei_passo1'),
    path('abrir-mei/passo-2/', views.abrir_mei_passo2, name='abrir_mei_passo2'),
    path('abrir-mei/sucesso/<int:protocolo>/', views.abrir_mei_sucesso, name='abrir_mei_sucesso'),
    path('abrir-mei/voltar/', views.abrir_mei_voltar_passo1, name='abrir_mei_voltar'),
    path('regularizar-mei/', views.regularizar_mei, name='regularizar_mei'),
    path('declaracao-mei/', views.declaracao_mei, name='declaracao_mei'),
    path('<slug:slug>/', views.ServicoDetailView.as_view(), name='detalhe'),
    path('<slug:slug>/solicitar/', views.SolicitarServicoView.as_view(), name='solicitar'),
]