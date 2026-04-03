// /story_app/app/static/js/act_prompt_manager.js
"use strict";

const ActPromptManager = (() => {
    let fetchedPromptsCache = [];
    const API_BASE_URL = "/api/v1";

    const promptSelectDropdownId = 'prompt-select-dropdown';
    const promptTypeFilterDropdownId = 'act-prompt-type-filter-dropdown';
    const aiPromptInputId = 'ai-prompt-input';
    const clearSelectedPromptButtonId = 'clear-selected-prompt-button';
    const noPromptsMessageId = 'act-no-prompts-message';

    function _populateDropdownWithOptions(prompts, dropdownElement, noPromptsMsgElement, currentUserId) {
        if (!dropdownElement) {
            console.warn("ActPromptManager: Dropdown element not found for populating.");
            return;
        }
        dropdownElement.innerHTML = '<option value="">-- Select a prompt --</option>'; 
        
        if (prompts && prompts.length > 0) {
            // Sort alphabetically by title
            const sortedPrompts = prompts.sort((a, b) => (a.title || "Untitled Prompt").localeCompare(b.title || "Untitled Prompt"));
            
            sortedPrompts.forEach(prompt => {
                const option = document.createElement('option');
                option.value = prompt.prompt_content; 
                
                let ownerDisplay = 'System/Shared';
                if (prompt.owner) { 
                    ownerDisplay = prompt.owner.display_name || prompt.owner.username || `User ID ${prompt.user_id}`;
                    if (currentUserId && prompt.user_id === currentUserId) {
                        ownerDisplay = "Me";
                    }
                } else if (prompt.user_id) {
                     ownerDisplay = `User ID ${prompt.user_id}`; 
                }
                
                let promptTypeDisplay = prompt.prompt_type ? prompt.prompt_type.replace('_', ' ') : "Unknown";
                const titleText = prompt.title ? prompt.title : "Untitled Prompt";
                option.textContent = `${titleText} - ${promptTypeDisplay} - By: ${ownerDisplay}`;
                dropdownElement.appendChild(option);
            });
            if (noPromptsMsgElement) noPromptsMsgElement.style.display = 'none';
        } else {
            if (noPromptsMsgElement) { 
                noPromptsMsgElement.textContent = "No prompts found for selected type."; 
                noPromptsMsgElement.style.display = 'block';
            }
        }
    }

    function _filterPromptsByType(prompts, promptType) {
        if (!promptType) return prompts;
        return prompts.filter(prompt => prompt.prompt_type === promptType);
    }

    function _updatePromptDropdown() {
        const typeFilterElement = document.getElementById(promptTypeFilterDropdownId);
        const dropdownElement = document.getElementById(promptSelectDropdownId);
        const noPromptsMsgElement = document.getElementById(noPromptsMessageId);
        
        if (!dropdownElement) return;
        
        // If no type filter element exists, show all prompts
        const selectedType = typeFilterElement ? typeFilterElement.value : null;
        const filteredPrompts = _filterPromptsByType(fetchedPromptsCache, selectedType);
        
        // Get current user ID from a global variable or data attribute if available
        const currentUserIdElement = document.getElementById('current-user-id');
        const currentUserId = currentUserIdElement ? parseInt(currentUserIdElement.value, 10) : (window.currentUserId || null);
        
        _populateDropdownWithOptions(filteredPrompts, dropdownElement, noPromptsMsgElement, currentUserId);
        
        // Clear the prompt input when filter changes
        const aiPromptInputElement = document.getElementById(aiPromptInputId);
        const clearButtonElement = document.getElementById(clearSelectedPromptButtonId);
        if (aiPromptInputElement) aiPromptInputElement.value = "";
        if (clearButtonElement) clearButtonElement.style.display = 'none';
    }

    async function fetchAndPopulatePrompts(currentUserId) {
        const dropdownElement = document.getElementById(promptSelectDropdownId);
        const noPromptsMsgElement = document.getElementById(noPromptsMessageId);

        if (!dropdownElement) {
            console.warn("ActPromptManager: Act prompt select dropdown not found during fetch.");
            return;
        }
        
        fetchedPromptsCache = []; 

        try {
            console.log("ActPromptManager: Fetching all active 'my' and 'shared' prompts (excluding SYSTEM).");
            const [myPromptsRes, sharedPromptsRes] = await Promise.all([
                // --- MODIFIED: Changed limit from 500 to 200 ---
                fetch(`${API_BASE_URL}/prompts/my-prompts?limit=200&filter_is_active=true`, { credentials: 'include' }),
                fetch(`${API_BASE_URL}/prompts/shared?limit=200&filter_is_active=true`, { credentials: 'include' })
                // --- END MODIFICATION ---
            ]);

            const myPrompts = myPromptsRes.ok ? await myPromptsRes.json() : [];
            const sharedPrompts = sharedPromptsRes.ok ? await sharedPromptsRes.json() : [];
            
            let combinedPrompts = [];
            const seenIds = new Set();

            myPrompts.forEach(p => {
                // Added check for p.title existence for sorting
                if (p && p.id && p.prompt_type && p.prompt_type !== 'SYSTEM') { 
                    combinedPrompts.push(p);
                    seenIds.add(p.id);
                }
            });

            sharedPrompts.forEach(p => {
                if (p && p.id && !seenIds.has(p.id) && p.prompt_type && p.prompt_type !== 'SYSTEM') { 
                    combinedPrompts.push(p);
                }
            });
            
            fetchedPromptsCache = combinedPrompts; 
            
            // Initial population with all prompts (filtered by current type filter if any)
            _updatePromptDropdown();

        } catch (error) {
            console.error("ActPromptManager: Error fetching prompts for Act editor dropdown:", error);
            if (noPromptsMsgElement) { 
                noPromptsMsgElement.textContent = "Could not load prompts."; 
                noPromptsMsgElement.style.display = 'block';
            }
            if (typeof showToast === 'function') showToast("Error loading prompts for Act editor.", "error");
        }
    }

    function setupEventListeners() {
        const dropdownElement = document.getElementById(promptSelectDropdownId);
        const typeFilterElement = document.getElementById(promptTypeFilterDropdownId);
        const aiPromptInputElement = document.getElementById(aiPromptInputId);
        const clearButtonElement = document.getElementById(clearSelectedPromptButtonId);

        // Type filter change listener (only if it exists)
        if (typeFilterElement) {
            typeFilterElement.addEventListener('change', () => {
                _updatePromptDropdown();
            });
        }

        // Prompt selection listener
        if (dropdownElement && aiPromptInputElement) {
            dropdownElement.addEventListener('change', () => {
                if (dropdownElement.value) {
                    aiPromptInputElement.value = dropdownElement.value;
                    if (clearButtonElement) clearButtonElement.style.display = 'inline-block';
                } else {
                    if (clearButtonElement) clearButtonElement.style.display = 'none';
                }
            });
        } else {
            console.warn("ActPromptManager: Dropdown or AI prompt input not found for event listener setup.");
        }

        // Clear button listener
        if (clearButtonElement && dropdownElement && aiPromptInputElement) {
            clearButtonElement.addEventListener('click', () => {
                dropdownElement.value = "";
                aiPromptInputElement.value = ""; 
                clearButtonElement.style.display = 'none';
                // Also reset the type filter
                if (typeFilterElement) {
                    typeFilterElement.value = "";
                    _updatePromptDropdown();
                }
            });
        } else {
             console.warn("ActPromptManager: Clear button, dropdown or AI prompt input not found for clear listener setup.");
        }
    }
    
    function initialize(currentUserId) {
        console.log("ActPromptManager: Initializing...");
        const dropdownElement = document.getElementById(promptSelectDropdownId);
        const clearButtonElement = document.getElementById(clearSelectedPromptButtonId);
        
        if (dropdownElement) {
            // Set up event listeners first
            setupEventListeners();
            // Then fetch and populate prompts
            fetchAndPopulatePrompts(currentUserId);
            if(clearButtonElement) clearButtonElement.style.display = 'none'; 
        } else {
            console.log("ActPromptManager: Prompt select dropdown not found for Act editor. Manager not fully initialized.");
        }
    }

    return {
        initialize: initialize
    };
})();
