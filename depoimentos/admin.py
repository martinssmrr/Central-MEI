from django.contrib import admin
from .models import Depoimento

@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'empresa', 'ativo', 'criado_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'empresa', 'conteudo']
    list_editable = ['ativo']
    ordering = ['-criado_em']
