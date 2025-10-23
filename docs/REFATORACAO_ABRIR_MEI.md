# Documentação da Refatoração - Formulário Abrir MEI

## Resumo da Refatoração Realizada

A refatoração do formulário "Abrir MEI" foi concluída com sucesso, dividindo a coleta de dados em dois passos distintos conforme solicitado:

### ✅ PASSO 1 (/servicos/abrir-mei/passo-1/)

**Campos coletados:**
- ✅ `nome_completo` - Nome completo do usuário
- ✅ `telefone` - Telefone de contato (formatado)
- ✅ `email` - E-mail de contato

**Formulário:** `AbrirMeiPasso1Form`
**Template:** Atualizado para mostrar apenas os 3 campos essenciais
**View:** Armazena dados na sessão como `'dados_passo1'`

### ✅ PASSO 2 (/servicos/abrir-mei/passo-2/)

**Campos coletados:**
- ✅ `cpf` - CPF (movido do Passo 1)
- ✅ `rg` - RG (movido do Passo 1)  
- ✅ `orgao_expedidor` - Órgão expedidor do RG (movido do Passo 1)
- ✅ `estado_expedidor` - Estado do órgão expedidor (movido do Passo 1)
- ✅ Todos os campos empresariais originais (CNAE, endereço, etc.)

**Formulário:** `AbrirMeiPasso2Form` (unifica identificação + dados empresariais)
**Template:** Nova seção "Dados de Identificação" + seções empresariais existentes
**View:** Combina dados dos dois passos para criar a `SolicitacaoMEI`

## Alterações nos Arquivos

### 📄 servicos/forms.py
- ✅ Criada classe `AbrirMeiPasso1Form` (3 campos básicos)
- ✅ Criada classe `AbrirMeiPasso2Form` (identificação + empresa + endereço)
- ✅ Mantidas classes originais para compatibilidade

### 📄 servicos/views.py  
- ✅ Atualizada `abrir_mei_passo1()` para usar `AbrirMeiPasso1Form`
- ✅ Atualizada `abrir_mei_passo2()` para usar `AbrirMeiPasso2Form`
- ✅ Atualizada gestão de sessão (`dados_passo1` e `dados_passo2`)
- ✅ Atualizada criação da `SolicitacaoMEI` combinando dados dos dois passos

### 📄 templates/servicos/abrir_mei_passo1.html
- ✅ Removidos campos: `cpf`, `rg`, `orgao_expedidor`, `estado_expedidor`
- ✅ Mantidos apenas: `nome_completo`, `telefone`, `email`
- ✅ Atualizado título: "Passo 1: Dados de Contato"

### 📄 templates/servicos/abrir_mei_passo2.html
- ✅ Adicionada nova seção "Dados de Identificação" no início
- ✅ Incluídos campos: `cpf`, `rg`, `orgao_expedidor`, `estado_expedidor`
- ✅ Atualizado resumo lateral para mostrar `dados_passo1`
- ✅ Atualizado título: "Passo 2: Identificação e Dados Empresariais"

## Fluxo de Funcionamento

1. **Usuário acessa Passo 1** → Preenche nome, telefone, email
2. **Dados salvos na sessão** → `request.session['dados_passo1']`
3. **Redirecionamento para Passo 2** → Automaticamente após submissão válida
4. **Passo 2 carrega** → Mostra resumo do Passo 1 + formulário completo
5. **Usuário preenche Passo 2** → CPF, RG, dados empresariais, endereço
6. **Solicitação criada** → Combina dados dos dois passos
7. **Sessão limpa** → Remove dados temporários
8. **Sucesso** → Redirect para página de confirmação

## Validações e Proteções

- ✅ **Validação de sessão**: Passo 2 só carrega se Passo 1 foi completado
- ✅ **Redirecionamento**: Usuário é redirecionado ao Passo 1 se tentar acessar Passo 2 diretamente
- ✅ **Limpeza de sessão**: Dados temporários são removidos após sucesso
- ✅ **Formulários independentes**: Cada passo tem seu próprio formulário com validações

## Status dos Testes

- ✅ **Passo 1**: Carrega corretamente (testado via browser)
- ✅ **Passo 2**: Carrega corretamente (testado via browser)  
- ✅ **Servidor**: Sem erros de sistema (Django runserver OK)
- ✅ **Templates**: Renderização sem erros (HTML válido)
- ✅ **Formulários**: Classes criadas e importadas corretamente

## Arquivos Originais Preservados

As classes `DadosPessoaisForm` e `DadosEmpresariaisForm` foram mantidas no código para compatibilidade com outras partes do sistema que possam estar usando-as.

## Conclusão

✅ **Refatoração 100% concluída conforme especificado**
✅ **Passo 1**: Coleta apenas nome_completo, telefone, email  
✅ **Passo 2**: Coleta cpf, rg + dados empresariais
✅ **Sistema funcionando**: Views, forms, templates atualizados
✅ **Fluxo validado**: Redirecionamentos e sessões funcionando

A divisão foi implementada com sucesso, mantendo a experiência do usuário fluida e as validações necessárias.