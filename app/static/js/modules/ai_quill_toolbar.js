// /story_app/app/static/js/modules/ai_quill_toolbar.js
"use strict";

/**
 * AIQuillToolbar - Modular AI text manipulation for Quill editors
 * 
 * Usage:
 * const aiToolbar = new AIQuillToolbar(quillInstance, {
 *     contextProvider: async () => ({ ... }),
 *     beforeTransform: async (text, op) => true,
 *     afterTransform: async (original, transformed, op) => { ... }
 * });
 */
class AIQuillToolbar {
    constructor(quill, options = {}) {
        this.quill = quill;
        this.options = this.validateOptions(options);
        this.operations = [];
        this.undoStack = [];
        this.isLoading = false;
        this.toolbarButton = null;
        this.contextMenu = null;
        this.previewModal = null;
        this.loadingModal = null;
        this.savedSelection = null; // Store selection when button is clicked
        
        // Bind methods to preserve context
        this.handleTextSelection = this.handleTextSelection.bind(this);
        this.handleContextMenu = this.handleContextMenu.bind(this);
        this.handleToolbarClick = this.handleToolbarClick.bind(this);
        
        this.init();
    }
    
    validateOptions(options) {
        if (!options.contextProvider || typeof options.contextProvider !== 'function') {
            throw new Error('AIQuillToolbar requires a contextProvider function');
        }
        
        return {
            contextProvider: options.contextProvider,
            beforeTransform: options.beforeTransform || null,
            afterTransform: options.afterTransform || null,
            position: options.position || 'toolbar',
            theme: options.theme || 'default',
            maxTextLength: options.maxTextLength || 5000,
            showCostEstimate: options.showCostEstimate !== false
        };
    }
    
    async init() {
        try {
            await this.loadOperations();
            this.setupToolbar();
            this.setupContextMenu();
            this.setupPreviewModal();
            this.setupLoadingModal();
            this.bindEvents();
            console.log('AIQuillToolbar initialized successfully');
        } catch (error) {
            console.error('Failed to initialize AIQuillToolbar:', error);
            this.showError('Failed to initialize AI text tools');
        }
    }
    
    async loadOperations() {
        try {
            const response = await fetch('/api/v1/ai-text/operations', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                throw new Error(`Failed to load operations: ${response.status}`);
            }
            
            const data = await response.json();
            this.operations = data.operations || [];
            
            if (this.operations.length === 0) {
                console.warn('No QuickAI operations available');
            }
            
        } catch (error) {
            console.error('Error loading AI operations:', error);
            this.operations = [];
        }
    }
    
    setupToolbar() {
        if (this.options.position !== 'toolbar') return;
        
        // Find the Quill toolbar
        const toolbar = this.quill.getModule('toolbar');
        if (!toolbar) return;
        
        const toolbarContainer = toolbar.container;
        if (!toolbarContainer) return;
        
        // Create AI dropdown button
        this.toolbarButton = document.createElement('button');
        this.toolbarButton.type = 'button';
        this.toolbarButton.className = 'ql-ai-transform';
        this.toolbarButton.innerHTML = '<i class="fas fa-magic"></i>';
        this.toolbarButton.title = 'AI Text Transform';
        this.toolbarButton.addEventListener('click', this.handleToolbarClick);
        
        // Add to toolbar
        const formatGroup = toolbarContainer.querySelector('.ql-formats');
        if (formatGroup) {
            formatGroup.appendChild(this.toolbarButton);
        } else {
            toolbarContainer.appendChild(this.toolbarButton);
        }
        
        // Update toolbar state (will show active state if text is selected)
        this.updateToolbarState();
    }
    
    setupContextMenu() {
        // Create context menu element
        this.contextMenu = document.createElement('div');
        this.contextMenu.className = 'ai-quill-context-menu';
        this.contextMenu.style.display = 'none';
        document.body.appendChild(this.contextMenu);
        
        // Bind context menu events
        this.quill.root.addEventListener('contextmenu', this.handleContextMenu);
        document.addEventListener('click', this.hideContextMenu.bind(this));
    }
    
