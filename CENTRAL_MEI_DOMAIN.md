# 🌐 CENTRAL MEI - CONFIGURAÇÃO PARA centralmeumei.com.br

## ✅ DOMÍNIO CONFIGURADO

### 🔧 **Configurações Aplicadas:**

**Arquivo .env atualizado com:**
```env
# Hosts permitidos
ALLOWED_HOSTS=localhost,127.0.0.1,centralmeumei.com.br,www.centralmeumei.com.br

# URLs Mercado Pago
MERCADOPAGO_SUCCESS_URL=https://centralmeumei.com.br/pagamentos/sucesso/
MERCADOPAGO_FAILURE_URL=https://centralmeumei.com.br/pagamentos/erro/
MERCADOPAGO_PENDING_URL=https://centralmeumei.com.br/pagamentos/pendente/

# Produção
DEBUG=False
```

### 🚀 **URLs do Sistema:**

- **Site Principal:** https://centralmeumei.com.br/
- **Admin:** https://centralmeumei.com.br/admin/
- **Abertura MEI:** https://centralmeumei.com.br/servicos/abrir-mei/
- **Checkout:** https://centralmeumei.com.br/pagamentos/checkout/[ID]/

### 🔒 **Configurações de Segurança:**

- ✅ HTTPS obrigatório (SSL configurado)
- ✅ DEBUG=False em produção
- ✅ ALLOWED_HOSTS restrito ao domínio
- ✅ Credenciais Mercado Pago de produção

### 💳 **Fluxo de Pagamento:**

1. **Cliente acessa:** https://centralmeumei.com.br/servicos/abrir-mei/
2. **Preenche dados** → Sistema cria pagamento
3. **Checkout transparente** → Mercado Pago processa
4. **Retorno automático** → Sucesso/Erro/Pendente

### 📋 **Checklist Final:**

- [x] Domínio configurado no .env
- [x] URLs Mercado Pago atualizadas
- [x] HTTPS configurado
- [x] DEBUG=False
- [ ] Servidor configurado com SSL
- [ ] DNS apontando para servidor
- [ ] python manage.py collectstatic executado
- [ ] python manage.py migrate executado

### 🎯 **Para Testar:**

1. Acesse: https://centralmeumei.com.br/servicos/abrir-mei/
2. Preencha o formulário de abertura MEI
3. Proceda com o pagamento no checkout transparente
4. Verifique o retorno após pagamento

---
**Status:** 🟢 CONFIGURADO PARA centralmeumei.com.br