from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
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

def regularizar_mei_passo_1(request):
    """
    View para o primeiro passo da regularização do MEI.
    Coleta dados de contato: Nome Completo, E-mail e Telefone.
    """
    from django.contrib import messages
    from .forms import RegularizarMeiPasso1Form
    
    if request.method == 'POST':
        form = RegularizarMeiPasso1Form(request.POST)
        
        if form.is_valid():
            # Armazenar dados do passo 1 na sessão
            request.session['regularizar_mei_step1_data'] = form.cleaned_data
            
            # Mensagem de sucesso
            messages.success(
                request,
                '✅ Dados de contato salvos com sucesso! Agora preencha os dados do MEI.'
            )
            
            # Redirecionar para o passo 2
            return redirect('servicos:regularizar_mei_passo_2')
        
        else:
            # Mensagem de erro
            messages.error(
                request,
                '❌ Por favor, corrija os erros abaixo e tente novamente.'
            )
    
    else:
        form = RegularizarMeiPasso1Form()
    
    # Context para o template
    context = {
        'form': form,
        'breadcrumbs': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Regularizar MEI', 'url': None}
        ]
    }
    
    return render(request, 'servicos/regularizar_mei_passo1.html', context)


def regularizar_mei_passo_2(request):
    """
    View para o segundo passo da regularização do MEI.
    Coleta CPF, RG, CNPJ e endereço completo.
    """
    from django.contrib import messages
    from .forms import RegularizarMeiPasso2Form
    from .models import RegularizacaoMEI
    
    # Verificar se os dados do passo 1 existem na sessão
    dados_passo_1 = request.session.get('regularizar_mei_step1_data')
    if not dados_passo_1:
        messages.warning(
            request,
            '⚠️ Por favor, preencha primeiro os dados de contato.'
        )
        return redirect('servicos:regularizar_mei_passo_1')
    
    if request.method == 'POST':
        form = RegularizarMeiPasso2Form(request.POST)
        
        if form.is_valid():
            # Combinar dados do passo 1 com os dados do passo 2
            dados_completos = {**dados_passo_1, **form.cleaned_data}
            
            # Criar e salvar o objeto no banco de dados
            regularizacao = RegularizacaoMEI.objects.create(
                # Dados do passo 1
                nome_completo=dados_completos['nome_completo'],
                email=dados_completos['email'],
                telefone=dados_completos['telefone'],
                
                # Dados do passo 2
                cpf=dados_completos['cpf'],
                rg=dados_completos['rg'],
                cnpj=dados_completos['cnpj'],
                cep=dados_completos['cep'],
                rua=dados_completos['rua'],
                numero=dados_completos['numero'],
                complemento=dados_completos.get('complemento', ''),
                bairro=dados_completos['bairro'],
                cidade=dados_completos['cidade'],
                estado=dados_completos['estado'],
                observacoes=dados_completos.get('observacoes', ''),
                
                # Associar ao usuário logado, se houver
                usuario=request.user if request.user.is_authenticated else None
            )
            
            # Limpar dados da sessão
            if 'regularizar_mei_step1_data' in request.session:
                del request.session['regularizar_mei_step1_data']
            
            # Mensagem de sucesso
            messages.success(
                request,
                f'✅ Solicitação de regularização do MEI enviada com sucesso! '
                f'Protocolo: #{regularizacao.id}. '
                f'Em breve entraremos em contato.'
            )
            
            # Redirecionar para página de sucesso
            return redirect('servicos:regularizar_mei_sucesso', pk=regularizacao.id)
        
        else:
            # Mensagem de erro
            messages.error(
                request,
                '❌ Por favor, corrija os erros abaixo e tente novamente.'
            )
    
    else:
        form = RegularizarMeiPasso2Form()
    
    # Context para o template
    context = {
        'form': form,
        'dados_passo1': dados_passo_1,
        'breadcrumbs': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Regularizar MEI', 'url': '/servicos/regularizar-mei/'},
            {'name': 'Dados do MEI', 'url': None}
        ]
    }
    
    return render(request, 'servicos/regularizar_mei_passo2.html', context)