    setupPreviewModal() {
        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="ai-transform-preview-modal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-magic me-2"></i>
                                AI Text Transformation Preview
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3" id="cost-estimate-section" style="display: none;">
                                <div class="alert alert-info mb-0">
                                    <i class="fas fa-calculator me-2"></i>
                                    <strong>Tokens Used:</strong> <span id="tokens-used">0</span>
                                </div>
                            </div>
                            <div class="mb-3" id="action-buttons-section">
                                <div class="d-flex gap-2 justify-content-end">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                        <i class="fas fa-times me-1"></i>Reject
                                    </button>
                                    <button type="button" class="btn btn-primary" id="accept-transform-btn">
                                        <i class="fas fa-check me-1"></i>Accept
                                    </button>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-12">
                                    <h6>Original Text</h6>
                                    <div class="border rounded p-3 bg-light" id="original-text-preview" style="max-height: 120px; overflow-y: auto;"></div>
                                </div>
                            </div>
                            <div class="row mt-3">
                                <div class="col-12">
                                    <h6>Transformed Text</h6>
                                    <div class="border rounded p-3 bg-success-light" id="transformed-text-preview" style="max-height: 300px; overflow-y: auto;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <div class="text-muted small">
                                Review the transformation above and click Accept to apply the changes.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer);
        
        this.previewModal = new bootstrap.Modal(document.getElementById('ai-transform-preview-modal'));
        
