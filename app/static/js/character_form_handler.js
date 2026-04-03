// /story_app/app/static/js/character_form_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Character Form Handler: DOMContentLoaded event fired. (v_style_prompt_load_fix)");

    const characterForm = document.getElementById('character-form');
    const characterFormErrorMessage = document.getElementById('character-form-error-message');
    const saveCharacterButton = document.getElementById('save-character-button');
    
    const generatedContextDisplay = document.getElementById('generated-context-display');
    const characterIdForContext = characterForm ? characterForm.dataset.characterId : null;
    const isEditMode = characterForm ? characterForm.dataset.pageAction === "Edit" : false;
    const worldId = characterForm ? characterForm.dataset.worldId : null;
    
    const currentLocationSelect = document.getElementById('current_location_id');
    const imageStyleSelect = document.getElementById('image_style_select');
    
    const API_BASE_URL = "/api/v1";

    async function loadLocationsForDropdown() {
        if (!currentLocationSelect || !worldId) return;
        try {
            const response = await fetch(`${API_BASE_URL}/worlds/${worldId}/locations?limit=500`, { credentials: 'include' });
            if (!response.ok) {
                console.warn("Failed to load locations for character form:", response.status);
                return;
            }
            const locations = await response.json();
            
            while (currentLocationSelect.children.length > 1) {
                currentLocationSelect.removeChild(currentLocationSelect.lastChild);
            }
            locations.forEach(location => {
                const option = document.createElement('option');
                option.value = location.id;
                const scaleText = location.scale ? ` (${location.scale.replace('_', ' ')})` : '';
                option.textContent = `${location.name}${scaleText}`;
                currentLocationSelect.appendChild(option);
            });
            const currentValue = currentLocationSelect.dataset.currentValue;
            if (currentValue) {
                currentLocationSelect.value = currentValue;
            }
        } catch (error) {
            console.error("Error loading locations for character form:", error);
        }
    }

    async function loadStylePrompts() {
        if (!imageStyleSelect) {
            console.log("Character Form Handler: No image style select element found.");
            return;
        }
        console.log("Character Form Handler: Loading image style prompts...");

        try {
            const [myStylesRes, sharedStylesRes] = await Promise.all([
                fetch(`${API_BASE_URL}/prompts/my-prompts?filter_prompt_type=IMAGE_STYLE&filter_is_active=true`, { credentials: 'include' }),
                fetch(`${API_BASE_URL}/prompts/shared?filter_prompt_type=IMAGE_STYLE&filter_is_active=true`, { credentials: 'include' })
            ]);

            const myStyles = myStylesRes.ok ? await myStylesRes.json() : [];
            const sharedStyles = sharedStylesRes.ok ? await sharedStylesRes.json() : [];
            
            const combinedStyles = [];
            const seenIds = new Set();
            
            myStyles.forEach(p => {
                if (p && p.id && !seenIds.has(p.id)) { combinedStyles.push(p); seenIds.add(p.id); }
            });
            sharedStyles.forEach(p => {
                if (p && p.id && !seenIds.has(p.id)) { combinedStyles.push(p); }
            });

            while (imageStyleSelect.children.length > 1) {
                imageStyleSelect.removeChild(imageStyleSelect.lastChild);
            }
            
            combinedStyles.sort((a,b) => a.title.localeCompare(b.title)).forEach(style => {
                const option = document.createElement('option');
                option.value = style.prompt_content;
                option.textContent = style.title;
                imageStyleSelect.appendChild(option);
            });

        } catch (error) {
            console.error("Error loading image style prompts:", error);
            showToast("Could not load image style prompts.", "warning");
        }
    }

    async function fetchAndDisplayGeneratedContext(elementId, displayElement, apiUrl) {
        if (!displayElement) return;
        if (!elementId) {
            displayElement.textContent = "N/A (Save character first to generate context)";
            return;
        }
        displayElement.textContent = "Loading AI-generated context...";

        try {
            const response = await fetch(apiUrl, { credentials: 'include' });
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                displayElement.textContent = errData.error || `Failed to load context: ${response.statusText}`;
                return;
            }
            const data = await response.json();
            if (data.error) {
                displayElement.textContent = data.error;
            } else if (data.content !== null && data.content !== undefined) {
                displayElement.textContent = data.content;
            } else {
                displayElement.textContent = "No AI-generated context found for this character.";
            }
        } catch (error) {
            console.error("Network error fetching generated context:", error);
            displayElement.textContent = "Failed to load context due to a network error.";
        }
    }

    if (characterForm && saveCharacterButton) {
        if (isEditMode && characterIdForContext && generatedContextDisplay) {
            const apiUrl = `${API_BASE_URL}/characters/${characterIdForContext}/generated-context`;
            fetchAndDisplayGeneratedContext(characterIdForContext, generatedContextDisplay, apiUrl);
        } else if (generatedContextDisplay && !isEditMode) {
            generatedContextDisplay.textContent = "AI-generated context will appear here after the character is first saved.";
        }
        
        loadLocationsForDropdown();
        loadStylePrompts(); // <-- FIX: This call was missing

        characterForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            if (characterFormErrorMessage) {
                characterFormErrorMessage.textContent = '';
                characterFormErrorMessage.style.display = 'none';
            }

            const originalButtonText = saveCharacterButton.textContent;
            saveCharacterButton.disabled = true;
            saveCharacterButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> ${isEditMode ? "Saving..." : "Creating..."}`;

            const formData = new FormData(characterForm);
            const data = {}; 

            formData.forEach((value, key) => {
                if (key === 'image_style_select') return;
                if (typeof value === 'string') {
                    if (value.trim() !== '' || key === 'name') { 
                        data[key] = value.trim(); 
                    } else if (['description', 'personality_traits', 'backstory', 'placement_note', 'image_prompt_definition', 'relationships'].includes(key) && value.trim() === '') {
                        data[key] = null; 
                    }
                } else {
                     data[key] = value;
                }
            });

            if (data.current_location_id === '' || data.current_location_id === undefined) {
                data.current_location_id = null;
            } else if (data.current_location_id) {
                data.current_location_id = parseInt(data.current_location_id);
            }

            if (data.importance_rating === '' || data.importance_rating === undefined) {
                data.importance_rating = null;
            } else if (data.importance_rating) {
                data.importance_rating = parseInt(data.importance_rating);
            }
            
            const formActionUrl = characterForm.action;
            const httpMethod = isEditMode ? 'PUT' : 'POST';
            
            if (data.hasOwnProperty('world_id')) { delete data.world_id; }

            try {
                const response = await fetch(formActionUrl, {
                    method: httpMethod,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                    credentials: 'include'
                });

                if (response.ok) {
                    const result = await response.json();
                    
                    // Track character creation/update
                    if (window.trackFeatureUse) {
                        const action = isEditMode ? 'character_updated' : 'character_created';
                        window.trackFeatureUse('world_building', action);
                    }
                    
                    showToast(`Character ${isEditMode ? 'updated' : 'created'} successfully!`, "success");
                    
                    if (!isEditMode && result.id) {
                        window.location.href = `/ui/worlds/characters/${result.id}/edit`;
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || "An unknown error occurred.";
                    if (characterFormErrorMessage) {
                        characterFormErrorMessage.textContent = errorMessage;
                        characterFormErrorMessage.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error");
                    }
                }
            } catch (error) {
                const networkErrorMsg = 'An error occurred. Please check your connection and try again.';
                if (characterFormErrorMessage) {
                    characterFormErrorMessage.textContent = networkErrorMsg;
                    characterFormErrorMessage.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                if (saveCharacterButton) {
                    saveCharacterButton.disabled = false;
                    saveCharacterButton.innerHTML = originalButtonText;
                }
            }
        });
    } else {
        console.warn("Character form elements not found. Handler not attached.");
    }
});

