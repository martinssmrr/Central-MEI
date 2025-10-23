# 🚀 CONFIGURAÇÕES PARA DEPLOY EM PRODUÇÃO

## ⚙️ Configurações Necessárias no .env

### 1. **Domínio e Hosts**
```env
# Central MEI - Domínio configurado
ALLOWED_HOSTS=localhost,127.0.0.1,centralmeumei.com.br,www.centralmeumei.com.br

# URLs do Mercado Pago - Central MEI
MERCADOPAGO_SUCCESS_URL=https://centralmeumei.com.br/pagamentos/sucesso/
MERCADOPAGO_FAILURE_URL=https://centralmeumei.com.br/pagamentos/erro/
MERCADOPAGO_PENDING_URL=https://centralmeumei.com.br/pagamentos/pendente/
```

### 2. **Segurança**
```env
DEBUG=False
SECRET_KEY=sua-chave-secreta-super-segura-aqui
```

### 3. **Banco de Dados (se usar PostgreSQL em produção)**
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=central_mei_db
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

## 🔐 Mercado Pago - Configuração de Produção

### Credenciais já configuradas:
- ✅ ACCESS_TOKEN: Produção (APP_USR-...)
- ✅ PUBLIC_KEY: Produção (APP_USR-...)
- ✅ Modo sandbox: DESABILITADO

### ⚠️ IMPORTANTE:
- As credenciais atuais são válidas para produção
- Checkout transparente configurado para ambiente real
- SSL obrigatório em produção (HTTPS)

## 📋 Checklist antes do Deploy

- [ ] Atualizar ALLOWED_HOSTS com domínio real
- [ ] Atualizar URLs do Mercado Pago com domínio real
- [ ] Configurar SSL/HTTPS no servidor
- [ ] Executar `python manage.py collectstatic`
- [ ] Executar `python manage.py migrate`
- [ ] Testar formulário de checkout em produção

## 🧪 Como Testar em Produção

1. **Acessar checkout:**
   ```
   https://centralmeumei.com.br/servicos/abrir-mei/
   ```

2. **Preencher formulário e proceder ao pagamento**

3. **Usar cartão de teste (se necessário):**
   - Cartão: 4509 9535 6623 3704
   - Vencimento: 11/25
   - CVV: 123
   - Nome: APRO (aprovado)

## 🔧 Comandos de Deploy

```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Aplicar migrações
python manage.py migrate

# Criar superusuário (se necessário)
python manage.py createsuperuser
```

## 📈 Monitoramento

- Verificar logs do servidor para erros
- Monitorar transações no painel do Mercado Pago
- Testar fluxo completo de pagamento

---
**Status:** ✅ Configurado para PRODUÇÃO com checkout transparente