        // Bind accept button
        document.getElementById('accept-transform-btn').addEventListener('click', () => {
            this.acceptTransformation();
        });
    }
    
    setupLoadingModal() {
        // Create loading modal HTML
        const loadingModalHTML = `
            <div class="modal fade" id="ai-transform-loading-modal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-body text-center py-5">
                            <div class="mb-3">
                                <i class="fas fa-magic fa-3x text-primary fa-spin"></i>
                            </div>
                            <h5 class="mb-3">AI is transforming your text...</h5>
                            <p class="text-muted mb-4">
                                This may take a few moments. Please wait while the AI processes your request.
                            </p>
                            <div class="progress mb-3">
                                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                     role="progressbar" style="width: 100%"></div>
                            </div>
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                Processing time varies based on text length and complexity
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add loading modal to page
        const loadingModalContainer = document.createElement('div');
        loadingModalContainer.innerHTML = loadingModalHTML;
        document.body.appendChild(loadingModalContainer);
        
        this.loadingModal = new bootstrap.Modal(document.getElementById('ai-transform-loading-modal'));
    }
    
    showLoadingModal() {
        if (!this.loadingModal) {
            this.setupLoadingModal();
        }
        this.loadingModal.show();
    }
    
    hideLoadingModal() {
        if (this.loadingModal) {
            this.loadingModal.hide();
        }
    }
    
    bindEvents() {
        // Listen for text selection changes
        this.quill.on('selection-change', this.handleTextSelection);
        
        // Listen for keyboard shortcuts
        this.quill.keyboard.addBinding({
            key: 'T',
            ctrlKey: true,
            altKey: true
        }, this.handleKeyboardShortcut.bind(this));
    }
    
    handleTextSelection(range) {
        this.updateToolbarState();
        
        // Hide context menu if selection changes
        if (this.contextMenu) {
            this.contextMenu.style.display = 'none';
        }
    }
    
    handleContextMenu(event) {
        const selection = this.quill.getSelection();
        if (!selection || selection.length === 0) {
            return; // Let default context menu show
        }
        
        // Save the selection for context menu operations
        this.savedSelection = selection;
        
        event.preventDefault();
        this.showContextMenu(event.clientX, event.clientY);
    }
    
    handleToolbarClick(event) {
        event.preventDefault();
        event.stopPropagation();
        
        // Save the current selection immediately before it's lost
        this.savedSelection = this.quill.getSelection();
        
        // Always show the dropdown, even if no text is selected
        this.showOperationsDropdown(event.target);
    }
    
    handleKeyboardShortcut() {
        const selection = this.quill.getSelection();
        if (selection && selection.length > 0) {
            this.showOperationsDropdown(this.toolbarButton);
        }
    }
    
    updateToolbarState() {
        if (!this.toolbarButton) return;
        
        const selection = this.quill.getSelection();
        const hasSelection = selection && selection.length > 0;
        
        // Only disable button when loading, not when no text is selected
        this.toolbarButton.disabled = this.isLoading;
        this.toolbarButton.classList.toggle('ql-active', hasSelection);
    }
    
    showOperationsDropdown(targetElement) {
        if (this.operations.length === 0) {
            this.showError('No AI operations available');
            return;
        }
        
        // Create dropdown menu
        const dropdown = document.createElement('div');
        dropdown.className = 'ai-operations-dropdown';
        dropdown.innerHTML = this.operations.map(op => `
            <div class="dropdown-item" data-operation-id="${op.id}">
                <i class="${op.icon || 'fas fa-magic'} me-2"></i>
                <span>${op.title}</span>
                ${op.description ? `<small class="text-muted d-block">${op.description}</small>` : ''}
            </div>
        `).join('');
        
        // Position dropdown
        const rect = targetElement.getBoundingClientRect();
        dropdown.style.position = 'fixed';
        dropdown.style.top = `${rect.bottom + 5}px`;
        dropdown.style.left = `${rect.left}px`;
        dropdown.style.zIndex = '9999';
        
        document.body.appendChild(dropdown);
        
        // Handle dropdown clicks
        dropdown.addEventListener('click', (e) => {
            const item = e.target.closest('.dropdown-item');
            if (item) {
                const operationId = parseInt(item.dataset.operationId);
                dropdown.remove();
                
                // Check for text selection when operation is clicked
                if (!this.savedSelection || this.savedSelection.length === 0) {
                    this.showError('Please select some text first');
                    return;
                }
                
                // Also check if the saved selection contains actual text
                const savedSelectedText = this.quill.getText(this.savedSelection.index, this.savedSelection.length);
                if (!savedSelectedText || savedSelectedText.trim().length === 0) {
                    this.showError('Selected text is empty. Please select some actual text first');
                    return;
                }
                
                this.executeTransformation(operationId);
            } else {
                dropdown.remove();
            }
        });
        
        // Remove dropdown when clicking outside
        const removeDropdown = (e) => {
            if (!dropdown.contains(e.target)) {
                dropdown.remove();
                document.removeEventListener('click', removeDropdown);
            }
        };
        setTimeout(() => {
            document.addEventListener('click', removeDropdown);
        }, 0);
    }
    
    showContextMenu(x, y) {
        if (this.operations.length === 0) return;
        
        this.contextMenu.innerHTML = this.operations.map(op => `
            <div class="context-menu-item" data-operation-id="${op.id}">
                <i class="${op.icon || 'fas fa-magic'} me-2"></i>
                ${op.title}
            </div>
        `).join('');
        
        this.contextMenu.style.left = `${x}px`;
        this.contextMenu.style.top = `${y}px`;
        this.contextMenu.style.display = 'block';
        
        // Handle context menu clicks
        this.contextMenu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (item) {
                const operationId = parseInt(item.dataset.operationId);
                this.executeTransformation(operationId);
            }
            this.hideContextMenu();
        });
    }
    
    hideContextMenu() {
        if (this.contextMenu) {
            this.contextMenu.style.display = 'none';
        }
    }
    
    async executeTransformation(operationId) {
        if (this.isLoading) return;
        
        // Use saved selection if available, otherwise get current selection
        const selection = this.savedSelection || this.quill.getSelection();
        if (!selection || selection.length === 0) {
            this.showError('No text selected');
            return;
        }
        
        const selectedText = this.quill.getText(selection.index, selection.length);
        
        // Debug logging
        console.log('Selection details:', {
            selection: selection,
            selectedText: selectedText,
            textLength: selectedText.length,
            textPreview: selectedText.substring(0, 100)
        });
        
        // Check if text is empty or just whitespace
        if (!selectedText || selectedText.trim().length === 0) {
            this.showError('Selected text is empty or contains only whitespace. Please select some actual text.');
            return;
        }
        
        if (selectedText.length > this.options.maxTextLength) {
            this.showError(`Selected text is too long (${selectedText.length} characters). Maximum allowed: ${this.options.maxTextLength}`);
            return;
        }
        
        try {
            this.setLoading(true);
            
            // Show loading modal immediately
            this.showLoadingModal();
            
            // Call before transform hook
            if (this.options.beforeTransform) {
                const proceed = await this.options.beforeTransform(selectedText, operationId);
                if (!proceed) {
                    this.setLoading(false);
                    this.hideLoadingModal();
                    return;
                }
            }
            
            // Get context
            const context = await this.options.contextProvider();
            
            // Skip cost estimation for now
            let costEstimate = null;
            
            // Execute transformation
            const result = await this.callTransformAPI({
                text: selectedText,
                operation_id: operationId,
                context: context
            });
            
            // Hide loading modal and show preview
            this.hideLoadingModal();
            this.showPreview(selectedText, result, costEstimate);
            
        } catch (error) {
            console.error('Transformation failed:', error);
            this.hideLoadingModal();
            this.showError('Transformation failed: ' + error.message);
        } finally {
            this.setLoading(false);
        }
    }
    
    async estimateCost(text, operationId) {
        try {
            const response = await fetch('/api/v1/ai-text/estimate-cost', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({
                    text: text,
                    operation_id: operationId
                })
            });
            
            if (!response.ok) {
                throw new Error(`Cost estimation failed: ${response.status}`);
            }
            
            return await response.json();
            
        } catch (error) {
            console.warn('Cost estimation failed:', error);
            return null;
        }
    }
    
    async callTransformAPI(request) {
        const response = await fetch('/api/v1/ai-text/transform', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(request)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Transformation failed');
        }
        
        return await response.json();
    }
    
    showPreview(originalText, transformResult, costEstimate) {
        // Fill preview content
        document.getElementById('original-text-preview').textContent = originalText;
        document.getElementById('transformed-text-preview').textContent = transformResult.transformed_text;
        
        // Show token count if available
        const costSection = document.getElementById('cost-estimate-section');
        if (transformResult.tokens_used && transformResult.tokens_used > 0) {
            document.getElementById('tokens-used').textContent = transformResult.tokens_used;
            costSection.style.display = 'block';
        } else {
            costSection.style.display = 'none';
        }
        
        // Store result for acceptance
        this.pendingTransformation = {
            originalText: originalText,
            transformedText: transformResult.transformed_text,
            operationId: transformResult.operation_used,
            selection: this.savedSelection || this.quill.getSelection()
        };
        
        // Show modal
        this.previewModal.show();
    }
    
    acceptTransformation() {
        if (!this.pendingTransformation) return;
        
        const { originalText, transformedText, operationId, selection } = this.pendingTransformation;
        
        // Add to undo stack
        this.undoStack.push({
            range: selection,
            originalText: originalText,
            transformedText: transformedText,
            timestamp: Date.now()
        });
        
        // Create the formatted replacement text with markers
        const formattedText = this.createFormattedReplacementText(originalText, transformedText);
        
        // Apply transformation
        this.quill.deleteText(selection.index, selection.length, 'user');
        
        // Insert the formatted text with proper styling
        this.insertFormattedText(selection.index, formattedText);
        
        // Set selection to the entire replaced content
        this.quill.setSelection(selection.index, formattedText.totalLength);
        
        // Call after transform hook
        if (this.options.afterTransform) {
            this.options.afterTransform(originalText, transformedText, operationId);
        }
        
        // Hide modal
        this.previewModal.hide();
        this.pendingTransformation = null;
        this.savedSelection = null; // Clear saved selection
        
        this.showSuccess('Text transformed successfully');
    }
    
    createFormattedReplacementText(originalText, transformedText) {
        // Create the formatted text structure
        const quickAIStart = "Quick AI Start";
        const quickAIEnd = "Quick AI End";
        const aiResultStart = "AI Result Start";
        const aiResultEnd = "AI Result End";
        
        // Calculate lengths for selection
        const startMarkerLength = quickAIStart.length;
        const originalTextLength = originalText.length;
        const endMarkerLength = quickAIEnd.length;
        const resultStartLength = aiResultStart.length;
        const transformedTextLength = transformedText.length;
        const resultEndLength = aiResultEnd.length;
        
        const totalLength = startMarkerLength + originalTextLength + endMarkerLength + 
                           resultStartLength + transformedTextLength + resultEndLength + 6; // +6 for newlines
        
        return {
            quickAIStart,
            originalText,
            quickAIEnd,
            aiResultStart,
            transformedText,
            aiResultEnd,
            totalLength,
            startMarkerLength,
            originalTextLength,
            endMarkerLength,
            resultStartLength,
            transformedTextLength,
            resultEndLength
        };
    }
    
    insertFormattedText(index, formattedText) {
        let currentIndex = index;
        
        // Insert "Quick AI Start" in bold on its own line
        this.quill.insertText(currentIndex, formattedText.quickAIStart, { bold: true }, 'user');
        currentIndex += formattedText.startMarkerLength;
        
        // Insert newline
        this.quill.insertText(currentIndex, '\n', 'user');
        currentIndex += 1;
        
        // Insert original text (normal formatting)
        this.quill.insertText(currentIndex, formattedText.originalText, 'user');
        currentIndex += formattedText.originalTextLength;
        
        // Insert newline
        this.quill.insertText(currentIndex, '\n', 'user');
        currentIndex += 1;
        
        // Insert "Quick AI End" in bold on its own line
        this.quill.insertText(currentIndex, formattedText.quickAIEnd, { bold: true }, 'user');
        currentIndex += formattedText.endMarkerLength;
        
        // Insert newline
        this.quill.insertText(currentIndex, '\n', 'user');
        currentIndex += 1;
        
        // Insert "AI Result Start" in bold on its own line
        this.quill.insertText(currentIndex, formattedText.aiResultStart, { bold: true }, 'user');
        currentIndex += formattedText.resultStartLength;
        
        // Insert newline
        this.quill.insertText(currentIndex, '\n', 'user');
        currentIndex += 1;
        
        // Insert transformed text (normal formatting)
        this.quill.insertText(currentIndex, formattedText.transformedText, 'user');
        currentIndex += formattedText.transformedTextLength;
        
        // Insert newline
        this.quill.insertText(currentIndex, '\n', 'user');
        currentIndex += 1;
        
        // Insert "AI Result End" in bold on its own line
        this.quill.insertText(currentIndex, formattedText.aiResultEnd, { bold: true }, 'user');
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        
        if (this.toolbarButton) {
            this.toolbarButton.disabled = loading;
            this.toolbarButton.innerHTML = loading ? 
                '<i class="fas fa-spinner fa-spin"></i>' : 
                '<i class="fas fa-magic"></i>';
        }
    }
    
    showError(message) {
        if (window.showToast) {
            window.showToast(message, 'error');
        } else {
            console.error('AIQuillToolbar:', message);
            alert(message);
        }
    }
    
    showSuccess(message) {
        if (window.showToast) {
            window.showToast(message, 'success');
        } else {
            console.log('AIQuillToolbar:', message);
        }
    }
    
    // Public API
    undo() {
        if (this.undoStack.length === 0) return false;
        
        const lastTransform = this.undoStack.pop();
        const { range, originalText } = lastTransform;
        
        // Restore original text
        this.quill.deleteText(range.index, lastTransform.transformedText.length, 'user');
        this.quill.insertText(range.index, originalText, 'user');
        this.quill.setSelection(range.index, originalText.length);
        
        return true;
    }
    
    destroy() {
        // Remove event listeners
        this.quill.off('selection-change', this.handleTextSelection);
        this.quill.root.removeEventListener('contextmenu', this.handleContextMenu);
        
        // Remove DOM elements
        if (this.toolbarButton) {
            this.toolbarButton.remove();
        }
        if (this.contextMenu) {
            this.contextMenu.remove();
        }
        if (this.loadingModal) {
            document.getElementById('ai-transform-loading-modal')?.remove();
        }
        
        // Clean up
        this.operations = [];
        this.undoStack = [];
        this.pendingTransformation = null;
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AIQuillToolbar;
}

// Make available globally
window.AIQuillToolbar = AIQuillToolbar;
