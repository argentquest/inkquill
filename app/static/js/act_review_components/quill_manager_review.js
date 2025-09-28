// /ai_rag_story_app/app/static/js/act_review_components/quill_manager_review.js
"use strict";

const QuillManager_Review = (() => {
    let quillInstance = null;
    const editorDivId = 'act-content-editor-review-page'; // Ensure this matches HTML
    const hiddenTextareaId = 'act-content-for-quill-hidden-review-page'; // Ensure this matches HTML

    function initialize() {
        console.log("QuillManager_Review: Initializing editable Quill for AI Review page.");
        const editorDiv = document.getElementById(editorDivId);
        const hiddenTextarea = document.getElementById(hiddenTextareaId);

        if (typeof Quill === 'undefined') {
            console.error("QuillManager_Review: Quill library not loaded.");
            if (editorDiv) editorDiv.innerHTML = "<p style='color:red;'>Editor library missing.</p>";
            return null;
        }
        if (!editorDiv) {
            console.error(`QuillManager_Review: Editor target div '${editorDivId}' not found.`);
            return null;
        }

        try {
            quillInstance = new Quill(editorDiv, { // Target the correct div
                theme: 'snow',
                modules: {
                    toolbar: [
                        [{ 'header': [1, 2, 3, false] }], ['bold', 'italic', 'underline', 'strike'],
                        [{ 'list': 'ordered' }, { 'list': 'bullet' }], [{ 'indent': '-1' }, { 'indent': '+1' }],
                        [{ 'align': [] }], ['link'], ['clean']
                    ]
                },
                placeholder: 'Edit your Act content here while reviewing AI suggestions...'
            });
            console.log("QuillManager_Review: Quill instance CREATED.");

            if (hiddenTextarea && hiddenTextarea.value) {
                const initialContent = hiddenTextarea.value;
                if (typeof initialContent === 'string' && initialContent.trim() !== '' && initialContent.trim() !== '<p><br></p>') {
                    quillInstance.root.innerHTML = initialContent;
                }
            }
        } catch (e) {
            console.error("QuillManager_Review: CRITICAL ERROR during Quill initialization:", e);
            if (editorDiv) editorDiv.innerHTML = `<p style='color:red;'>Error initializing editor.</p>`;
            quillInstance = null;
        }
        return quillInstance;
    }

    function getContentHtml() {
        if (quillInstance) {
            const html = quillInstance.root.innerHTML;
            return (html === '<p><br></p>') ? "" : html;
        }
        console.warn("QuillManager_Review: Quill instance not available for getContentHtml.");
        const hiddenTextarea = document.getElementById(hiddenTextareaId);
        return hiddenTextarea ? hiddenTextarea.value : "";
    }

    function getText() {
        if (quillInstance) {
            return quillInstance.getText();
        }
        console.warn("QuillManager_Review: Quill instance not available for getText.");
        return "";
    }
    
    function setSelection(index, length = 0, source = 'api') {
        if (quillInstance) {
            quillInstance.setSelection(index, length, source);
        }
    }

    function focus() {
        if (quillInstance) {
            quillInstance.focus();
        }
    }

    function getBounds(index, length = 0) {
        if (quillInstance) {
            return quillInstance.getBounds(index, length);
        }
        return null;
    }
    
    function getScrollingContainer() {
        if (quillInstance) {
            return quillInstance.scrollingContainer;
        }
        return null;
    }


    return {
        initialize,
        getContentHtml,
        getText,
        setSelection,
        focus,
        getBounds,
        getScrollingContainer,
        getInstance: () => quillInstance // To allow direct access if absolutely needed
    };
})();