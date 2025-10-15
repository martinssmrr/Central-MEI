/**
 * Editor WYSIWYG para posts do blog - Central MEI
 * Utiliza CKEditor 5 com configuração personalizada
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configuração do CKEditor para o campo de conteúdo
    initializeCKEditor();
    
    // Contadores em tempo real
    initializeWordCounter();
    
    // Validações de formulário
    initializeFormValidation();
    
    // Melhorias de UX
    initializeUXEnhancements();
});

/**
 * Inicializa o CKEditor no campo de conteúdo
 */
function initializeCKEditor() {
    const contentField = document.querySelector('#id_conteudo');
    
    if (!contentField) {
        console.log('Campo de conteúdo não encontrado');
        return;
    }

    // Verificar se CKEditor está disponível
    if (typeof ClassicEditor === 'undefined') {
        console.log('CKEditor não carregado, usando textarea simples');
        enhanceTextarea(contentField);
        return;
    }
    
    // Configuração personalizada do CKEditor
    ClassicEditor
        .create(contentField, {
            // Toolbar configurada para blog posts
            toolbar: [
                'heading',
                '|',
                'bold',
                'italic',
                '|',
                'link',
                'bulletedList',
                'numberedList',
                '|',
                'blockQuote',
                'insertTable',
                '|',
                'undo',
                'redo'
            ],
            
            // Configuração de cabeçalhos (sem H1)
            heading: {
                options: [
                    { model: 'paragraph', title: 'Parágrafo', class: 'ck-heading_paragraph' },
                    { model: 'heading2', view: 'h2', title: 'Título 2', class: 'ck-heading_heading2' },
                    { model: 'heading3', view: 'h3', title: 'Título 3', class: 'ck-heading_heading3' },
                    { model: 'heading4', view: 'h4', title: 'Título 4', class: 'ck-heading_heading4' }
                ]
            },
            
            // Placeholder
            placeholder: 'Escreva o conteúdo do seu artigo aqui...'
        })
        .then(editor => {
            window.blogEditor = editor;
            
            // Evento para contagem de palavras em tempo real
            editor.model.document.on('change:data', () => {
                updateWordCount();
            });
            
            // Configurar altura mínima
            editor.editing.view.change(writer => {
                writer.setStyle(
                    'min-height',
                    '400px',
                    editor.editing.view.document.getRoot()
                );
            });
            
            console.log('CKEditor inicializado com sucesso para Central MEI Blog');
        })
        .catch(error => {
            console.error('Erro ao inicializar CKEditor:', error);
            
            // Fallback: melhorar textarea padrão
            enhanceTextarea(contentField);
        });
}

/**
 * Melhora o textarea padrão se CKEditor falhar
 */
function enhanceTextarea(textarea) {
    textarea.style.fontFamily = 'Georgia, "Times New Roman", serif';
    textarea.style.fontSize = '16px';
    textarea.style.lineHeight = '1.6';
    textarea.style.padding = '20px';
    textarea.style.minHeight = '400px';
    
    // Adicionar atalhos de teclado básicos
    textarea.addEventListener('keydown', function(e) {
        // Ctrl+B para negrito
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            wrapSelectedText(textarea, '<strong>', '</strong>');
        }
        
        // Ctrl+I para itálico
        if (e.ctrlKey && e.key === 'i') {
            e.preventDefault();
            wrapSelectedText(textarea, '<em>', '</em>');
        }
    });
}

/**
 * Envolve texto selecionado com tags HTML
 */
function wrapSelectedText(textarea, startTag, endTag) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = textarea.value.substring(start, end);
    
    const replacement = startTag + selectedText + endTag;
    
    textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
    
    // Restaurar seleção
    textarea.selectionStart = start + startTag.length;
    textarea.selectionEnd = start + startTag.length + selectedText.length;
    textarea.focus();
}

/**
 * Inicializa contador de palavras em tempo real
 */
function initializeWordCounter() {
    const contentField = document.querySelector('#id_conteudo');
    
    if (!contentField) return;
    
    // Criar elemento para exibir contagem
    const counterDiv = document.createElement('div');
    counterDiv.className = 'word-count-display';
    counterDiv.id = 'word-counter';
    
    // Inserir após o campo de conteúdo
    const fieldWrapper = contentField.closest('.field-conteudo') || contentField.parentElement;
    if (fieldWrapper) {
        fieldWrapper.appendChild(counterDiv);
    }
    
    // Atualizar contador
    updateWordCount();
    
    // Listener para mudanças no textarea (fallback)
    contentField.addEventListener('input', updateWordCount);
}

/**
 * Atualiza a contagem de palavras
 */
function updateWordCount() {
    const counter = document.getElementById('word-counter');
    if (!counter) return;
    
    let content = '';
    
    // Obter conteúdo do editor ou textarea
    if (window.blogEditor) {
        content = window.blogEditor.getData();
    } else {
        const textarea = document.querySelector('#id_conteudo');
        content = textarea ? textarea.value : '';
    }
    
    // Remover HTML e contar palavras
    const textOnly = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    const wordCount = textOnly ? textOnly.split(' ').length : 0;
    
    // Calcular tempo de leitura (200 palavras por minuto)
    const readingTime = Math.max(1, Math.round(wordCount / 200));
    
    // Atualizar display
    counter.innerHTML = `
        <strong>${wordCount}</strong> palavras | 
        <strong>${readingTime}</strong> min de leitura
        ${wordCount < 300 ? ' <span style="color: #dc3545;">• Muito curto</span>' : ''}
        ${wordCount > 2000 ? ' <span style="color: #ffc107;">• Muito longo</span>' : ''}
    `;
}

