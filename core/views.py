from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from depoimentos.models import Depoimento
from blog.models import Post
from servicos.models import Servico, SolicitacaoMEI, SolicitacaoServico

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Serviços principais para exibir na home
        servicos_principais = Servico.objects.filter(
            ativo=True,
            tipo__in=['abrir_mei', 'regularizar_mei', 'declaracao_anual_mei']
        )[:3]
        
        # Depoimentos ativos (todos para o scroll horizontal)
        depoimentos = Depoimento.objects.filter(ativo=True)
        
        # Posts em destaque para a home
        posts_recentes = Post.objects.filter(publicado=True, destaque_home=True)[:3]
        
        context.update({
            'servicos_principais': servicos_principais,
            'depoimentos': depoimentos,
            'posts_recentes': posts_recentes,
        })
        
        return context

home = HomeView.as_view()


class CustomLoginView(LoginView):
    """
    View customizada para login do cliente.
    
    Utiliza o sistema de autenticação nativo do Django com 
    template personalizado e mensagens de feedback.
    """
    template_name = 'core/auth/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('core:minha_conta')
    
    def get_success_url(self):
        """Redireciona para 'minha conta' após login bem-sucedido."""
        messages.success(self.request, '✅ Login realizado com sucesso! Bem-vindo de volta.')
        return reverse_lazy('core:minha_conta')
    
    def form_invalid(self, form):
        """Adiciona mensagem de erro quando credenciais estão incorretas."""
        messages.error(self.request, '❌ Credenciais inválidas. Verifique seu e-mail e senha.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    View customizada para logout do cliente.
    
    Encerra a sessão e redireciona para home com mensagem de confirmação.
    """
    next_page = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        """Adiciona mensagem de confirmação de logout."""
        if request.user.is_authenticated:
            messages.success(request, '👋 Sessão encerrada com sucesso. Até logo!')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class MinhaContaView(LoginRequiredMixin, TemplateView):
    """
    View para página 'Minha Conta' do cliente.
    
    Exibe informações do usuário e suas solicitações no sistema.
    Requer autenticação para acesso.
    """
    template_name = 'core/auth/minha_conta.html'
    login_url = reverse_lazy('core:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Buscar solicitações MEI do usuário
        solicitacoes_mei = SolicitacaoMEI.objects.filter(
            usuario=user
        ).order_by('-criado_em')
        
        # Buscar outras solicitações de serviços
        solicitacoes_servicos = SolicitacaoServico.objects.filter(
            usuario=user
        ).order_by('-criado_em')
        
        # Estatísticas do usuário
        total_solicitacoes = solicitacoes_mei.count() + solicitacoes_servicos.count()
        solicitacoes_pendentes = (
            solicitacoes_mei.filter(status='pendente').count() + 
            solicitacoes_servicos.filter(status='pendente').count()
        )
        solicitacoes_concluidas = (
            solicitacoes_mei.filter(status='concluido').count() + 
            solicitacoes_servicos.filter(status='concluido').count()
        )
        
        context.update({
            'solicitacoes_mei': solicitacoes_mei,
            'solicitacoes_servicos': solicitacoes_servicos,
            'total_solicitacoes': total_solicitacoes,
            'solicitacoes_pendentes': solicitacoes_pendentes,
            'solicitacoes_concluidas': solicitacoes_concluidas,
        })
        
        return context


@method_decorator(login_required, name='dispatch') 
class DetalheSolicitacaoView(LoginRequiredMixin, TemplateView):
    """
    View para exibir detalhes de uma solicitação específica.
    
    Permite ao usuário visualizar informações completas de suas solicitações.
    """
    template_name = 'core/auth/detalhe_solicitacao.html'
    login_url = reverse_lazy('core:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        solicitacao_id = kwargs.get('pk')
        tipo = self.request.GET.get('tipo', 'mei')
        
        try:
            if tipo == 'mei':
                solicitacao = SolicitacaoMEI.objects.get(
                    id=solicitacao_id, 
                    usuario=self.request.user
                )
            else:
                solicitacao = SolicitacaoServico.objects.get(
                    id=solicitacao_id, 
                    usuario=self.request.user
                )
                
            context['solicitacao'] = solicitacao
            context['tipo'] = tipo
            
        except (SolicitacaoMEI.DoesNotExist, SolicitacaoServico.DoesNotExist):
            messages.error(self.request, '❌ Solicitação não encontrada.')
            return redirect('core:minha_conta')
            
        return context


def sobre_nos(request):
    """
    View para a página Sobre Nós.
    
    Exibe informações institucionais sobre a Central MEI.
    """
    return render(request, 'core/institucional/sobre_nos.html')


def politicas_privacidade(request):
    """
    View para a página de Políticas de Privacidade.
    
    Exibe as políticas de privacidade e tratamento de dados.
    """
    return render(request, 'core/institucional/politicas_privacidade.html')


def fale_conosco(request):
    """
    View para a página Fale Conosco.
    
    Exibe informações de contato e formulário de comunicação.
    """
    return render(request, 'core/institucional/fale_conosco.html')


def termos_uso(request):
    """
    View para a página de Termos de Uso.
    
    Exibe os termos e condições de uso dos serviços.
    """
    return render(request, 'core/institucional/termos_uso.html')
