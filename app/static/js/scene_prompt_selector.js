// /story_app/app/static/js/scene_prompt_selector.js
"use strict";

const ScenePromptSelector = (() => {
    let fetchedPromptsCacheScene = [];
    const API_BASE_URL = "/api/v1";

    const promptSelectDropdownIdScene = 'scene-ai-personal-prompt-select';
    const promptTypeFilterDropdownIdScene = 'scene-prompt-type-filter-dropdown';
    const aiPromptInputIdScene = 'scene-ai-instruction';
    const clearSelectedPromptButtonIdScene = 'scene-clear-selected-personal-prompt-button';
    const noPromptsMessageIdScene = 'scene-no-personal-prompts-message';

    function _populateDropdownWithOptionsScene(prompts, dropdownElement, noPromptsMsgElement, currentUserId) {
        if (!dropdownElement) {
            console.warn("ScenePromptSelector: Dropdown element not found for populating.");
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

    function _filterPromptsByTypeScene(prompts, promptType) {
        if (!promptType) return prompts;
        return prompts.filter(prompt => prompt.prompt_type === promptType);
    }

    function _updatePromptDropdownScene() {
        const typeFilterElement = document.getElementById(promptTypeFilterDropdownIdScene);
        const dropdownElement = document.getElementById(promptSelectDropdownIdScene);
        const noPromptsMsgElement = document.getElementById(noPromptsMessageIdScene);
        
        if (!dropdownElement) return;
        
        // If no type filter element exists, show all prompts
        const selectedType = typeFilterElement ? typeFilterElement.value : null;
        const filteredPrompts = _filterPromptsByTypeScene(fetchedPromptsCacheScene, selectedType);
        
        // Get current user ID from a global variable or data attribute if available
        const currentUserIdElement = document.getElementById('current-user-id');
        const currentUserId = currentUserIdElement ? parseInt(currentUserIdElement.value, 10) : (window.currentUserId || null);
        
        _populateDropdownWithOptionsScene(filteredPrompts, dropdownElement, noPromptsMsgElement, currentUserId);
        
        // Clear the prompt input when filter changes
        const aiPromptInputElement = document.getElementById(aiPromptInputIdScene);
        const clearButtonElement = document.getElementById(clearSelectedPromptButtonIdScene);
        if (aiPromptInputElement) aiPromptInputElement.value = "";
        if (clearButtonElement) clearButtonElement.style.display = 'none';
    }

    async function fetchAndPopulatePromptsScene(currentUserId) {
        const dropdownElement = document.getElementById(promptSelectDropdownIdScene);
        const noPromptsMsgElement = document.getElementById(noPromptsMessageIdScene);

        if (!dropdownElement) {
            console.warn("ScenePromptSelector: Scene prompt select dropdown not found during fetch.");
            return;
        }
        
        fetchedPromptsCacheScene = []; 

        try {
            const [myPromptsRes, sharedPromptsRes] = await Promise.all([
                fetch(`${API_BASE_URL}/prompts/my-prompts?limit=200&filter_is_active=true`, { credentials: 'include' }),
                fetch(`${API_BASE_URL}/prompts/shared?limit=200&filter_is_active=true`, { credentials: 'include' })
            ]);

            const myPrompts = myPromptsRes.ok ? await myPromptsRes.json() : [];
            const sharedPrompts = sharedPromptsRes.ok ? await sharedPromptsRes.json() : [];
            
            let combinedPrompts = [];
            const seenIds = new Set();

            myPrompts.forEach(p => {
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
            
            
            fetchedPromptsCacheScene = combinedPrompts; 
            
            // Initial population with all prompts (filtered by current type filter if any)
            _updatePromptDropdownScene();

        } catch (error) {
            console.error("ScenePromptSelector: Error fetching prompts for Scene editor dropdown:", error);
            if (noPromptsMsgElement) { 
                noPromptsMsgElement.textContent = "Could not load prompts."; 
                noPromptsMsgElement.style.display = 'block';
            }
            if (typeof showToast === 'function') showToast("Error loading prompts for Scene editor.", "error");
        }
    }

    function setupEventListenersScene() {
        const dropdownElement = document.getElementById(promptSelectDropdownIdScene);
        const typeFilterElement = document.getElementById(promptTypeFilterDropdownIdScene);
        const aiPromptInputElement = document.getElementById(aiPromptInputIdScene);
        const clearButtonElement = document.getElementById(clearSelectedPromptButtonIdScene);

        // Type filter change listener (only if it exists)
        if (typeFilterElement) {
            typeFilterElement.addEventListener('change', () => {
                _updatePromptDropdownScene();
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
            console.warn("ScenePromptSelector: Dropdown or AI prompt input not found for event listener setup.");
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
                    _updatePromptDropdownScene();
                }
            });
        } else {
             console.warn("ScenePromptSelector: Clear button, dropdown or AI prompt input not found for clear listener setup.");
        }
    }
    
    function initializeScene(currentUserId) {
        console.log("ScenePromptSelector: Initializing...");
        const dropdownElement = document.getElementById(promptSelectDropdownIdScene);
        const typeFilterElement = document.getElementById(promptTypeFilterDropdownIdScene);
        const clearButtonElement = document.getElementById(clearSelectedPromptButtonIdScene);
        
        
        if (dropdownElement) {
            // Set up event listeners first
            setupEventListenersScene();
            // Then fetch and populate prompts
            fetchAndPopulatePromptsScene(currentUserId);
            if(clearButtonElement) clearButtonElement.style.display = 'none'; 
        } else {
            console.log("ScenePromptSelector: Scene prompt select dropdown not found on this page. Manager not fully initialized.");
        }
    }

    return {
        initialize: initializeScene 
    };
})();
