// /ai_rag_story_app/app/static/js/scene_quill_manager.js
"use strict";

const SceneQuillManager = (() => {
    let quillInstance = null;
    const editorDivId = 'scene-content-editor';
    const hiddenTextareaId = 'scene-content-hidden-textarea';

    function initialize() {
        const editorDiv = document.getElementById(editorDivId);
        const hiddenTextarea = document.getElementById(hiddenTextareaId);

        if (typeof Quill === 'undefined') {
            console.error("Quill library not loaded. Scene content editor cannot be initialized.");
            if (editorDiv) {
                editorDiv.innerHTML = '<p style="color: red;">Error: Rich text editor library (Quill) could not be loaded.</p>';
            }
            return null;
        }

        if (!editorDiv) {
            console.error(`Quill setup: Element with ID '${editorDivId}' not found.`);
            return null;
        }

        try {
            quillInstance = new Quill(`#${editorDivId}`, {
                theme: 'snow',
                modules: {
                    toolbar: [
                        [{ 'header': [1, 2, 3, false] }],
                        ['bold', 'italic', 'underline', 'strike'],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'indent': '-1'}, { 'indent': '+1' }],
                        [{ 'align': [] }],
                        ['link'],
                        ['clean']
                    ]
                },
                placeholder: 'Enter the narrative content for this scene...'
            });

            if (hiddenTextarea && hiddenTextarea.value && hiddenTextarea.value.trim() !== '') {
                quillInstance.root.innerHTML = hiddenTextarea.value;
            }
            
            console.log(`Quill editor initialized for #${editorDivId} (from scene_quill_manager.js)`);

        } catch (e) {
            console.error("Error initializing Quill for Scene content:", e);
            if (editorDiv) editorDiv.innerHTML = '<p style="color: red;">Error initializing rich text editor.</p>';
            return null;
        }
        return quillInstance;
    }

    function getContentHtml() {
        if (quillInstance) {
            const html = quillInstance.root.innerHTML;
            return (html === '<p><br></p>') ? "" : html;
        }
        const hiddenTextarea = document.getElementById(hiddenTextareaId);
        if (hiddenTextarea) return hiddenTextarea.value;
        console.warn("SceneQuillManager: Quill instance not available for getContentHtml.");
        return "";
    }

    function setContentHtml(htmlContent) {
        if (quillInstance) {
            quillInstance.root.innerHTML = htmlContent || "";
        } else {
            const hiddenTextarea = document.getElementById(hiddenTextareaId);
            if (hiddenTextarea) hiddenTextarea.value = htmlContent || "";
            console.warn("SceneQuillManager: Quill instance not available for setContentHtml.");
        }
    }

    function appendContentHtml(htmlToAppend) {
        if (!htmlToAppend || !quillInstance) return;
        const length = quillInstance.getLength();
        let prefix = (length > 1 && quillInstance.getText(length - 2, 1) !== '\n') ? "<p><br></p>" : "";
        quillInstance.clipboard.dangerouslyPasteHTML(quillInstance.getLength() - 1, prefix + htmlToAppend, 'user');
        quillInstance.setSelection(quillInstance.getLength());
    }

    function getSelectedText() {
        if (!quillInstance) return null;
        const range = quillInstance.getSelection();
        if (range && range.length > 0) {
            return quillInstance.getText(range.index, range.length);
        }
        return null;
    }

    function replaceSelectedText(newText) {
        if (!quillInstance) return;
        const range = quillInstance.getSelection();
        const newHtml = `<p>${newText.replace(/\n\n+/g, '</p><p>').replace(/\n/g, '<br>')}</p>`;

        if (range && range.length > 0) {
            quillInstance.deleteText(range.index, range.length, 'user');
            quillInstance.clipboard.dangerouslyPasteHTML(range.index, newHtml, 'user');
        } else {
            appendContentHtml(newHtml);
        }
    }
    
    function getInstance() { return quillInstance; }
    function getQuillInstance() { return quillInstance; }
    function focusEditor() { if (quillInstance) quillInstance.focus(); }
    
    function getWordCount() {
        if (!quillInstance) return 0;
        const text = quillInstance.getText().trim();
        if (!text) return 0;
        return text.split(/\s+/).filter(word => word.length > 0).length;
    }

    return {
        initialize,
        getContentHtml,
        setContentHtml,
        appendContentHtml,
        getSelectedText,
        replaceSelectedText,
        getInstance,
        getQuillInstance,
        focusEditor,
        getWordCount
    };
})();