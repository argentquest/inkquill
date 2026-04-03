// /story_app/app/static/js/act_editor_main.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("ActEditorMain: Initializing Act Editor Orchestrator (v.clean_final)");

    const storyIdElement = document.getElementById('story-id');
    const actIdElement = document.getElementById('act-id');
    const storyId = storyIdElement ? storyIdElement.value : null;
    const actId = actIdElement ? actIdElement.value : null;

    const currentUserIdElement = document.getElementById('current-user-id'); 
    const currentUserId = currentUserIdElement ? parseInt(currentUserIdElement.value, 10) : null;

    const aiGenerateButton = document.getElementById('ai-generate-button');
    const aiPromptInput = document.getElementById('ai-prompt-input');
    const incorporateSuggestionButton = document.getElementById('incorporate-suggestion-button');
    const clearSuggestionButton = document.getElementById('clear-suggestion-button');
    const useAIFollowupButton = document.getElementById('use-ai-followup-button');
    const saveActButton = document.getElementById('save-act-button'); // Main save for the page

    if (!storyId || !actId) {
        console.error("ActEditorMain: Story ID or Act ID is missing. Orchestrator cannot initialize properly.");
        if (typeof showToast === 'function') showToast("Critical error: Page context is incomplete. Some features may be disabled.", "error", 10000);
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        if (saveActButton) saveActButton.disabled = true;
        return;
    }

    if (typeof ActQuillManager === 'undefined' || 
        typeof ActWebSocketHandler === 'undefined' ||
        typeof ActAIProcessor === 'undefined' ||
        typeof ActUIUpdater === 'undefined' ||
        typeof ActPromptManager === 'undefined' ||
        typeof ActSaveHandler === 'undefined' ||
        typeof showToast !== 'function') {
        console.error("ActEditorMain: One or more required JavaScript modules (ActQuillManager, ActWebSocketHandler, ActAIProcessor, ActUIUpdater, ActPromptManager, ActSaveHandler, or showToast) are not loaded. Ensure all act_*.js and notifications.js files are included correctly in the HTML before this script.");
        if (document.body) { // Attempt to show an error on the page itself if possible
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger m-3';
            errorDiv.textContent = 'Critical Page Error: Required JavaScript components are missing. Please contact support or try refreshing.';
            document.body.prepend(errorDiv);
        }
        return;
    }

    let isAIStreaming = false;
    let currentFullAIResponseStream = "";

    function handleActWebSocketOpen(event) {
        console.log("ActEditorMain: Act AI WebSocket connection opened successfully.");
        isAIStreaming = false; 
        ActUIUpdater.setAIControlsState(false, false); 
        if (aiGenerateButton) aiGenerateButton.disabled = false;
        showToast("AI Assistant connected for Act.", "success");
    }

    function handleActWebSocketMessage(messageData) {
        console.log("ActEditorMain: Orchestrator received message from ActWebSocketHandler:", messageData.type);

        switch (messageData.type) {
            case "context_info":
                const contextDisplayData = ActAIProcessor.processContextMessage(messageData.data);
                ActUIUpdater.updateContextDetailsTab(contextDisplayData.details);
                break;
            case "full_prompt_info":
                const promptDisplayData = ActAIProcessor.processFullPromptMessage(messageData.data);
                ActUIUpdater.updateAIPromptTab(promptDisplayData.details);
                break;
            case "generation_start":
                isAIStreaming = true;
                currentFullAIResponseStream = "";
                ActUIUpdater.setAIControlsState(true, false); 
                ActUIUpdater.setRawAIStreamDisplay("AI is generating stream...", false); 
                ActUIUpdater.setExtractedNarrativePreview("");
                ActUIUpdater.updateFollowupButton("");
                break;
            case "content_chunk":
                currentFullAIResponseStream += messageData.data;
                ActUIUpdater.setRawAIStreamDisplay(messageData.data, true); 
                break;
            case "generation_end":
                isAIStreaming = false;
                ActUIUpdater.setRawAIStreamDisplay(currentFullAIResponseStream.trim() || "[AI stream ended, no content or only whitespace]", false);
                const processedActContent = ActAIProcessor.processStreamForDelimiters(currentFullAIResponseStream);
                ActUIUpdater.setExtractedNarrativePreview(processedActContent.extractedNarrative);
                ActUIUpdater.updateFollowupButton(processedActContent.followupText);
                ActUIUpdater.setAIControlsState(false, !!processedActContent.extractedNarrative);
                if (messageData.data && messageData.data.startsWith("[STREAM_END_AI_ERROR_")) {
                    showToast("Act AI generation ended with an error from server.", "error");
                }
                break;
            case "error":
                isAIStreaming = false;
                const errorMsg = messageData.data || "Unknown AI error for act.";
                ActUIUpdater.setRawAIStreamDisplay(`SERVER ERROR:\n${errorMsg}`, false);
                ActUIUpdater.setExtractedNarrativePreview(`Error: ${errorMsg}`);
                ActUIUpdater.setAIControlsState(false, false); 
                showToast(`Act AI Error: ${errorMsg}`, "error", 7000);
                break;
            default:
                console.warn("ActEditorMain: Orchestrator received unhandled WebSocket message type:", messageData.type);
        }
    }

    function handleActWebSocketClose(event) {
        console.warn("ActEditorMain: Act AI WebSocket connection closed.", event.code, event.reason);
        isAIStreaming = false;
        ActUIUpdater.setAIControlsState(true, false); 
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("AI Assistant for Act disconnected. Refresh to reconnect.", "warning", 7000);
    }
    
    function handleActWebSocketError(event) {
        console.error("ActEditorMain: Act AI WebSocket error occurred.", event);
        isAIStreaming = false;
        ActUIUpdater.setAIControlsState(true, false); 
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("Act AI connection error. Please try refreshing.", "error", 7000);
    }

    ActQuillManager.initialize();
    ActPromptManager.initialize(currentUserId); 
    ActSaveHandler.initialize(actId); 

    if (actId && storyId && aiGenerateButton) {
        ActWebSocketHandler.initialize(
            storyId, 
            actId, 
            handleActWebSocketMessage,
            handleActWebSocketOpen,
            handleActWebSocketClose,
            handleActWebSocketError
        );
    } else {
        console.warn("ActEditorMain: Not initializing ActWebSocketHandler due to missing IDs or AI Generate button.");
        if (aiGenerateButton) {
            aiGenerateButton.disabled = true;
            aiGenerateButton.title = "Act context missing or save needed to enable AI.";
        }
        const tabsToDisable = ['ai-assistant-tab-act', 'ai-prompt-debug-tab-act', 'rag-details-tab-act']; 
        tabsToDisable.forEach(tabId => {
            const tabButton = document.getElementById(tabId);
            if (tabButton) {
                tabButton.classList.add('disabled');
                const tabPaneId = tabButton.getAttribute('data-bs-target');
                const tabPane = tabPaneId ? document.querySelector(tabPaneId) : null;
                if (tabPane) tabPane.innerHTML = '<div class="alert alert-warning">AI features for this Act are unavailable until critical context is loaded or the Act is saved.</div>';
            }
        });
    }

    if (aiGenerateButton && aiPromptInput) {
        aiGenerateButton.addEventListener('click', () => {
            const userInstruction = aiPromptInput.value.trim();
            if (!userInstruction) {
                showToast("Please provide an instruction for the AI.", "warning");
                return;
            }
            const currentActHTML = ActQuillManager.getContentHtml();
            
            ActUIUpdater.setRawAIStreamDisplay("Sending request to AI...", false);
            ActUIUpdater.setExtractedNarrativePreview("");
            ActUIUpdater.clearContextDisplays();
            ActUIUpdater.updateAIPromptTab("Waiting for AI prompt data from server...");
            
            const success = ActWebSocketHandler.sendMessage({ 
                user_instruction: userInstruction, 
                current_act_content: currentActHTML 
            });

            if (success) {
                isAIStreaming = true; 
                ActUIUpdater.setAIControlsState(true, false);
            } else {
                ActUIUpdater.setAIControlsState(false, false); 
            }
        });
    }

    if (incorporateSuggestionButton) { 
        incorporateSuggestionButton.addEventListener('click', () => {
            const extractedPreview = document.getElementById('ai-extracted-content-preview');
            if (!extractedPreview) return;
            const contentToIncorporate = extractedPreview.textContent.trim(); 
            if (contentToIncorporate) {
                ActQuillManager.appendContentHtml(contentToIncorporate); 
                ActUIUpdater.setExtractedNarrativePreview("");
                ActUIUpdater.updateFollowupButton(""); 
                ActUIUpdater.setRawAIStreamDisplay("Suggestion incorporated. Stream cleared.", false); 
                currentFullAIResponseStream = ""; 
                ActUIUpdater.setAIControlsState(isAIStreaming, false); 
                if (incorporateSuggestionButton) incorporateSuggestionButton.disabled = true;
                showToast("AI suggestion incorporated into Act content!", "success");
            } else {
                showToast("No extracted content to incorporate.", "info");
            }
        });
    } 
    
    if (clearSuggestionButton) { 
        clearSuggestionButton.addEventListener('click', () => {
            ActUIUpdater.resetAIInteractionAreas(false); 
        });
    }

    if (useAIFollowupButton && aiPromptInput) { 
        useAIFollowupButton.addEventListener('click', () => {
            const followupText = useAIFollowupButton.dataset.followup;
            if (followupText && followupText.trim() !== "" && aiPromptInput) {
                aiPromptInput.value = followupText.trim();
                showToast("AI commentary/follow-up copied to instruction input.", "info");
            }
        });
    }
        
    ActUIUpdater.setAIControlsState(false, false); 
    const clearPromptBtn = document.getElementById('clear-selected-prompt-button');
    if (clearPromptBtn) clearPromptBtn.style.display = 'none'; 
    
    console.log("ActEditorMain: Orchestrator initialization complete.");
});

