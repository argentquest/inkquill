// /story_app/app/static/js/story_form_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Story Form Handler: DOMContentLoaded event fired.");

    const storyForm = document.getElementById('story-form');
    const storyFormErrorMessage = document.getElementById('story-form-error-message');
    const saveStoryButton = document.getElementById('save-story-button');
    const imageStyleSelect = document.getElementById('image_style_select');

    const API_BASE_URL = "/api/v1";

    async function loadStylePrompts() {
        if (!imageStyleSelect) return;
        console.log("Story Form Handler: Loading image style prompts...");

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
            console.error("Error loading image style prompts for story form:", error);
            showToast("Could not load image style prompts.", "warning");
        }
    }

    if (storyForm && saveStoryButton) {
        
        loadStylePrompts();

        storyForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 

            if (storyFormErrorMessage) {
                storyFormErrorMessage.textContent = '';
                storyFormErrorMessage.style.display = 'none';
            }

            const originalButtonText = saveStoryButton.textContent;
            saveStoryButton.disabled = true;
            const isEditMode = storyForm.dataset.pageAction === "Edit";
            saveStoryButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> ${isEditMode ? "Saving..." : "Creating..."}`;

            const formData = new FormData(storyForm);
            const data = {};
            formData.forEach((value, key) => {
                if (key === 'image_style_select') return;
                if (typeof value === 'string') {
                    if (value.trim() !== '' || ['title', 'world_id'].includes(key)) { 
                        data[key] = value.trim(); 
                    } else if (value.trim() === '') {
                        data[key] = null;
                    }
                } else {
                    data[key] = value;
                }
            });

            if (data.world_id) {
                data.world_id = parseInt(data.world_id, 10);
            }
            if (data.short_description === undefined) data.short_description = null;
            if (data.image_prompt_definition === undefined) data.image_prompt_definition = null;

            const formActionUrl = storyForm.action;
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
                    showToast(`Story ${isEditMode ? 'updated' : 'created'} successfully!`, "success");
                    if (!isEditMode && result.id) {
                        window.location.href = `/ui/stories/${result.id}/edit`;
                    }
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const errorMessage = errorData.detail || "An unknown error occurred.";
                    if (storyFormErrorMessage) {
                        storyFormErrorMessage.textContent = errorMessage;
                        storyFormErrorMessage.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error");
                    }
                }
            } catch (error) {
                const networkErrorMsg = 'An error occurred. Please check your connection.';
                if (storyFormErrorMessage) {
                    storyFormErrorMessage.textContent = networkErrorMsg;
                    storyFormErrorMessage.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                if (saveStoryButton) {
                    saveStoryButton.disabled = false;
                    saveStoryButton.innerHTML = originalButtonText;
                }
            }
        });
    } else {
        console.warn("Story form elements not found. Handler not attached.");
    }
});
