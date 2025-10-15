from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
import re

class Post(models.Model):
    """
    Modelo para posts do blog com suporte completo a HTML e metadados SEO.
    
    Este modelo permite a criação de artigos com conteúdo rico em HTML,
    metadados para SEO e controle completo de autoria e publicação.
    """
    
    # Campos básicos do artigo
    titulo = models.CharField(
        max_length=200,
        help_text="Título principal do artigo (máx. 200 caracteres)"
    )
    
    slug = models.SlugField(
        unique=True, 
        max_length=200,
        help_text="URL amigável do artigo (gerada automaticamente a partir do título)"
    )
    
    conteudo = models.TextField(
        help_text="Use o editor para criar conteúdo com formatação rica. Evite títulos H1 (use H2, H3, etc.)"
    )
    
    # Mídia e resumo
    imagem = models.ImageField(
        upload_to='blog/', 
        blank=True, 
        null=True,
        help_text="Imagem destacada do artigo (recomendado: 1200x630px)"
    )
    
    resumo = models.TextField(
        max_length=300, 
        help_text="Breve resumo do post usado na listagem e redes sociais (máx. 300 caracteres)"
    )
    
    # Autoria e dados customizáveis
    autor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Autor do artigo (usuário do sistema)"
    )
    
    nome_autor_display = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nome do autor para exibição (se diferente do usuário). Deixe vazio para usar o nome do usuário."
    )
    
    # Datas editáveis
    data_publicacao = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data de publicação personalizada. Deixe vazio para usar a data de criação."
    )
    
    # SEO e metadados
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Descrição para SEO (máx. 160 caracteres). Se vazio, usará o resumo."
    )
    
    palavras_chave = models.CharField(
        max_length=255,
        blank=True,
        help_text="Palavras-chave separadas por vírgula (ex: MEI, empreendedorismo, contabilidade)"
    )
    
    tags_seo = models.TextField(
        blank=True,
        help_text="""
        Tags HTML adicionais para SEO (opcional). 
        Ex: <meta property="article:section" content="Negócios">
        """
    )
    
    # Campos do sistema
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    publicado = models.BooleanField(
        default=True,
        help_text="Marque para tornar o artigo visível no site"
    )
    
    destaque_home = models.BooleanField(
        default=False,
        help_text="Marque para exibir este artigo na página inicial (máximo 3 recomendados)"
    )

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Post do Blog'
        verbose_name_plural = 'Posts do Blog'

    def clean(self):
        """Validação personalizada do modelo."""
        super().clean()
        
        # Validar HTML básico no conteúdo
        if self.conteudo:
            # Verificar se há tags H1 no conteúdo (não recomendado)
            if '<h1>' in self.conteudo.lower() or '<h1 ' in self.conteudo.lower():
                raise ValidationError({
                    'conteudo': 'Evite usar tags <h1> no conteúdo. Use <h2> ou <h3> para subtítulos.'
                })
        
        # Auto-preencher meta_description se vazio
        if not self.meta_description and self.resumo:
            self.meta_description = self.resumo[:160]

    def save(self, *args, **kwargs):
        """Override do save para aplicar validações automáticas."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        """URL absoluta do post."""
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def get_display_author(self):
        """Retorna o nome do autor para exibição."""
        if self.nome_autor_display:
            return self.nome_autor_display
        return self.autor.get_full_name() or self.autor.username
    
    def get_publication_date(self):
        """Retorna a data de publicação ou criação."""
        return self.data_publicacao or self.criado_em
    
    def get_meta_description(self):
        """Retorna a meta description ou o resumo."""
        return self.meta_description or self.resumo
    
    def get_reading_time(self):
        """Calcula tempo estimado de leitura (aproximadamente 200 palavras por minuto)."""
        if not self.conteudo:
            return 1
        
        # Remove tags HTML e conta palavras
        text_only = strip_tags(self.conteudo)
        word_count = len(text_only.split())
        reading_time = max(1, round(word_count / 200))
        
        return reading_time
    
    def get_word_count(self):
        """Conta palavras no conteúdo (sem HTML)."""
        if not self.conteudo:
            return 0
        
        text_only = strip_tags(self.conteudo)
        return len(text_only.split())
    
    @property
    def keywords_list(self):
        """Retorna lista de palavras-chave."""
        if not self.palavras_chave:
            return []
        return [keyword.strip() for keyword in self.palavras_chave.split(',') if keyword.strip()]
