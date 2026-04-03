// /story_app/app/static/js/location_form_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Location Form Handler: DOMContentLoaded event fired. (v_style_prompt_load_fix)");

    const locationForm = document.getElementById('location-form');
    const locationFormErrorMessage = document.getElementById('location-form-error-message');
    const saveLocationButton = document.getElementById('save-location-button');

    const generatedContextDisplayLoc = document.getElementById('generated-context-display-loc');
    const locationIdForContext = locationForm ? locationForm.dataset.locationId : null;
    const isEditModeLoc = locationForm ? locationForm.dataset.pageAction === "Edit" : false;
    
    const parentLocationSelect = document.getElementById('parent_location_id');
    const worldId = locationForm ? locationForm.dataset.worldId : null;
    
    // --- FIX: Add a reference to the image style select dropdown ---
    const imageStyleSelect = document.getElementById('image_style_select');
    // --- END FIX ---
    
    const API_BASE_URL = "/api/v1";

    console.log("Location Form Handler Initial State:", {
        locationFormExists: !!locationForm,
        generatedContextDisplayLocExists: !!generatedContextDisplayLoc,
        locationIdForContext: locationIdForContext,
        isEditModeLoc: isEditModeLoc
    });

    async function loadParentLocations() {
        if (!parentLocationSelect || !worldId) return;
        try {
            const response = await fetch(`${API_BASE_URL}/worlds/${worldId}/locations?limit=1000`, {
                credentials: 'include'
            });

            if (!response.ok) {
                console.error("Failed to load locations for parent dropdown:", response.status);
                return;
            }

            const locations = await response.json();
            
            while (parentLocationSelect.children.length > 1) {
                parentLocationSelect.removeChild(parentLocationSelect.lastChild);
            }

            const currentLocationId = parseInt(locationIdForContext);
            locations.forEach(location => {
                if (location.id !== currentLocationId) {
                    const option = document.createElement('option');
                    option.value = location.id;
                    option.textContent = `${location.name}${location.scale ? ` (${location.scale.replace('_', ' ')})` : ''}`;
                    if (isEditModeLoc && parentLocationSelect.dataset.currentValue && location.id === parseInt(parentLocationSelect.dataset.currentValue)) {
                        option.selected = true;
                    }
                    parentLocationSelect.appendChild(option);
                }
            });
        } catch (error) {
            console.error("Error loading parent locations:", error);
        }
    }
    
    // --- FIX: Add the function to load style prompts ---
    async function loadStylePrompts() {
        if (!imageStyleSelect) {
            console.log("Location Form Handler: No image style select element found.");
            return;
        }
        console.log("Location Form Handler: Loading image style prompts...");

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
            showToast("Could not load image style prompts.", "warning");
        }
    }
    // --- END FIX ---

    async function fetchAndDisplayGeneratedContext(elementId, displayElement, apiUrl) {
        if (!displayElement) return;
        if (!elementId) {
            displayElement.textContent = "N/A (Save location first to generate context)";
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
                displayElement.textContent = "No AI-generated context found for this location.";
            }
        } catch (error) {
            console.error("Network error fetching generated context:", error);
            displayElement.textContent = "Failed to load context due to a network error.";
        }
    }

    if (locationForm && saveLocationButton) {
        if (isEditModeLoc && locationIdForContext && generatedContextDisplayLoc) {
            const apiUrl = `${API_BASE_URL}/locations/${locationIdForContext}/generated-context`;
            fetchAndDisplayGeneratedContext(locationIdForContext, generatedContextDisplayLoc, apiUrl);
        } else if (generatedContextDisplayLoc && !isEditModeLoc) {
            generatedContextDisplayLoc.textContent = "AI-generated context will appear here after the location is first saved.";
        }
        
        loadParentLocations();
        loadStylePrompts(); // <-- FIX: Call the new function

        locationForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 
            // ... rest of the submit handler remains the same ...
            if (locationFormErrorMessage) {
                locationFormErrorMessage.textContent = '';
                locationFormErrorMessage.style.display = 'none';
            }

            const originalButtonText = saveLocationButton.textContent;
            saveLocationButton.disabled = true;
            saveLocationButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${isEditModeLoc ? "Saving..." : "Creating..."}`;

            const formData = new FormData(locationForm);
            const data = {};

            formData.forEach((value, key) => {
                if (key === 'image_style_select') return;
                if (value instanceof File) { return; }
                if (typeof value === 'string') {
                    if (value.trim() !== '' || key === 'name') { data[key] = value.trim(); } 
                    else if (key !== 'name' && value.trim() === '') { data[key] = null; }
                } else { data[key] = value; }
            });
            
            ['description', 'atmosphere', 'significance', 'image_prompt_definition', 'image_blob_path', 'dimension_unit', 'placement_note', 'geography', 'cultural_context', 'connected_elements'].forEach(field => {
                if (!formData.has(field) && data[field] === undefined) { data[field] = null; }
            });

            ['parent_location_id', 'map_x', 'map_y', 'map_z', 'dimension_x', 'dimension_y', 'dimension_z'].forEach(field => {
                if (data[field] === '' || data[field] === undefined) {
                    data[field] = null;
                } else if (data[field]) {
                    data[field] = parseFloat(data[field]);
                }
            });

            if (data.importance_rating === '' || data.importance_rating === undefined) {
                data.importance_rating = null;
            } else if (data.importance_rating) {
                data.importance_rating = parseInt(data.importance_rating);
            }

            if (data.scale === '') {
                data.scale = null;
            }

            const formActionUrl = locationForm.action;
            const httpMethod = isEditModeLoc ? 'PUT' : 'POST';
            
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
                    
                    // Track location creation/update
                    if (window.trackFeatureUse) {
                        const action = isEditModeLoc ? 'location_updated' : 'location_created';
                        window.trackFeatureUse('world_building', action);
                    }
                    
                    if (typeof showToast === 'function') {
                        showToast(`Location ${isEditModeLoc ? 'updated' : 'created'} successfully!`, "success");
                    }
                    
                    if (!isEditModeLoc && result.id) {
                        window.location.href = `/ui/worlds/locations/${result.id}/edit`;
                    } else if (isEditModeLoc && result.id && generatedContextDisplayLoc) {
                        setTimeout(() => {
                            fetchAndDisplayGeneratedContext(result.id, generatedContextDisplayLoc, `${API_BASE_URL}/locations/${result.id}/generated-context`);
                        }, 2000);
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || "An unknown error occurred.";
                    if (locationFormErrorMessage) {
                        locationFormErrorMessage.textContent = errorMessage;
                        locationFormErrorMessage.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error");
                    }
                }
            } catch (error) {
                const networkErrorMsg = 'An error occurred. Please check your connection.';
                if (locationFormErrorMessage) {
                    locationFormErrorMessage.textContent = networkErrorMsg;
                    locationFormErrorMessage.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                if (saveLocationButton) {
                    saveLocationButton.disabled = false;
                    saveLocationButton.innerHTML = originalButtonText;
                }
            }
        });
    } else {
        console.warn("Location form elements not found. Handler not attached.");
    }
});

