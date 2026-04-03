// /story_app/app/static/js/quill_manager.js
"use strict";

/**
 * Generic Quill Editor Manager
 * Provides a reusable Quill editor instance for various forms
 */
const QuillManager = (() => {
    let instances = new Map();
    
    /**
     * Initialize a Quill editor for a specific element
     * @param {string} editorId - The ID of the div element to turn into a Quill editor
     * @param {string} hiddenTextareaId - The ID of the hidden textarea to sync content with
     * @param {Object} options - Quill configuration options
     */
    function initialize(editorId, hiddenTextareaId, options = {}) {
        const editorDiv = document.getElementById(editorId);
        const hiddenTextarea = document.getElementById(hiddenTextareaId);

        if (typeof Quill === 'undefined') {
            console.error("Quill library not loaded. Editor cannot be initialized.");
            if (editorDiv) {
                editorDiv.innerHTML = '<p style="color: red;">Error: Rich text editor library (Quill) could not be loaded.</p>';
            }
            return null;
        }

        if (!editorDiv) {
            console.error(`Quill setup: Element with ID '${editorId}' not found.`);
            return null;
        }

        // Default configuration
        const defaultConfig = {
            theme: 'snow',
            modules: {
                toolbar: {
                    container: [
                        [{ 'header': [1, 2, 3, false] }],
                        ['bold', 'italic', 'underline', 'strike'],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'indent': '-1'}, { 'indent': '+1' }],
                        [{ 'align': [] }],
                        ['link'],
                        ['blockquote', 'code-block'],
                        ['clean', 'clear-all-formatting']
                    ],
                    handlers: {
                        'clear-all-formatting': function() {
                            clearAllFormattingHandler(this.quill);
                        }
                    }
                }
            },
            placeholder: options.placeholder || 'Start writing...'
        };

        // Merge with provided options
        const config = { ...defaultConfig, ...options };

        try {
            const quillInstance = new Quill(`#${editorId}`, config);

            // Load initial content from hidden textarea
            if (hiddenTextarea && hiddenTextarea.value && hiddenTextarea.value.trim() !== '') {
                quillInstance.root.innerHTML = hiddenTextarea.value;
            }

            // Set up content sync between Quill and hidden textarea
            quillInstance.on('text-change', function() {
                if (hiddenTextarea) {
                    const html = quillInstance.root.innerHTML;
                    hiddenTextarea.value = (html === '<p><br></p>') ? "" : html;
                }
            });

            // Store the instance
            instances.set(editorId, {
                quill: quillInstance,
                hiddenTextareaId: hiddenTextareaId
            });
            
            console.log(`Quill editor initialized for #${editorId}`);
            return quillInstance;

        } catch (e) {
            console.error("Error initializing Quill editor:", e);
            if (editorDiv) {
                editorDiv.innerHTML = '<p style="color: red;">Error initializing rich text editor.</p>';
            }
            return null;
        }
    }

    /**
     * Get the HTML content from a Quill instance
     * @param {string} editorId - The ID of the editor
     */
    function getContentHtml(editorId) {
        const instance = instances.get(editorId);
        if (instance && instance.quill) {
            const html = instance.quill.root.innerHTML;
            return (html === '<p><br></p>') ? "" : html;
        }
        
        // Fallback to hidden textarea
        const hiddenTextarea = document.getElementById(instance?.hiddenTextareaId);
        if (hiddenTextarea) return hiddenTextarea.value;
        
        console.warn(`QuillManager: Instance not found for ${editorId}`);
        return "";
    }

    /**
     * Set the HTML content of a Quill instance
     * @param {string} editorId - The ID of the editor
     * @param {string} htmlContent - The HTML content to set
     */
    function setContentHtml(editorId, htmlContent) {
        const instance = instances.get(editorId);
        if (instance && instance.quill) {
            instance.quill.root.innerHTML = htmlContent || "";
        } else {
            const hiddenTextarea = document.getElementById(instance?.hiddenTextareaId);
            if (hiddenTextarea) hiddenTextarea.value = htmlContent || "";
            console.warn(`QuillManager: Instance not found for ${editorId}`);
        }
    }

    /**
     * Get the plain text content from a Quill instance
     * @param {string} editorId - The ID of the editor
     */
    function getContentText(editorId) {
        const instance = instances.get(editorId);
        if (instance && instance.quill) {
            return instance.quill.getText();
        }
        console.warn(`QuillManager: Instance not found for ${editorId}`);
        return "";
    }

    /**
     * Focus a Quill editor
     * @param {string} editorId - The ID of the editor
     */
    function focusEditor(editorId) {
        const instance = instances.get(editorId);
        if (instance && instance.quill) {
            instance.quill.focus();
        } else {
            console.warn(`QuillManager: Instance not found for ${editorId}`);
        }
    }

    /**
     * Get a Quill instance
     * @param {string} editorId - The ID of the editor
     */
    function getInstance(editorId) {
        const instance = instances.get(editorId);
        return instance ? instance.quill : null;
    }

    /**
     * Check if editor has content
     * @param {string} editorId - The ID of the editor
     */
    function hasContent(editorId) {
        const content = getContentText(editorId);
        return content && content.trim().length > 0;
    }

    /**
     * Clear all content from an editor
     * @param {string} editorId - The ID of the editor
     */
    function clearContent(editorId) {
        setContentHtml(editorId, "");
    }

    /**
     * Setup character counter for an editor
     * @param {string} editorId - The ID of the editor
     * @param {string} counterId - The ID of the element to display character count
     * @param {number} maxLength - Maximum character limit (optional)
     */
    function setupCharacterCounter(editorId, counterId, maxLength = null) {
        const instance = instances.get(editorId);
        const counterElement = document.getElementById(counterId);
        
        if (!instance || !counterElement) {
            console.warn(`QuillManager: Cannot setup character counter for ${editorId}`);
            return;
        }

        function updateCounter() {
            const textLength = getContentText(editorId).length;
            let counterText = textLength.toLocaleString();
            
            if (maxLength) {
                counterText += `/${maxLength.toLocaleString()}`;
                
                // Add warning styles if approaching limit
                if (textLength > maxLength * 0.9) {
                    counterElement.className = 'text-warning';
                } else if (textLength > maxLength) {
                    counterElement.className = 'text-danger';
                } else {
                    counterElement.className = 'text-muted';
                }
            } else {
                counterElement.className = 'text-muted';
            }
            
            counterElement.textContent = counterText + ' characters';
        }

        // Update counter on text change
        instance.quill.on('text-change', updateCounter);
        
        // Initial update
        updateCounter();
    }

    return {
        initialize,
        getContentHtml,
        setContentHtml,
        getContentText,
        focusEditor,
        getInstance,
        hasContent,
        clearContent,
        setupCharacterCounter
    };
})();
