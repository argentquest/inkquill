// /story_app/app/static/js/scene_editor_main.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("SceneEditorMain: Initializing Scene Editor Orchestrator (v_restored_and_enhanced)");

    // --- Element Selectors ---
    const storyIdElement = document.getElementById('story-id');
    const actIdElement = document.getElementById('act-id');
    const sceneIdElement = document.getElementById('scene-id');
    const storyId = storyIdElement ? storyIdElement.value : null;
    const actId = actIdElement ? actIdElement.value : null;
    const sceneId = sceneIdElement ? sceneIdElement.value : null;
    const isEditMode = !!sceneId;
    const currentUserIdElement = document.getElementById('current-user-id');
    const currentUserId = currentUserIdElement ? parseInt(currentUserIdElement.value, 10) : null;
    const aiGenerateButton = document.getElementById('scene-ai-generate-button');
    const aiPromptInput = document.getElementById('scene-ai-instruction');
    const incorporateSuggestionButton = document.getElementById('scene-incorporate-suggestion-button');
    const clearSuggestionButton = document.getElementById('scene-clear-suggestion-button');
    const useAIFollowupButton = document.getElementById('scene-use-ai-followup-button');
    const saveSceneButton = document.getElementById('save-scene-button');
    const aiCommandCenter = document.getElementById('scene-ai-command-center');
    const modelConfigSelect = document.getElementById('scene-ai-model-config-select'); // NEW

    if (!storyId || !actId || (isEditMode && !sceneId) || !aiCommandCenter || !modelConfigSelect) {
        console.error("SceneEditorMain: Critical context is missing.");
        if (typeof showToast === 'function') showToast("Critical error: Page context is incomplete.", "error");
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        if (saveSceneButton) saveSceneButton.disabled = true;
        return;
    }
    
    // --- Module & State Initialization ---
    if (typeof SceneQuillManager === 'undefined' || typeof SceneWebSocketHandler === 'undefined' || typeof SceneAIProcessor === 'undefined' || typeof SceneUIUpdater === 'undefined' || typeof ScenePromptSelector === 'undefined' || typeof SceneSaveHandler === 'undefined' || typeof AIModelSelector === 'undefined') {
        console.error("SceneEditorMain: One or more required JavaScript modules are not loaded.");
        return;
    }

    let isNarrativeStreamingScene = false;
    let isMetadataStreamingScene = false;
    let currentFullSceneNarrativeStream = "";
    let activeGenerationMode = 'Continue/Append'; // RESTORED

    // --- WebSocket Handlers (remain the same as original) ---
    function handleSceneWebSocketOpen(event) {
        SceneUIUpdater.setAIControlsState(false, false, false);
        if (aiGenerateButton) aiGenerateButton.disabled = false;
        showToast("AI Assistant connected for Scene.", "success");
    }

    function handleSceneWebSocketMessage(messageData) {
        switch (messageData.type) {
            case "context_info":
                SceneUIUpdater.updateContextDetailsTab(SceneAIProcessor.processContextMessage(messageData.data).details);
                break;
            case "narrative_prompt_info":
                SceneUIUpdater.updateAIPromptTab(SceneAIProcessor.processFullPromptMessage(messageData.data).details);
                break;
            case "narrative_generation_start":
                isNarrativeStreamingScene = true;
                currentFullSceneNarrativeStream = "";
                SceneUIUpdater.setAIControlsState(true, false, false);
                SceneUIUpdater.setExtractedNarrativePreview("AI is generating narrative...", false);
                SceneUIUpdater.updateFollowupButton("");
                SceneUIUpdater.clearMetadataSuggestions();
                SceneUIUpdater.setRawAIJsonResponse("Narrative stream started...", false);
                break;
            case "narrative_content_chunk":
                if (!isNarrativeStreamingScene) return;
                currentFullSceneNarrativeStream += messageData.data;
                SceneUIUpdater.setRawAIJsonResponse(messageData.data, true);
                SceneUIUpdater.setExtractedNarrativePreview(currentFullSceneNarrativeStream, false);
                break;
            case "narrative_generation_end":
                isNarrativeStreamingScene = false;
                SceneUIUpdater.setAIControlsState(true, true, !!currentFullSceneNarrativeStream.trim());
                if (clearSuggestionButton) clearSuggestionButton.disabled = false;
                break;
            case "metadata_generation_start":
                isMetadataStreamingScene = true;
                SceneUIUpdater.setRawAIJsonResponse("\n\n--- AI generating metadata (JSON)... ---", true);
                break;
            case "metadata_result":
                isMetadataStreamingScene = false;
                const rawMetadata = messageData.data;
                SceneUIUpdater.setRawAIJsonResponse(`\n\n--- METADATA RESPONSE ---\n${rawMetadata}`, true);
                if (rawMetadata && typeof rawMetadata === 'string') {
                    const processed = SceneAIProcessor.processFullJsonResponse(rawMetadata);
                    if (!processed.parseError) {
                        SceneUIUpdater.updateFollowupButton(processed.aiGeneralCommentary);
                        SceneUIUpdater.updateMetadataSuggestions(processed);
                    }
                }
                SceneUIUpdater.setAIControlsState(false, false, !!currentFullSceneNarrativeStream.trim());
                break;
            case "error":
            case "overall_generation_end_with_error":
                isNarrativeStreamingScene = isMetadataStreamingScene = false;
                const errorMsg = messageData.data || "Unknown AI error.";
                SceneUIUpdater.setRawAIJsonResponse(`\n\n--- SERVER ERROR ---\n${errorMsg}`, true);
                SceneUIUpdater.setExtractedNarrativePreview(`Error: ${errorMsg}`);
                SceneUIUpdater.setAIControlsState(false, false, false);
                showToast(`Scene AI Error: ${errorMsg}`, "error");
                break;
            default:
                console.warn("SceneEditorMain: Unhandled message type:", messageData.type);
        }
    }

    function handleSceneWebSocketClose(event) {
        SceneUIUpdater.setAIControlsState(true, false, false);
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("AI Assistant for Scene disconnected. Refresh to reconnect.", "warning");
    }

    function handleSceneWebSocketError(event) {
        SceneUIUpdater.setAIControlsState(true, false, false);
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("Scene AI connection error. Please try refreshing.", "error");
    }

    // --- Initialize All Modules ---
    SceneQuillManager.initialize();
    ScenePromptSelector.initialize(currentUserId);
    SceneSaveHandler.initialize(sceneId, actId);
    AIModelSelector.initialize('scene-ai-model-config-select'); // NEW
    
    // Initialize AI Quill Toolbar
    if (typeof AIQuillToolbar !== 'undefined' && SceneQuillManager.getQuillInstance()) {
        const contextProvider = async () => {
            // Get story title from breadcrumb
            const storyTitleElement = document.querySelector('.breadcrumb-item a[href*="/stories/"]');
            const storyTitle = storyTitleElement ? storyTitleElement.textContent.trim() : 'Unknown Story';
            
            // Get act title from breadcrumb or context
            const actTitleElement = document.querySelector('.breadcrumb-item a[href*="/acts/"]');
            const actTitle = actTitleElement ? actTitleElement.textContent.trim() : `Act ${actIdElement ? actIdElement.value : 'Unknown'}`;
            
            // Get scene title from the form field
            const sceneTitle = document.getElementById('scene_title_main_editor')?.value || 'New Scene';
            
            return {
                type: 'scene',
                story_id: storyId,
                act_id: actId,
                scene_id: sceneId,
                story_title: storyTitle,
                act_title: actTitle,
                scene_title: sceneTitle,
                current_content: SceneQuillManager.getContentHtml(),
                word_count: SceneQuillManager.getWordCount(),
                context_summary: `Scene "${sceneTitle}" in ${actTitle} of "${storyTitle}"`
            };
        };
        
        const aiQuillToolbar = new AIQuillToolbar(SceneQuillManager.getQuillInstance(), {
            contextProvider: contextProvider,
            beforeTransform: async (text, operationId) => {
                console.log('Scene AI Transform - Before:', { text: text.substring(0, 50) + '...', operationId });
                return true;
            },
            afterTransform: async (originalText, transformedText, operationId) => {
                console.log('Scene AI Transform - After:', { 
                    originalLength: originalText.length, 
                    transformedLength: transformedText.length,
                    operationId 
                });
                // Mark scene as modified
                if (typeof SceneSaveHandler !== 'undefined') {
                    SceneSaveHandler.markAsModified();
                }
            },
            showCostEstimate: true,
            maxTextLength: 3000
        });
        
        console.log('AIQuillToolbar initialized for scene editor');
    }

    if (isEditMode) {
        SceneWebSocketHandler.initialize(storyId, actId, sceneId, handleSceneWebSocketMessage, handleSceneWebSocketOpen, handleSceneWebSocketClose, handleSceneWebSocketError);
    } else {
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("Please save this scene first to enable AI features.", "info");
    }

    // --- MERGED Generate Button Logic ---
    if (aiGenerateButton && aiPromptInput) {
        aiGenerateButton.addEventListener('click', () => {
            const userInstruction = aiPromptInput.value.trim();
            if (!userInstruction) {
                showToast("Please provide an instruction for the AI.", "warning");
                return;
            }

            // RESTORED: Get generation mode
            activeGenerationMode = aiCommandCenter.querySelector('input[name="scene_ai_generation_mode"]:checked').value;
            
            // RESTORED: Get selected text
            let selectedText = null;
            if (activeGenerationMode === 'Elaborate/Expand' || activeGenerationMode === 'Rewrite') {
                selectedText = SceneQuillManager.getSelectedText();
                if (!selectedText) {
                    showToast("Please highlight text in the editor for this mode.", "warning");
                    return;
                }
            }

            // NEW: Get model preset ID
            const selectedModelConfigId = modelConfigSelect.value;
            if (!selectedModelConfigId) {
                showToast("Please select an AI Model Preset.", "warning");
                return;
            }

            const currentSceneHTML = SceneQuillManager.getContentHtml();
            SceneUIUpdater.resetAIInteractionAreas(false);

            // MERGED PAYLOAD
            const payload = {
                user_instruction_for_scene: userInstruction,
                generation_mode: activeGenerationMode,
                selected_text: selectedText || "",
                scene_current_content: currentSceneHTML,
                model_config_id: parseInt(selectedModelConfigId, 10)
            };

            const success = SceneWebSocketHandler.sendMessage(payload);
            if (success) {
                isNarrativeStreamingScene = true;
                SceneUIUpdater.setAIControlsState(true, false, false);
            }
        });
    }

    // --- Button Event Handlers ---
    if (incorporateSuggestionButton) {
        incorporateSuggestionButton.addEventListener('click', () => {
            const contentToIncorporate = currentFullSceneNarrativeStream.trim();
            if (!contentToIncorporate) {
                showToast("No new content from AI to incorporate.", "info");
                return;
            }
            const newHtml = `<p>${contentToIncorporate.replace(/\n\n+/g, '</p><p>').replace(/\n/g, '<br>')}</p>`;

            if (activeGenerationMode === 'Rewrite' || activeGenerationMode === 'Elaborate/Expand') {
                SceneQuillManager.replaceSelectedText(contentToIncorporate);
                showToast("Highlighted text replaced with AI content!", "success");
            } else {
                SceneQuillManager.appendContentHtml(newHtml);
                showToast("AI content appended to editor!", "success");
            }
            SceneUIUpdater.resetAIInteractionAreas(false);
            currentFullSceneNarrativeStream = "";
        });
    }

    if (clearSuggestionButton) {
        clearSuggestionButton.addEventListener('click', () => {
            SceneUIUpdater.resetAIInteractionAreas(false);
            currentFullSceneNarrativeStream = "";
        });
    }
    
    if (useAIFollowupButton && aiPromptInput) {
        useAIFollowupButton.addEventListener('click', () => {
            const followupText = useAIFollowupButton.dataset.followup;
            if (followupText) {
                aiPromptInput.value = followupText.trim();
                showToast("AI commentary copied to instruction field.", "info");
            }
        });
    }

    // Final state setup
    SceneUIUpdater.setAIControlsState(!isEditMode, false, false);
});

