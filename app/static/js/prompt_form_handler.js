// /story_app/app/static/js/prompt_form_handler.js

/**
 * prompt_form_handler.js
 * ----------------------
 * Handles the asynchronous submission of the prompt creation and edit forms.
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const promptForm = document.getElementById('prompt-form');
    const promptFormErrorMessage = document.getElementById('prompt-form-error-message'); // For inline form errors
    const savePromptButton = document.getElementById('save-prompt-button');

    const API_BASE_URL = "/api/v1"; 

    if (promptForm && savePromptButton) {
        promptForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 

            if (promptFormErrorMessage) {
                promptFormErrorMessage.textContent = '';
                promptFormErrorMessage.style.display = 'none'; // Hide error display initially
            }

            const originalButtonText = savePromptButton.textContent;
            savePromptButton.disabled = true;
            savePromptButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${promptForm.dataset.pageAction === "Edit" ? "Saving..." : "Creating..."}`;

            const formData = new FormData(promptForm);
            const data = {};
            formData.forEach((value, key) => {
                // The 'is_active' checkbox is handled separately below, so we skip it here.
                if (key === 'is_active') {
                    return; 
                }
                // Include fields that have a value or are required (like title)
                if (value.trim() !== '' || ['title', 'prompt_content', 'prompt_type'].includes(key)) {
                    data[key] = value;
                } else if (['reason_to_use', 'comment'].includes(key) && value.trim() === '') {
                    // Send null for empty optional fields based on Pydantic model handling.
                    data[key] = null; 
                }
            });

            // --- FIX: Correctly handle the 'is_active' checkbox ---
            // An unchecked checkbox is not present in formData. `formData.has()` is the correct way to check for its presence.
            data.is_active = formData.has('is_active');
            // --- END FIX ---

            // Ensure optional fields not in formData (if empty and not touched) are null
            if (!formData.has('reason_to_use') && data.reason_to_use === undefined) data.reason_to_use = null;
            if (!formData.has('comment') && data.comment === undefined) data.comment = null;


            const formActionUrl = promptForm.action; 
            const isEditMode = promptForm.dataset.pageAction === "Edit";
            const httpMethod = isEditMode ? 'PUT' : 'POST';

            console.log("Submitting Prompt data:", data);
            console.log("URL:", formActionUrl, "Method:", httpMethod);

            try {
                const response = await fetch(formActionUrl, {
                    method: httpMethod,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                    credentials: 'include' 
                });

                if (response.ok) { 
                    const result = await response.json(); 
                    console.log("Prompt operation successful:", result);
                    showToast(`Prompt ${isEditMode ? 'updated' : 'created'} successfully!`, "success", 5000);
                    
                    // Redirect to the prompt library page after a short delay
                    setTimeout(() => {
                        window.location.href = '/ui/prompts'; 
                    }, 1500);

                } else {
                    const errorData = await response.json().catch(() => ({ detail: `Operation failed with status ${response.status}` }));
                    let errorMessage = errorData.detail || "An unknown error occurred.";
                     if (response.status === 401) {
                        errorMessage = "Unauthorized. You may need to log in again.";
                    } else if (response.status === 403) {
                        errorMessage = "Forbidden. You do not have permission to perform this action.";
                    } else if (response.status === 422) {
                        // Handle validation errors more gracefully if possible
                        if (Array.isArray(errorData.detail)) { // FastAPI validation errors
                            errorMessage = errorData.detail.map(err => `${err.loc.join('.')} - ${err.msg}`).join('; ');
                        } else {
                            errorMessage = errorData.detail || "Validation error.";
                        }
                    }
                    console.error("Prompt operation failed:", errorMessage, "Response data:", errorData);
                    if (promptFormErrorMessage) {
                        promptFormErrorMessage.textContent = errorMessage;
                        promptFormErrorMessage.style.display = 'block';
                    } else {
                        showToast(errorMessage, "error", 7000); // Longer display for errors
                    }
                }
            } catch (error) {
                console.error('Error during prompt form submission:', error);
                const networkErrorMsg = 'An error occurred. Please check your connection and try again.';
                if (promptFormErrorMessage) {
                    promptFormErrorMessage.textContent = networkErrorMsg;
                    promptFormErrorMessage.style.display = 'block';
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                if (savePromptButton) {
                    savePromptButton.disabled = false;
                    savePromptButton.innerHTML = originalButtonText;
                }
            }
        });
    } else {
        console.warn("Prompt form elements (prompt-form, save-prompt-button) not found. Handler not attached.");
    }
    console.log("Prompt form JS initialized with toast notifications.");
});
