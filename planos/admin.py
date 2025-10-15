from django.contrib import admin
from .models import Plano

@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'ativo', 'destaque', 'ordem']
    list_filter = ['ativo', 'destaque', 'criado_em']
    search_fields = ['nome', 'descricao']
    list_editable = ['ativo', 'destaque', 'ordem', 'preco']
    ordering = ['ordem', 'nome']
