from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/lista.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        return Post.objects.filter(publicado=True)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detalhe.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Post.objects.filter(publicado=True)
