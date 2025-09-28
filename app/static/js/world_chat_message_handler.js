// /ai_rag_story_app/app/static/js/world_chat_message_handler.js
"use strict";

const WorldChatMessageHandler = (() => {
    const API_BASE_URL = "/api/v1/world-chat";
    
    let worldId = null;
    let callbacks = {};
    
    function init(worldIdParam, callbacksParam) {
        worldId = worldIdParam;
        callbacks = callbacksParam || {};
    }
    
    async function sendMessage(sessionId, message, options = {}) {
        try {
            if (callbacks.onMessageSent) {
                callbacks.onMessageSent(message);
            }
            
            const requestData = {
                message: message,
                element_type: options.elementType || null,
                element_id: options.elementId || null,
                ai_model_config_id: options.aiModelConfigId || null
            };
            
            const response = await fetch(`${API_BASE_URL}/sessions/${worldId}/${sessionId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData),
                credentials: 'include'
            });
            
            // Track AI interaction
            if (window.trackAIInteraction) {
                const elementContext = options.elementType ? `${options.elementType}_context` : 'general';
                window.trackAIInteraction('world_chat', `world_chat_${elementContext}`);
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }
            
            const responseData = await response.json();
            
            if (callbacks.onResponseReceived) {
                callbacks.onResponseReceived(responseData.ai_response.content, responseData);
            }
            
            return responseData;
            
        } catch (error) {
            console.error("MessageHandler: Error sending message:", error);
            if (callbacks.onError) {
                callbacks.onError("Failed to send message: " + error.message);
            }
            throw error;
        }
    }
    
    return {
        init,
        sendMessage
    };
})();