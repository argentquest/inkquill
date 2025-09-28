// /ai_rag_story_app/app/static/js/act_ai_review_page.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    // Get static IDs from the page
    const storyIdElement = document.getElementById('story-id-for-review');
    const actIdElement = document.getElementById('act-id-for-review');
    const storyId = storyIdElement ? storyIdElement.value : null;
    const actId = actIdElement ? actIdElement.value : null;

    const triggerReviewButton = document.getElementById('trigger-ai-review-button');
    const saveActButton = document.getElementById('save-act-changes-button-review');
    const statusMessageElement = document.getElementById('ai-review-status-message');
    const suggestionsContainer = document.getElementById('ai-review-suggestions-container');


    console.log("Main ActReviewPageJS: DOMContentLoaded. StoryID:", storyId, "ActID:", actId);

    if (!storyId || !actId) {
        if (statusMessageElement) statusMessageElement.textContent = "Error: Page context incomplete.";
        if (triggerReviewButton) triggerReviewButton.disabled = true;
        if (saveActButton) saveActButton.disabled = true;
        console.error("Main ActReviewPageJS: Story ID or Act ID missing.");
        return;
    }

    // Initialize Modules
    const quillInstance = QuillManager_Review.initialize();
    if (!quillInstance) {
        console.error("Main ActReviewPageJS: Quill editor could not be initialized. Page functionality limited.");
        // Disable buttons that rely on Quill
        if (triggerReviewButton) triggerReviewButton.disabled = true;
        if (saveActButton) saveActButton.disabled = true;
        return; 
    }
    TextHighlighter_Review.initialize(quillInstance); // Pass Quill instance to highlighter
    
    // Initialize AI Model Selector
    if (typeof AIModelSelector !== 'undefined') {
        AIModelSelector.initialize('ai-model-config-select-review');
    } else {
        console.warn("Main ActReviewPageJS: AIModelSelector not loaded.");
    }

    // --- Function to handle applying suggestions ---
    function handleApplySuggestion(applyButton, quillInstance) {
        // Recommendation: The AI response should provide start and length indices.
        // These would be passed to the button's dataset.
        const startIndex = parseInt(applyButton.dataset.startIndex, 10);
        const length = parseInt(applyButton.dataset.length, 10);
        const proposedSolution = applyButton.dataset.proposedSolution;
        const suggestionId = applyButton.dataset.suggestionId;

        if (isNaN(startIndex) || isNaN(length) || !proposedSolution) {
            // Fallback to old method or show an error. Using alert for demonstration.
            alert('Cannot apply this suggestion: Invalid text range or solution provided.');
            return;
        }

        try {
            const originalText = quillInstance.getText(startIndex, length);
            if (originalText.length === 0 && length > 0) {
                alert('Cannot find the text to replace. The content may have changed significantly.');
                return;
            }

            // Confirm the replacement
            // Recommendation: Replace confirm() with a non-blocking UI modal for better UX.
            const confirmMessage = `Apply this suggestion?\n\nCurrent: "${originalText}"\n\nProposed: "${proposedSolution}"`;
            if (!confirm(confirmMessage)) {
                return;
            }

            // Apply the replacement
            quillInstance.deleteText(startIndex, length);
            quillInstance.insertText(startIndex, proposedSolution);

            // Visual feedback
            applyButton.innerHTML = '<i class="fas fa-check me-1"></i>Applied';
            applyButton.classList.remove('btn-success');
            applyButton.classList.add('btn-success');
            applyButton.disabled = true;

            // Show success message
            if (statusMessageElement) {
                statusMessageElement.textContent = `Applied suggestion: ${proposedSolution.substring(0, 50)}${proposedSolution.length > 50 ? '...' : ''}`;
                statusMessageElement.className = "text-success small mt-2";
            }

            console.log(`Applied suggestion ${suggestionId}: Replaced "${originalText}" with "${proposedSolution}" at index ${startIndex}`);

        } catch (error) {
            console.error('Error applying suggestion:', error);
            alert('An error occurred while applying the suggestion. Please try again.');
        }
    }

    // --- Event Listener for dynamically created suggestion items ---
    if (suggestionsContainer) {
        suggestionsContainer.addEventListener('click', (event) => {
            // Handle Apply button clicks
            const applyButton = event.target.closest('.apply-suggestion-btn');
            if (applyButton) {
                handleApplySuggestion(applyButton, quillInstance);
                return;
            }
            
            // Handle suggestion item clicks for highlighting
            const suggestionItem = event.target.closest('.suggestion-item-clickable');
            if (suggestionItem) {
                const startSnippet = suggestionItem.dataset.contextStart;
                const endSnippet = suggestionItem.dataset.contextEnd;
                TextHighlighter_Review.highlight(startSnippet, endSnippet);
            }
        });
    }


    // --- Event Listener for "Get AI Review" Button ---
    if (triggerReviewButton) {
        triggerReviewButton.addEventListener('click', async () => {
            if (!statusMessageElement || !saveActButton) return;

            statusMessageElement.textContent = "Requesting AI review...";
            statusMessageElement.className = "text-info small mt-2";
            triggerReviewButton.disabled = true;
            saveActButton.disabled = true; // Disable save during review
            const originalButtonHTML = triggerReviewButton.innerHTML;
            triggerReviewButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Fetching...`;

            UIUpdater_Review.clearAllPlaceholders();
            UIUpdater_Review.updateRawAIOutput("Fetching raw AI response...");
            UIUpdater_Review.updateAIPromptDisplay("Preparing prompt data...");
            if (suggestionsContainer) suggestionsContainer.innerHTML = "";
            const metricsContainer = document.getElementById('ai-review-metrics-container');
            if (metricsContainer) metricsContainer.innerHTML = "";


            const currentContent = QuillManager_Review.getContentHtml();
            
            // Get selected AI model
            const modelSelector = document.getElementById('ai-model-config-select-review');
            const selectedModelId = modelSelector && modelSelector.value ? parseInt(modelSelector.value, 10) : null;
            
            // Update prompt display with client-side args
            try {
                const promptArgsForDisplay = {
                    note_from_frontend: "Client-side arguments sent (Backend adds more context).",
                    client_sent_payload: {
                        act_content_to_analyze_override_details: {
                            length_chars: currentContent.length,
                            content_preview_on_client: currentContent.substring(0, 500) + (currentContent.length > 500 ? "..." : "")
                            // For full content in this display, pass currentContent directly if desired, but be mindful of large text
                        },
                        selected_model_id: selectedModelId
                    }
                };
                UIUpdater_Review.updateAIPromptDisplay(JSON.stringify(promptArgsForDisplay, null, 2));
            } catch (e) {
                UIUpdater_Review.updateAIPromptDisplay("Error formatting prompt arguments for display.");
            }


            const result = await APIHandler_Review.fetchAIReview(actId, currentContent, selectedModelId);

            UIUpdater_Review.updateRawAIOutput(result.rawText, !result.parseError && result.parsedJson); // Pretty print if no parse error

            if (!result.ok || result.parseError) {
                const errorMessage = result.errorDetail || (result.parseError ? "AI returned improperly formatted data." : "Failed to get AI review.");
                statusMessageElement.textContent = `Error: ${errorMessage}`;
                statusMessageElement.className = "text-danger small mt-2";
                if (typeof showToast === 'function') showToast(`Error fetching review: ${errorMessage}`, "error");
                UIUpdater_Review.showPlaceholder('suggestions');
                UIUpdater_Review.showPlaceholder('metrics');
            } else {
                console.log("AIReview: Success! Full parsed response:", result.parsedJson);
                console.log("AIReview: Suggestions array:", result.parsedJson.suggestions);
                console.log("AIReview: Metrics object:", result.parsedJson.metrics);
                UIUpdater_Review.renderSuggestions(result.parsedJson.suggestions || []);
                UIUpdater_Review.renderMetrics(result.parsedJson.metrics || null);
                
                let messageForUser = "";
                if (result.parsedJson.suggestions && result.parsedJson.suggestions.length > 0) messageForUser += "Suggestions loaded. ";
                if (result.parsedJson.metrics) messageForUser += "Metrics loaded.";
                if (!messageForUser) messageForUser = result.parsedJson.message || "AI analysis complete.";

                statusMessageElement.textContent = messageForUser.trim();
                statusMessageElement.className = "text-success small mt-2";
                if (typeof showToast === 'function') showToast("AI review data processed!", "success");
            }
            
            triggerReviewButton.disabled = false;
            triggerReviewButton.innerHTML = originalButtonHTML;
            if (saveActButton) saveActButton.disabled = false;
        });
    } else {
        console.warn("Main ActReviewPageJS: Trigger AI Review button not found.");
    }

    // --- Event Listener for "Save Act Content" Button ---
    if (saveActButton) {
        saveActButton.addEventListener('click', async () => {
            const contentToSave = QuillManager_Review.getContentHtml();
            const originalButtonText = saveActButton.textContent;
            saveActButton.disabled = true;
            if (triggerReviewButton) triggerReviewButton.disabled = true;
            saveActButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Saving...`;

            const result = await APIHandler_Review.saveActContent(actId, contentToSave);

            if (result.success) {
                if(typeof showToast === 'function') showToast("Act content saved successfully!", "success");
                const hiddenTextarea = document.getElementById('act-content-for-quill-hidden-review-page');
                if(hiddenTextarea) hiddenTextarea.value = contentToSave; // Update hidden textarea
            } else {
                if(typeof showToast === 'function') showToast(`Error saving Act: ${result.error}`, "error");
            }
            saveActButton.disabled = false;
            saveActButton.innerHTML = originalButtonText;
            if (triggerReviewButton) triggerReviewButton.disabled = false;
        });
    } else {
        console.warn("Main ActReviewPageJS: Save Act Content button not found.");
    }
    
    // Initial placeholder display
    UIUpdater_Review.showPlaceholder('suggestions');
    UIUpdater_Review.showPlaceholder('metrics');
    UIUpdater_Review.updateAIPromptDisplay("Client-side prompt arguments will appear here...");
    UIUpdater_Review.updateRawAIOutput("Raw AI response will appear here...");

    console.log("Main ActReviewPageJS: Initialization complete with modular components.");
});