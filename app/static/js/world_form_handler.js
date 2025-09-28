// /ai_rag_story_app/app/static/js/world_form_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("World Form Handler: DOMContentLoaded event fired.");

    const worldForm = document.getElementById('world-form');
    const worldFormErrorMessage = document.getElementById('world-form-error-message');
    const saveWorldButton = document.getElementById('save-world-button');
    const imageStyleSelect = document.getElementById('image_style_select');
    
    const API_BASE_URL = "/api/v1";

    async function loadStylePrompts() {
        if (!imageStyleSelect) {
            console.log("World Form Handler: No image style select element found.");
            return;
        }
        console.log("World Form Handler: Loading image style prompts...");

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
            console.error("Error loading image style prompts for world form:", error);
            showToast("Could not load image style prompts.", "warning");
        }
    }

    if (worldForm && saveWorldButton) {
        
        loadStylePrompts();

        worldForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 

            if (worldFormErrorMessage) {
                worldFormErrorMessage.textContent = '';
                worldFormErrorMessage.style.display = 'none';
            }

            const originalButtonText = saveWorldButton.textContent;
            saveWorldButton.disabled = true;
            const isEditMode = worldForm.dataset.pageAction === "Edit";
            saveWorldButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> ${isEditMode ? "Saving..." : "Creating..."}`;

            const formData = new FormData(worldForm);
            const data = {};
            formData.forEach((value, key) => {
                if (key === 'image_style_select') return;
                if (typeof value === 'string') {
                    if (value.trim() !== '' || key === 'name') { 
                        data[key] = value.trim(); 
                    } else if (value.trim() === '') {
                        data[key] = null;
                    }
                } else {
                    data[key] = value;
                }
            });

            // Handle checkbox for is_free_chat_enabled
            const isFreeChat = document.getElementById('is_free_chat_enabled');
            data.is_free_chat_enabled = isFreeChat ? isFreeChat.checked : false;

            // Ensure optional fields have proper defaults
            if (data.description === undefined) data.description = null;
            if (data.short_description === undefined) data.short_description = null;
            if (data.image_prompt_definition === undefined) data.image_prompt_definition = null;

            const formActionUrl = worldForm.action;
            const httpMethod = isEditMode ? 'PUT' : 'POST';

            try {
                const response = await fetch(formActionUrl, {
                    method: httpMethod,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                    credentials: 'include'
                });

                if (response.ok) {
                    const result = await response.json();
                    showToast(`World ${isEditMode ? 'updated' : 'created'} successfully!`, "success");
                    if (!isEditMode && result.id) {
                        window.location.href = `/ui/worlds/${result.id}/edit`;
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || "An unknown error occurred.";
                    if (worldFormErrorMessage) {
                        worldFormErrorMessage.textContent = errorMessage;
                        worldFormErrorMessage.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error");
                    }
                }
            } catch (error) {
                const networkErrorMsg = 'An error occurred. Please check your connection.';
                if (worldFormErrorMessage) {
                    worldFormErrorMessage.textContent = networkErrorMsg;
                    worldFormErrorMessage.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                if (saveWorldButton) {
                    saveWorldButton.disabled = false;
                    saveWorldButton.innerHTML = originalButtonText;
                }
            }
        });
    }
});