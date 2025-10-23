from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroUsuarioForm
from .models import Profile

def cadastro_usuario(request):
    """
    View para cadastro de novos usuários
    """
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                # Cria o usuário
                user = form.save()
                
                # Mensagem de sucesso
                messages.success(
                    request, 
                    f'Conta criada com sucesso! Bem-vindo(a), {user.first_name}!'
                )
                
                # Faz login automático do usuário
                login(request, user)
                
                # Redireciona para a página inicial ou dashboard
                return redirect('core:home')  # Ajuste conforme sua URL
                
            except Exception as e:
                messages.error(
                    request,
                    'Ocorreu um erro ao criar sua conta. Tente novamente.'
                )
        else:
            # Se o formulário tem erros, eles serão exibidos no template
            messages.error(
                request,
                'Por favor, corrija os erros abaixo e tente novamente.'
            )
    else:
        form = RegistroUsuarioForm()
    
    context = {
        'form': form,
        'title': 'Criar Conta - Central MEI'
    }
    
    return render(request, 'usuarios/cadastro.html', context)

def cadastro_sucesso(request):
    """
    Página de sucesso após o cadastro
    """
    return render(request, 'usuarios/cadastro_sucesso.html')

class CustomLoginView(LoginView):
    """
    View customizada para login
    """
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core:home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Bem-vindo de volta, {form.get_user().first_name}!')
        return super().form_valid(form)
