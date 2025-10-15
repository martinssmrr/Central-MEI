from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Servico, SolicitacaoServico


class ServicoListView(ListView):
    model = Servico
    template_name = 'servicos/lista.html'
    context_object_name = 'servicos'
    paginate_by = 12
    
    def get_queryset(self):
        return Servico.objects.filter(ativo=True)


class ServicoDetailView(DetailView):
    model = Servico
    template_name = 'servicos/detalhe.html'
    context_object_name = 'servico'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'


# Views específicas para serviços principais
def abrir_mei(request):
    # Redireciona diretamente para o formulário passo 1
    return redirect('servicos:abrir_mei_passo1')

def abrir_mei_info(request):
    # Página informativa sobre abertura de MEI
    return render(request, 'servicos/abrir_mei.html')

def regularizar_mei(request):
    return render(request, 'servicos/regularizar_mei.html')

def declaracao_mei(request):
    return render(request, 'servicos/declaracao_mei.html')

# Views para formulário MEI em duas etapas
from django.contrib import messages
from django.http import JsonResponse
from .models import SolicitacaoMEI
from .forms import DadosPessoaisForm, DadosEmpresariaisForm

def abrir_mei_passo1(request):
    """Primeira etapa: Dados Pessoais"""
    if request.method == 'POST':
        form = DadosPessoaisForm(request.POST)
        if form.is_valid():
            # Armazenar os dados na sessão
            request.session['dados_pessoais'] = form.cleaned_data
            request.session['dados_pessoais']['cpf'] = form.cleaned_data['cpf'].replace('.', '').replace('-', '')
            request.session['dados_pessoais']['telefone'] = form.cleaned_data['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
            return redirect('servicos:abrir_mei_passo2')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Se há dados na sessão, pré-preenche o formulário
        form_data = request.session.get('dados_pessoais', {})
        form = DadosPessoaisForm(initial=form_data)
    
    return render(request, 'servicos/abrir_mei_passo1.html', {'form': form})

def abrir_mei_passo2(request):
    """Segunda etapa: Dados Empresariais"""
    # Verifica se o usuário completou o passo 1
    if 'dados_pessoais' not in request.session:
        messages.warning(request, 'Por favor, complete primeiro os dados pessoais.')
        return redirect('servicos:abrir_mei_passo1')
    
    if request.method == 'POST':
        form = DadosEmpresariaisForm(request.POST)
        if form.is_valid():
            # Recuperar dados da sessão
            dados_pessoais = request.session.get('dados_pessoais', {})
            
            # Criar a solicitação MEI
            try:
                solicitacao = SolicitacaoMEI.objects.create(
                    # Dados pessoais
                    nome_completo=dados_pessoais.get('nome_completo'),
                    cpf=dados_pessoais.get('cpf'),
                    rg=dados_pessoais.get('rg'),
                    orgao_expedidor=dados_pessoais.get('orgao_expedidor'),
                    estado_expedidor=dados_pessoais.get('estado_expedidor'),
                    email=dados_pessoais.get('email'),
                    telefone=dados_pessoais.get('telefone'),
                    
                    # Dados empresariais
                    cnae_primario=form.cleaned_data['cnae_primario'],
                    cnaes_secundarios=form.cleaned_data.get('cnae_secundario', ''),
                    forma_atuacao=form.cleaned_data['forma_atuacao'],
                    capital_inicial=form.cleaned_data['capital_inicial'],
                    
                    # Endereço
                    cep=form.cleaned_data['cep'].replace('-', ''),
                    cidade=form.cleaned_data['cidade'],
                    estado=form.cleaned_data['estado'],
                    rua=form.cleaned_data['rua'],
                    numero=form.cleaned_data['numero'],
                    bairro=form.cleaned_data['bairro'],
                    complemento=form.cleaned_data.get('complemento', ''),
                    
                    # Usuário (se logado)
                    usuario=request.user if request.user.is_authenticated else None,
                )
                
                # Limpar dados da sessão
                if 'dados_pessoais' in request.session:
                    del request.session['dados_pessoais']
                
                messages.success(request, 
                    f'Solicitação de abertura MEI enviada com sucesso! '
                    f'Protocolo: #{solicitacao.id}. '
                    'Nossa equipe entrará em contato em até 24 horas.')
                
                return redirect('servicos:abrir_mei_sucesso', protocolo=solicitacao.id)
                
            except Exception as e:
                messages.error(request, 'Erro ao processar sua solicitação. Tente novamente.')
                return redirect('servicos:abrir_mei_passo2')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Se há dados na sessão, pré-preenche o formulário
        form_data = request.session.get('dados_empresariais', {})
        form = DadosEmpresariaisForm(initial=form_data)
    
    # Recuperar dados pessoais para exibir resumo
    dados_pessoais = request.session.get('dados_pessoais', {})
    
    return render(request, 'servicos/abrir_mei_passo2.html', {
        'form': form,
        'dados_pessoais': dados_pessoais
    })

def abrir_mei_sucesso(request, protocolo):
    """Página de confirmação da solicitação"""
    try:
        solicitacao = get_object_or_404(SolicitacaoMEI, id=protocolo)
        return render(request, 'servicos/abrir_mei_sucesso.html', {
            'solicitacao': solicitacao
        })
    except:
        messages.error(request, 'Protocolo não encontrado.')
        return redirect('core:home')

def abrir_mei_voltar_passo1(request):
    """Permite voltar para o passo 1 mantendo os dados"""
    if request.method == 'POST' and 'dados_empresariais' in request.POST:
        # Salvar dados do passo 2 na sessão antes de voltar
        form = DadosEmpresariaisForm(request.POST)
        if form.is_valid():
            request.session['dados_empresariais'] = form.cleaned_data
    
    return redirect('servicos:abrir_mei_passo1')


class SolicitarServicoView(LoginRequiredMixin, CreateView):
    model = SolicitacaoServico
    template_name = 'servicos/solicitar.html'
    fields = ['observacoes']
    success_url = reverse_lazy('core:home')
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.servico = get_object_or_404(Servico, slug=self.kwargs['slug'])
        return super().form_valid(form)
