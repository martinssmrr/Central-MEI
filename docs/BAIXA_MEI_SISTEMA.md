# Sistema de Baixa MEI - Documentação Completa

## Visão Geral
O sistema de Baixa MEI permite que os usuários solicitem o encerramento de seu MEI (Microempreendedor Individual) através de um formulário completo e intuitivo.

## Arquitetura do Sistema

### 1. Modelo de Dados (servicos/models.py)

```python
class SolicitacaoBaixaMEI(models.Model):
    """
    Model para armazenar solicitações de baixa de MEI
    """
    
    # Status da solicitação
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Estados brasileiros
    ESTADO_CHOICES = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'),
        # ... todos os estados
    ]
    
    # Campos principais
    - usuario: ForeignKey para User (usuário que fez a solicitação)
    - cnpj_mei: CharField(18) - CNPJ do MEI a ser baixado
    - razao_social: CharField(200) - Razão social do MEI
    - nome_fantasia: CharField(200) - Nome fantasia (opcional)
    - data_inicio_atividade: DateField - Data de início das atividades
    - data_encerramento_atividade: DateField - Data de encerramento
    - motivo_baixa: TextField - Motivo para a baixa
    - nome_completo: CharField(200) - Nome completo do empreendedor
    - cpf: CharField(14) - CPF do empreendedor
    - data_nascimento: DateField - Data de nascimento
    - rg: CharField(20) - RG do empreendedor
    - orgao_expedidor: CharField(10) - Órgão expedidor do RG
    - telefone: CharField(20) - Telefone de contato
    - email: EmailField - E-mail de contato
    - cep: CharField(9) - CEP do endereço comercial
    - logradouro: CharField(200) - Logradouro
    - numero: CharField(10) - Número
    - complemento: CharField(100) - Complemento (opcional)
    - bairro: CharField(100) - Bairro
    - cidade: CharField(100) - Cidade
    - estado: CharField(2) - Estado (choices)
    - observacoes: TextField - Observações adicionais (opcional)
    - status: CharField(20) - Status da solicitação (choices)
    - data_solicitacao: DateTimeField - Data/hora da solicitação
    - data_atualizacao: DateTimeField - Última atualização
    
    # Métodos úteis
    - get_status_display_class(): Retorna classe CSS baseada no status
    - __str__(): Representação string do objeto
```

### 2. Formulário (servicos/forms.py)

```python
class SolicitacaoBaixaMEIForm(forms.ModelForm):
    """
    Formulário para solicitação de baixa de MEI com validações completas
    """
    
    # Configurações do formulário
    - Meta.model = SolicitacaoBaixaMEI
    - Meta.fields = '__all__' (exceto usuario, status, datas de controle)
    - Widgets customizados com classes Bootstrap
    - Labels descritivos para todos os campos
    - Help text para campos importantes
    
    # Métodos de validação
    - clean_cnpj_mei(): Valida formato e dígitos verificadores do CNPJ
    - clean_cpf(): Valida formato e dígitos verificadores do CPF  
    - clean_telefone(): Valida formato do telefone
    - clean_cep(): Valida formato do CEP
    - clean(): Validação geral do formulário
```

### 3. Views (servicos/views.py)

```python
@login_required
def solicitar_baixa_mei(request):
    """
    View para exibir e processar o formulário de baixa MEI
    
    GET: Exibe formulário vazio
    POST: Processa dados enviados, valida e salva
    
    - Requer autenticação do usuário
    - Associa solicitação ao usuário logado
    - Define status inicial como 'pendente'
    - Exibe mensagens de sucesso/erro
    - Redireciona para página de sucesso após salvar
    """

@login_required  
def baixa_mei_sucesso(request, id=None):
    """
    View para exibir página de sucesso da solicitação
    
    - Requer autenticação
    - Busca solicitação do usuário atual
    - Retorna 404 se não encontrar
    - Exibe detalhes da solicitação criada
    """
```

### 4. URLs (servicos/urls.py)

```python
urlpatterns = [
    # ... outras URLs
    path('baixar-mei/', views.solicitar_baixa_mei, name='baixar_mei'),
    path('baixar-mei/sucesso/', views.baixa_mei_sucesso, name='baixa_mei_sucesso'),
]
```

