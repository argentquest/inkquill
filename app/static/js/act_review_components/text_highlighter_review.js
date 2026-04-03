// /story_app/app/static/js/act_review_components/text_highlighter_review.js
"use strict";

const TextHighlighter_Review = (() => {
    let _quillInstance = null;

    function initialize(quillInstance) {
        _quillInstance = quillInstance;
        console.log("TextHighlighter_Review: Initialized with Quill instance.");
    }

    function highlight(startSnippet, endSnippet) {
        if (!_quillInstance) {
            if(typeof showToast === 'function') showToast("Editor not ready for highlighting.", "warning");
            console.warn("TextHighlighter_Review: Quill instance not set. Cannot highlight.");
            return;
        }
        _quillInstance.setSelection(null); // Clear previous

        if (!startSnippet && !endSnippet) {
            if(typeof showToast === 'function') showToast("No context snippets to highlight.", "info");
            return;
        }

        const fullText = _quillInstance.getText();
        let startIndex = -1, endIndex = -1;

        if (startSnippet) startIndex = fullText.indexOf(startSnippet);
        if (endSnippet) {
            let searchFrom = (startIndex !== -1) ? startIndex : 0;
            let tempEnd = fullText.indexOf(endSnippet, searchFrom);
            if (tempEnd !== -1) endIndex = tempEnd + endSnippet.length;
        }
        
        console.log(`TextHighlighter_Review: Start: "${startSnippet}", End: "${endSnippet}". Indices: ${startIndex}, ${endIndex}`);

        if (startIndex !== -1 && endIndex !== -1 && endIndex > startIndex) {
            _quillInstance.setSelection(startIndex, endIndex - startIndex, 'user');
        } else if (startIndex !== -1) {
            _quillInstance.setSelection(startIndex, startSnippet.length, 'user');
        } else if (endSnippet && endIndex !== -1) {
            _quillInstance.setSelection(endIndex - endSnippet.length, endSnippet.length, 'user');
        } else {
            if(typeof showToast === 'function') showToast("Could not locate text segment for highlighting.", "warning");
            return; // Don't proceed if no match
        }
        
        _quillInstance.focus();
        const currentSelection = _quillInstance.getSelection();
        if (currentSelection) {
            const bounds = _quillInstance.getBounds(currentSelection.index, currentSelection.length);
            if (bounds && _quillInstance.scrollingContainer) {
                _quillInstance.scrollingContainer.scrollTop = bounds.top - 50; // Adjust offset
            }
        }
        if(typeof showToast === 'function') showToast("Text segment highlighted.", "success", 2000);
    }

    return {
        initialize,
        highlight
    };
})();
