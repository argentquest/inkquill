// /ai_rag_story_app/app/static/js/scene_ui_updater.js
"use strict";

const SceneUIUpdater = (() => {

    function updateAIPromptTab(promptDataString) {
        const element = document.getElementById('scene-ai-full-prompt-preview-area'); 
        if (element) {
            element.textContent = promptDataString || "No AI prompt data available to display for Scene narrative.";
        } else {
            console.warn("SceneUIUpdater: Element 'scene-ai-full-prompt-preview-area' for narrative prompt not found.");
        }
    }

    function updateRAGDetailsTab(ragDetailsString) {
        const element = document.getElementById('scene-ai-rag-context-full-details-area');
        if (element) {
            element.textContent = ragDetailsString || "No RAG details available to display for Scene.";
        } else {
            console.warn("SceneUIUpdater: Element 'scene-ai-rag-context-full-details-area' not found.");
        }
    }

    function updateRAGSummaryDisplay(summaryString) {
        // This function is now effectively OBSOLETE for the AI Assistant tab, as the RAG summary
        // display area was removed from scene_editor_ui.html's AI Assistant tab.
        // If you need to display a RAG summary elsewhere, this function can be reused.
        // For now, we'll log a warning if it's called, as it implies an old call path.
        console.warn("SceneUIUpdater: updateRAGSummaryDisplay called, but RAG summary area was removed from AI Assistant tab in scene editor. Check JS calls.");
        const displayArea = document.getElementById('scene-rag-context-display-area'); // This ID might be gone
        const contentElement = document.getElementById('scene-rag-context-content'); // This ID might be gone
        if (displayArea && contentElement) {
            if (summaryString && summaryString.trim() !== "") {
                contentElement.textContent = summaryString;
                displayArea.style.display = 'block';
            } else {
                contentElement.textContent = "No RAG summary to display for Scene.";
                displayArea.style.display = 'none';
            }
        } else {
            // console.warn("SceneUIUpdater: Scene RAG summary display elements not found (as expected if removed).");
        }
    }
    
    function clearRAGDisplays() {
        // The summary display is gone from the AI assistant tab.
        // const summaryDisplayArea = document.getElementById('scene-rag-context-display-area');
        // const summaryContentElement = document.getElementById('scene-rag-context-content');
        const detailsArea = document.getElementById('rag-context-full-details-area');

        // if (summaryContentElement) summaryContentElement.textContent = "";
        // if (summaryDisplayArea) summaryDisplayArea.style.display = 'none';
        if (detailsArea) detailsArea.textContent = "RAG context details will appear here.";
    }

    function setRawAIJsonResponse(jsonString, append = false) { 
        const element = document.getElementById('scene-ai-full-response-display-area'); 
        if (element) {
            if (jsonString && typeof jsonString === 'string') {
                if (!append && !jsonString.startsWith("[STREAM_END_AI_")) { 
                    try {
                        const parsed = JSON.parse(jsonString);
                        element.textContent = JSON.stringify(parsed, null, 2);
                    } catch (e) {
                        element.textContent = (append ? element.textContent : "") + jsonString;
                    }
                } else { 
                     element.textContent = (append ? element.textContent : "") + jsonString;
                }
            } else if (!append) { 
                element.textContent = "No raw AI Output data to display for Scene.";
            }
            if (element.textContent.length > 0 && !append) {
                 element.scrollTop = 0;
            } else if (append && element.textContent.length > 0) {
                 element.scrollTop = element.scrollHeight;
            }
        } else {
            console.warn("SceneUIUpdater: Element 'raw-ai-json-output-area' not found.");
        }
    }

    function setExtractedNarrativePreview(narrativeText, append = false) {
        const element = document.getElementById('scene-ai-extracted-content-preview');
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
            console.warn("SceneUIUpdater: Element 'scene-ai-extracted-content-preview' not found.");
        }
    }

    function updateFollowupButton(followupText) {
        const button = document.getElementById('scene-use-ai-followup-button');
        const commentaryDisplay = document.getElementById('scene-ai-commentary-display-area'); // NEW

        if (button) {
            if (followupText && followupText.trim() !== "") {
                button.disabled = false;
                button.dataset.followup = followupText;
                if (commentaryDisplay) commentaryDisplay.textContent = followupText; // NEW: Display it
            } else {
                button.disabled = true;
                button.dataset.followup = "";
                if (commentaryDisplay) commentaryDisplay.textContent = "No AI commentary available."; // NEW
            }
        } else {
            console.warn("SceneUIUpdater: Element 'scene-use-ai-followup-button' not found.");
            if (commentaryDisplay) commentaryDisplay.textContent = "Button missing."; // NEW
        }
    }

    function updateMetadataSuggestions(metadataObj) {
        // Handle both new format (object) and legacy format (individual parameters)
        if (typeof metadataObj === 'string') {
            // Legacy call format: updateMetadataSuggestions(mood, characters, plotPoints)
            const mood = arguments[0];
            const characters = arguments[1];
            const plotPoints = arguments[2];
            
            const moodSpan = document.getElementById('scene-ai-suggested-mood');
            const charsSpan = document.getElementById('scene-ai-suggested-characters');
            const plotSpan = document.getElementById('scene-ai-suggested-plot-points');
            
            if (moodSpan) moodSpan.textContent = mood || "N/A";
            if (charsSpan) charsSpan.textContent = characters || "N/A";
            if (plotSpan) plotSpan.textContent = plotPoints || "N/A";
            return;
        }

        // New comprehensive metadata update
        const elements = {
            'scene-ai-suggested-summary-points': metadataObj.suggestedSummaryPoints,
            'scene-ai-conflict-analysis': metadataObj.conflictAnalysis,
            'scene-ai-themes-motifs': metadataObj.themesMotifs,
            'scene-ai-foreshadowing': metadataObj.foreshadowingElements,
            'scene-ai-character-developments': metadataObj.characterDevelopments,
            'scene-ai-dialogue-assessment': metadataObj.dialogueAssessment,
            'scene-ai-tension-pacing': metadataObj.tensionPacing,
            'scene-ai-setting-utilization': metadataObj.settingUtilization,
            'scene-ai-narrative-strengths': metadataObj.narrativeStrengths,
            'scene-ai-improvement-suggestions': metadataObj.improvementSuggestions
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

        // Handle apply buttons for basic metadata only
        const applyButtonsContainer = document.getElementById('scene-ai-suggested-metadata-area');
        if (applyButtonsContainer) {
            const hasBasicSuggestions = (metadataObj.suggestedMood && metadataObj.suggestedMood !== "N/A") || 
                                       (metadataObj.suggestedCharacters && metadataObj.suggestedCharacters !== "N/A") || 
                                       (metadataObj.suggestedPlotPoints && metadataObj.suggestedPlotPoints !== "N/A");
            applyButtonsContainer.querySelectorAll('.apply-metadata-btn').forEach(btn => {
                btn.style.display = hasBasicSuggestions ? 'inline-block' : 'none';
            });
            console.log("SceneUIUpdater: Enhanced scene metadata suggestions updated. Has suggestions:", hasBasicSuggestions);
        }
    }
    
    function clearMetadataSuggestions() {
        const clearObj = {
            suggestedSummaryPoints: "N/A",
            conflictAnalysis: "N/A",
            themesMotifs: "N/A",
            foreshadowingElements: "N/A",
            characterDevelopments: "N/A",
            dialogueAssessment: "N/A",
            tensionPacing: "N/A",
            settingUtilization: "N/A",
            narrativeStrengths: "N/A",
            improvementSuggestions: "N/A"
        };
        updateMetadataSuggestions(clearObj);
    }


    function setAIControlsState(isNarrativeStreaming, isMetadataStreaming, hasNarrativeContentForIncorporate) {
        const generateButton = document.getElementById('scene-ai-generate-button');
        const incorporateButton = document.getElementById('scene-incorporate-suggestion-button');
        const clearButton = document.getElementById('scene-clear-suggestion-button');
        const followupButton = document.getElementById('scene-use-ai-followup-button');
        const applyMetaButtons = document.querySelectorAll('#scene-ai-suggested-metadata-area .apply-metadata-btn');

        const isAnyAIStreaming = isNarrativeStreaming || isMetadataStreaming;

        if (generateButton) {
            generateButton.disabled = isAnyAIStreaming;
        }
        if (incorporateButton) {
            incorporateButton.disabled = isAnyAIStreaming || !hasNarrativeContentForIncorporate;
        }
        if (clearButton) {
            clearButton.disabled = isAnyAIStreaming; 
        }
        if (followupButton) {
            if(isAnyAIStreaming) {
                followupButton.disabled = true;
            } else {
                // Enable/disable based on actual followup text presence (handled by updateFollowupButton)
                // This function just handles the streaming state.
            }
        }
        if (applyMetaButtons) {
            applyMetaButtons.forEach(btn => {
                if(isAnyAIStreaming) btn.style.display = 'none';
            });
        }
    }
    
    function resetAIInteractionAreas(clearInstruction = false) {
        setExtractedNarrativePreview(""); 
        setRawAIJsonResponse("");       
        updateFollowupButton(""); // This will also clear the commentary display
        clearRAGDisplays();
        clearMetadataSuggestions();

        const aiPromptInputElement = document.getElementById('scene-ai-instruction');
        if (clearInstruction && aiPromptInputElement) {
            aiPromptInputElement.value = "";
            const promptSelect = document.getElementById('scene-ai-personal-prompt-select');
            const clearPromptBtn = document.getElementById('scene-clear-selected-personal-prompt-button');
            if(promptSelect) promptSelect.value = "";
            if(clearPromptBtn) clearPromptBtn.style.display = 'none';
        }
        
        const fullPromptPreviewArea = document.getElementById('full-ai-prompt-preview-area');
        if (fullPromptPreviewArea) fullPromptPreviewArea.textContent = "Waiting for next AI generation for Scene.";
        
        setAIControlsState(false, false, false); 
        if (typeof showToast === 'function') showToast("Scene AI interaction areas cleared.", "info");
    }

    return {
        updateAIPromptTab: updateAIPromptTab,
        updateRAGDetailsTab: updateRAGDetailsTab,
        updateRAGSummaryDisplay: updateRAGSummaryDisplay, // Kept for now, but logs warning
        clearRAGDisplays: clearRAGDisplays,
        setRawAIJsonResponse: setRawAIJsonResponse, 
        setExtractedNarrativePreview: setExtractedNarrativePreview, 
        updateFollowupButton: updateFollowupButton,
        updateMetadataSuggestions: updateMetadataSuggestions,
        clearMetadataSuggestions: clearMetadataSuggestions,
        setAIControlsState: setAIControlsState,
        resetAIInteractionAreas: resetAIInteractionAreas
    };
})();