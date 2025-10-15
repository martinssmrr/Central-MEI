# Central MEI - Sistema de Contabilidade MEI

Sistema web completo desenvolvido em Django para gestão de serviços contábeis para Microempreendedores Individuais (MEI).

## 🚀 Funcionalidades

### Principais Serviços MEI
- ✅ Abrir MEI
- ✅ Regularizar MEI
- ✅ Declaração Anual MEI (DASN-SIMEI)
- ✅ Baixar MEI
- ✅ Alteração MEI
- ✅ Inscrição Estadual
- ✅ Parcelamento MEI
- ✅ Certificado MEI (CCMEI)
- ✅ Desenquadramento MEI
- ✅ Reenquadramento MEI
- ✅ Nota Fiscal
- ✅ Buscar MEI pelo CPF
- ✅ Certidão Negativa de Débitos
- ✅ Situação MEI
- ✅ Alvará de Funcionamento
- ✅ Dívidas MEI
- ✅ Licença Maternidade
- ✅ Extrato CNPJ MEI
- ✅ Certidão Negativa de FGTS
- ✅ Certidão Negativa de Débitos Trabalhistas
- ✅ Certidão de INSS
- ✅ Aposentadoria MEI
- ✅ Certificado Digital

### Sistema Completo
- 🏠 **Homepage** com seção hero, cards de serviços e depoimentos
- 📋 **Sistema de Planos** (Basic, Standard, Premium)
- 📰 **Blog** para conteúdo educativo
- 💬 **Sistema de Depoimentos**
- 💳 **Integração com Mercado Pago**
- 🎨 **Design Responsivo** com Bootstrap 5
- 👤 **Sistema de Usuários**
- 🛠️ **Painel Administrativo** Django

## 🛠️ Tecnologias Utilizadas

- **Backend:** Django 4.2.7
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Pagamentos:** Mercado Pago SDK
- **Formulários:** Django Crispy Forms
- **Imagens:** Pillow

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- pip
- Git

### Passo a passo

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/central-mei.git
cd central-mei
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**

Windows:
```bash
venv\\Scripts\\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Configure o banco de dados**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

7. **Execute o servidor de desenvolvimento**
```bash
python manage.py runserver
```

8. **Acesse o sistema**
- Frontend: http://localhost:8000/
- Admin: http://localhost:8000/admin/

## ⚙️ Configuração

### Mercado Pago

1. Crie uma conta no [Mercado Pago Developers](https://www.mercadopago.com.br/developers)

2. Obtenha suas credenciais de teste e produção

3. Configure no arquivo `central_mei/mercadopago_settings.py`:

```python
# Configurações do Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = 'SEU_ACCESS_TOKEN_AQUI'
MERCADOPAGO_PUBLIC_KEY = 'SEU_PUBLIC_KEY_AQUI'

# URLs de retorno (configurar conforme seu domínio)
MERCADOPAGO_SUCCESS_URL = 'https://seudominio.com/pagamento/sucesso/'
MERCADOPAGO_FAILURE_URL = 'https://seudominio.com/pagamento/erro/'
MERCADOPAGO_PENDING_URL = 'https://seudominio.com/pagamento/pendente/'
```

### Arquivos Estáticos e Media

Os arquivos estáticos estão configurados para desenvolvimento. Para produção, configure um servidor de arquivos estáticos (nginx, Apache, AWS S3, etc.).

## 📁 Estrutura do Projeto

```
central_mei/
├── central_mei/          # Configurações do projeto
├── core/                 # App principal (homepage)
├── servicos/             # App de serviços MEI
├── planos/              # App de planos de assinatura
├── blog/                # App do blog
├── depoimentos/         # App de depoimentos
├── usuarios/            # App de usuários
├── templates/           # Templates HTML
├── static/              # Arquivos estáticos (CSS, JS, imagens)
├── media/               # Uploads de usuários
└── requirements.txt     # Dependências Python
```

### Apps Modulares

- **core**: Homepage, navegação principal
- **servicos**: Todos os serviços MEI, formulários, pagamentos
- **planos**: Sistema de assinatura mensal
- **blog**: Sistema de conteúdo educativo
- **depoimentos**: Sistema de avaliações de clientes
- **usuarios**: Gestão de usuários e perfis

## 🎨 Design e UX

- **Design Responsivo**: Funciona perfeitamente em desktop, tablet e mobile
- **Bootstrap 5**: Framework CSS moderno e componentes reutilizáveis
- **UX Otimizada**: Navegação intuitiva e formulários simples
- **Acessibilidade**: HTML semântico e boas práticas de acessibilidade
- **Performance**: Otimizado para carregamento rápido

## 🔐 Segurança

- Proteção CSRF habilitada
- Validação de formulários server-side
- Sanitização de dados de entrada
- Configurações de segurança Django

## 📱 Páginas Principais

### Homepage (`/`)
- Hero section com imagem de fundo
- Cards dos 3 principais serviços
- Seção de depoimentos
- Posts recentes do blog
- Call-to-action

### Serviços (`/servicos/`)
- Lista completa de todos os serviços
- Filtros e busca
- Páginas detalhadas para cada serviço
- Formulários de contratação

### Planos (`/planos/`)
- 3 planos de assinatura
- Comparativo de funcionalidades
- Integração com pagamentos

### Blog (`/blog/`)
- Listagem de posts
- Páginas de detalhe
- Sistema de categorias
- Gerenciamento via admin

## 🛡️ Administração

O Django Admin está configurado para gerenciar:

- ✅ Posts do blog
- ✅ Serviços MEI
- ✅ Depoimentos de clientes
- ✅ Planos de assinatura
- ✅ Solicitações de serviços
- ✅ Usuários do sistema

Acesse: `http://localhost:8000/admin/`

## 🚀 Próximos Passos

- [ ] Implementar sistema completo de pagamentos
- [ ] Adicionar dashboard do cliente
- [ ] Sistema de notificações por email
- [ ] API REST para integrações
- [ ] Sistema de chat/suporte
- [ ] Módulo de relatórios
- [ ] Integração com contadores

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua funcionalidade (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte, envie um email para contato@centralmei.com ou crie uma issue no repositório.

---

**Central MEI** - Simplificando a contabilidade para microempreendedores! 🚀