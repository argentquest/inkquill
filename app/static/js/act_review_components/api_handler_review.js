// /ai_rag_story_app/app/static/js/act_review_components/api_handler_review.js
"use strict";

const APIHandler_Review = (() => {
    const API_BASE_URL = "/api/v1";

    async function fetchAIReview(actId, currentActContentForReview, modelConfigId = null) {
        const requestPayload = { 
            act_content_to_analyze_override: currentActContentForReview,
            model_config_id: modelConfigId 
        };
        const apiUrl = `${API_BASE_URL}/acts/${actId}/ai/review`;
        console.log("APIHandler_Review: Fetching AI review from URL:", apiUrl, "with payload (content length):", currentActContentForReview.length, "model ID:", modelConfigId);

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestPayload),
                credentials: 'include'
            });
            
            const rawResponseText = await response.text();
            let parsedJson = null;
            let parseError = null;
            try {
                parsedJson = JSON.parse(rawResponseText);
            } catch (e) {
                parseError = e;
            }

            return { 
                ok: response.ok, 
                status: response.status,
                rawText: rawResponseText, 
                parsedJson: parsedJson, // Will be null if parsing failed
                parseError: parseError, // Will contain error object if parsing failed
                errorDetail: (!response.ok && parsedJson && parsedJson.detail) ? parsedJson.detail : null
            };
        } catch (networkError) {
            console.error("APIHandler_Review: Network error during fetchAIReview:", networkError);
            return { 
                ok: false, 
                status: 0, // Or some indicator of network error
                rawText: "Network error occurred.", 
                parsedJson: null, 
                parseError: networkError,
                errorDetail: "Network error. Please check your connection."
            };
        }
    }

    async function saveActContent(actId, contentHtml) {
        const payload = { description: (contentHtml === "") ? null : contentHtml };
        const saveApiUrl = `${API_BASE_URL}/acts/${actId}`;
        console.log("APIHandler_Review: Saving Act content. URL:", saveApiUrl);

        try {
            const response = await fetch(saveApiUrl, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload),
                credentials: 'include'
            });

            if (response.ok) {
                const result = await response.json();
                return { success: true, data: result };
            } else {
                const errorData = await response.json().catch(() => ({}));
                return { success: false, error: errorData.detail || `Failed to save (Status: ${response.status})` };
            }
        } catch (error) {
            console.error("APIHandler_Review: Network error during saveActContent:", error);
            return { success: false, error: "Network error saving Act content." };
        }
    }

    return {
        fetchAIReview,
        saveActContent
    };
})();