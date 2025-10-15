from django import forms
from django.utils import timezone
from .models import (
    CategoriaPlanoContas, 
    SubcategoriaPlanoContas, 
    Produto, 
    Venda, 
    MovimentacaoCaixa
)

class CategoriaPlanoContasForm(forms.ModelForm):
    class Meta:
        model = CategoriaPlanoContas
        fields = ['nome', 'tipo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da categoria'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
        }

class SubcategoriaPlanoContasForm(forms.ModelForm):
    class Meta:
        model = SubcategoriaPlanoContas
        fields = ['categoria', 'nome', 'descricao']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da subcategoria'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição (opcional)'}),
        }

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'categoria']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto/serviço'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição (opcional)'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
        }

class VendaForm(forms.ModelForm):
    class Meta:
        model = Venda
        fields = [
            'cliente_nome', 'cliente_email', 'cliente_telefone', 'cliente_cpf_cnpj',
            'produto', 'quantidade', 'valor_unitario', 'desconto',
            'status', 'forma_pagamento', 'observacoes', 'data_pagamento'
        ]
        widgets = {
            'cliente_nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do cliente'}),
            'cliente_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'cliente_telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'cliente_cpf_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CPF ou CNPJ'}),
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'desconto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'value': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
            'data_pagamento': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar apenas produtos ativos
        self.fields['produto'].queryset = Produto.objects.filter(ativo=True)
        
        # Se tem um produto selecionado, preencher o valor unitário
        if self.instance.pk and self.instance.produto:
            self.fields['valor_unitario'].initial = self.instance.produto.preco

class MovimentacaoCaixaForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(
        queryset=CategoriaPlanoContas.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_categoria'}),
        label='Categoria'
    )
    
    class Meta:
        model = MovimentacaoCaixa
        fields = ['tipo', 'categoria', 'subcategoria', 'descricao', 'valor', 'data_movimentacao', 'observacoes']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'subcategoria': forms.Select(attrs={'class': 'form-select', 'id': 'id_subcategoria'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição da movimentação'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'data_movimentacao': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicialmente, subcategoria vazia (será preenchida via AJAX)
        self.fields['subcategoria'].queryset = SubcategoriaPlanoContas.objects.none()
        
        # Data padrão: agora
        if not self.instance.pk:
            self.fields['data_movimentacao'].initial = timezone.now()
        
        # Se tem categoria selecionada, filtrar subcategorias
        if 'categoria' in self.data:
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = SubcategoriaPlanoContas.objects.filter(
                    categoria_id=categoria_id, ativo=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.subcategoria:
            self.fields['categoria'].initial = self.instance.subcategoria.categoria
            self.fields['subcategoria'].queryset = SubcategoriaPlanoContas.objects.filter(
                categoria=self.instance.subcategoria.categoria, ativo=True
            )


class RelatorioForm(forms.Form):
    """Form para filtros de relatórios financeiros"""
    
    TIPO_CHOICES = [
        ('', 'Todos os tipos'),
        ('entrada', 'Apenas Entradas'),
        ('saida', 'Apenas Saídas'),
    ]
    
    PERIODO_CHOICES = [
        ('', 'Período personalizado'),
        ('hoje', 'Hoje'),
        ('ontem', 'Ontem'),
        ('esta_semana', 'Esta semana'),
        ('semana_passada', 'Semana passada'),
        ('este_mes', 'Este mês'),
        ('mes_passado', 'Mês passado'),
        ('ultimos_7_dias', 'Últimos 7 dias'),
        ('ultimos_30_dias', 'Últimos 30 dias'),
        ('ultimos_90_dias', 'Últimos 90 dias'),
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_tipo_relatorio'
        }),
        label='Tipo de Movimentação'
    )
    
    categoria = forms.ModelChoiceField(
        queryset=CategoriaPlanoContas.objects.filter(ativo=True),
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_categoria_relatorio'
        }),
        label='Categoria'
    )
    
    subcategoria = forms.ModelChoiceField(
        queryset=SubcategoriaPlanoContas.objects.filter(ativo=True),
        required=False,
        empty_label='Todas as subcategorias',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_subcategoria_relatorio'
        }),
        label='Subcategoria'
    )
    
    periodo_predefinido = forms.ChoiceField(
        choices=PERIODO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_periodo_predefinido'
        }),
        label='Período Pré-definido'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_data_inicio'
        }),
        label='Data Início'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'id_data_fim'
        }),
        label='Data Fim'
    )
    
    incluir_observacoes = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_incluir_observacoes'
        }),
        label='Incluir observações no relatório'
    )
    
    ordenacao = forms.ChoiceField(
        choices=[
            ('data_desc', 'Data (mais recente primeiro)'),
            ('data_asc', 'Data (mais antiga primeiro)'),
            ('valor_desc', 'Valor (maior primeiro)'),
            ('valor_asc', 'Valor (menor primeiro)'),
            ('categoria', 'Categoria (A-Z)'),
        ],
        initial='data_desc',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_ordenacao'
        }),
        label='Ordenação'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicialmente subcategoria vazia (será preenchida via AJAX)
        self.fields['subcategoria'].queryset = SubcategoriaPlanoContas.objects.none()
        
        # Se tem categoria selecionada, filtrar subcategorias
        if 'categoria' in self.data and self.data.get('categoria'):
            try:
                categoria_id = int(self.data.get('categoria'))
                self.fields['subcategoria'].queryset = SubcategoriaPlanoContas.objects.filter(
                    categoria_id=categoria_id, ativo=True
                )
            except (ValueError, TypeError):
                pass