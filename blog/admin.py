from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Configuração avançada do Django Admin para posts do blog.
    
    Inclui editor WYSIWYG, organização por fieldsets e validações customizadas.
    """
    
    # Listagem principal
    list_display = [
        'titulo',
        'get_display_author_admin', 
        'get_publication_date_admin',
        'publicado',
        'destaque_home',
        'get_word_count_admin',
        'criado_em'
    ]
    
    list_filter = [
        'publicado',
        'destaque_home', 
        'criado_em', 
        'data_publicacao',
        'autor'
    ]
    
    search_fields = [
        'titulo', 
        'conteudo', 
        'resumo',
        'palavras_chave',
        'nome_autor_display'
    ]
    
    prepopulated_fields = {'slug': ('titulo',)}
    
    list_editable = ['publicado', 'destaque_home']
    
    ordering = ['-criado_em']
    
    list_per_page = 25
    
    # Organização do formulário por seções
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'slug', 'resumo'),
            'description': 'Informações principais do artigo'
        }),
        
        ('Conteúdo', {
            'fields': ('conteudo', 'imagem'),
            'classes': ('wide',),
            'description': 'Conteúdo principal do artigo com suporte a HTML'
        }),
        
        ('Autoria e Publicação', {
            'fields': (
                ('autor', 'nome_autor_display'),
                ('publicado', 'destaque_home'),
                'data_publicacao'
            ),
            'description': 'Configurações de autor, publicação e destaque na home'
        }),
        
        ('SEO e Metadados', {
            'fields': (
                'meta_description',
                'palavras_chave', 
                'tags_seo'
            ),
            'classes': ('collapse',),
            'description': 'Configurações para otimização em motores de busca'
        }),
        
        ('Informações do Sistema', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
            'description': 'Dados automáticos do sistema (somente leitura)'
        }),
    )
    
    readonly_fields = ('criado_em', 'atualizado_em')
    
    # Widget customizado para editor WYSIWYG
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'class': 'wysiwyg-editor',
                'rows': 20,
                'cols': 100
            })
        },
    }
    
    # Métodos para exibição customizada na lista
    def get_display_author_admin(self, obj):
        """Exibe o nome do autor formatado."""
        author_name = obj.get_display_author()
        if obj.nome_autor_display:
            return format_html(
                '<span title="Nome personalizado: {}">{}</span>',
                obj.nome_autor_display,
                author_name
            )
        return author_name
    get_display_author_admin.short_description = 'Autor'
    get_display_author_admin.admin_order_field = 'autor'
    
    def get_publication_date_admin(self, obj):
        """Exibe a data de publicação formatada."""
        pub_date = obj.get_publication_date()
        if obj.data_publicacao:
            return format_html(
                '<span title="Data personalizada" style="color: #0066cc;">{}</span>',
                pub_date.strftime('%d/%m/%Y %H:%M')
            )
        return pub_date.strftime('%d/%m/%Y %H:%M')
    get_publication_date_admin.short_description = 'Data Publicação'
    get_publication_date_admin.admin_order_field = 'data_publicacao'
    
    def get_word_count_admin(self, obj):
        """Exibe contagem de palavras com tempo estimado de leitura."""
        word_count = obj.get_word_count()
        reading_time = obj.get_reading_time()
        
        if word_count > 0:
            return format_html(
                '<span title="Tempo de leitura: {} min">{} palavras</span>',
                reading_time,
                word_count
            )
        return '0 palavras'
    get_word_count_admin.short_description = 'Palavras'
    
    class Media:
        """Inclui arquivos CSS e JS necessários para o editor."""
        css = {
            'all': (
                'admin/css/blog-admin.css',
                'https://cdn.ckeditor.com/ckeditor5/40.0.0/classic/ckeditor.css',
            )
        }
        js = (
            'https://cdn.ckeditor.com/ckeditor5/40.0.0/classic/ckeditor.js',
            'admin/js/blog-editor-simple.js',
        )
    
    def save_model(self, request, obj, form, change):
        """Override para definir autor padrão se não especificado."""
        if not obj.autor_id:
            obj.autor = request.user
        super().save_model(request, obj, form, change)
