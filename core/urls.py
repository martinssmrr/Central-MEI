from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Página inicial
    path('', views.home, name='home'),
    
    # Autenticação
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Área do cliente
    path('minha-conta/', views.MinhaContaView.as_view(), name='minha_conta'),
    path('solicitacao/<int:pk>/', views.DetalheSolicitacaoView.as_view(), name='detalhe_solicitacao'),
    
    # Páginas institucionais
    path('sobre-nos/', views.sobre_nos, name='sobre_nos'),
    path('politicas-privacidade/', views.politicas_privacidade, name='politicas_privacidade'),
    path('fale-conosco/', views.fale_conosco, name='fale_conosco'),
    path('termos-uso/', views.termos_uso, name='termos_uso'),
]