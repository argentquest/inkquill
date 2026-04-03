// /story_app/app/static/js/act_ui_updater.js
"use strict";

const ActUIUpdater = (() => {
    // IDs for Act Editor elements - ensure these match your act_editor_ui.html
    const actAIPromptTabId = 'act-ai-full-prompt-preview-area'; // For narrative prompt
    const actContextDetailsTabId = 'act-ai-context-full-details-area';
    
    // For AI Assistant Tab in Act Editor
    const actRawAIStreamDisplayId = 'ai-full-response-display-act'; // Shows narrative stream, then metadata JSON
    const actExtractedNarrativePreviewId = 'ai-extracted-content-preview'; // Shows accumulating/final narrative
    const actUseAIFollowupButtonId = 'use-ai-followup-button'; // Button for Act
    const actAICommentaryDisplayAreaId = 'act-ai-commentary-display-area'; // NEW: For Act commentary

    // NEW: IDs for Act-specific metadata suggestions (you'll need to add these to act_editor_ui.html)
    const actSuggestedSummaryPointsSpanId = 'act-ai-suggested-summary-points';
    const actKeyCharacterDevelopmentsSpanId = 'act-ai-key-character-developments';
    const actPacingCommentarySpanId = 'act-ai-pacing-commentary';
    const actApplyMetadataButtonsContainerId = 'act-ai-suggested-metadata-area';


    function updateAIPromptTab(promptDataString) {
        const element = document.getElementById(actAIPromptTabId);
        if (element) {
            element.textContent = promptDataString || "No AI prompt data available for Act.";
        } else {
            console.warn("ActUIUpdater: Element for Act AI Prompt Tab not found:", actAIPromptTabId);
        }
    }

    function updateContextDetailsTab(contextDetailsString) {
        const element = document.getElementById(actContextDetailsTabId);
        if (element) {
            element.textContent = contextDetailsString || "No context details available for Act.";
        } else {
            console.warn("ActUIUpdater: Element for Act Context Details Tab not found:", actContextDetailsTabId);
        }
    }

    function clearContextDisplays() {
        ActUIUpdater.updateContextDetailsTab("Context details will appear here for Act.");
    }

    function setRawAIStreamDisplay(text, append = false) { // Will show narrative stream, then metadata JSON
        const element = document.getElementById(actRawAIStreamDisplayId);
        if (element) {
            if (append) {
                element.textContent += text;
            } else {
                element.textContent = text;
            }
            if (text.length > 0) { 
                 element.scrollTop = element.scrollHeight;
            }
        } else {
            console.warn("ActUIUpdater: Element for Raw AI Stream Display not found:", actRawAIStreamDisplayId);
        }
    }

    function setExtractedNarrativePreview(narrativeText, append = false) {
        const element = document.getElementById(actExtractedNarrativePreviewId);
        if (element) {
            if (append) {
                element.textContent += narrativeText;
            } else {
                element.textContent = narrativeText || "";
            }
            if (narrativeText.length > 0) {
                 element.scrollTop = element.scrollHeight;
            }
        } else {
            console.warn("ActUIUpdater: Element for Extracted Narrative Preview not found:", actExtractedNarrativePreviewId);
        }
    }

    function updateFollowupButton(followupText) { // For AI General Commentary
        const button = document.getElementById(actUseAIFollowupButtonId);
        const commentaryDisplay = document.getElementById(actAICommentaryDisplayAreaId);

        if (button) {
            if (followupText && followupText.trim() !== "") {
                button.disabled = false;
                button.dataset.followup = followupText;
                if (commentaryDisplay) commentaryDisplay.textContent = followupText;
            } else {
                button.disabled = true;
                button.dataset.followup = "";
                if (commentaryDisplay) commentaryDisplay.textContent = "No AI general commentary available for this Act.";
            }
        } else {
            console.warn("ActUIUpdater: Use AI Followup Button not found:", actUseAIFollowupButtonId);
            if (commentaryDisplay) commentaryDisplay.textContent = "Follow-up button missing.";
        }
    }

    // NEW: Function to update Act-specific metadata suggestions
    function updateActMetadataSuggestions(metadataObj) {
        // Handle both new format (object) and legacy format (individual parameters)
        if (typeof metadataObj === 'string') {
            // Legacy call format: updateActMetadataSuggestions(summaryPoints, charDev, pacingCommentary)
            const summaryPoints = arguments[0];
            const charDev = arguments[1];
            const pacingCommentary = arguments[2];
            
            const summarySpan = document.getElementById(actSuggestedSummaryPointsSpanId);
            const charDevSpan = document.getElementById(actKeyCharacterDevelopmentsSpanId);
            const pacingSpan = document.getElementById(actPacingCommentarySpanId);
            
            if (summarySpan) summarySpan.textContent = summaryPoints || "N/A";
            if (charDevSpan) charDevSpan.textContent = charDev || "N/A";
            if (pacingSpan) pacingSpan.textContent = pacingCommentary || "N/A";
            return;
        }

        // New comprehensive metadata update
        const elements = {
            'act-ai-suggested-summary-points': metadataObj.suggestedActSummaryPoints,
            'act-ai-character-developments': metadataObj.keyCharacterDevelopments,
            'act-ai-conflict-analysis': metadataObj.conflictAnalysis,
            'act-ai-themes-motifs': metadataObj.themesMotifs,
            'act-ai-setting-utilization': metadataObj.settingUtilization,
            'act-ai-dialogue-assessment': metadataObj.dialogueAssessment,
            'act-ai-tension-pacing': metadataObj.tensionPacing,
            'act-ai-foreshadowing': metadataObj.foreshadowingElements,
            'act-ai-narrative-strengths': metadataObj.narrativeStrengths,
            'act-ai-improvement-suggestions': metadataObj.improvementSuggestions
        };

        // Update all metadata elements
        Object.keys(elements).forEach(elementId => {
            const element = document.getElementById(elementId);
            if (element) {
                const value = elements[elementId] || "N/A";
                element.style.whiteSpace = 'pre-wrap'; // Preserve line breaks
                element.textContent = value;
            }
        });

        const applyButtonsContainer = document.getElementById(actApplyMetadataButtonsContainerId);
        if (applyButtonsContainer) {
            const hasSuggestions = Object.values(elements).some(value => value && value !== "N/A");
            console.log("ActUIUpdater: Enhanced act metadata suggestions updated. Has suggestions:", hasSuggestions);
        }
    }
    
    function clearActMetadataSuggestions() {
        const clearObj = {
            suggestedActSummaryPoints: "N/A",
            keyCharacterDevelopments: "N/A",
            conflictAnalysis: "N/A",
            themesMotifs: "N/A",
            settingUtilization: "N/A",
            dialogueAssessment: "N/A",
            tensionPacing: "N/A",
            foreshadowingElements: "N/A",
            narrativeStrengths: "N/A",
            improvementSuggestions: "N/A"
        };
        updateActMetadataSuggestions(clearObj);
    }

    function setAIControlsState(isNarrativeStreaming, isMetadataStreaming, hasNarrativeContentForIncorporate) {
        const generateButton = document.getElementById('ai-generate-button'); // Assuming this ID is unique to Act editor page context
        const incorporateButton = document.getElementById('incorporate-suggestion-button');
        const clearButton = document.getElementById('clear-suggestion-button');
        const followupButton = document.getElementById(actUseAIFollowupButtonId);
        // const applyMetaButtons = document.querySelectorAll(`#${actApplyMetadataButtonsContainerId} .apply-act-metadata-btn`);

        const isAnyAIStreaming = isNarrativeStreaming || isMetadataStreaming;

        if (generateButton) generateButton.disabled = isAnyAIStreaming;
        if (incorporateButton) incorporateButton.disabled = isAnyAIStreaming || !hasNarrativeContentForIncorporate;
        if (clearButton) clearButton.disabled = isAnyAIStreaming;
        
        if (followupButton) {
            if(isAnyAIStreaming) followupButton.disabled = true;
        }
        // if (applyMetaButtons) {
        //     applyMetaButtons.forEach(btn => {
        //         if(isAnyAIStreaming) btn.style.display = 'none';
        //     });
        // }
    }
    
    function resetAIInteractionAreas(clearInstruction = false) {
        setExtractedNarrativePreview(""); 
        setRawAIStreamDisplay(""); // Clears the combined narrative/metadata display area
        updateFollowupButton("");    
        clearContextDisplays();
        clearActMetadataSuggestions(); // Clear Act-specific metadata

        const aiPromptInput = document.getElementById('ai-prompt-input'); // Assuming unique ID for Act editor
        if (clearInstruction && aiPromptInput) {
            aiPromptInput.value = "";
            const promptSelect = document.getElementById('prompt-select-dropdown'); // Unique ID for Act editor
            const clearPromptBtn = document.getElementById('clear-selected-prompt-button'); // Unique ID
            if(promptSelect) promptSelect.value = "";
            if(clearPromptBtn) clearPromptBtn.style.display = 'none';
        }
        
        updateAIPromptTab("Waiting for next AI generation for Act.");
        setAIControlsState(false, false, false); 
        if (typeof showToast === 'function') showToast("Act AI interaction areas cleared.", "info");
    }

    return {
        updateAIPromptTab,
        updateContextDetailsTab,
        clearContextDisplays,
        setRawAIStreamDisplay,
        setExtractedNarrativePreview,
        updateFollowupButton,
        updateActMetadataSuggestions, // New
        clearActMetadataSuggestions, // New
        setAIControlsState,
        resetAIInteractionAreas
    };
})();

