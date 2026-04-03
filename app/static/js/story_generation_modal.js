// /story_app/app/static/js/story_generation_modal.js
"use strict";

class StoryGenerationModal {
    constructor() {
        this.worldId = null;
        this.selectedElements = {
            characters: [],
            locations: [],
            lore_items: []
        };
        this.limits = {
            characters: Infinity,
            locations: Infinity,
            lore_items: Infinity
        };
        this.storyOptions = {
            genres: [],
            tones: [],
            conflicts: []
        };
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.bindEvents();
        });
    }
    
    bindEvents() {
        const modal = document.getElementById('storyGenerationModal');
        const generateBtn = document.getElementById('generate-story-btn');
        
        if (modal) {
            modal.addEventListener('show.bs.modal', (event) => {
                this.onModalShow(event);
            });
            
            modal.addEventListener('hide.bs.modal', () => {
                this.resetModal();
            });
        }
        
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateStory();
            });
        }
        
        // Bind story parameter dropdowns
        this.bindParameterDropdowns();
        
        // Bind author concept textarea
        this.bindAuthorConcept();
        
        // Bind element selection using event delegation
        this.bindElementSelection();
    }
    
    bindParameterDropdowns() {
        const genreSelect = document.getElementById('story-genre-select');
        const toneSelect = document.getElementById('story-tone-select');
        const conflictSelect = document.getElementById('conflict-type-select');
        
        if (genreSelect) {
            genreSelect.addEventListener('change', (e) => {
                this.showDescription(e.target, 'genre-description');
                this.validateForm();
            });
        }
        
        if (toneSelect) {
            toneSelect.addEventListener('change', (e) => {
                this.showDescription(e.target, 'tone-description');
                this.validateForm();
            });
        }
        
        if (conflictSelect) {
            conflictSelect.addEventListener('change', (e) => {
                this.showDescription(e.target, 'conflict-description');
                this.validateForm();
            });
        }
    }
    
    bindAuthorConcept() {
        const conceptInput = document.getElementById('author-concept-input');
        const charCountElement = document.getElementById('concept-char-count');
        
        if (conceptInput && charCountElement) {
            // Update character count as user types
            conceptInput.addEventListener('input', () => {
                const length = conceptInput.value.length;
                charCountElement.textContent = length;
                
                // Add visual feedback when approaching limit
                if (length > 180) {
                    charCountElement.style.color = '#dc3545'; // Red
                } else if (length > 150) {
                    charCountElement.style.color = '#fd7e14'; // Orange
                } else {
                    charCountElement.style.color = '#6c757d'; // Gray
                }
            });
            
            // Initial count update
            charCountElement.textContent = conceptInput.value.length;
        }
    }
    
    bindElementSelection() {
        // Use event delegation on the modal for all element grids
        const modal = document.getElementById('storyGenerationModal');
        if (modal) {
            modal.addEventListener('click', (event) => {
                const elementCard = event.target.closest('.element-card');
                if (elementCard) {
                    const elementType = elementCard.dataset.elementType;
                    if (elementType) {
                        this.handleElementSelection(event, elementType);
                    }
                }
            });
        }
    }
    
    showDescription(selectElement, descriptionId) {
        const selectedOption = selectElement.options[selectElement.selectedIndex];
        const descriptionElement = document.getElementById(descriptionId);
        
        if (selectedOption && selectedOption.dataset.description && descriptionElement) {
            descriptionElement.textContent = selectedOption.dataset.description;
            descriptionElement.style.display = 'block';
        } else if (descriptionElement) {
            descriptionElement.style.display = 'none';
        }
    }
    
    async onModalShow(event) {
        // Get world ID from the button that triggered the modal
        const button = event.relatedTarget;
        this.worldId = button?.dataset.worldId;
        
        if (!this.worldId) {
            console.error('No world ID provided for story generation');
            return;
        }
        
        console.log('Story generation modal opened for world:', this.worldId);
        
        // Load all necessary data
        await Promise.all([
            this.loadWorldElements(),
            this.loadStoryOptions(),
            this.loadAIModels()
        ]);
    }
    
    async loadWorldElements() {
        try {
            // Load characters
            const charactersResponse = await fetch(`/api/v1/worlds/${this.worldId}/characters`, {
                credentials: 'include'
            });
            const characters = charactersResponse.ok ? await charactersResponse.json() : [];
            
            // Load locations
            const locationsResponse = await fetch(`/api/v1/worlds/${this.worldId}/locations`, {
                credentials: 'include'
            });
            const locations = locationsResponse.ok ? await locationsResponse.json() : [];
            
            // Load lore items
            const loreResponse = await fetch(`/api/v1/worlds/${this.worldId}/lore-items`, {
                credentials: 'include'
            });
            const loreItems = loreResponse.ok ? await loreResponse.json() : [];
            
            // Populate the grids
            this.populateElementGrid('characters', characters);
            this.populateElementGrid('locations', locations);
            this.populateElementGrid('lore_items', loreItems);
            
        } catch (error) {
            console.error('Error loading world elements:', error);
            this.showError('Failed to load world elements');
        }
    }
    
    async loadStoryOptions() {
        try {
            console.log('Loading story options from API...');
            const response = await fetch('/api/v1/prompts/story-options', {
                credentials: 'include'
            });
            
            if (response.ok) {
                this.storyOptions = await response.json();
                console.log('Story options loaded:', this.storyOptions);
                console.log('Genres count:', this.storyOptions.genres?.length || 0);
                console.log('Tones count:', this.storyOptions.tones?.length || 0);
                console.log('Conflicts count:', this.storyOptions.conflicts?.length || 0);
                this.populateStoryParameterDropdowns();
                console.log('Story parameter dropdowns populated');
            } else {
                console.error('Failed to load story options, status:', response.status);
            }
        } catch (error) {
            console.error('Error loading story options:', error);
        }
    }
    
    async loadAIModels() {
        try {
            // This endpoint would need to be implemented
            const response = await fetch('/api/v1/ai-models/user-available', {
                credentials: 'include'
            });
            
            const modelSelect = document.getElementById('ai-model-select');
            if (response.ok && modelSelect) {
                const models = await response.json();
                
                // Clear existing options except the first
                while (modelSelect.children.length > 1) {
                    modelSelect.removeChild(modelSelect.lastChild);
                }
                
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.display_name || model.name;
                    modelSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading AI models:', error);
        }
    }
    
    populateElementGrid(elementType, elements) {
        // Convert underscore to hyphen for HTML IDs
        const htmlElementType = elementType.replace('_', '-');
        const grid = document.getElementById(`${htmlElementType}-grid`);
        if (!grid) return;
        
        if (elements.length === 0) {
            grid.innerHTML = `
                <div class="text-center py-3 text-muted">
                    <i class="fas fa-info-circle me-2"></i>
                    No ${elementType} found in this world
                </div>
            `;
            return;
        }
        
        grid.innerHTML = elements.map(element => {
            const name = element.name || element.title;
            const description = element.description || '';
            const elementId = element.id;
            const iconClass = this.getElementIconClass(elementType);
            const tooltipAttr = description ? `title="${this.escapeHtml(description)}" data-bs-toggle="tooltip" data-bs-placement="top"` : '';
            
            return `
                <div class="element-card" data-element-id="${elementId}" data-element-type="${elementType}" ${tooltipAttr}>
                    <input type="checkbox" class="element-checkbox" value="${elementId}">
                    <div class="element-card-icon ${iconClass}"></div>
                    <div class="element-card-content">
                        <div class="element-card-title">${this.escapeHtml(name)}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Initialize Bootstrap tooltips for the new elements
        this.initializeTooltips(grid);
    }
    
    initializeTooltips(container) {
        // Initialize Bootstrap tooltips for elements with data-bs-toggle="tooltip"
        const tooltipElements = container.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipElements.forEach(element => {
            new bootstrap.Tooltip(element);
        });
    }
    
    getElementIconClass(elementType) {
        switch(elementType) {
            case 'characters':
                return 'default-character';
            case 'locations':
                return 'default-location';
            case 'lore_items':
                return 'default-lore';
            default:
                return 'default-character';
        }
    }
    
    populateStoryParameterDropdowns() {
        this.populateDropdown('story-genre-select', this.storyOptions.genres);
        this.populateDropdown('story-tone-select', this.storyOptions.tones);
        this.populateDropdown('conflict-type-select', this.storyOptions.conflicts);
    }
    
    populateDropdown(selectId, options) {
        console.log(`Populating dropdown ${selectId} with ${options?.length || 0} options`);
        const select = document.getElementById(selectId);
        if (!select) {
            console.error(`Dropdown element ${selectId} not found`);
            return;
        }
        
        // Clear existing options except the first
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        if (!options || options.length === 0) {
            console.warn(`No options provided for ${selectId}`);
            return;
        }
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.title;
            optionElement.textContent = option.title;
            optionElement.dataset.description = option.reason_to_use || '';
            select.appendChild(optionElement);
        });
        
        console.log(`Successfully populated ${selectId} with ${options.length} options`);
    }
    
    handleElementSelection(event, elementType) {
        const elementCard = event.target.closest('.element-card');
        const checkbox = elementCard?.querySelector('.element-checkbox');
        
        if (!elementCard || !checkbox) return;
        
        const elementId = parseInt(elementCard.dataset.elementId);
        const limit = this.limits[elementType];
        
        // Initialize array if it doesn't exist
        if (!this.selectedElements[elementType]) {
            console.warn(`Initializing missing selectedElements array for ${elementType}`);
            this.selectedElements[elementType] = [];
        }
        
        if (checkbox.checked) {
            // Unselect
            checkbox.checked = false;
            elementCard.classList.remove('selected');
            this.selectedElements[elementType] = this.selectedElements[elementType].filter(id => id !== elementId);
        } else {
            // Select element (no limit check)
            checkbox.checked = true;
            elementCard.classList.add('selected');
            this.selectedElements[elementType].push(elementId);
        }
        
        // Update count display
        this.updateSelectionCount(elementType);
        this.validateForm();
    }
    
    updateSelectionCount(elementType) {
        // Convert underscore to hyphen for HTML IDs
        const htmlElementType = elementType.replace('_', '-');
        const countElement = document.getElementById(`${htmlElementType}-count`);
        if (countElement) {
            countElement.textContent = this.selectedElements[elementType].length;
        }
    }
    
    validateForm() {
        const generateBtn = document.getElementById('generate-story-btn');
        if (!generateBtn) return;
        
        const hasElements = Object.values(this.selectedElements).some(arr => arr.length > 0);
        const hasGenre = document.getElementById('story-genre-select')?.value;
        const hasTone = document.getElementById('story-tone-select')?.value;
        const hasConflict = document.getElementById('conflict-type-select')?.value;
        const hasModel = document.getElementById('ai-model-select')?.value;
        
        const isValid = hasElements && hasGenre && hasTone && hasConflict && hasModel;
        generateBtn.disabled = !isValid;
    }
    
    async generateStory() {
        const generateBtn = document.getElementById('generate-story-btn');
        const progressDiv = document.getElementById('generation-progress');
        
        try {
            // Show progress
            generateBtn.disabled = true;
            if (progressDiv) {
                progressDiv.style.display = 'block';
            }
            
            // Prepare request data
            const requestData = {
                selected_characters: this.selectedElements.characters,
                selected_locations: this.selectedElements.locations,
                selected_lore_items: this.selectedElements.lore_items,
                story_genre: document.getElementById('story-genre-select').value,
                story_tone: document.getElementById('story-tone-select').value,
                primary_conflict_type: document.getElementById('conflict-type-select').value,
                ai_model_config_id: parseInt(document.getElementById('ai-model-select').value),
                author_concept: document.getElementById('author-concept-input').value
            };
            
            console.log('Generating story with data:', requestData);
            
            // Call the API
            const response = await fetch(`/api/v1/worlds/${this.worldId}/stories/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showToast('Story generated successfully!', 'success');
                // Redirect to the new story
                if (result.story_id) {
                    window.location.href = `/ui/stories/${result.story_id}`;
                }
            } else {
                let errorMessage = result.error || 'Failed to generate story';
                
                // If there's debugging info, show it
                if (result.partial_data && result.partial_data.raw_response) {
                    console.log('AI Raw Response:', result.partial_data.full_response);
                    errorMessage += '\n\nAI Response Preview:\n' + result.partial_data.raw_response;
                }
                
                this.showError(errorMessage);
            }
            
        } catch (error) {
            console.error('Error generating story:', error);
            this.showError('Network error occurred while generating story');
        } finally {
            generateBtn.disabled = false;
            if (progressDiv) {
                progressDiv.style.display = 'none';
            }
        }
    }
    
    resetModal() {
        // Clear selections
        this.selectedElements = {
            characters: [],
            locations: [],
            lore_items: []
        };
        
        // Reset form
        const form = document.getElementById('story-generation-form');
        if (form) {
            form.reset();
        }
        
        // Reset author concept character count
        const charCountElement = document.getElementById('concept-char-count');
        if (charCountElement) {
            charCountElement.textContent = '0';
            charCountElement.style.color = '#6c757d'; // Reset to gray
        }
        
        // Reset count displays
        Object.keys(this.limits).forEach(type => {
            this.updateSelectionCount(type);
        });
        
        // Hide descriptions
        ['genre-description', 'tone-description', 'conflict-description'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.style.display = 'none';
            }
        });
        
        // Cleanup tooltips to prevent memory leaks
        this.cleanupTooltips();
        
        // Reset validation
        this.validateForm();
    }
    
    cleanupTooltips() {
        // Dispose of all Bootstrap tooltips in the modal
        const modal = document.getElementById('storyGenerationModal');
        if (modal) {
            const tooltipElements = modal.querySelectorAll('[data-bs-toggle="tooltip"]');
            tooltipElements.forEach(element => {
                const tooltip = bootstrap.Tooltip.getInstance(element);
                if (tooltip) {
                    tooltip.dispose();
                }
            });
        }
    }
    
    showError(message) {
        if (typeof showToast === 'function') {
            showToast(message, 'error');
        } else {
            alert(message);
        }
    }
    
    showToast(message, type = 'info') {
        if (typeof showToast === 'function') {
            showToast(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    escapeHtml(unsafe) {
        if (unsafe === null || typeof unsafe === 'undefined') return '';
        return String(unsafe)
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
}

// Initialize the modal handler
const storyGenerationModal = new StoryGenerationModal();
