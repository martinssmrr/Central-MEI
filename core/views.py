from django.shortcuts import render
from django.views.generic import TemplateView
from depoimentos.models import Depoimento
from blog.models import Post
from servicos.models import Servico

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
