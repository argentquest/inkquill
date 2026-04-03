// /story_app/app/static/js/scene_save_handler.js
"use strict";

const SceneSaveHandler = (() => {
    const API_BASE_URL = "/api/v1";
    let currentSceneId = null; // Will be set if editing an existing scene
    let parentActId = null;    // Will be set from the page, needed for creating new scenes
    let saveButtonElement = null;
    let isEditMode = false;

    const titleInputId = 'scene_title_main_editor';
    const numberInputId = 'scene_order_main_editor';
    const summaryTextareaId = 'scene_summary';
    const aiSummaryTextareaId = 'scene_ai_summary';
    const charactersInputId = 'scene_characters_present';  // May not exist in form
    const moodInputId = 'scene_mood';  // May not exist in form
    const plotPointsTextareaId = 'scene_plot_points';  // May not exist in form
    const storyClassSelectId = 'scene-story-class-id';  // Using hidden input

    function collectDataForSave() {
        const dataToSave = {};

        if (typeof SceneQuillManager !== 'undefined' && SceneQuillManager.getContentHtml) {
            dataToSave.content = SceneQuillManager.getContentHtml();
        } else {
            console.warn("SceneSaveHandler: SceneQuillManager not available. Scene content will not be included.");
            dataToSave.content = undefined; 
        }

        const titleInput = document.getElementById(titleInputId);
        if (titleInput) dataToSave.title = titleInput.value.trim();
        else dataToSave.title = undefined;

        const numberInput = document.getElementById(numberInputId);
        if (numberInput && numberInput.value.trim() !== "") {
            const parsedNumber = parseInt(numberInput.value, 10);
            if (!isNaN(parsedNumber) && parsedNumber > 0) {
                dataToSave.scene_number = parsedNumber;
            } else {
                if (typeof showToast === 'function') showToast("Scene Number is invalid. It must be a positive integer.", "error");
                dataToSave.scene_number = undefined; // Mark as invalid for filtering
            }
        } else if (numberInput && numberInput.value.trim() === "") {
            if (typeof showToast === 'function') showToast("Scene Number is required.", "error");
            dataToSave.scene_number = undefined; // Required, so mark as invalid if empty
        } else {
            dataToSave.scene_number = undefined;
        }
        
        // Check prominent field first, then fallback to sidebar field
        const prominentSummaryTextarea = document.getElementById('scene_summary_prominent');
        const summaryTextarea = document.getElementById(summaryTextareaId);
        
        if (prominentSummaryTextarea) {
            dataToSave.summary = prominentSummaryTextarea.value.trim();
            // Sync to sidebar field if it exists
            if (summaryTextarea) summaryTextarea.value = prominentSummaryTextarea.value;
        } else if (summaryTextarea) {
            dataToSave.summary = summaryTextarea.value.trim();
        } else {
            dataToSave.summary = undefined;
        }
        
        const aiSummaryTextarea = document.getElementById(aiSummaryTextareaId);
        if (aiSummaryTextarea) dataToSave.ai_summary = aiSummaryTextarea.value.trim();
        else dataToSave.ai_summary = undefined;
        
        // These fields may not exist in the current form
        const charactersInput = document.getElementById(charactersInputId);
        if (charactersInput) dataToSave.characters_present = charactersInput.value.trim();
        else dataToSave.characters_present = undefined;

        const moodInput = document.getElementById(moodInputId);
        if (moodInput) dataToSave.mood = moodInput.value.trim();
        else dataToSave.mood = undefined;

        const plotPointsTextarea = document.getElementById(plotPointsTextareaId);
        if (plotPointsTextarea) dataToSave.plot_points = plotPointsTextarea.value.trim();
        else dataToSave.plot_points = undefined;

        // Get story class ID from hidden input
        const storyClassInput = document.getElementById(storyClassSelectId);
        if (storyClassInput && storyClassInput.value) {
            dataToSave.story_class_id = parseInt(storyClassInput.value, 10);
        } else {
            dataToSave.story_class_id = null;
        }
        
        // Get image prompt definition
        const imagePromptTextarea = document.getElementById('scene_image_prompt');
        if (imagePromptTextarea) {
            dataToSave.image_prompt_definition = imagePromptTextarea.value.trim();
        } else {
            dataToSave.image_prompt_definition = undefined;
        }
        
        const finalPayload = Object.fromEntries(Object.entries(dataToSave).filter(([_, v]) => v !== undefined));
        
        // Ensure content (description in schema) is sent as null if it was an empty string from Quill
        // and it's the only field or if explicitly cleared.
        if (finalPayload.hasOwnProperty('content') && finalPayload.content === "" && Object.keys(finalPayload).length === 1) {
            finalPayload.content = null; 
        } else if (!finalPayload.hasOwnProperty('content') && dataToSave.hasOwnProperty('content') && dataToSave.content === "") {
            finalPayload.content = null;
        }
        
        return finalPayload;
    }

    async function handleSaveClick() {
        if (!saveButtonElement) {
            console.error("SceneSaveHandler: Save button element reference is missing.");
            return;
        }
        if (!isEditMode && !parentActId) {
            if (typeof showToast === 'function') showToast("Error: Parent Act context is missing. Cannot create new scene.", "error");
            console.error("SceneSaveHandler: parentActId is not set for new scene. Save aborted.");
            return;
        }
        if (isEditMode && !currentSceneId) {
            if (typeof showToast === 'function') showToast("Error: Scene context (ID) is missing. Cannot save changes.", "error");
            console.error("SceneSaveHandler: currentSceneId is not set for edit. Save aborted.");
            return;
        }


        const sceneDataPayload = collectDataForSave();

        // Client-side validation for required fields (scene_number and title for scenes)
        if (!sceneDataPayload.scene_number || isNaN(sceneDataPayload.scene_number) || sceneDataPayload.scene_number <= 0) {
            if (typeof showToast === 'function') showToast("Scene Number is required and must be a positive integer.", "error");
            const numInput = document.getElementById(numberInputId);
            if (numInput) numInput.focus();
            return;
        }
        if (!sceneDataPayload.title || sceneDataPayload.title.trim() === "") {
            if (typeof showToast === 'function') showToast("Scene Title is required.", "error");
            const titleIn = document.getElementById(titleInputId);
            if (titleIn) titleIn.focus();
            return;
        }

        if (Object.keys(sceneDataPayload).length === 0) {
            if (typeof showToast === 'function') showToast("No changes detected to save for the scene.", "info");
            return;
        }

        const originalButtonText = saveButtonElement.textContent;
        saveButtonElement.disabled = true;
        saveButtonElement.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${isEditMode ? "Saving" : "Creating"} Scene...`;
        
        let apiUrl = "";
        let httpMethod = "";

        if (isEditMode) {
            apiUrl = `${API_BASE_URL}/scenes/${currentSceneId}`;
            httpMethod = 'PUT';
        } else {
            apiUrl = `${API_BASE_URL}/acts/${parentActId}/scenes/`;
            httpMethod = 'POST';
        }
        
        console.log(`SceneSaveHandler: ${httpMethod} Scene. URL: ${apiUrl}`, "Payload:", sceneDataPayload);

        try {
            const response = await fetch(apiUrl, { 
                method: httpMethod, 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(sceneDataPayload), 
                credentials: 'include' 
            });

            if (response.ok) { 
                const result = await response.json(); 
                console.log(`SceneSaveHandler: Scene ${isEditMode ? 'updated' : 'created'} successfully.`, result);
                if (typeof showToast === 'function') showToast(`Scene ${isEditMode ? 'updated' : 'created'} successfully!`, "success");
                
                if (!isEditMode && result.id) { // If created new scene, redirect to its edit page
                    window.location.href = `/ui/scenes/${result.id}/edit`;
                } else if (isEditMode) {
                    // Optionally, update any fields on the page if server returns updated data,
                    // e.g., if updated_at is displayed. For now, just success.
                }
            } else { 
                const errorData = await response.json().catch(() => ({ detail: `Failed to ${isEditMode ? 'update' : 'create'} scene (Status: ${response.status})`}));
                console.error(`SceneSaveHandler: Error ${isEditMode ? 'updating' : 'creating'} scene -`, errorData);
                if (typeof showToast === 'function') showToast(`Error ${isEditMode ? 'updating' : 'creating'} scene: ${errorData.detail || response.statusText}`, "error");
            }
        } catch (error) { 
            console.error(`SceneSaveHandler: Network error ${isEditMode ? 'updating' : 'creating'} scene:`, error); 
            if (typeof showToast === 'function') showToast(`Network error ${isEditMode ? 'updating' : 'creating'} scene.`, "error");
        } finally { 
            if (saveButtonElement) {
                saveButtonElement.disabled = false; 
                saveButtonElement.textContent = originalButtonText;
            }
        }
    }

    async function loadStoryClasses() {
        const storyClassSelect = document.getElementById(storyClassSelectId);
        if (!storyClassSelect) return;
        
        try {
            const response = await fetch(`${API_BASE_URL}/story-classes/options`, {
                credentials: 'include'
            });
            
            if (!response.ok) {
                console.warn('Failed to load story classes for scene editor');
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
                
                // Set selected if this scene has this class
                const currentSceneClassId = document.getElementById('scene-story-class-id')?.value;
                if (currentSceneClassId && currentSceneClassId == storyClass.id) {
                    option.selected = true;
                }
                
                storyClassSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Error loading story classes for scene:', error);
        }
    }
    
    function getBrightness(hexColor) {
        // Convert hex to RGB and calculate brightness
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        return (r * 299 + g * 587 + b * 114) / 1000;
    }

    function initialize(sceneIdFromPage, actIdFromPage) {
        currentSceneId = sceneIdFromPage; // Will be null/empty for new scenes
        parentActId = actIdFromPage;     // Must be present for new scenes
        isEditMode = !!currentSceneId;

        saveButtonElement = document.getElementById('save-scene-button');

        if ((isEditMode && !currentSceneId) || (!isEditMode && !parentActId)) {
            console.error("SceneSaveHandler: Initialization failed - critical ID (sceneId for edit, or actId for new) is missing.");
            if (saveButtonElement) saveButtonElement.disabled = true;
            return;
        }
        
        if (saveButtonElement) {
            saveButtonElement.addEventListener('click', handleSaveClick);
            console.log("SceneSaveHandler: Initialized and event listener attached to 'save-scene-button'. Mode:", isEditMode ? "Edit" : "Create");
        } else {
            console.warn("SceneSaveHandler: Save button ('save-scene-button') not found. Scene save functionality disabled.");
        }
        
        // Load story classes
        loadStoryClasses();
    }

    return {
        initialize: initialize,
        saveScene: async function() {
            // Public method to save scene programmatically
            const dataToSave = collectDataForSave();
            
            // Filter out undefined/invalid fields
            const filteredData = Object.fromEntries(Object.entries(dataToSave).filter(([_, v]) => v !== undefined));
            
            // Check for critical missing data
            if (isEditMode && !currentSceneId) {
                throw new Error("Cannot save - Scene ID is missing.");
            }
            if (!isEditMode && !parentActId) {
                throw new Error("Cannot save - Act ID is missing for new scene.");
            }
            
            const endpoint = isEditMode 
                ? `${API_BASE_URL}/scenes/${currentSceneId}` 
                : `${API_BASE_URL}/acts/${parentActId}/scenes/`;
            
            const method = isEditMode ? 'PUT' : 'POST';
            
            const response = await fetch(endpoint, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(filteredData),
                credentials: 'include'
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Failed to save scene (Status: ${response.status})`);
            }
            
            return await response.json();
        }
    };
})();

// Make SceneSaveHandler available globally
window.SceneSaveHandler = SceneSaveHandler;
