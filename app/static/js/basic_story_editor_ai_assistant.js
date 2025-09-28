// AI Assistant functionality for Basic Story Editor
(function() {
    'use strict';
    
document.addEventListener('DOMContentLoaded', function() {
    // AI Assistant variables (namespaced to avoid conflicts)
    let aiCurrentAssistanceType = 'continue';
    let aiResponseText = '';
    let aiIsGenerating = false;
    let aiGenerationController = null;

    // Save functionality variables
    let isSaving = false;
    let hasUnsavedChanges = false;

    // Get story data from URL or page - try multiple methods
    let storyId = null;

    function detectStoryId() {
        // Method 1: URL query parameters
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('story_id')) {
            storyId = parseInt(urlParams.get('story_id'));
        }
        
        // Method 2: URL path segments (e.g., /stories/123/editor)
        if (!storyId) {
            const pathMatch = window.location.pathname.match(/\/stories\/(\d+)/);
            if (pathMatch) {
                storyId = parseInt(pathMatch[1]);
            }
        }
        
        // Method 3: Data attribute on page element
        if (!storyId) {
            const editorElement = document.querySelector('.basic-story-editor');
            if (editorElement && editorElement.dataset.storyId) {
                storyId = parseInt(editorElement.dataset.storyId);
            }
        }
        
        // Method 4: Hidden input or meta tag
        if (!storyId) {
            const storyIdInput = document.querySelector('input[name="story_id"]');
            const storyIdMeta = document.querySelector('meta[name="story-id"]');
            if (storyIdInput) {
                storyId = parseInt(storyIdInput.value);
            } else if (storyIdMeta) {
                storyId = parseInt(storyIdMeta.getAttribute('content'));
            }
        }
        
        // Debug logging
        console.log('Story ID detection:', {
            currentURL: window.location.href,
            pathname: window.location.pathname,
            search: window.location.search,
            detectedStoryId: storyId
        });
        
        return storyId;
    }

    // Initialize save functionality (delay to ensure DOM is ready)
    setTimeout(function() {
        storyId = detectStoryId();
        initializeSaveFunctionality();
    }, 100);

    // Show AI Assistant by default (after variables are initialized)
    setTimeout(function() {
        showAIAssistant();
    }, 100);

    function showAIAssistant() {
        try {
            const panel = document.getElementById('ai-assistant-panel');
            const editor = document.querySelector('.basic-story-editor');
            
            if (!panel || !editor) {
                console.error('AI Assistant panel or editor not found');
                if (typeof showToast === 'function') {
                    showToast('error', 'AI Assistant interface error. Please refresh the page.');
                }
                return;
            }
            
            panel.classList.add('show');
            editor.classList.add('ai-assistant-open');
            
            // Initialize tooltips for assistance buttons
            try {
                const tooltipTriggerList = panel.querySelectorAll('[data-bs-toggle="tooltip"]');
                const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            } catch (tooltipError) {
                console.warn('Tooltip initialization failed:', tooltipError);
            }
            
            // Set default assistance type
            setAssistanceType('continue');
        } catch (error) {
            console.error('Error showing AI Assistant:', error);
            if (typeof showToast === 'function') {
                showToast('error', 'AI Assistant initialization error. Please refresh the page.');
            }
        }
    }

    function hideAIAssistant() {
        try {
            const panel = document.getElementById('ai-assistant-panel');
            const editor = document.querySelector('.basic-story-editor');
            
            if (panel) panel.classList.remove('show');
            if (editor) editor.classList.remove('ai-assistant-open');
            
            // Stop any ongoing generation
            if (aiIsGenerating && aiGenerationController) {
                aiGenerationController.abort();
            }
        } catch (error) {
            console.error('Error hiding AI Assistant:', error);
        }
    }

    function setAssistanceType(type) {
        aiCurrentAssistanceType = type;
        
        // Update button states
        document.querySelectorAll('.assistance-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const targetBtn = document.querySelector(`[data-type="${type}"]`);
        if (targetBtn) {
            targetBtn.classList.add('active');
        }
        
        // Update custom request placeholder based on type
        const customRequestTextarea = document.getElementById('custom-request-text');
        if (customRequestTextarea) {
            const placeholders = {
                'continue': 'Continue the story from where it left off...',
                'what_happens_next': 'What should happen next in the story...',
                'dialogue': 'Help me write dialogue for this scene...',
                'improve': 'Make this text more engaging...',
                'plot_twist': 'Add an unexpected plot twist...',
                'character_dev': 'Develop these characters further...',
                'creative': 'Generate creative ideas for my story...',
                'problem': 'Describe your specific problem here (e.g., "How do I reveal that the mentor is the villain without it feeling forced?" or "My protagonist feels too passive in chapter 3")'
            };
            
            customRequestTextarea.placeholder = placeholders[type] || 'Describe what you need help with...';
        }
    }

    function setAIStatus(status, message, showSpinner = false) {
        const statusEl = document.getElementById('ai-status');
        if (!statusEl) return;
        
        const icon = statusEl.querySelector('i');
        const span = statusEl.querySelector('span');
        
        statusEl.className = `ai-status ${status}`;
        if (span) span.textContent = message;
        
        if (icon) {
            if (showSpinner) {
                icon.className = 'fas fa-spinner fa-spin';
            } else {
                const icons = {
                    'ready': 'fas fa-circle',
                    'generating': 'fas fa-spinner fa-spin',
                    'success': 'fas fa-check-circle',
                    'error': 'fas fa-exclamation-circle'
                };
                icon.className = icons[status] || 'fas fa-circle';
            }
        }
    }

    async function generateAssistance() {
        if (aiIsGenerating) return;
        
        let customRequest = '';
        let storyContent = '';
        
        try {
            const customRequestEl = document.getElementById('custom-request-text');
            if (customRequestEl) {
                customRequest = customRequestEl.value.trim();
            }
            
            // Get story content from namespaced Quill editor (content_editor partial)
            const editorWrapper = document.querySelector('.editor-wrapper[data-entity-type="story"]');
            let quillEditor = null;
            
            if (editorWrapper) {
                const entityType = editorWrapper.dataset.entityType;
                const entityId = editorWrapper.dataset.entityId;
                quillEditor = window[`quill_${entityType}_${entityId}`];
            }
            
            if (quillEditor) {
                storyContent = quillEditor.getText();
            } else {
                // Fallback to textarea or other editor
                const editorEl = document.querySelector('#story-editor, .story-content, [data-story-content]');
                if (editorEl) {
                    storyContent = editorEl.value || editorEl.textContent || editorEl.innerText || '';
                }
            }
            
            if (!storyContent || storyContent.trim().length === 0) {
                if (typeof showToast === 'function') {
                    showToast('error', 'Please write some content first before requesting AI assistance.');
                } else {
                    alert('Please write some content first before requesting AI assistance.');
                }
                return;
            }
        } catch (error) {
            console.error('Error accessing AI assistant elements:', error);
            if (typeof showToast === 'function') {
                showToast('error', 'AI Assistant interface error. Please refresh the page.');
            }
            return;
        }
        
        // Reset response
        aiResponseText = '';
        const responseContent = document.getElementById('response-content');
        if (responseContent) {
            responseContent.textContent = '';
        }
        
        // Switch to Result tab
        const resultTab = document.getElementById('result-tab');
        const resultPanel = document.getElementById('result-panel');
        const queryTab = document.getElementById('query-tab');
        const queryPanel = document.getElementById('query-panel');
        
        if (resultTab && resultPanel && queryTab && queryPanel) {
            // Activate Result tab
            resultTab.classList.add('active');
            resultTab.setAttribute('aria-selected', 'true');
            queryTab.classList.remove('active');
            queryTab.setAttribute('aria-selected', 'false');
            
            // Show Result panel
            resultPanel.classList.add('show', 'active');
            queryPanel.classList.remove('show', 'active');
        }
        
        // Hide no-response message
        const noResponseMsg = document.getElementById('no-response-message');
        if (noResponseMsg) {
            noResponseMsg.style.display = 'none';
        }
        
        // Show response area and content immediately
        const responseArea = document.getElementById('ai-response');
        if (responseArea) {
            responseArea.classList.add('show');
        }
        
        // Make sure response content is visible for streaming
        if (responseContent) {
            responseContent.style.display = 'block';
            responseContent.classList.remove('d-none');
        }
        
        // Hide response header during generation
        const responseHeader = document.getElementById('response-header');
        const insertSelected = document.getElementById('insert-selected');
        if (responseHeader) responseHeader.style.display = 'none';
        if (insertSelected) insertSelected.style.display = 'none';
        
        // Update UI states
        aiIsGenerating = true;
        setAIStatus('generating', 'Generating response...', true);
        
        const generateBtn = document.getElementById('generate-assistance');
        const stopBtn = document.getElementById('stop-generation');
        
        if (generateBtn) generateBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-block';
        
        // Create abort controller
        aiGenerationController = new AbortController();
        
        try {
            // Get story ID from editor wrapper or URL
            let storyId = null;
            
            // First try to get from editor wrapper (content_editor partial)
            const editorWrapper = document.querySelector('.editor-wrapper[data-entity-type="story"]');
            if (editorWrapper) {
                storyId = editorWrapper.dataset.entityId;
            }
            
            // Fallback: try data-story-id attribute
            if (!storyId) {
                const editorEl = document.querySelector('[data-story-id]');
                if (editorEl) {
                    storyId = editorEl.dataset.storyId;
                }
            }
            
            // Fallback: extract from URL
            if (!storyId) {
                const urlParts = window.location.pathname.split('/');
                const storyIndex = urlParts.findIndex(part => part === 'stories' || part === 'story');
                if (storyIndex >= 0 && urlParts[storyIndex + 1]) {
                    storyId = urlParts[storyIndex + 1];
                }
            }
            
            if (!storyId) {
                throw new Error('Story ID not found');
            }
            
            const response = await fetch(`/api/v1/stories/basic/${storyId}/ai-assist`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                },
                body: JSON.stringify({
                    assistance_type: aiCurrentAssistanceType,
                    story_content: storyContent,
                    specific_request: customRequest || null
                }),
                signal: aiGenerationController.signal
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Handle streaming response
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            console.log('Starting to read streaming response...');
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) {
                    console.log('Streaming response completed, total length:', aiResponseText.length);
                    break;
                }
                
                const chunk = decoder.decode(value, { stream: true });
                aiResponseText += chunk;
                if (responseContent) {
                    responseContent.textContent = aiResponseText;
                    // Auto-scroll to bottom
                    responseContent.scrollTop = responseContent.scrollHeight;
                }
                
                // Log progress
                if (aiResponseText.length % 100 === 0) {
                    console.log('Streaming progress:', aiResponseText.length, 'characters received');
                }
            }
            
            setAIStatus('success', 'Response generated successfully');
            
            // Show response header and content when response is complete
            if (responseHeader) {
                responseHeader.style.display = 'flex';
                responseHeader.classList.remove('d-none');
            }
            if (responseContent) {
                responseContent.style.display = 'block';
                responseContent.classList.remove('d-none');
            }
            
        } catch (error) {
            if (error.name === 'AbortError') {
                setAIStatus('ready', 'Generation stopped');
            } else {
                console.error('AI generation error:', error);
                setAIStatus('error', 'Generation failed');
                if (typeof showToast === 'function') {
                    showToast('error', 'Failed to generate AI response. Please try again.');
                } else {
                    alert('Failed to generate AI response. Please try again.');
                }
            }
        } finally {
            aiIsGenerating = false;
            if (generateBtn) generateBtn.style.display = 'inline-block';
            if (stopBtn) stopBtn.style.display = 'none';
            aiGenerationController = null;
        }
    }

    function stopGeneration() {
        if (aiIsGenerating && aiGenerationController) {
            aiGenerationController.abort();
        }
    }

    function insertResponse() {
        console.log('insertResponse called');
        
        if (!aiResponseText.trim()) {
            if (typeof showToast === 'function') {
                showToast('error', 'No response to insert.');
            } else {
                alert('No response to insert.');
            }
            return;
        }
        
        // Check if there's selected text in the response
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        const responseContent = document.getElementById('response-content');
        
        let textToInsert = aiResponseText.trim();
        let message = 'Full AI response inserted into your story!';
        
        // If there's selected text within the response content, use only that
        if (selectedText && selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            if (responseContent && responseContent.contains(range.commonAncestorContainer)) {
                textToInsert = selectedText;
                message = 'Selected text inserted into your story!';
            }
        }
        
        // Get namespaced Quill editor (content_editor partial)
        const editorWrapper = document.querySelector('.editor-wrapper[data-entity-type="story"]');
        let quillEditor = null;
        
        if (editorWrapper) {
            const entityType = editorWrapper.dataset.entityType;
            const entityId = editorWrapper.dataset.entityId;
            quillEditor = window[`quill_${entityType}_${entityId}`];
        }
        
        // Try to insert into Quill editor first
        if (quillEditor) {
            const quillRange = quillEditor.getSelection();
            const insertIndex = quillRange ? quillRange.index : quillEditor.getLength();
            
            // Insert the text
            quillEditor.insertText(insertIndex, '\n' + textToInsert + '\n');
            
            // Move cursor to end of inserted text
            quillEditor.setSelection(insertIndex + textToInsert.length + 2);
            
            // Focus back on editor
            quillEditor.focus();
            
            // Trigger content-changed event for auto-save
            const event = new CustomEvent('content-changed', {
                detail: {
                    content: quillEditor.root.innerHTML,
                    entity_type: editorWrapper.dataset.entityType,
                    entity_id: editorWrapper.dataset.entityId
                }
            });
            document.dispatchEvent(event);
        } else {
            // Fallback for other editors
            const editorEl = document.querySelector('#story-editor, .story-content, [data-story-content]');
            if (editorEl) {
                if (editorEl.tagName === 'TEXTAREA' || editorEl.tagName === 'INPUT') {
                    const cursorPos = editorEl.selectionStart || editorEl.value.length;
                    const before = editorEl.value.substring(0, cursorPos);
                    const after = editorEl.value.substring(cursorPos);
                    editorEl.value = before + '\n' + textToInsert + '\n' + after;
                    editorEl.focus();
                } else if (editorEl.contentEditable === 'true') {
                    // For contenteditable elements
                    const range = window.getSelection().getRangeAt(0);
                    const textNode = document.createTextNode('\n' + textToInsert + '\n');
                    range.insertNode(textNode);
                    range.setStartAfter(textNode);
                    range.setEndAfter(textNode);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    editorEl.focus();
                }
            }
        }
        
        // Clear any text selection
        selection.removeAllRanges();
        
        // Show success message
        if (typeof showToast === 'function') {
            showToast('success', message);
        }
    }

    function insertSelectedText() {
        console.log('insertSelectedText called');
        
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();
        const responseContent = document.getElementById('response-content');
        
        if (!selectedText) {
            if (typeof showToast === 'function') {
                showToast('error', 'Please select some text from the AI response to insert.');
            } else {
                alert('Please select some text from the AI response to insert.');
            }
            return;
        }
        
        // Verify selection is within response content
        if (selection.rangeCount === 0) {
            if (typeof showToast === 'function') {
                showToast('error', 'No text selected.');
            }
            return;
        }
        
        const range = selection.getRangeAt(0);
        if (!responseContent || !responseContent.contains(range.commonAncestorContainer)) {
            if (typeof showToast === 'function') {
                showToast('error', 'Please select text from the AI response.');
            }
            return;
        }
        
        // Get namespaced Quill editor (content_editor partial)
        const editorWrapper = document.querySelector('.editor-wrapper[data-entity-type="story"]');
        let quillEditor = null;
        
        if (editorWrapper) {
            const entityType = editorWrapper.dataset.entityType;
            const entityId = editorWrapper.dataset.entityId;
            quillEditor = window[`quill_${entityType}_${entityId}`];
        }
        
        // Try to insert into Quill editor first
        if (quillEditor) {
            const quillRange = quillEditor.getSelection();
            const insertIndex = quillRange ? quillRange.index : quillEditor.getLength();
            
            // Insert the selected text
            quillEditor.insertText(insertIndex, '\n' + selectedText + '\n');
            
            // Move cursor to end of inserted text
            quillEditor.setSelection(insertIndex + selectedText.length + 2);
            
            // Focus back on editor
            quillEditor.focus();
            
            // Trigger content-changed event for auto-save
            const event = new CustomEvent('content-changed', {
                detail: {
                    content: quillEditor.root.innerHTML,
                    entity_type: editorWrapper.dataset.entityType,
                    entity_id: editorWrapper.dataset.entityId
                }
            });
            document.dispatchEvent(event);
        } else {
            // Fallback for other editors
            const editorEl = document.querySelector('#story-editor, .story-content, [data-story-content]');
            if (editorEl) {
                if (editorEl.tagName === 'TEXTAREA' || editorEl.tagName === 'INPUT') {
                    const cursorPos = editorEl.selectionStart || editorEl.value.length;
                    const before = editorEl.value.substring(0, cursorPos);
                    const after = editorEl.value.substring(cursorPos);
                    editorEl.value = before + '\n' + selectedText + '\n' + after;
                    editorEl.focus();
                } else if (editorEl.contentEditable === 'true') {
                    // For contenteditable elements
                    const editorRange = window.getSelection().getRangeAt(0);
                    const textNode = document.createTextNode('\n' + selectedText + '\n');
                    editorRange.insertNode(textNode);
                    editorRange.setStartAfter(textNode);
                    editorRange.setEndAfter(textNode);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(editorRange);
                    editorEl.focus();
                }
            }
        }
        
        // Clear selection and hide button
        selection.removeAllRanges();
        const insertSelectedBtn = document.getElementById('insert-selected');
        if (insertSelectedBtn) {
            insertSelectedBtn.style.display = 'none';
        }
        
        // Show success message
        if (typeof showToast === 'function') {
            showToast('success', 'Selected text inserted into your story!');
        }
    }

    function copyResponse() {
        if (!aiResponseText.trim()) {
            if (typeof showToast === 'function') {
                showToast('error', 'No response to copy.');
            } else {
                alert('No response to copy.');
            }
            return;
        }
        
        if (navigator.clipboard) {
            navigator.clipboard.writeText(aiResponseText).then(() => {
                if (typeof showToast === 'function') {
                    showToast('success', 'Response copied to clipboard!');
                }
            }).catch(err => {
                console.error('Failed to copy text: ', err);
                if (typeof showToast === 'function') {
                    showToast('error', 'Failed to copy to clipboard.');
                } else {
                    alert('Failed to copy to clipboard.');
                }
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = aiResponseText;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                if (typeof showToast === 'function') {
                    showToast('success', 'Response copied to clipboard!');
                }
            } catch (err) {
                console.error('Failed to copy text: ', err);
                if (typeof showToast === 'function') {
                    showToast('error', 'Failed to copy to clipboard.');
                } else {
                    alert('Failed to copy to clipboard.');
                }
            }
            document.body.removeChild(textArea);
        }
    }

    function clearResponse() {
        aiResponseText = '';
        
        const responseContent = document.getElementById('response-content');
        const responseHeader = document.getElementById('response-header');
        const insertSelected = document.getElementById('insert-selected');
        const noResponseMessage = document.getElementById('no-response-message');
        
        if (responseContent) {
            responseContent.textContent = '';
            responseContent.style.display = 'none';
        }
        if (responseHeader) responseHeader.style.display = 'none';
        if (insertSelected) insertSelected.style.display = 'none';
        if (noResponseMessage) noResponseMessage.style.display = 'block';
        
        setAIStatus('ready', 'Ready');
        
        // Switch back to Query tab
        const queryTab = document.getElementById('query-tab');
        const queryPanel = document.getElementById('query-panel');
        const resultTab = document.getElementById('result-tab');
        const resultPanel = document.getElementById('result-panel');
        
        if (queryTab && queryPanel && resultTab && resultPanel) {
            // Activate Query tab
            queryTab.classList.add('active');
            queryTab.setAttribute('aria-selected', 'true');
            resultTab.classList.remove('active');
            resultTab.setAttribute('aria-selected', 'false');
            
            // Show Query panel
            queryPanel.classList.add('show', 'active');
            resultPanel.classList.remove('show', 'active');
        }
    }

    // Event listeners for AI Assistant
    document.querySelectorAll('.assistance-type-btn').forEach(btn => {
        btn.addEventListener('click', () => setAssistanceType(btn.dataset.type));
    });
    
    const generateBtn = document.getElementById('generate-assistance');
    const stopBtn = document.getElementById('stop-generation');
    const insertBtn = document.getElementById('insert-response');
    const insertSelectedBtn = document.getElementById('insert-selected');
    const copyBtn = document.getElementById('copy-response');
    const clearBtn = document.getElementById('clear-response');
    
    if (generateBtn) generateBtn.addEventListener('click', generateAssistance);
    if (stopBtn) stopBtn.addEventListener('click', stopGeneration);
    if (insertBtn) insertBtn.addEventListener('click', insertResponse);
    if (insertSelectedBtn) insertSelectedBtn.addEventListener('click', insertSelectedText);
    if (copyBtn) copyBtn.addEventListener('click', copyResponse);
    if (clearBtn) clearBtn.addEventListener('click', clearResponse);
    
    // Handle text selection in AI response to show/hide Insert Selected button
    const responseContent = document.getElementById('response-content');
    if (responseContent) {
        responseContent.addEventListener('mouseup', function() {
            const selection = window.getSelection();
            const selectedText = selection.toString().trim();
            const insertSelectedBtn = document.getElementById('insert-selected');
            
            if (selectedText && selection.rangeCount > 0) {
                const range = selection.getRangeAt(0);
                
                // Check if selection is within the response content
                if (responseContent.contains(range.commonAncestorContainer)) {
                    if (insertSelectedBtn) insertSelectedBtn.style.display = 'inline-block';
                } else {
                    if (insertSelectedBtn) insertSelectedBtn.style.display = 'none';
                }
            } else {
                if (insertSelectedBtn) insertSelectedBtn.style.display = 'none';
            }
        });
    }
    
    // Hide Insert Selected button when clicking outside
    document.addEventListener('click', function(e) {
        const responseContent = document.getElementById('response-content');
        const insertSelectedBtn = document.getElementById('insert-selected');
        
        if (responseContent && insertSelectedBtn && 
            !responseContent.contains(e.target) && 
            !insertSelectedBtn.contains(e.target)) {
            insertSelectedBtn.style.display = 'none';
        }
    });

    // AI Assist button event listener
    const aiAssistBtn = document.getElementById('ai-assist-btn');
    if (aiAssistBtn) {
        aiAssistBtn.addEventListener('click', function() {
            const panel = document.getElementById('ai-assistant-panel');
            if (panel && panel.classList.contains('show')) {
                hideAIAssistant();
            } else {
                showAIAssistant();
            }
        });
    }

    // Listen for content-changed events from content_editor partial
    document.addEventListener('content-changed', function(event) {
        const { content, entity_type, entity_id } = event.detail;
        
        if (entity_type === 'story' && content) {
            // Update word count
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = content;
            const text = tempDiv.textContent || tempDiv.innerText || '';
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            
            const wordCountEl = document.getElementById('word-count');
            if (wordCountEl) {
                wordCountEl.textContent = `${wordCount} words`;
            }
            
            // Update save status to show saving
            const saveStatusEl = document.getElementById('save-status');
            if (saveStatusEl) {
                const icon = saveStatusEl.querySelector('i');
                const span = saveStatusEl.querySelector('span');
                
                if (icon) icon.className = 'fas fa-spinner fa-spin';
                if (span) span.textContent = 'Saving...';
                
                // Show saved status after delay (simulating auto-save)
                setTimeout(() => {
                    if (icon) icon.className = 'fas fa-check-circle';
                    if (span) span.textContent = 'Saved';
                }, 1500);
            }
        }
    });

    // Save functionality
    function initializeSaveFunctionality() {
        const saveBtn = document.getElementById('save-btn');
        const titleInput = document.getElementById('story-title-input');
        const saveStatus = document.getElementById('save-status');
        
        if (!saveBtn || !titleInput) {
            console.warn('Save button or title input not found');
            return;
        }

        // Add event listener for save button
        saveBtn.addEventListener('click', handleSave);

        // Track changes in title
        titleInput.addEventListener('input', function() {
            hasUnsavedChanges = true;
            updateSaveStatus('unsaved');
        });

        // Track changes in editor content - listen for content-changed events
        document.addEventListener('content-changed', function(event) {
            // Check if this event is for our story
            if (event.detail && event.detail.entity_type === 'story' && 
                event.detail.entity_id === storyId) {
                hasUnsavedChanges = true;
                updateSaveStatus('unsaved');
                console.log('Content change detected for story', storyId);
            }
        });

        // Auto-save every 30 seconds if there are unsaved changes
        setInterval(function() {
            if (hasUnsavedChanges && !isSaving) {
                handleSave(true); // true = auto-save
            }
        }, 30000);

        // Add keyboard shortcut for save (Ctrl+S)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                handleSave();
            }
        });

        // Initialize other button handlers
        initializePublishButton();
        initializeExportPdfButton();
        initializePreviewButton();
        initializeHelpButton();
    }

    async function handleSave(isAutoSave = false) {
        if (isSaving) return;
        
        if (!storyId) {
            console.error('Story ID not found');
            if (typeof showToast === 'function') {
                showToast('error', 'Unable to save: Story ID not found');
            }
            return;
        }

        isSaving = true;
        updateSaveStatus('saving');

        try {
            const titleInput = document.getElementById('story-title-input');
            const title = titleInput ? titleInput.value.trim() : '';
            
            // Get content from partial editor - try multiple methods
            let content = '';
            
            // Method 1: Try global Quill instance for story editor
            const entityType = 'story';
            const entityId = storyId;
            if (window[`quill_${entityType}_${entityId}`]) {
                content = window[`quill_${entityType}_${entityId}`].root.innerHTML;
                console.log('Content extracted via global Quill instance:', content.length, 'characters');
            }
            // Method 2: Try content getter function
            else if (window[`getContentEditor_${entityType}_${entityId}`]) {
                content = window[`getContentEditor_${entityType}_${entityId}`]();
                console.log('Content extracted via getter function:', content.length, 'characters');
            }
            // Method 3: Try generic window.quill (fallback)
            else if (window.quill) {
                content = window.quill.root.innerHTML;
                console.log('Content extracted via generic window.quill:', content.length, 'characters');
            }
            // Method 4: Try to find editor by DOM
            else {
                const editorElement = document.querySelector(`#contentEditor_${entityType}_${entityId} .ql-editor`);
                if (editorElement) {
                    content = editorElement.innerHTML;
                    console.log('Content extracted via DOM query:', content.length, 'characters');
                } else {
                    console.warn('No editor found to extract content from');
                }
            }

            const saveData = {
                title: title,
                content: content
            };
            
            console.log('Save data being sent:', {
                title: title,
                contentLength: content ? content.length : 0,
                contentPreview: content ? content.substring(0, 100) + '...' : 'No content'
            });

            const response = await fetch(`/api/v1/stories/basic/${storyId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(saveData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save story');
            }

            const result = await response.json();
            
            hasUnsavedChanges = false;
            updateSaveStatus('saved');
            
            if (!isAutoSave && typeof showToast === 'function') {
                showToast('success', 'Story saved successfully!');
            }

        } catch (error) {
            console.error('Error saving story:', error);
            updateSaveStatus('error');
            
            if (typeof showToast === 'function') {
                showToast('error', error.message || 'Failed to save story');
            }
        } finally {
            isSaving = false;
        }
    }

    function updateSaveStatus(status) {
        const saveStatus = document.getElementById('save-status');
        const saveBtn = document.getElementById('save-btn');
        
        if (!saveStatus) return;

        const icon = saveStatus.querySelector('i');
        const span = saveStatus.querySelector('span');

        switch (status) {
            case 'saving':
                if (icon) icon.className = 'fas fa-spinner fa-spin';
                if (span) span.textContent = 'Saving...';
                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
                }
                break;
            case 'saved':
                if (icon) icon.className = 'fas fa-check-circle text-success';
                if (span) span.textContent = 'Saved';
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save';
                }
                break;
            case 'unsaved':
                if (icon) icon.className = 'fas fa-exclamation-circle text-warning';
                if (span) span.textContent = 'Unsaved changes';
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save';
                }
                break;
            case 'error':
                if (icon) icon.className = 'fas fa-times-circle text-danger';
                if (span) span.textContent = 'Save failed';
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = '<i class="fas fa-save me-1"></i>Save';
                }
                break;
        }
    }

    // Publish button functionality
    function initializePublishButton() {
        const publishBtn = document.getElementById('publish-btn');
        if (!publishBtn) return;

        publishBtn.addEventListener('click', function() {
            openPublishModal();
        });
    }

    function openPublishModal() {
        if (!storyId) {
            if (typeof showToast === 'function') {
                showToast('error', 'Story ID not found');
            }
            return;
        }

        // Get current story data
        const titleInput = document.getElementById('story-title-input');
        const title = titleInput ? titleInput.value.trim() : 'Untitled Story';
        
        // Get content for word count
        const content = getCurrentStoryContent();
        const wordCount = content ? content.replace(/<[^>]*>/g, '').trim().split(/\s+/).filter(word => word.length > 0).length : 0;
        const readTime = Math.max(1, Math.ceil(wordCount / 200)); // Average 200 words per minute

        // Update modal content
        const modal = document.getElementById('story-publish-modal');
        if (modal) {
            modal.querySelector('#publish-story-title').textContent = title;
            modal.querySelector('#publish-word-count').textContent = wordCount;
            modal.querySelector('#publish-read-time').textContent = readTime;
            
            // Set description from story if available
            const descriptionTextarea = modal.querySelector('#publish-description');
            if (descriptionTextarea) {
                // Get story description from title input or use existing
                const titleInput = document.getElementById('story-title-input');
                const currentTitle = titleInput ? titleInput.value.trim() : title;
                
                // You could set a default description or leave it empty for user input
                if (!descriptionTextarea.value) {
                    descriptionTextarea.placeholder = `A captivating story titled "${currentTitle}" with ${wordCount} words of engaging content.`;
                }
            }
            
            // Update preview card
            modal.querySelector('#preview-card-title').textContent = title;
            modal.querySelector('#preview-card-stats').textContent = `${wordCount} words • ${readTime} min read`;
            modal.querySelector('#preview-card-date').textContent = 'Just now';
            
            // Update preview card description dynamically as user types
            const descriptionInput = modal.querySelector('#publish-description');
            const previewDescription = modal.querySelector('#preview-card-description');
            if (descriptionInput && previewDescription) {
                descriptionInput.addEventListener('input', function() {
                    const desc = this.value.trim();
                    previewDescription.textContent = desc || 'No description provided.';
                });
                
                // Set initial preview description
                const initialDesc = descriptionInput.value.trim();
                previewDescription.textContent = initialDesc || 'No description provided.';
            }
            
            // Show modal
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Add publish handler
            const confirmBtn = modal.querySelector('#confirm-publish');
            if (confirmBtn) {
                confirmBtn.onclick = function() {
                    handlePublish();
                };
            }
        }
    }

    async function handlePublish() {
        if (!storyId) {
            if (typeof showToast === 'function') {
                showToast('error', 'Story ID not found');
            }
            return;
        }

        try {
            // Get publish data from modal
            const modal = document.getElementById('story-publish-modal');
            const title = modal.querySelector('#publish-story-title').textContent.trim();
            const description = modal.querySelector('#publish-description').value.trim();
            const visibility = modal.querySelector('#publish-visibility').value;
            
            // Get current story content
            const content = getCurrentStoryContent();
            
            if (!content || content.trim() === '' || content.trim() === '<p><br></p>') {
                if (typeof showToast === 'function') {
                    showToast('error', 'Please add some content to your story before publishing.');
                }
                return;
            }

            // Show publishing state
            const confirmBtn = modal.querySelector('#confirm-publish');
            const originalBtnText = confirmBtn.innerHTML;
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Publishing...';

            // Prepare publish data
            const publishData = {
                title: title,
                description: description || null,
                content: content,
                visibility: visibility
            };

            console.log('Publishing story with data:', {
                storyId: storyId,
                title: title,
                contentLength: content.length,
                visibility: visibility
            });

            // Send publish request
            const response = await fetch(`/api/v1/stories/basic/${storyId}/publish`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(publishData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to publish story');
            }

            const result = await response.json();
            
            if (typeof showToast === 'function') {
                showToast('success', 'Story published successfully!');
            }

            // Close modal
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) bsModal.hide();

            // Update publish button text to show it's published
            const publishBtn = document.getElementById('publish-btn');
            if (publishBtn) {
                publishBtn.innerHTML = '<i class="fas fa-check me-1"></i>Published';
                publishBtn.classList.remove('btn');
                publishBtn.classList.add('btn', 'btn-success');
            }

            // Update publish status badge
            const statusBadge = document.getElementById('publish-status-badge');
            if (statusBadge) {
                statusBadge.innerHTML = '<i class="fas fa-globe me-1"></i>Published';
                statusBadge.classList.remove('bg-warning');
                statusBadge.classList.add('bg-success');
            }

            console.log('Story published successfully:', result);

        } catch (error) {
            console.error('Error publishing story:', error);
            
            if (typeof showToast === 'function') {
                showToast('error', error.message || 'Failed to publish story');
            }
        } finally {
            // Reset button state
            const modal = document.getElementById('story-publish-modal');
            const confirmBtn = modal.querySelector('#confirm-publish');
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i class="fas fa-globe me-1"></i>Publish Story';
            }
        }
    }

    // Export PDF button functionality
    function initializeExportPdfButton() {
        const exportPdfBtn = document.getElementById('export-pdf-btn');
        if (!exportPdfBtn) return;

        exportPdfBtn.addEventListener('click', function() {
            exportStoryToPdf();
        });
    }

    async function exportStoryToPdf() {
        if (!storyId) {
            if (typeof showToast === 'function') {
                showToast('error', 'Story ID not found');
            }
            return;
        }

        const exportBtn = document.getElementById('export-pdf-btn');
        if (!exportBtn) return;

        // Show loading state
        const originalContent = exportBtn.innerHTML;
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Generating PDF...';

        try {
            // Get current story title and content
            const titleInput = document.getElementById('story-title-input');
            const title = titleInput ? titleInput.value.trim() : 'Untitled Story';
            const content = getCurrentStoryContent();

            if (!content || content.trim() === '') {
                if (typeof showToast === 'function') {
                    showToast('warning', 'Please add some content to your story before exporting to PDF');
                }
                return;
            }

            // Save story first to ensure latest content is captured
            await handleSave();

            // Call the PDF export API
            console.log(`Calling PDF export for story ${storyId}`, { title, contentLength: content.length });
            
            const response = await fetch(`/api/v1/stories/basic/${storyId}/export-pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',  // Include cookies for authentication
                body: JSON.stringify({
                    title: title,
                    content: content
                })
            });

            console.log('PDF export response:', response.status, response.statusText);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'Failed to export PDF' }));
                console.error('PDF export error:', errorData);
                throw new Error(errorData.detail || 'Failed to export PDF');
            }

            // Get the PDF as blob and show download modal
            const blob = await response.blob();
            console.log('PDF blob received:', blob.size, 'bytes, type:', blob.type);
            
            const url = window.URL.createObjectURL(blob);
            const filename = `${title.replace(/[^a-zA-Z0-9\s-]/g, '').replace(/\s+/g, '_')}.pdf`;
            console.log('Creating download link with filename:', filename);
            
            // Show the download modal instead of auto-download
            showPdfDownloadModal(url, filename);

            if (typeof showToast === 'function') {
                showToast('success', 'PDF exported successfully!');
            }

        } catch (error) {
            console.error('❌ Error exporting PDF:', error);
            console.error('Error stack:', error.stack);
            
            if (typeof showToast === 'function') {
                showToast('error', error.message || 'Failed to export PDF');
            }
        } finally {
            // Reset button state
            exportBtn.disabled = false;
            exportBtn.innerHTML = originalContent;
        }
    }

    function showPdfDownloadModal(pdfUrl, filename) {
        console.log('🔄 showPdfDownloadModal called with:', { pdfUrl, filename });
        
        // Get modal elements
        const modal = document.getElementById('pdf-download-modal');
        const downloadLink = document.getElementById('pdf-download-link');
        
        console.log('🔍 Modal elements found:', { 
            modal: !!modal, 
            downloadLink: !!downloadLink 
        });
        
        if (!modal) {
            console.error('❌ PDF download modal element not found');
            alert('Error: PDF download modal not found on page');
            return;
        }
        
        if (!downloadLink) {
            console.error('❌ PDF download link element not found');
            alert('Error: PDF download link not found in modal');
            return;
        }

        // Set up the download link
        downloadLink.href = pdfUrl;
        downloadLink.download = filename;
        console.log('✅ Download link configured:', { href: downloadLink.href, download: downloadLink.download });
        
        // Check if Bootstrap is available
        if (typeof bootstrap === 'undefined') {
            console.error('❌ Bootstrap is not available');
            alert('Error: Bootstrap is not loaded');
            return;
        }
        
        // Show the modal
        try {
            console.log('🚀 Creating Bootstrap modal...');
            const bsModal = new bootstrap.Modal(modal);
            console.log('✅ Bootstrap modal created:', bsModal);
            
            console.log('🚀 Showing modal...');
            bsModal.show();
            console.log('✅ Modal show() called successfully');
            
            // Clean up the blob URL when modal is closed
            modal.addEventListener('hidden.bs.modal', function cleanup() {
                console.log('🧹 Cleaning up PDF blob URL');
                window.URL.revokeObjectURL(pdfUrl);
                modal.removeEventListener('hidden.bs.modal', cleanup);
            });
            
            console.log('🎉 PDF download modal shown with filename:', filename);
            
        } catch (error) {
            console.error('❌ Error showing modal:', error);
            alert('Error showing PDF download modal: ' + error.message);
        }
    }

    // Preview button functionality
    function initializePreviewButton() {
        const previewBtn = document.getElementById('preview-btn');
        if (!previewBtn) return;

        previewBtn.addEventListener('click', function() {
            openPreviewModal();
        });
    }

    function openPreviewModal() {
        if (!storyId) {
            if (typeof showToast === 'function') {
                showToast('error', 'Story ID not found');
            }
            return;
        }

        // Get current story data
        const titleElement = document.querySelector('.page-title');
        const title = titleElement ? titleElement.textContent.trim() : 'Untitled Story';
        const content = getCurrentStoryContent();
        
        // Get story image
        const storyImage = document.getElementById('story-image');
        const hasImage = storyImage && storyImage.src && !storyImage.src.includes('placeholder');
        
        // Calculate stats
        const wordCount = content ? content.replace(/<[^>]*>/g, '').trim().split(/\s+/).filter(word => word.length > 0).length : 0;
        const readTime = Math.max(1, Math.ceil(wordCount / 200));

        // Update modal content
        const modal = document.getElementById('story-preview-modal');
        if (modal) {
            // Update header title (keep existing functionality)
            modal.querySelector('#preview-story-title').textContent = title;
            
            // Update large title in header section
            const previewTitleLarge = modal.querySelector('#preview-story-title-large');
            if (previewTitleLarge) {
                previewTitleLarge.textContent = title;
            }
            
            // Update story image in preview
            const previewImage = modal.querySelector('#preview-story-image');
            const previewNoImage = modal.querySelector('#preview-no-image');
            
            if (hasImage && previewImage) {
                previewImage.src = storyImage.src;
                previewImage.style.display = 'block';
                if (previewNoImage) previewNoImage.classList.add('d-none');
            } else {
                if (previewImage) previewImage.style.display = 'none';
                if (previewNoImage) previewNoImage.classList.remove('d-none');
            }
            
            // Update content and stats
            modal.querySelector('#preview-story-content').innerHTML = content || '<p class="text-muted">No content yet. Start writing to see your preview!</p>';
            modal.querySelector('#preview-word-count').textContent = `${wordCount} words`;
            modal.querySelector('#preview-read-time').textContent = `${readTime} min read`;
            
            // Show modal
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
            
            // Initialize preview controls
            initializePreviewControls(modal);
        }
    }

    function initializePreviewControls(modal) {
        // Font size controls
        const fontButtons = modal.querySelectorAll('[id^="font-size-"]');
        fontButtons.forEach(btn => {
            btn.onclick = function() {
                fontButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const size = this.id.replace('font-size-', '');
                const content = modal.querySelector('#preview-story-content');
                content.className = content.className.replace(/font-size-\w+/g, '');
                content.classList.add(`font-size-${size}`);
            };
        });

        // Theme controls
        const themeButtons = modal.querySelectorAll('[id^="theme-"]');
        themeButtons.forEach(btn => {
            btn.onclick = function() {
                themeButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                const theme = this.id.replace('theme-', '');
                const content = modal.querySelector('#preview-story-content');
                content.className = content.className.replace(/theme-\w+/g, '');
                content.classList.add(`theme-${theme}`);
            };
        });

        // Print button
        const printBtn = modal.querySelector('#print-story');
        if (printBtn) {
            printBtn.onclick = function() {
                const content = modal.querySelector('#preview-story-content').innerHTML;
                const title = modal.querySelector('#preview-story-title').textContent;
                printStory(title, content);
            };
        }
    }

    function printStory(title, content) {
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>${title}</title>
                <style>
                    body { font-family: 'Times New Roman', serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
                    h1 { text-align: center; margin-bottom: 30px; }
                    @media print { body { margin: 0; padding: 15px; } }
                </style>
            </head>
            <body>
                <h1>${title}</h1>
                <div>${content}</div>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }

    // Help button functionality
    function initializeHelpButton() {
        const helpBtn = document.getElementById('help-btn');
        if (!helpBtn) return;

        helpBtn.addEventListener('click', function() {
            openHelpPanel();
        });
    }

    function openHelpPanel() {
        // Check if there's a help system available
        if (typeof window.showHelp === 'function') {
            window.showHelp('basic-story-editor');
        } else {
            // Fallback: open help in new tab or show modal
            const helpUrl = '/static/help/basic_story/basic_story_overview.html';
            const helpWindow = window.open(helpUrl, '_blank', 'width=800,height=600,scrollbars=yes');
            
            if (!helpWindow) {
                if (typeof showToast === 'function') {
                    showToast('info', 'Help popup blocked. Please allow popups or check the help section in the menu.');
                } else {
                    alert('Help popup blocked. Please allow popups to view help.');
                }
            }
        }
    }

    // Helper function to get current story content
    function getCurrentStoryContent() {
        const entityType = 'story';
        const entityId = storyId;
        
        // Try multiple methods to get content
        if (window[`quill_${entityType}_${entityId}`]) {
            return window[`quill_${entityType}_${entityId}`].root.innerHTML;
        } else if (window[`getContentEditor_${entityType}_${entityId}`]) {
            return window[`getContentEditor_${entityType}_${entityId}`]();
        } else if (window.quill) {
            return window.quill.root.innerHTML;
        } else {
            const editorElement = document.querySelector(`#contentEditor_${entityType}_${entityId} .ql-editor`);
            return editorElement ? editorElement.innerHTML : '';
        }
    }

    // =============================================================================
    // IMAGE FUNCTIONALITY (Using existing image generation modal)
    // =============================================================================

    // Handler function for when image is updated via the modal
    window.handleImageUpdate = function(result) {
        if (result && result.url) {
            // Update the story image display
            const storyImage = document.getElementById('story-image');
            const storyImagePlaceholder = document.getElementById('story-image-placeholder');
            const changeImageMobileBtn = document.querySelector('.btn[onclick*="showStoryImageModal"]');
            const changeImageHeroBtn = document.getElementById('change-image-hero-btn');

            // Update main story image
            if (storyImage) {
                storyImage.src = result.url;
                storyImage.classList.remove('d-none');
            }
            if (storyImagePlaceholder) {
                storyImagePlaceholder.classList.add('d-none');
            }
            
            // Update button text for mobile button
            if (changeImageMobileBtn) {
                const text = result.url ? 'Change' : 'Add';
                changeImageMobileBtn.innerHTML = `<i class="fas fa-camera me-1"></i>${text} Image`;
            }
            
            // Update button text for hero button
            if (changeImageHeroBtn) {
                const text = result.url ? 'Change' : 'Add';
                changeImageHeroBtn.innerHTML = `<i class="fas fa-camera me-1"></i>${text} Image`;
            }

            // Update preview modal if it's currently open
            updatePreviewModalImage(result.url);

            // Show success notification
            if (typeof showToast === 'function') {
                showToast('Story image updated successfully!', 'success');
            } else {
                console.log('Story image updated successfully!');
            }
        } else {
            // Handle case where no image URL is provided (image removed)
            const storyImage = document.getElementById('story-image');
            const storyImagePlaceholder = document.getElementById('story-image-placeholder');
            
            if (storyImage) {
                storyImage.classList.add('d-none');
                storyImage.src = '';
            }
            if (storyImagePlaceholder) {
                storyImagePlaceholder.classList.remove('d-none');
            }
            
            // Update preview modal if it's currently open
            updatePreviewModalImage(null);
        }
    };

    // Function to update the preview modal image if it's open
    window.updatePreviewModalImage = function(imageUrl) {
        const previewModal = document.getElementById('story-preview-modal');
        if (previewModal && previewModal.classList.contains('show')) {
            // Preview modal is currently open, update the image
            const previewImage = previewModal.querySelector('#preview-story-image');
            const previewNoImage = previewModal.querySelector('#preview-no-image');
            
            if (imageUrl && previewImage) {
                previewImage.src = imageUrl;
                previewImage.style.display = 'block';
                if (previewNoImage) previewNoImage.classList.add('d-none');
            } else {
                if (previewImage) previewImage.style.display = 'none';
                if (previewNoImage) previewNoImage.classList.remove('d-none');
            }
        }
    };

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 4000);
    }

    // Make handleImageUpdate available globally for the modal callback
    window.handleImageUpdate = handleImageUpdate;

    // Global functions for external access
    window.AIAssistant = {
        showAIAssistant,
        hideAIAssistant,
        setAssistanceType,
        generateAssistance,
        stopGeneration,
        insertResponse,
        copyResponse,
        clearResponse,
        // Add save functions to global access
        handleSave,
        updateSaveStatus,
        // Add button functions to global access
        openPublishModal,
        openPreviewModal,
        openHelpPanel
    };
});

})(); // End namespace