def regularizar_mei_sucesso(request, pk):
    """
    View para exibir a página de sucesso após a solicitação de regularização do MEI.
    """
    from django.shortcuts import get_object_or_404
    from .models import RegularizacaoMEI
    
    # Buscar a solicitação
    regularizacao = get_object_or_404(RegularizacaoMEI, pk=pk)
    
    # Context para o template
    context = {
        'regularizacao': regularizacao,
        'protocolo': regularizacao.id,
        'data_solicitacao': regularizacao.criado_em,
        'breadcrumbs': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Regularizar MEI', 'url': '/servicos/regularizar-mei/'},
            {'name': 'Sucesso', 'url': None}
        ]
    }
    
    return render(request, 'servicos/regularizar_mei_sucesso.html', context)

def declaracao_mei_passo_1(request):
    """Primeira etapa da Declaração MEI: dados de contato (nome, email, telefone)"""
    from .forms import DeclaracaoMeiPasso1Form
    
    if request.method == 'POST':
        form = DeclaracaoMeiPasso1Form(request.POST)
        if form.is_valid():
            # Armazenar os dados na sessão
            request.session['declaracao_mei_dados'] = form.cleaned_data
            return redirect('servicos:declaracao_mei_passo_2')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = DeclaracaoMeiPasso1Form()
    
    return render(request, 'servicos/declaracao_mei_passo1.html', {
        'form': form
    })


