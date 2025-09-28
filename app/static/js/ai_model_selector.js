"use strict";

const AIModelSelector = (() => {
    const API_BASE_URL = "/api/v1";

    async function initialize(selectElementId) {
        const selectElement = document.getElementById(selectElementId);
        if (!selectElement) {
            console.error(`AIModelSelector: Element with ID '${selectElementId}' not found.`);
            return;
        }

        selectElement.innerHTML = '<option value="">Loading AI Presets...</option>';
        selectElement.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/ai-models/`, { credentials: 'include' });
            if (!response.ok) throw new Error("Failed to fetch AI model configurations.");

            const models = await response.json();
            
            // Preserve current selection if any
            const currentValue = selectElement.value;
            
            selectElement.innerHTML = ''; // Clear loading message

            if (models.length === 0) {
                selectElement.innerHTML = '<option value="">No AI presets found</option>';
                return;
            }

            let defaultModelId = null;
            
            // Use current value if it exists and is valid
            if (currentValue && models.find(m => m.id == currentValue)) {
                defaultModelId = currentValue;
            } else if (models.length > 0) {
                // Default to first model if no current selection
                defaultModelId = models[0].id;
            }

            models.forEach((model) => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.display_name;
                option.title = model.description || `Uses the ${model.model_name} engine.`;
                
                selectElement.appendChild(option);
            });
            
            selectElement.disabled = false;
            
            // Set the selected value after all options are added
            if (defaultModelId) {
                // Multiple approaches to ensure the selection is visible
                
                // 1. Clear all selections first
                Array.from(selectElement.options).forEach(opt => opt.selected = false);
                
                // 2. Find and select the correct option
                const selectedOption = selectElement.querySelector(`option[value="${defaultModelId}"]`);
                if (selectedOption) {
                    selectedOption.selected = true;
                    selectElement.selectedIndex = Array.from(selectElement.options).indexOf(selectedOption);
                }
                
                // 3. Set the value property
                selectElement.value = defaultModelId;
                
                // 4. Force a visual refresh using multiple methods
                setTimeout(() => {
                    // Force re-render by temporarily hiding and showing
                    const originalDisplay = selectElement.style.display;
                    selectElement.style.display = 'none';
                    selectElement.offsetHeight; // Trigger reflow
                    selectElement.style.display = originalDisplay;
                    
                    // Trigger focus and blur to refresh Bootstrap styling
                    selectElement.focus();
                    selectElement.blur();
                    
                    // Trigger change event
                    selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                }, 100);
            }
            
            console.log(`AIModelSelector: Populated '${selectElementId}' with ${models.length} presets, selected: ${selectElement.value}`);

        } catch (error) {
            console.error("AIModelSelector: Error initializing.", error);
            selectElement.innerHTML = '<option value="">Error loading presets</option>';
            if (typeof showToast === 'function') showToast("Could not load AI presets.", "error");
        }
    }

    async function loadAndPopulateModels(selectElement) {
        if (!selectElement) {
            console.error('AIModelSelector: No select element provided to loadAndPopulateModels');
            return;
        }

        selectElement.innerHTML = '<option value="">Loading AI Models...</option>';
        selectElement.disabled = true;

        try {
            const response = await fetch(`${API_BASE_URL}/ai-models/`, { credentials: 'include' });
            if (!response.ok) throw new Error("Failed to fetch AI model configurations.");

            const models = await response.json();
            
            // Preserve current selection if any
            const currentValue = selectElement.value;
            
            selectElement.innerHTML = ''; // Clear loading message

            if (models.length === 0) {
                selectElement.innerHTML = '<option value="">No AI models found</option>';
                return;
            }

            let defaultModelId = null;
            
            // Use current value if it exists and is valid
            if (currentValue && models.find(m => m.id == currentValue)) {
                defaultModelId = currentValue;
            } else if (models.length > 0) {
                // Default to first model if no current selection
                defaultModelId = models[0].id;
            }

            models.forEach((model) => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.display_name;
                option.title = model.description || `Uses the ${model.model_name} engine.`;
                
                selectElement.appendChild(option);
            });
            
            selectElement.disabled = false;
            
            // Set the selected value after all options are added
            if (defaultModelId) {
                // Multiple approaches to ensure the selection is visible
                
                // 1. Clear all selections first
                Array.from(selectElement.options).forEach(opt => opt.selected = false);
                
                // 2. Find and select the correct option
                const selectedOption = selectElement.querySelector(`option[value="${defaultModelId}"]`);
                if (selectedOption) {
                    selectedOption.selected = true;
                    selectElement.selectedIndex = Array.from(selectElement.options).indexOf(selectedOption);
                }
                
                // 3. Set the value property
                selectElement.value = defaultModelId;
                
                // 4. Force a visual refresh using multiple methods
                setTimeout(() => {
                    // Force re-render by temporarily hiding and showing
                    const originalDisplay = selectElement.style.display;
                    selectElement.style.display = 'none';
                    selectElement.offsetHeight; // Trigger reflow
                    selectElement.style.display = originalDisplay;
                    
                    // Trigger focus and blur to refresh Bootstrap styling
                    selectElement.focus();
                    selectElement.blur();
                    
                    // Trigger change event
                    selectElement.dispatchEvent(new Event('change', { bubbles: true }));
                }, 100);
            }
            
            console.log(`AIModelSelector: Populated select with ${models.length} models, selected: ${selectElement.value}`);

        } catch (error) {
            console.error("AIModelSelector: Error loading models.", error);
            selectElement.innerHTML = '<option value="">Error loading models</option>';
            if (typeof showToast === 'function') showToast("Could not load AI models.", "error");
        }
    }

    return {
        initialize,
        loadAndPopulateModels
    };
})();