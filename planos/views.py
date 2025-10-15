from django.shortcuts import render
from django.views.generic import ListView
from .models import Plano


class PlanoListView(ListView):
    model = Plano
    template_name = 'planos/lista.html'
    context_object_name = 'planos'
    
    def get_queryset(self):
        return Plano.objects.filter(ativo=True)
