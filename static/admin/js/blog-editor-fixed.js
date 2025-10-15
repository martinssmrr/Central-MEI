/**
 * Editor WYSIWYG Simplificado para Blog - Central MEI
 * Versão corrigida sem bugs
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando editor do blog...');
    
    // Inicializar CKEditor
    initializeCKEditor();
    
    // Adicionar contador de palavras
    addWordCounter();
    
    // Melhorar campos SEO
    enhanceSEOFields();
});

/**
 * Inicializa CKEditor de forma segura
 */
function initializeCKEditor() {
    const contentField = document.querySelector('#id_conteudo');
    
    if (!contentField) {
        console.log('Campo de conteúdo não encontrado');
        return;
    }

    // Verificar se CKEditor está disponível
    if (typeof ClassicEditor === 'undefined') {
        console.log('CKEditor não disponível, melhorando textarea');
        enhanceTextarea(contentField);
        return;
    }
    
    // Configuração simples e confiável do CKEditor
    ClassicEditor
        .create(contentField, {
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
            heading: {
                options: [
                    { model: 'paragraph', title: 'Parágrafo' },
                    { model: 'heading2', view: 'h2', title: 'Título 2' },
                    { model: 'heading3', view: 'h3', title: 'Título 3' },
                    { model: 'heading4', view: 'h4', title: 'Título 4' }
                ]
            },
            placeholder: 'Escreva o conteúdo do seu artigo aqui...'
        })
        .then(editor => {
            console.log('CKEditor inicializado com sucesso');
            window.blogEditor = editor;
            
            // Atualizar contador ao digitar
            editor.model.document.on('change:data', () => {
                updateWordCount();
            });
            
            // Altura mínima do editor
            const editorElement = editor.ui.getEditableElement();
            if (editorElement) {
                editorElement.style.minHeight = '300px';
            }
        })
        .catch(error => {
            console.error('Erro no CKEditor:', error);
            enhanceTextarea(contentField);
        });
}

/**
 * Melhora textarea padrão como fallback
 */
function enhanceTextarea(textarea) {
    console.log('Usando textarea melhorado');
    
    textarea.style.fontFamily = 'Georgia, serif';
    textarea.style.fontSize = '16px';
    textarea.style.lineHeight = '1.6';
    textarea.style.padding = '15px';
    textarea.style.minHeight = '300px';
    textarea.style.border = '2px solid #ddd';
    textarea.style.borderRadius = '4px';
    
    textarea.addEventListener('input', updateWordCount);
}

/**
 * Adiciona contador de palavras
 */
function addWordCounter() {
    const contentField = document.querySelector('#id_conteudo');
    if (!contentField) return;
    
    // Criar elemento do contador
    const counter = document.createElement('div');
    counter.id = 'word-counter';
    counter.style.cssText = `
        margin-top: 10px;
        padding: 8px 12px;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        font-size: 14px;
        color: #495057;
    `;
    
    // Inserir contador após o campo
    contentField.parentNode.insertBefore(counter, contentField.nextSibling);
    
    // Atualização inicial
    updateWordCount();
    
    // Atualizar em mudanças no textarea (fallback)
    contentField.addEventListener('input', updateWordCount);
}

/**
 * Atualiza contador de palavras
 */
function updateWordCount() {
    const counter = document.getElementById('word-counter');
    if (!counter) return;
    
    let content = '';
    
    // Obter conteúdo do editor ou textarea
    if (window.blogEditor) {
        try {
            content = window.blogEditor.getData();
        } catch (e) {
            console.log('Erro ao obter dados do editor:', e);
            content = document.querySelector('#id_conteudo').value || '';
        }
    } else {
        const textarea = document.querySelector('#id_conteudo');
        content = textarea ? textarea.value : '';
    }
    
    // Remover HTML e contar palavras
    const textOnly = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    const wordCount = textOnly ? textOnly.split(' ').filter(word => word.length > 0).length : 0;
    
    // Calcular tempo de leitura
    const readingTime = Math.max(1, Math.round(wordCount / 200));
    
    // Atualizar contador
    counter.innerHTML = `
        <strong>${wordCount}</strong> palavras | 
        <strong>${readingTime}</strong> min de leitura
        ${wordCount < 100 ? ' <span style="color: #dc3545;">• Muito curto para SEO</span>' : ''}
        ${wordCount > 3000 ? ' <span style="color: #ffc107;">• Muito longo</span>' : ''}
    `;
}

/**
 * Melhora campos de SEO
 */
function enhanceSEOFields() {
    // Contador para meta description
    const metaField = document.querySelector('#id_meta_description');
    if (metaField) {
        addCharacterCounter(metaField, 160, 'Ideal: 120-160 caracteres');
    }
    
    // Geração automática de slug
    const titleField = document.querySelector('#id_titulo');
    const slugField = document.querySelector('#id_slug');
    
    if (titleField && slugField) {
        titleField.addEventListener('input', function() {
            if (!slugField.value || slugField.value === generateSlug(titleField.dataset.oldValue || '')) {
                slugField.value = generateSlug(this.value);
            }
            titleField.dataset.oldValue = this.value;
        });
    }
    
    // Tooltip para palavras-chave
    const keywordsField = document.querySelector('#id_palavras_chave');
    if (keywordsField) {
        keywordsField.placeholder = 'MEI, microempreendedor, CNPJ, abertura...';
        keywordsField.title = 'Palavras-chave separadas por vírgula';
    }
}

/**
 * Adiciona contador de caracteres a um campo
 */
function addCharacterCounter(field, maxLength, helpText) {
    const counter = document.createElement('div');
    counter.style.cssText = `
        margin-top: 5px;
        font-size: 12px;
        color: #6c757d;
    `;
    
    function updateCounter() {
        const length = field.value.length;
        const remaining = maxLength - length;
        
        counter.textContent = `${length}/${maxLength} caracteres`;
        
        if (remaining < 0) {
            counter.style.color = '#dc3545';
        } else if (remaining < 20) {
            counter.style.color = '#ffc107';
        } else {
            counter.style.color = '#28a745';
        }
        
        if (helpText && length === 0) {
            counter.textContent += ` - ${helpText}`;
        }
    }
    
    field.parentNode.insertBefore(counter, field.nextSibling);
    field.addEventListener('input', updateCounter);
    updateCounter();
}

/**
 * Gera slug a partir de string
 */
function generateSlug(text) {
    return text
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '') // Remove acentos
        .replace(/[^a-z0-9\s-]/g, '') // Remove caracteres especiais
        .trim()
        .replace(/\s+/g, '-') // Substitui espaços por hífens
        .replace(/-+/g, '-') // Remove hífens duplicados
        .substring(0, 50); // Limita tamanho
}

// Validação simples no envio do formulário
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Verificar H1 no conteúdo
            let content = '';
            
            if (window.blogEditor) {
                try {
                    content = window.blogEditor.getData();
                } catch (error) {
                    content = document.querySelector('#id_conteudo').value || '';
                }
            } else {
                content = document.querySelector('#id_conteudo').value || '';
            }
            
            if (content.toLowerCase().includes('<h1')) {
                alert('⚠️ Evite usar títulos H1 no conteúdo.\n\nO título H1 já é usado pelo título do artigo.\nUse H2, H3 ou H4 para organizar seu conteúdo.');
                e.preventDefault();
                return false;
            }
        });
    }
});

console.log('Editor do blog carregado com sucesso!');
terça-feira, 14 de outubro de 2025 19:35:06

