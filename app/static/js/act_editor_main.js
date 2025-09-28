// /ai_rag_story_app/app/static/js/act_editor_main.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const resizer = document.getElementById('editor-resizer');
    const leftPane = document.getElementById('editor-pane');
    if (resizer && leftPane) {
        let isResizing = false;
        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });
        function onMouseMove(e) {
            if (!isResizing) return;
            const container = document.getElementById('editor-layout-container');
            const containerRect = container.getBoundingClientRect();
            const minLeftWidth = 300;
            const minRightWidth = 350;
            let leftWidth = e.clientX - containerRect.left;
            if (leftWidth < minLeftWidth) leftWidth = minLeftWidth;
            if (container.getBoundingClientRect().width - leftWidth < minRightWidth) {
                leftWidth = container.getBoundingClientRect().width - minRightWidth;
            }
            leftPane.style.flexBasis = `${leftWidth}px`;
        }
        function onMouseUp() {
            isResizing = false;
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        }
    }

    const prefillPromptContent = localStorage.getItem('prefillAIPrompt');
    const aiPromptInput = document.getElementById('ai-prompt-input');
    if (prefillPromptContent && aiPromptInput) {
        aiPromptInput.value = prefillPromptContent;
        localStorage.removeItem('prefillAIPrompt');
        if (typeof showToast === 'function') showToast("Prompt content loaded into instruction field.", "info");
    }

    console.log("ActEditorMain: Initializing Act Editor Orchestrator (v_restored_and_enhanced)");

    const storyIdElement = document.getElementById('story-id');
    const actIdElement = document.getElementById('act-id');
    const storyId = storyIdElement ? storyIdElement.value : null;
    const actId = actIdElement ? actIdElement.value : null;
    const currentUserIdElement = document.getElementById('current-user-id');
    const currentUserId = currentUserIdElement ? parseInt(currentUserIdElement.value, 10) : null;
    const aiGenerateButton = document.getElementById('ai-generate-button');
    const incorporateSuggestionButton = document.getElementById('incorporate-suggestion-button');
    const clearSuggestionButton = document.getElementById('clear-suggestion-button');
    const useAIFollowupButton = document.getElementById('use-ai-followup-button');
    const saveActButton = document.getElementById('save-act-button');
    const aiCommandCenter = document.getElementById('ai-command-center-act');
    const modelConfigSelect = document.getElementById('ai-model-config-select'); // NEW

    if (!storyId || !actId || !aiCommandCenter || !modelConfigSelect) {
        console.error("ActEditorMain: Critical context (Story/Act ID, Command Center, or Model Select) is missing.");
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        if (saveActButton) saveActButton.disabled = true;
        return;
    }

    if (typeof ActQuillManager === 'undefined' || typeof ActWebSocketHandler === 'undefined' || typeof ActAIProcessor === 'undefined' || typeof ActUIUpdater === 'undefined' || typeof ActPromptManager === 'undefined' || typeof ActSaveHandler === 'undefined' || typeof AIModelSelector === 'undefined') {
        console.error("ActEditorMain: One or more required JavaScript modules are not loaded.");
        return;
    }

    let isNarrativeStreamingAct = false;
    let isMetadataStreamingAct = false;
    let currentFullActNarrativeStream = "";
    let activeGenerationMode = 'Continue/Append';

    function handleActWebSocketOpen(event) {
        ActUIUpdater.setAIControlsState(false, false, false);
        if (aiGenerateButton) aiGenerateButton.disabled = false;
        showToast("AI Assistant connected for Act.", "success");
    }

    function handleActWebSocketMessage(messageData) {
        switch (messageData.type) {
            case "rag_context_info_act":
                ActUIUpdater.updateRAGDetailsTab(ActAIProcessor.processRagContextMessage(messageData.data).details);
                break;
            case "narrative_prompt_info_act":
                ActUIUpdater.updateAIPromptTab(ActAIProcessor.processFullPromptMessage(messageData.data).details);
                break;
            case "narrative_generation_start_act":
                isNarrativeStreamingAct = true;
                currentFullActNarrativeStream = "";
                ActUIUpdater.setAIControlsState(true, false, false);
                ActUIUpdater.setExtractedNarrativePreview("AI is generating narrative...", false);
                ActUIUpdater.updateFollowupButton("");
                ActUIUpdater.clearActMetadataSuggestions();
                ActUIUpdater.setRawAIStreamDisplay("Narrative stream started...", false);
                break;
            case "narrative_content_chunk_act":
                if (!isNarrativeStreamingAct) return;
                currentFullActNarrativeStream += messageData.data;
                ActUIUpdater.setRawAIStreamDisplay(messageData.data, true);
                // Clean the content by removing generation markers before displaying
                const cleanedContent = currentFullActNarrativeStream.replace(/\[START_GENERATED_ACT_CONTENT\]/g, '').replace(/\[END_GENERATED_ACT_CONTENT\]/g, '');
                ActUIUpdater.setExtractedNarrativePreview(cleanedContent, false);
                break;
            case "narrative_generation_end_act":
                isNarrativeStreamingAct = false;
                // Clean the final accumulated content by removing generation markers
                currentFullActNarrativeStream = currentFullActNarrativeStream.replace(/\[START_GENERATED_ACT_CONTENT\]/g, '').replace(/\[END_GENERATED_ACT_CONTENT\]/g, '');
                ActUIUpdater.setAIControlsState(true, true, !!currentFullActNarrativeStream.trim());
                if (clearSuggestionButton) clearSuggestionButton.disabled = false;
                break;
            case "metadata_generation_start_act":
                isMetadataStreamingAct = true;
                ActUIUpdater.setRawAIStreamDisplay("\n\n--- AI generating metadata (JSON)... ---", true);
                break;
            case "metadata_result_act":
                isMetadataStreamingAct = false;
                const rawMetadata = messageData.data;
                ActUIUpdater.setRawAIStreamDisplay(`\n\n--- METADATA RESPONSE ---\n${rawMetadata}`, true);
                if (rawMetadata && typeof rawMetadata === 'string') {
                    const processed = ActAIProcessor.processActMetadataJsonResponse(rawMetadata);
                    if (!processed.parseError) {
                        ActUIUpdater.updateFollowupButton(processed.aiGeneralCommentary);
                        ActUIUpdater.updateActMetadataSuggestions(processed);
                    }
                }
                ActUIUpdater.setAIControlsState(false, false, !!currentFullActNarrativeStream.trim());
                break;
            case "error_act":
            case "overall_generation_end_with_error_act":
                isNarrativeStreamingAct = isMetadataStreamingAct = false;
                const errorMsg = messageData.data || "Unknown AI error.";
                ActUIUpdater.setRawAIStreamDisplay(`\n\n--- SERVER ERROR ---\n${errorMsg}`, true);
                ActUIUpdater.setExtractedNarrativePreview(`Error: ${errorMsg}`);
                ActUIUpdater.setAIControlsState(false, false, false);
                showToast(`Act AI Error: ${errorMsg}`, "error");
                break;
            default:
                console.warn("ActEditorMain: Unhandled message type:", messageData.type);
        }
    }

    function handleActWebSocketClose(event) {
        ActUIUpdater.setAIControlsState(true, false, false);
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("AI Assistant for Act disconnected. Refresh to reconnect.", "warning");
    }

    function handleActWebSocketError(event) {
        ActUIUpdater.setAIControlsState(true, false, false);
        if (aiGenerateButton) aiGenerateButton.disabled = true;
        showToast("Act AI connection error. Please try refreshing.", "error");
    }

    // --- Initialize all modules ---
    ActQuillManager.initialize();
    ActPromptManager.initialize(currentUserId);
    ActSaveHandler.initialize(actId);
    AIModelSelector.initialize('ai-model-config-select'); // NEW
    
    // Initialize AI Quill Toolbar
    if (typeof AIQuillToolbar !== 'undefined' && ActQuillManager.getQuillInstance()) {
        const contextProvider = async () => {
            // Get story title from page title or breadcrumb
            const storyTitleElement = document.querySelector('.breadcrumb-item a[href*="/stories/"]');
            const storyTitle = storyTitleElement ? storyTitleElement.textContent.trim() : 'Unknown Story';
            
            // Get act title and number from the form fields
            const actTitle = document.getElementById('act_title_main_editor')?.value || 'New Act';
            const actNumber = document.getElementById('act_number_main_editor')?.value || '1';
            
            return {
                type: 'act',
                story_id: storyId,
                act_id: actId,
                story_title: storyTitle,
                act_title: actTitle,
                act_number: actNumber,
                current_content: ActQuillManager.getContentHtml(),
                word_count: ActQuillManager.getWordCount(),
                context_summary: `Act ${actNumber}: "${actTitle}" from "${storyTitle}"`
            };
        };
        
        const aiQuillToolbar = new AIQuillToolbar(ActQuillManager.getQuillInstance(), {
            contextProvider: contextProvider,
            beforeTransform: async (text, operationId) => {
                console.log('Act AI Transform - Before:', { text: text.substring(0, 50) + '...', operationId });
                return true;
            },
            afterTransform: async (originalText, transformedText, operationId) => {
                console.log('Act AI Transform - After:', { 
                    originalLength: originalText.length, 
                    transformedLength: transformedText.length,
                    operationId 
                });
                // Mark act as modified
                if (typeof ActSaveHandler !== 'undefined') {
                    ActSaveHandler.markAsModified();
                }
            },
            showCostEstimate: true,
            maxTextLength: 5000
        });
        
        console.log('AIQuillToolbar initialized for act editor');
    }

    if (actId && storyId) {
        ActWebSocketHandler.initialize(storyId, actId, handleActWebSocketMessage, handleActWebSocketOpen, handleActWebSocketClose, handleActWebSocketError);
    }

    if (aiGenerateButton && aiPromptInput) {
        aiGenerateButton.addEventListener('click', () => {
            const userInstruction = aiPromptInput.value.trim();
            if (!userInstruction) {
                showToast("Please provide an instruction for the AI.", "warning");
                return;
            }

            // RESTORED: Get the generation mode
            activeGenerationMode = aiCommandCenter.querySelector('input[name="ai_generation_mode"]:checked').value;
            
            // RESTORED: Get selected text if needed
            let selectedText = null;
            if (activeGenerationMode === 'Elaborate/Expand' || activeGenerationMode === 'Rewrite') {
                selectedText = ActQuillManager.getSelectedText();
                if (!selectedText) {
                    showToast("Please highlight text in the editor for this mode.", "warning");
                    return;
                }
            }
            
            // NEW: Get the selected AI Model Preset ID
            const selectedModelConfigId = modelConfigSelect.value;
            if (!selectedModelConfigId) {
                showToast("Please select an AI Model Preset.", "warning");
                return;
            }

            const currentActHTML = ActQuillManager.getContentHtml();
            ActUIUpdater.resetAIInteractionAreas(false);
            
            // MERGED PAYLOAD: Includes all original and new fields
            const payload = {
                user_instruction: userInstruction,
                generation_mode: activeGenerationMode,        // RESTORED
                selected_text: selectedText || "",            // RESTORED
                current_act_content: currentActHTML,
                model_config_id: parseInt(selectedModelConfigId, 10) // NEW
            };

            const success = ActWebSocketHandler.sendMessage(payload);
            if (success) {
                isNarrativeStreamingAct = true;
                ActUIUpdater.setAIControlsState(true, false, false);
            }
        });
    }

    if (incorporateSuggestionButton) {
        incorporateSuggestionButton.addEventListener('click', () => {
            const contentToIncorporate = currentFullActNarrativeStream.trim();
            if (!contentToIncorporate) {
                showToast("No new content from AI to incorporate.", "info");
                return;
            }
            const newHtml = `<p>${contentToIncorporate.replace(/\n\n+/g, '</p><p>').replace(/\n/g, '<br>')}</p>`;

            if (activeGenerationMode === 'Rewrite' || activeGenerationMode === 'Elaborate/Expand') {
                ActQuillManager.replaceSelectedText(contentToIncorporate);
                showToast("Highlighted text replaced with AI content!", "success");
            } else {
                ActQuillManager.appendContentHtml(newHtml);
                showToast("AI content appended to editor!", "success");
            }
            ActUIUpdater.resetAIInteractionAreas(false);
            currentFullActNarrativeStream = "";
        });
    }

    if (clearSuggestionButton) {
        clearSuggestionButton.addEventListener('click', () => {
            ActUIUpdater.resetAIInteractionAreas(false);
            currentFullActNarrativeStream = "";
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

    ActUIUpdater.setAIControlsState(true, false, false);
});