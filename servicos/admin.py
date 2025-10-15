from django.contrib import admin
from django.contrib import messages
from .models import Servico, SolicitacaoServico, SolicitacaoMEI

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'preco', 'ativo', 'ordem']
    list_filter = ['ativo', 'tipo', 'criado_em']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    list_editable = ['ativo', 'ordem', 'preco']
    ordering = ['ordem', 'nome']

@admin.register(SolicitacaoServico)
class SolicitacaoServicoAdmin(admin.ModelAdmin):
    list_display = ['servico', 'usuario', 'status', 'criado_em']
    list_filter = ['status', 'criado_em', 'servico']
    search_fields = ['usuario__username', 'servico__nome']
    list_editable = ['status']
    ordering = ['-criado_em']

@admin.register(SolicitacaoMEI)
class SolicitacaoMEIAdmin(admin.ModelAdmin):
    list_display = [
        'nome_completo', 'cpf', 'email', 'status', 'valor_servico', 
        'venda_criada', 'criado_em'
    ]
    list_filter = [
        'status', 'venda_criada', 'criado_em', 'estado', 'forma_atuacao'
    ]
    search_fields = ['nome_completo', 'cpf', 'email', 'cidade']
    list_editable = ['status', 'valor_servico']
    readonly_fields = ['criado_em', 'atualizado_em', 'venda_criada']
    ordering = ['-criado_em']
    actions = ['marcar_como_concluido', 'marcar_como_pendente']
    
    fieldsets = (
        ('Dados Pessoais', {
            'fields': ('nome_completo', 'cpf', 'rg', 'orgao_expedidor', 'estado_expedidor', 'email', 'telefone')
        }),
        ('Dados Empresariais', {
            'fields': ('cnae_primario', 'cnaes_secundarios', 'forma_atuacao', 'capital_inicial')
        }),
        ('Endereço', {
            'fields': ('cep', 'cidade', 'estado', 'rua', 'numero', 'bairro', 'complemento')
        }),
        ('Financeiro e Controle', {
            'fields': ('valor_servico', 'status', 'venda_criada', 'observacoes', 'usuario'),
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def marcar_como_concluido(self, request, queryset):
        """
        Action para marcar solicitações como concluídas em lote.
        
        Automaticamente criará vendas no painel financeiro para as
        solicitações que ainda não possuem venda criada.
        """
        updated = queryset.update(status='concluido')
        
        if updated:
            self.message_user(
                request,
                f'{updated} solicitação(ões) marcada(s) como concluída(s). '
                f'As vendas serão criadas automaticamente no painel financeiro.',
                level='SUCCESS'
            )
        else:
            self.message_user(
                request,
                'Nenhuma solicitação foi atualizada.',
                level='WARNING'
            )
    
    marcar_como_concluido.short_description = "✅ Marcar como concluído (gera venda automática)"
    
    def marcar_como_pendente(self, request, queryset):
        """Action para marcar solicitações como pendentes em lote."""
        updated = queryset.update(status='pendente')
        
        if updated:
            self.message_user(
                request,
                f'{updated} solicitação(ões) marcada(s) como pendente(s).',
                level='INFO'
            )
    
    marcar_como_pendente.short_description = "⏳ Marcar como pendente"
    
    def save_model(self, request, obj, form, change):
        """
        Customiza o salvamento para mostrar mensagens informativas.
        """
        # Verificar se o status mudou para concluído
        if change:
            original = SolicitacaoMEI.objects.get(pk=obj.pk)
            if original.status != 'concluido' and obj.status == 'concluido':
                self.message_user(
                    request,
                    f'✅ Solicitação de {obj.nome_completo} marcada como concluída. '
                    f'Uma venda de R$ {obj.valor_servico} será criada automaticamente no painel financeiro.',
                    level='SUCCESS'
                )
        
        super().save_model(request, obj, form, change)
