// /ai_rag_story_app/app/static/js/act_form_handler.js

/**
 * act_form_handler.js
 * -------------------
 * Handles the asynchronous submission of the act creation and edit forms.
 * It intercepts the default form submission, collects data including new fields
 * (act_summary, writer_notes, system_prompt_id), gets HTML content from Quill editor
 * for the description, sends it as JSON to the API, and handles the response.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const actForm = document.getElementById('act-form');
    const actFormErrorMessage = document.getElementById('act-form-error-message');
    const saveActButton = document.getElementById('save-act-button');
    
    // Reference to the div Quill is initialized on for the 'description' field
    const descriptionEditorDiv = document.getElementById('description-editor'); 
    // The hidden textarea that might hold initial content for Quill
    const descriptionHiddenTextarea = document.getElementById('description');
    
    // Story class dropdown
    const storyClassSelect = document.getElementById('story_class_id');

    const API_BASE_URL = "/api/v1"; // Ensure this matches your API prefix
    
    // Load story classes on page load
    loadStoryClasses();

    if (actForm && saveActButton) {
        actForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default synchronous form submission

            // Clear previous error messages
            if (actFormErrorMessage) {
                actFormErrorMessage.textContent = '';
                actFormErrorMessage.style.display = 'none';
            }
            
            const originalButtonText = saveActButton.textContent;
            saveActButton.disabled = true;
            saveActButton.textContent = actForm.dataset.pageAction === "Edit" ? "Saving..." : "Creating...";

            // Collect form data
            const formData = new FormData(actForm);
            const data = {};
            formData.forEach((value, key) => {
                // Skip 'description' here, we'll get it from Quill editor instance
                if (key === 'description') return; 

                if (key === 'act_number') {
                    data[key] = parseInt(value, 10); // Ensure act_number is an integer
                } else if (key === 'system_prompt_id' || key === 'story_class_id') {
                    // Convert IDs to integer if a value is selected, otherwise null
                    data[key] = value ? parseInt(value, 10) : null;
                } else if (value.trim() !== '' || key === 'title') { // title is required
                    data[key] = value;
                } else if ((key === 'act_summary' || key === 'writer_notes') && value.trim() === '') {
                    // Send null for empty optional text fields if desired by backend Pydantic model
                    data[key] = null; 
                }
            });

            // Get content from Quill editor for the 'description'
            if (descriptionEditorDiv && descriptionEditorDiv.__quill) { // Check if Quill instance is attached
                data.description = descriptionEditorDiv.__quill.root.innerHTML;
                // If Quill editor is empty, it might return '<p><br></p>', clean if needed
                if (data.description === '<p><br></p>') {
                    data.description = null; // Or "" depending on how your backend handles empty rich text
                }
            } else if (descriptionHiddenTextarea) { 
                // Fallback if Quill instance not found (e.g., JS error during Quill init)
                data.description = descriptionHiddenTextarea.value.trim() ? descriptionHiddenTextarea.value : null;
                console.warn("act_form_handler.js: Quill instance for 'description' not found, using hidden textarea value as fallback.");
            } else {
                data.description = null; // Default to null if no editor/textarea found
                console.warn("act_form_handler.js: Neither Quill editor nor hidden textarea for 'description' found.");
            }
            
            // Ensure optional fields that might not be in formData if empty are explicitly handled
            // (if they weren't textareas that would submit empty strings)
            if (!formData.has('act_summary') && data.act_summary === undefined) data.act_summary = null;
            if (!formData.has('writer_notes') && data.writer_notes === undefined) data.writer_notes = null;
            // system_prompt_id is handled by the select, if "" it becomes null above.
            if ((!formData.has('system_prompt_id') || formData.get('system_prompt_id') === "") && data.system_prompt_id === undefined) {
                data.system_prompt_id = null;
            }


            const formActionUrl = actForm.action; 
            const isEditMode = actForm.dataset.pageAction === "Edit";
            const httpMethod = isEditMode ? 'PUT' : 'POST';

            console.log("Submitting Act data. Description (HTML from Quill, first 100 chars):", data.description ? data.description.substring(0,100) + "..." : "null", "Other data:", data);
            console.log("URL:", formActionUrl, "Method:", httpMethod);

            try {
                const response = await fetch(formActionUrl, {
                    method: httpMethod,
                    headers: {
                        'Content-Type': 'application/json',
                        // Include CSRF token if needed
                    },
                    body: JSON.stringify(data),
                    credentials: 'include' // Crucial for sending HttpOnly cookies
                });

                if (response.ok) { 
                    const result = await response.json(); 
                    console.log("Act operation successful:", result);
                    alert(`Act ${isEditMode ? 'updated' : 'created'} successfully!`);

                    let storyIdToRedirect = actForm.dataset.storyId; 
                    if (isEditMode && result.story_id) {
                        storyIdToRedirect = result.story_id;
                    } else if (result.story_id) { 
                        storyIdToRedirect = result.story_id;
                    }

                    if (storyIdToRedirect) {
                        window.location.href = `/ui/stories/${storyIdToRedirect}`; 
                    } else {
                        window.location.href = '/ui/stories'; 
                    }

                } else {
                    const errorData = await response.json().catch(() => ({ detail: `Operation failed with status ${response.status}` }));
                    let errorMessage = errorData.detail || "An unknown error occurred.";
                    if (response.status === 409) { 
                        errorMessage = errorData.detail || "An act with this number might already exist for this story.";
                    } else if (response.status === 401) {
                        errorMessage = "Unauthorized. You may need to log in again.";
                    } else if (response.status === 403) {
                        errorMessage = "Forbidden. You do not have permission to perform this action.";
                    }
                    console.error("Act operation failed:", errorMessage, "Response data:", errorData);
                    if (actFormErrorMessage) {
                        actFormErrorMessage.textContent = errorMessage;
                        actFormErrorMessage.style.display = 'block';
                    } else {
                        alert(errorMessage);
                    }
                }
            } catch (error) {
                console.error('Error during act form submission:', error);
                const networkErrorMsg = 'An error occurred. Please check your connection and try again.';
                if (actFormErrorMessage) {
                    actFormErrorMessage.textContent = networkErrorMsg;
                    actFormErrorMessage.style.display = 'block';
                } else {
                    alert(networkErrorMsg);
                }
            } finally {
                if (saveActButton) {
                    saveActButton.disabled = false;
                    saveActButton.textContent = originalButtonText;
                }
            }
        });
    } else {
        console.warn("Act form elements (act-form, save-act-button) not found. Form submission handler not attached.");
    }
    
    async function loadStoryClasses() {
        if (!storyClassSelect) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/story-classes/options`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                console.warn('Failed to load story classes, using default options');
                return;
            }
            
            const storyClasses = await response.json();
            
            // Clear existing options except the first "No Class" option
            while (storyClassSelect.children.length > 1) {
                storyClassSelect.removeChild(storyClassSelect.lastChild);
            }
            
            // Add story class options
            storyClasses.forEach(storyClass => {
                const option = document.createElement('option');
                option.value = storyClass.id;
                option.textContent = storyClass.name;
                option.style.backgroundColor = storyClass.color;
                option.style.color = getBrightness(storyClass.color) > 128 ? '#000000' : '#ffffff';
                
                // Set selected if this is an edit and the act has this class
                const currentActClassId = getActClassIdFromPage();
                if (currentActClassId && currentActClassId == storyClass.id) {
                    option.selected = true;
                }
                
                storyClassSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading story classes:', error);
        }
    }
    
    function getActClassIdFromPage() {
        // Try to extract the current act's story_class_id from the page
        // This could be set as a data attribute or in a script tag
        const actForm = document.getElementById('act-form');
        return actForm ? actForm.dataset.actStoryClassId : null;
    }
    
    function getBrightness(hexColor) {
        // Convert hex to RGB and calculate brightness
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        return (r * 299 + g * 587 + b * 114) / 1000;
    }
});