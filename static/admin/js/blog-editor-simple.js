/**
 * Editor Simples e Confiável - Central MEI Blog
 */

(function() {
    'use strict';
    
    console.log('Carregando editor simplificado...');
    
    // Aguardar DOM estar pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEditor);
    } else {
        initEditor();
    }
    
    function initEditor() {
        console.log('DOM pronto, inicializando editor...');
        
        const contentField = document.querySelector('#id_conteudo');
        if (!contentField) {
            console.log('Campo de conteúdo não encontrado');
            return;
        }
        
        // Aguardar CKEditor carregar
        let attempts = 0;
        const maxAttempts = 50;
        
        function tryInitCKEditor() {
            attempts++;
            
            if (typeof ClassicEditor !== 'undefined') {
                console.log('CKEditor encontrado, inicializando...');
                initCKEditor(contentField);
            } else if (attempts < maxAttempts) {
                console.log(`Tentativa ${attempts}: CKEditor não carregado ainda...`);
                setTimeout(tryInitCKEditor, 200);
            } else {
                console.log('CKEditor não carregou, usando textarea simples');
                setupSimpleEditor(contentField);
            }
        }
        
        tryInitCKEditor();
        
        // Sempre configurar funcionalidades básicas
        setupBasicFeatures();
    }
    
    function initCKEditor(contentField) {
        ClassicEditor
            .create(contentField, {
                toolbar: [
                    'heading', '|',
                    'bold', 'italic', '|',
                    'link', 'bulletedList', 'numberedList', '|',
                    'blockQuote', '|',
                    'undo', 'redo'
                ],
                heading: {
                    options: [
                        { model: 'paragraph', title: 'Parágrafo' },
                        { model: 'heading2', view: 'h2', title: 'Título 2' },
                        { model: 'heading3', view: 'h3', title: 'Título 3' }
                    ]
                },
                placeholder: 'Digite o conteúdo do artigo...'
            })
            .then(editor => {
                console.log('✅ CKEditor inicializado com sucesso!');
                window.blogEditor = editor;
                
                // Configurar altura
                const editableElement = editor.ui.getEditableElement();
                if (editableElement) {
                    editableElement.style.minHeight = '300px';
                }
                
                // Contador de palavras
                editor.model.document.on('change:data', updateWordCount);
                updateWordCount();
                
                // Validação anti-H1
                setupH1Validation(editor);
            })
            .catch(error => {
                console.error('❌ Erro no CKEditor:', error);
                setupSimpleEditor(contentField);
            });
    }
    
    function setupSimpleEditor(contentField) {
        console.log('Configurando editor simples...');
        
        contentField.style.minHeight = '300px';
        contentField.style.fontFamily = 'Georgia, serif';
        contentField.style.fontSize = '16px';
        contentField.style.lineHeight = '1.5';
        contentField.style.padding = '15px';
        
        contentField.addEventListener('input', updateWordCount);
        updateWordCount();
    }
    
    function setupBasicFeatures() {
        // Contador de palavras
        createWordCounter();
        
        // Melhorias nos campos SEO
        setupSEOFields();
        
        // Validação do formulário
        setupFormValidation();
    }
    
    function createWordCounter() {
        const contentField = document.querySelector('#id_conteudo');
        if (!contentField) return;
        
        const counter = document.createElement('div');
        counter.id = 'word-counter';
        counter.className = 'word-counter';
        counter.style.cssText = `
            margin: 10px 0;
            padding: 8px 12px;
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            font-size: 14px;
            color: #1976d2;
            border-radius: 0 4px 4px 0;
        `;
        
        // Inserir após o campo ou seu container
        const insertAfter = contentField.closest('.form-row') || contentField.parentNode;
        insertAfter.parentNode.insertBefore(counter, insertAfter.nextSibling);
        
        updateWordCount();
    }
    
    function updateWordCount() {
        const counter = document.getElementById('word-counter');
        if (!counter) return;
        
        let content = '';
        
        try {
            if (window.blogEditor) {
                content = window.blogEditor.getData();
            } else {
                const textarea = document.querySelector('#id_conteudo');
                content = textarea ? textarea.value : '';
            }
        } catch (e) {
            const textarea = document.querySelector('#id_conteudo');
            content = textarea ? textarea.value : '';
        }
        
        // Contar palavras (remover HTML primeiro)
        const textOnly = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
        const words = textOnly ? textOnly.split(' ').filter(w => w.length > 0) : [];
        const wordCount = words.length;
        
        // Tempo de leitura (250 palavras por minuto)
        const readingTime = Math.max(1, Math.round(wordCount / 250));
        
        // Status da qualidade
        let status = '';
        if (wordCount < 150) {
            status = ' • <span style="color: #f44336;">Muito curto para SEO</span>';
        } else if (wordCount > 2500) {
            status = ' • <span style="color: #ff9800;">Muito longo</span>';
        } else if (wordCount >= 300) {
            status = ' • <span style="color: #4caf50;">Tamanho ideal</span>';
        }
        
        counter.innerHTML = `
            <strong>${wordCount}</strong> palavras | 
            <strong>${readingTime}</strong> min leitura${status}
        `;
    }
    
    function setupSEOFields() {
        // Meta description com contador
        const metaField = document.querySelector('#id_meta_description');
        if (metaField) {
            addCharCounter(metaField, 160, 'Meta description (ideal: 120-160 caracteres)');
        }
        
        // Auto-slug do título
        const titleField = document.querySelector('#id_titulo');
        const slugField = document.querySelector('#id_slug');
        
        if (titleField && slugField) {
            titleField.addEventListener('input', function() {
                if (!slugField.value || slugField.dataset.autoGenerated === 'true') {
                    slugField.value = generateSlug(this.value);
                    slugField.dataset.autoGenerated = 'true';
                }
            });
            
            slugField.addEventListener('input', function() {
                slugField.dataset.autoGenerated = 'false';
            });
        }
        
        // Placeholder para palavras-chave
        const keywordsField = document.querySelector('#id_palavras_chave');
        if (keywordsField) {
            keywordsField.placeholder = 'Exemplo: MEI, microempreendedor, CNPJ, abertura empresa';
        }
    }
    
    function addCharCounter(field, maxChars, label) {
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.style.cssText = `
            margin-top: 5px;
            font-size: 12px;
            color: #666;
        `;
        
        function updateCounter() {
            const length = field.value.length;
            const remaining = maxChars - length;
            
            let color = '#666';
            if (length > maxChars) color = '#f44336';
            else if (remaining < 20) color = '#ff9800';
            else if (length > 120) color = '#4caf50';
            
            counter.style.color = color;
            counter.textContent = `${length}/${maxChars} caracteres - ${label}`;
        }
        
        field.parentNode.insertBefore(counter, field.nextSibling);
        field.addEventListener('input', updateCounter);
        updateCounter();
    }
    
    function generateSlug(text) {
        return text.toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9\s-]/g, '')
            .trim()
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .substring(0, 50);
    }
    
    function setupH1Validation(editor) {
        // Validação em tempo real
        editor.model.document.on('change:data', function() {
            const content = editor.getData();
            if (content.includes('<h1>') || content.includes('<h1 ')) {
                showH1Warning();
            } else {
                hideH1Warning();
            }
        });
    }
    
    function setupFormValidation() {
        const form = document.querySelector('form');
        if (!form) return;
        
        form.addEventListener('submit', function(e) {
            let content = '';
            
            try {
                if (window.blogEditor) {
                    content = window.blogEditor.getData();
                } else {
                    const textarea = document.querySelector('#id_conteudo');
                    content = textarea ? textarea.value : '';
                }
            } catch (err) {
                const textarea = document.querySelector('#id_conteudo');
                content = textarea ? textarea.value : '';
            }
            
            // Verificar H1
            if (content.includes('<h1>') || content.includes('<h1 ')) {
                e.preventDefault();
                alert('⚠️ ATENÇÃO: Não use títulos H1 no conteúdo!\n\nO título H1 já é usado pelo título do artigo.\nPara organizar o conteúdo, use H2, H3 ou H4.');
                return false;
            }
        });
    }
    
    function showH1Warning() {
        let warning = document.getElementById('h1-warning');
        if (!warning) {
            warning = document.createElement('div');
            warning.id = 'h1-warning';
            warning.style.cssText = `
                margin: 10px 0;
                padding: 10px;
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 4px;
                color: #856404;
            `;
            warning.innerHTML = '⚠️ <strong>Atenção:</strong> Evite usar H1 no conteúdo. Use H2, H3 ou H4.';
            
            const contentField = document.querySelector('#id_conteudo');
            const insertAfter = contentField.closest('.form-row') || contentField.parentNode;
            insertAfter.parentNode.insertBefore(warning, insertAfter.nextSibling);
        }
        warning.style.display = 'block';
    }
    
    function hideH1Warning() {
        const warning = document.getElementById('h1-warning');
        if (warning) {
            warning.style.display = 'none';
        }
    }
    
    console.log('✅ Editor simplificado carregado!');
})();