def declaracao_mei_passo_2(request):
    """Segunda etapa da Declaração MEI: CNPJ, CPF e endereço"""
    from .forms import DeclaracaoMeiPasso2Form
    from .models import SolicitacaoDeclaracaoMEI
    
    # Verificar se os dados do passo 1 existem na sessão
    if not request.session.get('declaracao_mei_dados'):
        messages.warning(request, 'Por favor, preencha primeiro os dados de contato.')
        return redirect('servicos:declaracao_mei_passo_1')
    
    if request.method == 'POST':
        form = DeclaracaoMeiPasso2Form(request.POST)
        if form.is_valid():
            try:
                # Recuperar dados do passo 1
                dados_passo1 = request.session['declaracao_mei_dados']
                
                # Combinar todos os dados
                dados_completos = {
                    # Dados do passo 1
                    'nome_completo': dados_passo1['nome_completo'],
                    'email': dados_passo1['email'],
                    'telefone': dados_passo1['telefone'],
                    # Dados do passo 2
                    'cnpj': form.cleaned_data['cnpj'],
                    'cpf': form.cleaned_data['cpf'],
                    'cep': form.cleaned_data['cep'],
                    'rua': form.cleaned_data['rua'],
                    'numero': form.cleaned_data['numero'],
                    'complemento': form.cleaned_data['complemento'],
                    'bairro': form.cleaned_data['bairro'],
                    'cidade': form.cleaned_data['cidade'],
                    'estado': form.cleaned_data['estado'],
                }
                
                # Criar solicitação no banco de dados
                solicitacao = SolicitacaoDeclaracaoMEI.objects.create(**dados_completos)
                
                # Definir usuário se logado
                if request.user.is_authenticated:
                    solicitacao.usuario = request.user
                    solicitacao.save()
                
                # Limpar sessão
                del request.session['declaracao_mei_dados']
                
                messages.success(request, f'Solicitação de Declaração MEI enviada com sucesso! Protocolo: {solicitacao.id}')
                return redirect('servicos:declaracao_mei_sucesso', protocolo=solicitacao.id)
                
            except Exception as e:
                messages.error(request, f'Erro ao processar solicitação: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = DeclaracaoMeiPasso2Form()
    
    # Recuperar dados do passo 1 para exibição
    dados_passo1 = request.session.get('declaracao_mei_dados', {})
    
    return render(request, 'servicos/declaracao_mei_passo2.html', {
        'form': form,
        'dados_passo1': dados_passo1
    })


def declaracao_mei_sucesso(request, protocolo):
    """Página de sucesso da Declaração MEI"""
    from .models import SolicitacaoDeclaracaoMEI
    
    try:
        solicitacao = SolicitacaoDeclaracaoMEI.objects.get(id=protocolo)
    except SolicitacaoDeclaracaoMEI.DoesNotExist:
        messages.error(request, 'Solicitação não encontrada.')
        return redirect('servicos:declaracao_mei_passo_1')
    
    return render(request, 'servicos/declaracao_mei_sucesso.html', {
        'solicitacao': solicitacao
    })


# View legada mantida para compatibilidade
def declaracao_mei(request):
    """Redireciona para o novo fluxo de declaração MEI"""
    return redirect('servicos:declaracao_mei_passo_1')

# Views para formulário MEI em duas etapas
from django.contrib import messages
from django.http import JsonResponse
from .models import SolicitacaoMEI
from .forms import AbrirMeiPasso1Form, AbrirMeiPasso2Form, DadosPessoaisForm, DadosEmpresariaisForm

def abrir_mei_passo1(request):
    """Primeira etapa: Dados básicos de contato (nome, telefone, email)"""
    if request.method == 'POST':
        form = AbrirMeiPasso1Form(request.POST)
        if form.is_valid():
            # Armazenar os dados na sessão
            dados_passo1 = form.cleaned_data.copy()
            # Limpar formatação do telefone para armazenamento
            dados_passo1['telefone'] = form.cleaned_data['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
            request.session['dados_passo1'] = dados_passo1
            return redirect('servicos:abrir_mei_passo2')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Se há dados na sessão, pré-preenche o formulário
        form_data = request.session.get('dados_passo1', {})
        form = AbrirMeiPasso1Form(initial=form_data)
    
    return render(request, 'servicos/abrir_mei_passo1.html', {'form': form})

def abrir_mei_passo2(request):
    """Segunda etapa: Dados de identificação + dados empresariais"""
    # Verifica se o usuário completou o passo 1
    if 'dados_passo1' not in request.session:
        messages.warning(request, 'Por favor, complete primeiro os dados básicos.')
        return redirect('servicos:abrir_mei_passo1')
    
    if request.method == 'POST':
        form = AbrirMeiPasso2Form(request.POST)
        if form.is_valid():
            # Recuperar dados do passo 1
            dados_passo1 = request.session.get('dados_passo1', {})
            
            # Criar a solicitação MEI
            try:
                solicitacao = SolicitacaoMEI.objects.create(
                    # Dados do passo 1
                    nome_completo=dados_passo1.get('nome_completo'),
                    email=dados_passo1.get('email'),
                    telefone=dados_passo1.get('telefone'),
                    
                    # Dados de identificação (passo 2)
                    cpf=form.cleaned_data['cpf'].replace('.', '').replace('-', ''),
                    rg=form.cleaned_data['rg'],
                    orgao_expedidor=form.cleaned_data['orgao_expedidor'],
                    estado_expedidor=form.cleaned_data['estado_expedidor'],
                    
                    # Dados empresariais (passo 2)
                    cnae_primario=form.cleaned_data['cnae_primario'],
                    cnaes_secundarios=form.cleaned_data.get('cnae_secundario', ''),
                    forma_atuacao=form.cleaned_data['forma_atuacao'],
                    capital_inicial=form.cleaned_data['capital_inicial'],
                    
                    # Endereço (passo 2)
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
                
                # Redirecionar para pagamento
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                
                # Preparar dados para pagamento
                request.session['pagamento_data'] = {
                    'solicitacao_id': solicitacao.id,
                    'tipo_servico': 'abrir_mei',
                    'nome_completo': solicitacao.nome_completo,
                    'email': solicitacao.email,
                    'telefone': solicitacao.telefone,
                }
                
                # Limpar dados da sessão dos passos
                if 'dados_passo1' in request.session:
                    del request.session['dados_passo1']
                if 'dados_passo2' in request.session:
                    del request.session['dados_passo2']
                
                # Redirecionar para pagamento
                return HttpResponseRedirect(
                    reverse('pagamentos:processar') + 
                    f'?solicitacao_id={solicitacao.id}&tipo_servico=abrir_mei'
                )
                
            except Exception as e:
                print(f"DEBUG - Erro ao criar solicitação: {e}")
                if 'cpf' in str(e).lower() and 'unique' in str(e).lower():
                    messages.error(request, 'Já existe uma solicitação com este CPF. Entre em contato conosco.')
                else:
                    messages.error(request, f'Erro ao processar sua solicitação: {e}')
                return redirect('servicos:abrir_mei_passo2')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        # Se há dados na sessão, pré-preenche o formulário
        form_data = request.session.get('dados_passo2', {})
        form = AbrirMeiPasso2Form(initial=form_data)
    
    # Recuperar dados do passo 1 para exibir resumo
    dados_passo1 = request.session.get('dados_passo1', {})
    
    return render(request, 'servicos/abrir_mei_passo2.html', {
        'form': form,
        'dados_passo1': dados_passo1
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
    if request.method == 'POST':
        # Salvar dados do passo 2 na sessão antes de voltar
        form = AbrirMeiPasso2Form(request.POST)
        if form.is_valid():
            request.session['dados_passo2'] = form.cleaned_data
    
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


def solicitar_baixa_mei(request):
    """
    View para solicitação de baixa do MEI.
    
    GET: Renderiza formulário em branco
    POST: Processa e valida os dados do formulário
    """
    from django.contrib import messages
    from .forms import SolicitacaoBaixaMEIForm
    
    if request.method == 'POST':
        form = SolicitacaoBaixaMEIForm(request.POST)
        
        if form.is_valid():
            # Salvar a solicitação
            solicitacao = form.save(commit=False)
            
            # Associar ao usuário logado, se houver
            if request.user.is_authenticated:
                solicitacao.usuario = request.user
            
            solicitacao.save()
            
            # Mensagem de sucesso
            messages.success(
                request,
                f'✅ Solicitação de baixa do MEI enviada com sucesso! '
                f'Protocolo: #{solicitacao.id}. '
                f'Em breve entraremos em contato.'
            )
            
            # Redirecionar para página de sucesso
            return redirect('servicos:baixa_mei_sucesso', pk=solicitacao.id)
        
        else:
            # Mensagem de erro
            messages.error(
                request,
                '❌ Por favor, corrija os erros abaixo e tente novamente.'
            )
    
    else:
        # GET: Formulário em branco
        form = SolicitacaoBaixaMEIForm()
    
    context = {
        'form': form,
        'title': 'Solicitar Baixa do MEI',
        'breadcrumb': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Baixar MEI', 'url': None}
        ]
    }
    
    return render(request, 'servicos/baixa_mei_form.html', context)


def baixa_mei_sucesso(request, pk):
    """
    View para página de sucesso após envio da solicitação.
    """
    from .models import SolicitacaoBaixaMEI
    
    solicitacao = get_object_or_404(SolicitacaoBaixaMEI, pk=pk)
    
    # Verificar se o usuário tem permissão para ver esta solicitação
    if request.user.is_authenticated and solicitacao.usuario != request.user:
        if not request.user.is_staff:
            return redirect('core:home')
    
    context = {
        'solicitacao': solicitacao,
        'title': 'Solicitação Enviada com Sucesso',
        'breadcrumb': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Baixar MEI', 'url': '/servicos/solicitar-baixa/'},
            {'name': 'Sucesso', 'url': None}
        ]
    }
    
    return render(request, 'servicos/baixa_mei_sucesso.html', context)


def baixar_mei_passo_1(request):
    """
    View para o primeiro passo da solicitação de baixa do MEI.
    Coleta dados de contato: Nome Completo, E-mail e Telefone.
    """
    from django.contrib import messages
    from .forms import BaixarMeiPasso1Form
    
    if request.method == 'POST':
        form = BaixarMeiPasso1Form(request.POST)
        
        if form.is_valid():
            # Armazenar dados do passo 1 na sessão
            request.session['baixar_mei_dados'] = form.cleaned_data
            
            # Mensagem de sucesso
            messages.success(
                request,
                '✅ Dados de contato salvos com sucesso! Agora preencha os dados do MEI.'
            )
            
            # Redirecionar para o passo 2
            return redirect('servicos:baixar_mei_passo_2')
        
        else:
            # Mensagem de erro
            messages.error(
                request,
                '❌ Por favor, corrija os erros abaixo e tente novamente.'
            )
    
    else:
        form = BaixarMeiPasso1Form()
    
    # Context para o template
    context = {
        'form': form,
        'breadcrumbs': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Baixar MEI', 'url': None}
        ]
    }
    
    return render(request, 'servicos/baixar_mei_passo1.html', context)


def baixar_mei_passo_2(request):
    """
    View para o segundo passo da solicitação de baixa do MEI.
    Coleta CNPJ, Nome Fantasia, CPF, RG, Data de Nascimento, Nome da Mãe e Endereço.
    """
    from django.contrib import messages
    from .forms import BaixarMeiPasso2Form
    from .models import SolicitacaoBaixaMEI
    
    # Verificar se os dados do passo 1 existem na sessão
    dados_passo_1 = request.session.get('baixar_mei_dados')
    if not dados_passo_1:
        messages.warning(
            request,
            '⚠️ Por favor, preencha primeiro os dados de contato.'
        )
        return redirect('servicos:baixar_mei_passo_1')
    
    if request.method == 'POST':
        form = BaixarMeiPasso2Form(request.POST)
        
        if form.is_valid():
            # Combinar dados do passo 1 com os dados do passo 2
            dados_completos = {**dados_passo_1, **form.cleaned_data}
            
            # Criar e salvar o objeto no banco de dados
            solicitacao = SolicitacaoBaixaMEI.objects.create(
                # Dados do passo 1
                nome_completo=dados_completos['nome_completo'],
                email=dados_completos['email'],
                telefone=dados_completos['telefone'],
                
                # Dados do passo 2
                cnpj_mei=dados_completos['cnpj_mei'],
                nome_fantasia=dados_completos['nome_fantasia'],
                cpf=dados_completos['cpf'],
                rg=dados_completos['rg'],
                orgao_emissor=dados_completos['orgao_emissor'],
                data_nascimento=dados_completos['data_nascimento'],
                nome_mae=dados_completos['nome_mae'],
                cep=dados_completos['cep'],
                rua=dados_completos['rua'],
                numero=dados_completos['numero'],
                complemento=dados_completos.get('complemento', ''),
                bairro=dados_completos['bairro'],
                cidade=dados_completos['cidade'],
                estado=dados_completos['estado'],
                observacoes=dados_completos.get('observacoes', ''),
                
                # Associar ao usuário logado, se houver
                usuario=request.user if request.user.is_authenticated else None
            )
            
            # Limpar dados da sessão
            if 'baixar_mei_dados' in request.session:
                del request.session['baixar_mei_dados']
            
            # Mensagem de sucesso
            messages.success(
                request,
                f'✅ Solicitação de baixa do MEI enviada com sucesso! '
                f'Protocolo: #{solicitacao.id}. '
                f'Em breve entraremos em contato.'
            )
            
            # Redirecionar para página de sucesso
            return redirect('servicos:baixar_mei_sucesso', pk=solicitacao.id)
        
        else:
            # Mensagem de erro
            messages.error(
                request,
                '❌ Por favor, corrija os erros abaixo e tente novamente.'
            )
    
    else:
        form = BaixarMeiPasso2Form()
    
    # Context para o template
    context = {
        'form': form,
        'dados_passo1': dados_passo_1,
        'breadcrumbs': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Baixar MEI', 'url': '/servicos/baixar-mei/'},
            {'name': 'Dados do MEI', 'url': None}
        ]
    }
    
    return render(request, 'servicos/baixar_mei_passo2.html', context)


def baixar_mei_sucesso(request, pk):
    """
    View para exibir a página de sucesso após a solicitação de baixa do MEI.
    """
    from django.shortcuts import get_object_or_404
    from .models import SolicitacaoBaixaMEI
    
    # Buscar a solicitação
    solicitacao = get_object_or_404(SolicitacaoBaixaMEI, pk=pk)
    
    # Context para o template
    context = {
        'solicitacao': solicitacao,
        'protocolo': solicitacao.id,
        'data_solicitacao': solicitacao.criado_em,
        'breadcrumbs': [
            {'name': 'Início', 'url': '/'},
            {'name': 'Serviços', 'url': '/servicos/'},
            {'name': 'Baixar MEI', 'url': '/servicos/baixar-mei/'},
            {'name': 'Sucesso', 'url': None}
        ]
    }
    
    return render(request, 'servicos/baixar_mei_sucesso.html', context)
