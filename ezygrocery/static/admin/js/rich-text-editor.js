// Simple Rich Text Editor for Django Admin
document.addEventListener('DOMContentLoaded', function() {
    // Apply grid layout to fieldsets
    applyGridLayout();
    
    // Find all textareas with rich-text-editor class
    const richTextAreas = document.querySelectorAll('textarea.rich-text-editor');
    
    richTextAreas.forEach(function(textarea) {
        // Create toolbar
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-text-toolbar';
        toolbar.style.cssText = `
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-bottom: none;
            padding: 8px;
            display: flex;
            gap: 5px;
            flex-wrap: wrap;
        `;
        
        // Toolbar buttons
        const buttons = [
            {name: 'Bold', tag: 'b', icon: 'B', style: 'font-weight: bold;'},
            {name: 'Italic', tag: 'i', icon: 'I', style: 'font-style: italic;'},
            {name: 'Underline', tag: 'u', icon: 'U', style: 'text-decoration: underline;'},
            {name: 'Heading 1', tag: 'h1', icon: 'H1'},
            {name: 'Heading 2', tag: 'h2', icon: 'H2'},
            {name: 'Heading 3', tag: 'h3', icon: 'H3'},
            {name: 'Paragraph', tag: 'p', icon: 'P'},
            {name: 'Link', tag: 'a', icon: '🔗'},
            {name: 'List', tag: 'ul', icon: '• List'},
            {name: 'Line Break', tag: 'br', icon: '↵'}
        ];
        
        buttons.forEach(function(btn) {
            const button = document.createElement('button');
            button.type = 'button';
            button.innerHTML = btn.icon;
            button.title = btn.name;
            button.style.cssText = `
                padding: 4px 8px;
                border: 1px solid #ccc;
                background: white;
                cursor: pointer;
                border-radius: 3px;
                font-size: 12px;
                ${btn.style || ''}
            `;
            
            button.addEventListener('click', function() {
                insertTag(textarea, btn.tag, btn.name);
            });
            
            toolbar.appendChild(button);
        });
        
        // Insert toolbar before textarea
        textarea.parentNode.insertBefore(toolbar, textarea);
        
        // Style the textarea
        textarea.style.cssText += `
            border-top: none;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        `;
    });
    
    function insertTag(textarea, tag, name) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        let replacement = '';
        
        switch(tag) {
            case 'a':
                const url = prompt('Enter URL:');
                if (url) {
                    replacement = `<a href="${url}">${selectedText || 'Link Text'}</a>`;
                }
                break;
            case 'ul':
                replacement = `<ul>\n<li>${selectedText || 'List item'}</li>\n</ul>`;
                break;
            case 'br':
                replacement = '<br>\n';
                break;
            default:
                if (selectedText) {
                    replacement = `<${tag}>${selectedText}</${tag}>`;
                } else {
                    replacement = `<${tag}>Text here</${tag}>`;
                }
        }
        
        if (replacement) {
            textarea.value = textarea.value.substring(0, start) + replacement + textarea.value.substring(end);
            textarea.focus();
            textarea.setSelectionRange(start + replacement.length, start + replacement.length);
        }
    }
});
/
/ Grid Layout Function
function applyGridLayout() {
    // Find all fieldsets with grid classes
    const gridFieldsets = document.querySelectorAll('.fieldset.grid-2-columns, .fieldset.grid-3-columns');
    
    gridFieldsets.forEach(function(fieldset) {
        const formRows = fieldset.querySelectorAll('.form-row');
        
        formRows.forEach(function(row) {
            // Skip rows that contain rich text editors
            const hasRichText = row.querySelector('.rich-text-editor');
            if (hasRichText) {
                row.style.display = 'block';
                return;
            }
            
            // Apply grid layout for non-rich text fields
            if (fieldset.classList.contains('grid-2-columns')) {
                row.style.display = 'grid';
                row.style.gridTemplateColumns = '1fr 1fr';
                row.style.gap = '20px';
                row.style.alignItems = 'start';
            } else if (fieldset.classList.contains('grid-3-columns')) {
                row.style.display = 'grid';
                row.style.gridTemplateColumns = '1fr 1fr 1fr';
                row.style.gap = '15px';
                row.style.alignItems = 'start';
            }
        });
    });
    
    // Handle responsive design
    function handleResize() {
        if (window.innerWidth <= 768) {
            gridFieldsets.forEach(function(fieldset) {
                const formRows = fieldset.querySelectorAll('.form-row');
                formRows.forEach(function(row) {
                    const hasRichText = row.querySelector('.rich-text-editor');
                    if (!hasRichText) {
                        row.style.gridTemplateColumns = '1fr';
                        row.style.gap = '10px';
                    }
                });
            });
        } else {
            gridFieldsets.forEach(function(fieldset) {
                const formRows = fieldset.querySelectorAll('.form-row');
                formRows.forEach(function(row) {
                    const hasRichText = row.querySelector('.rich-text-editor');
                    if (!hasRichText) {
                        if (fieldset.classList.contains('grid-2-columns')) {
                            row.style.gridTemplateColumns = '1fr 1fr';
                            row.style.gap = '20px';
                        } else if (fieldset.classList.contains('grid-3-columns')) {
                            row.style.gridTemplateColumns = '1fr 1fr 1fr';
                            row.style.gap = '15px';
                        }
                    }
                });
            });
        }
    }
    
    window.addEventListener('resize', handleResize);
}