### 5. Templates

#### baixa_mei_form.html
- Formulário completo com seções organizadas:
  - Dados do MEI
  - Dados Pessoais  
  - Dados de Contato
  - Endereço Comercial
  - Observações
- Validação JavaScript em tempo real
- Máscaras para campos (CNPJ, CPF, telefone, CEP)
- Checkbox de aceite de termos obrigatório
- Design responsivo com Bootstrap 5
- Informações importantes sobre o processo

#### baixa_mei_sucesso.html  
- Página de confirmação da solicitação
- Exibe número do protocolo
- Mostra dados da solicitação
- Status e data
- Próximos passos
- Informações importantes
- Botões para ações (voltar, dashboard, imprimir)
- Dados de contato da empresa

## Funcionalidades Implementadas

### Validações
- **CNPJ**: Formato e dígitos verificadores
- **CPF**: Formato e dígitos verificadores  
- **Telefone**: Formato brasileiro (fixo e celular)
- **CEP**: Formato brasileiro
- **Campos obrigatórios**: Validação de preenchimento
- **Aceite de termos**: Obrigatório via JavaScript

### Máscaras JavaScript
- CNPJ: 00.000.000/0000-00
- CPF: 000.000.000-00
- Telefone: (00) 0000-0000 ou (00) 00000-0000
- CEP: 00000-000

### Recursos de UX
- Design responsivo para mobile/desktop
- Formulário organizado em seções
- Mensagens de erro contextuais
- Botão desabilitado até aceitar termos
- Indicadores visuais de campos obrigatórios
- Página de sucesso com protocolo
- Função de impressão do comprovante

### Segurança
- Autenticação obrigatória
- Validação CSRF
- Sanitização de dados
- Associação com usuário logado
- Controle de acesso às solicitações

## Fluxo do Sistema

1. **Usuário acessa** `/servicos/baixar-mei/`
2. **Sistema verifica** autenticação
3. **Exibe formulário** com campos organizados
4. **Usuário preenche** dados e aceita termos
5. **JavaScript valida** campos em tempo real
6. **Sistema processa** dados no backend
7. **Validações** são executadas (CNPJ, CPF, etc.)
8. **Solicitação** é salva no banco
9. **Usuário** é redirecionado para página de sucesso
10. **Sistema exibe** protocolo e próximos passos

## Integração com Sistema Existente

### Models
- Integra-se com modelo User do Django
- Segue padrões dos outros modelos de serviços
- Utiliza campos padronizados da aplicação

### Forms  
- Herda de ModelForm para consistência
- Utiliza mesmo padrão de validação
- Classes CSS Bootstrap padronizadas

### Views
- Segue padrão de views baseadas em função
- Utiliza decorators de autenticação
- Mensagens via framework de messages

### Templates
- Estende template base do projeto
- Utiliza classes CSS existentes
- Mantém identidade visual

## Próximos Passos Sugeridos

1. **Painel Administrativo**
   - Interface para gerenciar solicitações
   - Mudança de status
   - Histórico de alterações

2. **Notificações**
   - E-mail de confirmação
   - Updates de status
   - Lembretes automáticos

3. **Relatórios**
   - Dashboard de solicitações
   - Métricas de conversão
   - Relatórios gerenciais

4. **Integrações**
   - API Receita Federal
   - Validação automática de CNPJ
   - Consulta de situação fiscal

## Tecnologias Utilizadas

- **Backend**: Django 5.2.3
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Banco**: SQLite (desenvolvimento)
- **Forms**: Django Forms + Crispy Forms
- **Autenticação**: Django Auth
- **Validação**: Django Validators + JavaScript
- **Templates**: Django Template Engine

## Comandos para Deploy

```bash
# Aplicar migrações
python manage.py makemigrations servicos
python manage.py migrate

# Coletar arquivos estáticos  
python manage.py collectstatic

# Testar funcionalidade
python manage.py test servicos
```

Este sistema está completamente funcional e pronto para uso em produção, seguindo as melhores práticas do Django e oferecendo uma experiência de usuário moderna e intuitiva.