/**
 * Inicializa validações do formulário
 */
function initializeFormValidation() {
    const form = document.querySelector('form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const errors = [];
        
        // Validar título
        const titulo = document.querySelector('#id_titulo');
        if (titulo && titulo.value.length < 10) {
            errors.push('Título muito curto (mínimo 10 caracteres)');
        }
        
        // Validar conteúdo
        let content = '';
        if (window.blogEditor) {
            content = window.blogEditor.getData();
        } else {
            const textarea = document.querySelector('#id_conteudo');
            content = textarea ? textarea.value : '';
        }
        
        if (content.length < 100) {
            errors.push('Conteúdo muito curto (mínimo 100 caracteres)');
        }
        
        // Verificar H1 no conteúdo
        if (content.toLowerCase().includes('<h1>') || content.toLowerCase().includes('<h1 ')) {
            errors.push('Evite usar títulos H1 no conteúdo, pois já é usado pelo título do artigo. Use H2, H3 ou H4.');
        }
        
        // Exibir erros se houver
        if (errors.length > 0) {
            e.preventDefault();
            alert('Erros encontrados:\n\n' + errors.join('\n'));
            return false;
        }
    });
}

/**
 * Melhorias de experiência do usuário
 */
function initializeUXEnhancements() {
    // Auto-salvar rascunho (simulado)
    setupAutoSave();
    
    // Melhorar campo de slug
    enhanceSlugField();
    
    // Melhorar campos de SEO
    enhanceSEOFields();
    
    // Adicionar tooltips informativos
    addTooltips();
}

/**
 * Configura salvamento automático
 */
function setupAutoSave() {
    let autoSaveTimer;
    
    function triggerAutoSave() {
        clearTimeout(autoSaveTimer);
        autoSaveTimer = setTimeout(() => {
            console.log('Auto-save seria executado aqui (não implementado por segurança)');
        }, 30000); // 30 segundos
    }
    
    // Monitorar mudanças
    if (window.blogEditor) {
        window.blogEditor.model.document.on('change:data', triggerAutoSave);
    }
    
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', triggerAutoSave);
    });
}

/**
 * Melhora o campo de slug
 */
function enhanceSlugField() {
    const slugField = document.querySelector('#id_slug');
    const titleField = document.querySelector('#id_titulo');
    
    if (!slugField || !titleField) return;
    
    // Auto-gerar slug ao digitar título
    titleField.addEventListener('input', function() {
        if (!slugField.value || slugField.hasAttribute('data-auto-generated')) {
            const slug = generateSlug(this.value);
            slugField.value = slug;
            slugField.setAttribute('data-auto-generated', 'true');
        }
    });
    
    // Remover flag ao editar slug manualmente
    slugField.addEventListener('input', function() {
        this.removeAttribute('data-auto-generated');
    });
}

/**
 * Gera slug a partir do título
 */
function generateSlug(text) {
    return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/[^a-z0-9]+/g, '-')     // Substitui caracteres especiais por hífens
        .replace(/^-+|-+$/g, '');        // Remove hífens do início e fim
}

/**
 * Melhora campos de SEO
 */
function enhanceSEOFields() {
    const metaDescField = document.querySelector('#id_meta_description');
    const resumoField = document.querySelector('#id_resumo');
    
    if (metaDescField && resumoField) {
        // Auto-preencher meta description do resumo
        resumoField.addEventListener('blur', function() {
            if (!metaDescField.value.trim()) {
                metaDescField.value = this.value.substring(0, 160);
            }
        });
        
        // Contador de caracteres para meta description
        const counter = document.createElement('small');
        counter.style.color = '#666';
        counter.style.display = 'block';
        counter.style.marginTop = '5px';
        
        metaDescField.parentElement.appendChild(counter);
        
        function updateMetaCounter() {
            const length = metaDescField.value.length;
            const color = length > 160 ? '#dc3545' : length > 140 ? '#ffc107' : '#28a745';
            counter.innerHTML = `<span style="color: ${color}">${length}/160 caracteres</span>`;
        }
        
        metaDescField.addEventListener('input', updateMetaCounter);
        updateMetaCounter();
    }
}

/**
 * Adiciona tooltips informativos
 */
function addTooltips() {
    const helpTexts = {
        '#id_titulo': 'Título atrativo e descritivo. Ideal entre 30-60 caracteres.',
        '#id_resumo': 'Resumo que aparece na listagem e redes sociais. Máximo 300 caracteres.',
        '#id_palavras_chave': 'Palavras-chave relevantes separadas por vírgula. Ex: MEI, contabilidade, empreendedorismo',
        '#id_meta_description': 'Descrição que aparece nos resultados de busca do Google. Ideal entre 120-160 caracteres.'
    };
    
    Object.entries(helpTexts).forEach(([selector, text]) => {
        const field = document.querySelector(selector);
        if (field) {
            field.setAttribute('title', text);
            field.style.cursor = 'help';
        }
    });
}