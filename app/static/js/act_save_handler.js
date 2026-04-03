// /story_app/app/static/js/act_save_handler.js
"use strict";

const ActSaveHandler = (() => {
    const API_BASE_URL = "/api/v1";
    let currentActId = null; 
    let saveButtonElement = null;
    
    const titleInputIdOnEditorPage = 'act_title_main_editor'; 
    const numberInputIdOnEditorPage = 'act_number_main_editor'; 
    const summaryInputId = 'act_summary';
    const writerNotesInputId = 'writer_notes';
    const systemPromptSelectId = 'system_prompt_id_editor';
    const storyClassSelectId = 'story_class_id_editor';

    function collectDataForSave() {
        const dataToSave = {};

        if (typeof ActQuillManager !== 'undefined' && ActQuillManager.getContentHtml) {
            dataToSave.description = ActQuillManager.getContentHtml();
        } else {
            console.warn("ActSaveHandler: ActQuillManager not available. Act description will not be included in save data.");
            dataToSave.description = undefined; 
        }

        // Check prominent field first, then fallback to sidebar field
        const prominentSummaryInput = document.getElementById('act_summary_prominent');
        const summaryInput = document.getElementById(summaryInputId);
        
        if (prominentSummaryInput) {
            dataToSave.act_summary = prominentSummaryInput.value.trim();
            // Sync to sidebar field if it exists
            if (summaryInput) summaryInput.value = prominentSummaryInput.value;
        } else if (summaryInput) {
            dataToSave.act_summary = summaryInput.value.trim();
        } else {
            dataToSave.act_summary = undefined;
        }
        
        const writerNotesInputEl = document.getElementById(writerNotesInputId);
        if (writerNotesInputEl) {
            dataToSave.writer_notes = writerNotesInputEl.value.trim();
        } else {
            dataToSave.writer_notes = undefined;
        }

        const systemPromptSelect = document.getElementById(systemPromptSelectId);
        if (systemPromptSelect) {
            dataToSave.system_prompt_id = systemPromptSelect.value ? parseInt(systemPromptSelect.value, 10) : null;
        } else {
            dataToSave.system_prompt_id = undefined;
        }

        const storyClassSelect = document.getElementById(storyClassSelectId);
        if (storyClassSelect) {
            dataToSave.story_class_id = storyClassSelect.value ? parseInt(storyClassSelect.value, 10) : null;
        } else {
            dataToSave.story_class_id = undefined;
        }

        const titleInput = document.getElementById(titleInputIdOnEditorPage);
        if (titleInput) { // Check if element exists
            if (titleInput.value.trim() !== "") {
                dataToSave.title = titleInput.value.trim();
            } else {
                // If title input exists but is empty, treat as undefined unless explicitly required to be empty string
                dataToSave.title = undefined; 
            }
        } else {
            dataToSave.title = undefined;
        }
        
        const numberInput = document.getElementById(numberInputIdOnEditorPage);
        if (numberInput) { // Check if element exists
            if (numberInput.value.trim() !== "") {
                const parsedNumber = parseInt(numberInput.value, 10);
                if (!isNaN(parsedNumber) && parsedNumber > 0) {
                    dataToSave.act_number = parsedNumber;
                } else {
                    if (typeof showToast === 'function') showToast("Act Number is invalid and will not be saved.", "warning");
                    dataToSave.act_number = undefined; 
                }
            } else {
                 dataToSave.act_number = undefined; 
            }
        } else {
            dataToSave.act_number = undefined;
        }
        
        const finalPayload = Object.fromEntries(Object.entries(dataToSave).filter(([_, v]) => v !== undefined));
        
        if (finalPayload.hasOwnProperty('description') && finalPayload.description === "" && Object.keys(finalPayload).length === 1) {
            finalPayload.description = null; 
        } else if (!finalPayload.hasOwnProperty('description') && dataToSave.hasOwnProperty('description') && dataToSave.description === "") {
            finalPayload.description = null;
        }


        return finalPayload;
    }

    async function handleSaveClick() {
        if (!currentActId) {
            if (typeof showToast === 'function') showToast("Error: Act context (ID) is missing. Cannot save.", "error");
            console.error("ActSaveHandler: currentActId is not set. Save aborted.");
            return;
        }

        if (!saveButtonElement) {
            console.error("ActSaveHandler: Save button element reference is missing.");
            return;
        }

        const actDataPayload = collectDataForSave();

        if (Object.keys(actDataPayload).length === 0) {
            if (typeof showToast === 'function') showToast("No changes detected to save.", "info");
            return;
        }
        
        if (actDataPayload.hasOwnProperty('title') && (!actDataPayload.title || actDataPayload.title.trim() === "")) {
            if (typeof showToast === 'function') showToast("Act Title cannot be empty if included in save.", "error");
            return;
        }
        if (actDataPayload.hasOwnProperty('act_number') && (actDataPayload.act_number === null || isNaN(actDataPayload.act_number) || actDataPayload.act_number <= 0)) {
             if (typeof showToast === 'function') showToast("Act Number must be a positive integer if included in save.", "error");
            return;
        }

        const originalButtonText = saveButtonElement.textContent;
        saveButtonElement.disabled = true;
        saveButtonElement.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving Act...`;
        
        const apiUrl = `${API_BASE_URL}/acts/${currentActId}`;
        console.log(`ActSaveHandler: Saving Act ID ${currentActId}. URL: ${apiUrl}`, "Payload:", actDataPayload);

        try {
            const response = await fetch(apiUrl, { 
                method: 'PUT', 
                headers: { 'Content-Type': 'application/json' }, 
                body: JSON.stringify(actDataPayload), 
                credentials: 'include' 
            });

            if (response.ok) { 
                const result = await response.json(); 
                console.log("ActSaveHandler: Act saved successfully.", result);
                if (typeof showToast === 'function') showToast("Act changes saved successfully!", "success");
            } else { 
                const errorData = await response.json().catch(() => ({ detail: `Failed to save act (Status: ${response.status})`}));
                console.error("ActSaveHandler: Error saving act -", errorData);
                if (typeof showToast === 'function') showToast(`Error saving act: ${errorData.detail || response.statusText}`, "error");
            }
        } catch (error) { 
            console.error("ActSaveHandler: Network error saving act:", error); 
            if (typeof showToast === 'function') showToast("Network error saving act. Please check connection.", "error");
        } finally { 
            if (saveButtonElement) {
                saveButtonElement.disabled = false; 
                saveButtonElement.textContent = originalButtonText;
            }
        }
    }

    function initialize(actIdFromPage) {
        currentActId = actIdFromPage;
        saveButtonElement = document.getElementById('save-act-button');

        if (!currentActId) {
            console.error("ActSaveHandler: Initialization failed - actIdFromPage is missing.");
            if (saveButtonElement) saveButtonElement.disabled = true;
            return;
        }
        
        if (saveButtonElement) {
            saveButtonElement.addEventListener('click', handleSaveClick);
            console.log("ActSaveHandler: Initialized and event listener attached to 'save-act-button'.");
        } else {
            console.warn("ActSaveHandler: Save button ('save-act-button') not found. Act save functionality disabled.");
        }
    }

    return {
        initialize: initialize
    };
})();
