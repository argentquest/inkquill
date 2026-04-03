// /story_app/app/static/js/lore_item_form_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Lore Item Form Handler: DOMContentLoaded");

    const loreItemForm = document.getElementById('lore-item-form');
    const loreItemFormErrorMessage = document.getElementById('lore-item-form-error-message');
    const saveLoreItemButton = document.getElementById('save-lore-item-button');

    const generatedContextDisplay = document.getElementById('generated-context-display-lore');
    const loreItemId = loreItemForm ? loreItemForm.dataset.loreItemId : null;
    const isEditMode = !!loreItemId;
    const worldId = loreItemForm ? loreItemForm.dataset.worldId : null;
    
    const currentLocationSelect = document.getElementById('current_location_id');
    const imageStyleSelect = document.getElementById('image_style_select');
    
    const API_BASE_URL = "/api/v1";

    async function loadLocationsForDropdown() {
        if (!currentLocationSelect || !worldId) return;
        try {
            const response = await fetch(`${API_BASE_URL}/worlds/${worldId}/locations?limit=1000`, { credentials: 'include' });
            if (!response.ok) return;
            const locations = await response.json();
            
            while (currentLocationSelect.children.length > 1) {
                currentLocationSelect.removeChild(currentLocationSelect.lastChild);
            }
            locations.forEach(location => {
                const option = document.createElement('option');
                option.value = location.id;
                option.textContent = `${location.name}${location.scale ? ` (${location.scale.replace('_', ' ')})` : ''}`;
                currentLocationSelect.appendChild(option);
            });
            const currentValue = currentLocationSelect.dataset.currentValue;
            if (currentValue) {
                currentLocationSelect.value = currentValue;
            }
        } catch (error) {
            console.error("Error loading locations for lore item form:", error);
        }
    }

    async function loadStylePrompts() {
        if (!imageStyleSelect) return;
        try {
            const [myStylesRes, sharedStylesRes] = await Promise.all([
                fetch(`${API_BASE_URL}/prompts/my-prompts?filter_prompt_type=IMAGE_STYLE&filter_is_active=true`, { credentials: 'include' }),
                fetch(`${API_BASE_URL}/prompts/shared?filter_prompt_type=IMAGE_STYLE&filter_is_active=true`, { credentials: 'include' })
            ]);
            const myStyles = myStylesRes.ok ? await myStylesRes.json() : [];
            const sharedStyles = sharedStylesRes.ok ? await sharedStylesRes.json() : [];
            const combinedStyles = [];
            const seenIds = new Set();
            myStyles.forEach(p => { if (p && p.id && !seenIds.has(p.id)) { combinedStyles.push(p); seenIds.add(p.id); } });
            sharedStyles.forEach(p => { if (p && p.id && !seenIds.has(p.id)) { combinedStyles.push(p); } });
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
        }
    }

    async function fetchAndDisplayGeneratedContext(elementId, displayElement, apiUrl) {
        if (!displayElement) return;
        if (!elementId) {
            displayElement.textContent = "N/A (Save lore item first to generate context)";
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
                displayElement.textContent = "No AI-generated context found for this lore item.";
            }
        } catch (error) {
            console.error("Network error fetching generated context for lore item:", error);
            displayElement.textContent = "Failed to load context due to a network error.";
        }
    }

    if (loreItemForm && saveLoreItemButton) {
        if (isEditMode && generatedContextDisplay) {
            const apiUrl = `${API_BASE_URL}/lore-items/${loreItemId}/generated-context`;
            fetchAndDisplayGeneratedContext(loreItemId, generatedContextDisplay, apiUrl);
        } else if (generatedContextDisplay) {
            generatedContextDisplay.textContent = "AI-generated context will appear here after the lore item is first saved.";
        }

        loadLocationsForDropdown();
        loadStylePrompts();

        // The save button is now type="button" to prevent default form submission
        saveLoreItemButton.addEventListener('click', async (event) => {
            event.preventDefault();

            if (loreItemFormErrorMessage) {
                loreItemFormErrorMessage.textContent = '';
                loreItemFormErrorMessage.style.display = 'none';
            }

            const originalButtonText = saveLoreItemButton.textContent;
            saveLoreItemButton.disabled = true;
            saveLoreItemButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> ${isEditMode ? "Saving..." : "Creating..."}`;

            const formData = new FormData(loreItemForm);
            const data = {};

            formData.forEach((value, key) => {
                if (key === 'image_style_select') return;
                if (typeof value === 'string' && (value.trim() !== '' || ['title', 'category'].includes(key))) {
                    data[key] = value.trim();
                } else if (value) {
                    data[key] = value;
                }
            });
            
            if (data.current_location_id === '' || data.current_location_id === undefined) {
                data.current_location_id = null;
            } else {
                data.current_location_id = parseInt(data.current_location_id, 10);
            }
            
            if (data.importance_rating === '' || data.importance_rating === undefined) {
                data.importance_rating = null;
            } else if (data.importance_rating) {
                data.importance_rating = parseInt(data.importance_rating);
            }
            
            ['placement_note', 'related_elements'].forEach(field => {
                if (data[field] === undefined) data[field] = null;
            });
            
            const formActionUrl = loreItemForm.action;
            const httpMethod = isEditMode ? 'PUT' : 'POST';
            
            if (data.hasOwnProperty('world_id')) delete data.world_id;

            try {
                const response = await fetch(formActionUrl, {
                    method: httpMethod,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                    credentials: 'include'
                });

                if (response.ok) {
                    const result = await response.json();
                    
                    // Track lore item creation/update
                    if (window.trackFeatureUse) {
                        const action = isEditMode ? 'lore_item_updated' : 'lore_item_created';
                        window.trackFeatureUse('world_building', action);
                    }
                    
                    showToast(`Lore Item ${isEditMode ? 'updated' : 'created'} successfully!`, "success");
                    if (!isEditMode && result.id) {
                        window.location.href = `/ui/worlds/lore-items/${result.id}/edit`;
                    } else if (isEditMode && generatedContextDisplay) {
                        setTimeout(() => {
                           fetchAndDisplayGeneratedContext(result.id, generatedContextDisplay, `${API_BASE_URL}/lore-items/${result.id}/generated-context`);
                        }, 2000);
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || "An unknown error occurred.";
                    if (loreItemFormErrorMessage) {
                        loreItemFormErrorMessage.textContent = errorMessage;
                        loreItemFormErrorMessage.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error");
                    }
                }
            } catch (error) {
                const networkErrorMsg = 'An error occurred. Please check your connection.';
                if (loreItemFormErrorMessage) {
                    loreItemFormErrorMessage.textContent = networkErrorMsg;
                    loreItemFormErrorMessage.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                if (saveLoreItemButton) {
                    saveLoreItemButton.disabled = false;
                    saveLoreItemButton.innerHTML = originalButtonText;
                }
            }
        });
    } else {
        console.warn("Lore Item form elements not found. Handler not attached.");
    }
});

