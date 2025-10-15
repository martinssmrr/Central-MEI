from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.core.paginator import Paginator

from .models import (
    CategoriaPlanoContas, 
    SubcategoriaPlanoContas, 
    Produto, 
    Venda, 
    MovimentacaoCaixa, 
    SaldoCaixa
)
from .forms import (
    VendaForm, 
    MovimentacaoCaixaForm, 
    ProdutoForm,
    CategoriaPlanoContasForm,
    SubcategoriaPlanoContasForm,
    RelatorioForm
)

def is_staff_user(user):
    """Verifica se o usuário é da equipe (staff)"""
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def dashboard_home(request):
    """Dashboard principal"""
    hoje = timezone.now().date()
    mes_atual = hoje.replace(day=1)
    
    # Estatísticas do mês atual
    vendas_mes = Venda.objects.filter(
        data_venda__gte=mes_atual,
        status='pago'
    )
    
    total_vendas_mes = vendas_mes.aggregate(
        total=Sum('valor_final')
    )['total'] or Decimal('0')
    
    qtd_vendas_mes = vendas_mes.count()
    
    # Movimentações do mês
    movimentacoes_mes = MovimentacaoCaixa.objects.filter(
        data_movimentacao__gte=mes_atual
    )
    
    entradas_mes = movimentacoes_mes.filter(tipo='entrada').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0')
    
    saidas_mes = movimentacoes_mes.filter(tipo='saida').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0')
    
    # Vendas por produto (top 5)
    produtos_mais_vendidos = Produto.objects.annotate(
        total_vendas=Count('vendas')
    ).filter(total_vendas__gt=0).order_by('-total_vendas')[:5]
    
    # Últimas movimentações
    ultimas_movimentacoes = MovimentacaoCaixa.objects.select_related(
        'subcategoria', 'usuario'
    )[:10]
    
    # Saldo atual
    try:
        saldo_atual = SaldoCaixa.objects.latest('data')
    except SaldoCaixa.DoesNotExist:
        saldo_atual = None
    
    context = {
        'total_vendas_mes': total_vendas_mes,
        'qtd_vendas_mes': qtd_vendas_mes,
        'entradas_mes': entradas_mes,
        'saidas_mes': saidas_mes,
        'saldo_mes': entradas_mes - saidas_mes,
        'produtos_mais_vendidos': produtos_mais_vendidos,
        'ultimas_movimentacoes': ultimas_movimentacoes,
        'saldo_atual': saldo_atual,
        'hoje': hoje,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(is_staff_user)
def vendas_list(request):
    """Lista de vendas com filtros"""
    vendas = Venda.objects.select_related('produto', 'vendedor').order_by('-data_venda')
    
    # Filtros
    status_filter = request.GET.get('status')
    produto_filter = request.GET.get('produto')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if status_filter:
        vendas = vendas.filter(status=status_filter)
    
    if produto_filter:
        vendas = vendas.filter(produto_id=produto_filter)
    
    if data_inicio:
        vendas = vendas.filter(data_venda__gte=data_inicio)
    
    if data_fim:
        vendas = vendas.filter(data_venda__lte=data_fim)
    
    # Paginação
    paginator = Paginator(vendas, 20)
    page = request.GET.get('page')
    vendas_page = paginator.get_page(page)
    
    # Para os filtros
    produtos = Produto.objects.filter(ativo=True)
    
    context = {
        'vendas': vendas_page,
        'produtos': produtos,
        'status_choices': Venda.STATUS_CHOICES,
        'filtros': {
            'status': status_filter,
            'produto': produto_filter,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    }
    
    return render(request, 'dashboard/vendas_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def venda_create(request):
    """Criar nova venda"""
    if request.method == 'POST':
        form = VendaForm(request.POST)
        if form.is_valid():
            venda = form.save(commit=False)
            venda.vendedor = request.user
            venda.save()
            
            # Se a venda foi paga, criar movimentação no caixa
            if venda.status == 'pago':
                criar_movimentacao_venda(venda)
            
            messages.success(request, 'Venda criada com sucesso!')
            return redirect('dashboard:vendas_list')
    else:
        form = VendaForm()
    
    return render(request, 'dashboard/venda_form.html', {'form': form, 'title': 'Nova Venda'})

@login_required
@user_passes_test(is_staff_user)
def movimentacoes_list(request):
    """Lista de movimentações do caixa"""
    movimentacoes = MovimentacaoCaixa.objects.select_related(
        'subcategoria', 'usuario'
    ).order_by('-data_movimentacao')
    
    # Filtros
    tipo_filter = request.GET.get('tipo')
    categoria_filter = request.GET.get('categoria')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if tipo_filter:
        movimentacoes = movimentacoes.filter(tipo=tipo_filter)
    
    if categoria_filter:
        movimentacoes = movimentacoes.filter(subcategoria__categoria_id=categoria_filter)
    
    if data_inicio:
        movimentacoes = movimentacoes.filter(data_movimentacao__gte=data_inicio)
    
    if data_fim:
        movimentacoes = movimentacoes.filter(data_movimentacao__lte=data_fim)
    
    # Paginação
    paginator = Paginator(movimentacoes, 20)
    page = request.GET.get('page')
    movimentacoes_page = paginator.get_page(page)
    
    # Para os filtros
    categorias = CategoriaPlanoContas.objects.filter(ativo=True)
    
    context = {
        'movimentacoes': movimentacoes_page,
        'categorias': categorias,
        'tipo_choices': MovimentacaoCaixa.TIPO_CHOICES,
        'filtros': {
            'tipo': tipo_filter,
            'categoria': categoria_filter,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        }
    }
    
    return render(request, 'dashboard/movimentacoes_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def movimentacao_create(request):
    """Criar nova movimentação"""
    if request.method == 'POST':
        form = MovimentacaoCaixaForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user
            movimentacao.save()
            
            # Atualizar saldo do caixa
            atualizar_saldo_caixa(movimentacao.data_movimentacao.date())
            
            messages.success(request, 'Movimentação criada com sucesso!')
            return redirect('dashboard:movimentacoes_list')
    else:
        form = MovimentacaoCaixaForm()
    
    return render(request, 'dashboard/movimentacao_form.html', {'form': form, 'title': 'Nova Movimentação'})

def criar_movimentacao_venda(venda):
    """Cria movimentação no caixa quando uma venda é paga"""
    MovimentacaoCaixa.objects.create(
        tipo='entrada',
        subcategoria=venda.produto.categoria,
        descricao=f"Venda #{venda.id} - {venda.produto.nome} - {venda.cliente_nome}",
        valor=venda.valor_final,
        data_movimentacao=venda.data_pagamento or timezone.now(),
        usuario=venda.vendedor,
        venda=venda
    )
    
    # Atualizar saldo do caixa
    data_movimentacao = venda.data_pagamento.date() if venda.data_pagamento else timezone.now().date()
    atualizar_saldo_caixa(data_movimentacao)

def atualizar_saldo_caixa(data):
    """Atualiza o saldo do caixa para uma data específica"""
    movimentacoes = MovimentacaoCaixa.objects.filter(data_movimentacao__date=data)
    
    total_entradas = movimentacoes.filter(tipo='entrada').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0')
    
    total_saidas = movimentacoes.filter(tipo='saida').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0')
    
    # Buscar saldo anterior
    try:
        saldo_anterior = SaldoCaixa.objects.filter(data__lt=data).latest('data')
        saldo_inicial = saldo_anterior.saldo_final
    except SaldoCaixa.DoesNotExist:
        saldo_inicial = Decimal('0')
    
    # Criar ou atualizar saldo do dia
    saldo, created = SaldoCaixa.objects.get_or_create(
        data=data,
        defaults={
            'saldo_inicial': saldo_inicial,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
        }
    )
    
    if not created:
        saldo.total_entradas = total_entradas
        saldo.total_saidas = total_saidas
    
    saldo.calcular_saldo()
    saldo.save()

@login_required
@user_passes_test(is_staff_user)
def get_subcategorias(request):
    """AJAX - Retorna subcategorias de uma categoria"""
    categoria_id = request.GET.get('categoria_id')
    subcategorias = SubcategoriaPlanoContas.objects.filter(
        categoria_id=categoria_id,
        ativo=True
    ).values('id', 'nome')
    
    return JsonResponse(list(subcategorias), safe=False)

@login_required
@user_passes_test(is_staff_user)
def get_categorias_por_tipo(request):
    """AJAX - Retorna categorias filtradas por tipo"""
    tipo = request.GET.get('tipo')
    categorias = CategoriaPlanoContas.objects.filter(
        tipo=tipo,
        ativo=True
    ).values('id', 'nome')
    
    return JsonResponse(list(categorias), safe=False)

# Views para Movimentações Financeiras
@login_required
@user_passes_test(is_staff_user)
def movimentacoes_list(request):
    """Lista todas as movimentações financeiras"""
    movimentacoes = MovimentacaoCaixa.objects.all().order_by('-data_movimentacao')
    
    # Filtros
    tipo_filter = request.GET.get('tipo')
    categoria_filter = request.GET.get('categoria')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    order = request.GET.get('order', '-data_movimentacao')
    
    if tipo_filter:
        movimentacoes = movimentacoes.filter(tipo=tipo_filter)
    
    if categoria_filter:
        movimentacoes = movimentacoes.filter(categoria_id=categoria_filter)
    
    if data_inicio:
        movimentacoes = movimentacoes.filter(data_movimentacao__date__gte=data_inicio)
    
    if data_fim:
        movimentacoes = movimentacoes.filter(data_movimentacao__date__lte=data_fim)
    
    # Ordenação
    if order:
        movimentacoes = movimentacoes.order_by(order)
    
    # Calcular totais
    total_entradas = movimentacoes.filter(tipo='entrada').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0')
    
    total_saidas = movimentacoes.filter(tipo='saida').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0')
    
    saldo = total_entradas - total_saidas
    
    # Paginação
    paginator = Paginator(movimentacoes, 25)
    page = request.GET.get('page')
    movimentacoes_page = paginator.get_page(page)
    
    # Para os filtros
    categorias = CategoriaPlanoContas.objects.filter(ativo=True)
    
    context = {
        'title': 'Movimentações Financeiras',
        'movimentacoes': movimentacoes_page,
        'categorias': categorias,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo': saldo,
    }
    
    return render(request, 'dashboard/movimentacoes_list.html', context)

@login_required
@user_passes_test(is_staff_user)
def movimentacao_create(request):
    """Criar nova movimentação financeira"""
    if request.method == 'POST':
        form = MovimentacaoCaixaForm(request.POST)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user
            movimentacao.save()
            
            # Atualizar saldo do caixa
            atualizar_saldo_caixa(movimentacao.data_movimentacao.date())
            
            messages.success(request, 'Movimentação cadastrada com sucesso!')
            return redirect('dashboard:movimentacoes_list')
        else:
            messages.error(request, 'Erro ao cadastrar movimentação. Verifique os dados.')
    else:
        form = MovimentacaoCaixaForm()
    
    context = {
        'title': 'Nova Movimentação',
        'form': form
    }
    
    return render(request, 'dashboard/movimentacao_form.html', context)

@login_required
@user_passes_test(is_staff_user)
def movimentacao_update(request, pk):
    """Editar movimentação financeira"""
    movimentacao = get_object_or_404(MovimentacaoCaixa, pk=pk)
    data_original = movimentacao.data_movimentacao.date()
    
    if request.method == 'POST':
        form = MovimentacaoCaixaForm(request.POST, instance=movimentacao)
        if form.is_valid():
            movimentacao_atualizada = form.save()
            
            # Atualizar saldo do caixa (data original e nova data se diferentes)
            atualizar_saldo_caixa(data_original)
            if movimentacao_atualizada.data_movimentacao.date() != data_original:
                atualizar_saldo_caixa(movimentacao_atualizada.data_movimentacao.date())
            
            messages.success(request, 'Movimentação atualizada com sucesso!')
            return redirect('dashboard:movimentacoes_list')
        else:
            messages.error(request, 'Erro ao atualizar movimentação. Verifique os dados.')
    else:
        form = MovimentacaoCaixaForm(instance=movimentacao)
    
    context = {
        'title': 'Editar Movimentação',
        'form': form,
        'movimentacao': movimentacao
    }
    
    return render(request, 'dashboard/movimentacao_form.html', context)

@login_required
@user_passes_test(is_staff_user)
def movimentacao_delete(request, pk):
    """Excluir movimentação financeira"""
    movimentacao = get_object_or_404(MovimentacaoCaixa, pk=pk)
    data = movimentacao.data_movimentacao.date()
    
    if request.method == 'POST':
        movimentacao.delete()
        
        # Atualizar saldo do caixa
        atualizar_saldo_caixa(data)
        
        messages.success(request, 'Movimentação excluída com sucesso!')
        return redirect('dashboard:movimentacoes_list')

# Views para Plano de Contas
@login_required
@user_passes_test(is_staff_user)
def plano_contas(request):
    """Plano de contas - gerenciar categorias e subcategorias"""
    categorias_entrada = CategoriaPlanoContas.objects.filter(tipo='entrada', ativo=True).prefetch_related('subcategorias')
    categorias_saida = CategoriaPlanoContas.objects.filter(tipo='saida', ativo=True).prefetch_related('subcategorias')
    todas_categorias = CategoriaPlanoContas.objects.filter(ativo=True)
    
    # Estatísticas
    total_subcategorias = SubcategoriaPlanoContas.objects.filter(ativo=True).count()
    
    # Categoria mais utilizada (baseada nas movimentações)
    categoria_mais_usada = MovimentacaoCaixa.objects.values('categoria__nome').annotate(
        count=Count('id')
    ).order_by('-count').first()
    
    if categoria_mais_usada:
        categoria_mais_usada = CategoriaPlanoContas.objects.get(nome=categoria_mais_usada['categoria__nome'])
    
    context = {
        'title': 'Plano de Contas',
        'categorias_entrada': categorias_entrada,
        'categorias_saida': categorias_saida,
        'todas_categorias': todas_categorias,
        'total_subcategorias': total_subcategorias,
        'categoria_mais_usada': categoria_mais_usada,
    }
    
    return render(request, 'dashboard/plano_contas.html', context)

@login_required
@user_passes_test(is_staff_user)
def categoria_create(request):
    """Criar nova categoria"""
    if request.method == 'POST':
        form = CategoriaPlanoContasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('dashboard:plano_contas')
        else:
            messages.error(request, 'Erro ao criar categoria. Verifique os dados.')
    
    return redirect('dashboard:plano_contas')

@login_required
@user_passes_test(is_staff_user)
def categoria_update(request, pk):
    """Atualizar categoria"""
    categoria = get_object_or_404(CategoriaPlanoContas, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaPlanoContasForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
        else:
            messages.error(request, 'Erro ao atualizar categoria. Verifique os dados.')
    
    return redirect('dashboard:plano_contas')

@login_required
@user_passes_test(is_staff_user)
def categoria_delete(request, pk):
    """Excluir categoria"""
    categoria = get_object_or_404(CategoriaPlanoContas, pk=pk)
    
    if request.method == 'POST':
        # Verificar se existem movimentações usando esta categoria
        if MovimentacaoCaixa.objects.filter(categoria=categoria).exists():
            messages.error(request, 'Não é possível excluir categoria que possui movimentações associadas.')
        else:
            categoria.delete()
            messages.success(request, 'Categoria excluída com sucesso!')
    
    return redirect('dashboard:plano_contas')

@login_required
@user_passes_test(is_staff_user)
def subcategoria_create(request):
    """Criar nova subcategoria"""
    if request.method == 'POST':
        form = SubcategoriaPlanoContasForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoria criada com sucesso!')
        else:
            messages.error(request, 'Erro ao criar subcategoria. Verifique os dados.')
    
    return redirect('dashboard:plano_contas')

@login_required
@user_passes_test(is_staff_user)
def subcategoria_update(request, pk):
    """Atualizar subcategoria"""
    subcategoria = get_object_or_404(SubcategoriaPlanoContas, pk=pk)
    
    if request.method == 'POST':
        form = SubcategoriaPlanoContasForm(request.POST, instance=subcategoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoria atualizada com sucesso!')
        else:
            messages.error(request, 'Erro ao atualizar subcategoria. Verifique os dados.')
    
    return redirect('dashboard:plano_contas')

@login_required
@user_passes_test(is_staff_user)
def subcategoria_delete(request, pk):
    """Excluir subcategoria"""
    subcategoria = get_object_or_404(SubcategoriaPlanoContas, pk=pk)
    
    if request.method == 'POST':
        # Verificar se existem movimentações usando esta subcategoria
        if MovimentacaoCaixa.objects.filter(subcategoria=subcategoria).exists():
            messages.error(request, 'Não é possível excluir subcategoria que possui movimentações associadas.')
        else:
            subcategoria.delete()
            messages.success(request, 'Subcategoria excluída com sucesso!')
    
    return redirect('dashboard:plano_contas')


def calcular_periodo(periodo_predefinido):
    """Calcula as datas de início e fim baseado no período pré-definido"""
    hoje = date.today()
    
    if periodo_predefinido == 'hoje':
        return hoje, hoje
    elif periodo_predefinido == 'ontem':
        ontem = hoje - timedelta(days=1)
        return ontem, ontem
    elif periodo_predefinido == 'esta_semana':
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        return inicio_semana, hoje
    elif periodo_predefinido == 'semana_passada':
        inicio_semana_passada = hoje - timedelta(days=hoje.weekday() + 7)
        fim_semana_passada = inicio_semana_passada + timedelta(days=6)
        return inicio_semana_passada, fim_semana_passada
    elif periodo_predefinido == 'este_mes':
        inicio_mes = hoje.replace(day=1)
        return inicio_mes, hoje
    elif periodo_predefinido == 'mes_passado':
        if hoje.month == 1:
            inicio_mes_passado = date(hoje.year - 1, 12, 1)
            fim_mes_passado = date(hoje.year, 1, 1) - timedelta(days=1)
        else:
            inicio_mes_passado = date(hoje.year, hoje.month - 1, 1)
            if hoje.month == 2:
                fim_mes_passado = date(hoje.year, hoje.month, 1) - timedelta(days=1)
            else:
                fim_mes_passado = date(hoje.year, hoje.month, 1) - timedelta(days=1)
        return inicio_mes_passado, fim_mes_passado
    elif periodo_predefinido == 'ultimos_7_dias':
        return hoje - timedelta(days=6), hoje
    elif periodo_predefinido == 'ultimos_30_dias':
        return hoje - timedelta(days=29), hoje
    elif periodo_predefinido == 'ultimos_90_dias':
        return hoje - timedelta(days=89), hoje
    
    return None, None


@login_required
@user_passes_test(is_staff_user)
def relatorios(request):
    """Página principal de relatórios financeiros"""
    form = RelatorioForm(request.GET or None)
    movimentacoes = None
    resumo = None
    periodo_texto = None
    
    if form.is_valid():
        # Construir query com filtros
        query = Q()
        
        # Filtro por tipo
        tipo = form.cleaned_data.get('tipo')
        if tipo:
            query &= Q(tipo=tipo)
        
        # Filtro por categoria
        categoria = form.cleaned_data.get('categoria')
        if categoria:
            query &= Q(categoria=categoria)
        
        # Filtro por subcategoria
        subcategoria = form.cleaned_data.get('subcategoria')
        if subcategoria:
            query &= Q(subcategoria=subcategoria)
        
        # Filtro por período
        periodo_predefinido = form.cleaned_data.get('periodo_predefinido')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        
        if periodo_predefinido:
            data_inicio, data_fim = calcular_periodo(periodo_predefinido)
            periodo_texto = dict(form.PERIODO_CHOICES)[periodo_predefinido]
        elif data_inicio or data_fim:
            if data_inicio and data_fim:
                periodo_texto = f"{data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}"
            elif data_inicio:
                periodo_texto = f"A partir de {data_inicio.strftime('%d/%m/%Y')}"
            elif data_fim:
                periodo_texto = f"Até {data_fim.strftime('%d/%m/%Y')}"
        
        if data_inicio:
            query &= Q(data_movimentacao__date__gte=data_inicio)
        
        if data_fim:
            query &= Q(data_movimentacao__date__lte=data_fim)
        
        # Buscar movimentações
        movimentacoes = MovimentacaoCaixa.objects.filter(query).select_related(
            'categoria', 'subcategoria', 'usuario'
        )
        
        # Ordenação
        ordenacao = form.cleaned_data.get('ordenacao', 'data_desc')
        if ordenacao == 'data_desc':
            movimentacoes = movimentacoes.order_by('-data_movimentacao')
        elif ordenacao == 'data_asc':
            movimentacoes = movimentacoes.order_by('data_movimentacao')
        elif ordenacao == 'valor_desc':
            movimentacoes = movimentacoes.order_by('-valor')
        elif ordenacao == 'valor_asc':
            movimentacoes = movimentacoes.order_by('valor')
        elif ordenacao == 'categoria':
            movimentacoes = movimentacoes.order_by('categoria__nome', 'subcategoria__nome')
        
        # Calcular resumo
        total_entradas = movimentacoes.filter(tipo='entrada').aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')
        
        total_saidas = movimentacoes.filter(tipo='saida').aggregate(
            total=Sum('valor')
        )['total'] or Decimal('0')
        
        saldo = total_entradas - total_saidas
        
        resumo = {
            'total_movimentacoes': movimentacoes.count(),
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo': saldo
        }
    
    context = {
        'title': 'Relatórios Financeiros',
        'form': form,
        'movimentacoes': movimentacoes,
        'resumo': resumo,
        'periodo_texto': periodo_texto,
    }
    
    return render(request, 'dashboard/relatorios.html', context)


@login_required
@user_passes_test(is_staff_user)
def relatorio_pdf(request):
    """Gera PDF do relatório financeiro - Funcionalidade em desenvolvimento"""
    messages.info(request, 'Funcionalidade de exportação PDF em desenvolvimento. Use a função de impressão por enquanto.')
    return redirect('dashboard:relatorios')
