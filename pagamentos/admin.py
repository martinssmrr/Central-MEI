from django.contrib import admin
from .models import Pagamento

@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('mp_external_reference', 'nome_cliente', 'tipo_servico', 'valor', 'status', 'criado_em')
    list_filter = ('status', 'tipo_servico', 'criado_em')
    search_fields = ('mp_external_reference', 'nome_cliente', 'email_cliente', 'mp_payment_id')
    readonly_fields = ('id', 'criado_em', 'atualizado_em', 'mp_payment_id')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('id', 'tipo_servico', 'valor', 'status')
        }),
        ('Cliente', {
            'fields': ('nome_cliente', 'email_cliente', 'telefone_cliente')
        }),
        ('Mercado Pago', {
            'fields': ('mp_external_reference', 'mp_preference_id', 'mp_payment_id')
        }),
        ('Relacionamentos', {
            'fields': ('usuario', 'solicitacao_mei')
        }),
        ('Metadados', {
            'fields': ('criado_em', 'atualizado_em', 'dados_extras')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # Editando objeto existente
            readonly.extend(['mp_external_reference', 'tipo_servico', 'valor'])
        return readonly
