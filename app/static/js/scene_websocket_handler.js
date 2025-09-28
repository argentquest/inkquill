// /ai_rag_story_app/app/static/js/scene_websocket_handler.js
"use strict";

const SceneWebSocketHandler = (() => {
    let sceneWebSocket = null; // Specific to scenes
    let onMessageCallback = null;
    let onOpenCallback = null;
    let onCloseCallback = null;
    let onErrorCallback = null;
    
    const API_BASE_URL = "/api/v1"; 

    async function getWSTicket() {
        console.log("SceneWebSocketHandler: Requesting WebSocket ticket...");
        try {
            const response = await fetch(`${API_BASE_URL}/auth/ws-ticket`, { 
                method: 'GET', 
                credentials: 'include' 
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail || `Failed to get WebSocket ticket: ${response.status}`;
                console.error("SceneWebSocketHandler: Failed to fetch WebSocket ticket -", detail);
                if (typeof showToast === 'function') showToast(`Error getting AI auth ticket: ${detail}`, "error");
                return null;
            }
            const data = await response.json();
            console.log("SceneWebSocketHandler: WebSocket ticket received.");
            return data.ticket;
        } catch (error) {
            console.error("SceneWebSocketHandler: Error fetching WebSocket ticket:", error);
            if (typeof showToast === 'function') showToast("Network error while getting AI auth ticket.", "error");
            return null;
        }
    }

    async function initialize(storyId, actId, sceneId, msgCallback, openCallback, closeCallback, errorCallback) {
        if (!storyId || !actId || !sceneId) { // sceneId is crucial for this WebSocket
            console.error("SceneWebSocketHandler: Story ID, Act ID, or Scene ID is missing. Cannot initialize WebSocket.");
            if (typeof showToast === 'function') showToast("Cannot connect to Scene AI: Missing critical context.", "error");
            if (errorCallback) errorCallback(new Error("Missing storyId, actId, or sceneId for Scene WebSocket."));
            return false;
        }

        onMessageCallback = msgCallback;
        onOpenCallback = openCallback;
        onCloseCallback = closeCallback;
        onErrorCallback = errorCallback;

        const ticket = await getWSTicket();
        if (!ticket) {
            console.error("SceneWebSocketHandler: No WebSocket ticket obtained. Cannot connect.");
            if (typeof showToast === 'function') showToast("Scene AI Authentication failed. AI features disabled.", "error");
            if (errorCallback) errorCallback(new Error("Failed to obtain WebSocket ticket for Scene AI."));
            return false;
        }

        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsURL = `${wsScheme}://${window.location.host}/ws/stories/${storyId}/acts/${actId}/scenes/${sceneId}/generate?ticket=${encodeURIComponent(ticket)}`;
        
        console.log(`SceneWebSocketHandler: Attempting to connect to Scene AI WebSocket: ${wsURL}`);

        if (sceneWebSocket && (sceneWebSocket.readyState === WebSocket.OPEN || sceneWebSocket.readyState === WebSocket.CONNECTING)) {
            console.log("SceneWebSocketHandler: Scene WebSocket already open or connecting.");
            return true; 
        }

        try {
            sceneWebSocket = new WebSocket(wsURL);
        } catch (e) {
            console.error("SceneWebSocketHandler: Error creating Scene WebSocket object:", e);
            if (typeof showToast === 'function') showToast("Error initializing Scene AI connection.", "error");
            if (onErrorCallback) onErrorCallback(e);
            return false;
        }
        
        sceneWebSocket.onopen = (event) => {
            console.log("SceneWebSocketHandler: Scene AI WebSocket connected.");
            if (onOpenCallback) onOpenCallback(event);
        };
        
        sceneWebSocket.onmessage = (event) => {
            let messageData;
            try {
                messageData = JSON.parse(event.data);
                console.log("SceneWebSocketHandler: Received message - Type:", messageData.type);
                if (onMessageCallback) onMessageCallback(messageData);
            } catch (e) {
                console.error("SceneWebSocketHandler: Non-JSON WebSocket message received or parse error:", event.data, e);
                if (onMessageCallback) onMessageCallback({ type: "raw_text_error", data: event.data, error: e.message });
            }
        };
        
        sceneWebSocket.onclose = (event) => {
            console.warn(`SceneWebSocketHandler: Scene AI WebSocket closed. Code: ${event.code}, Reason: '${event.reason}', Clean: ${event.wasClean}`);
            if (onCloseCallback) onCloseCallback(event);
            sceneWebSocket = null; 
        };
        
        sceneWebSocket.onerror = (event) => {
            console.error("SceneWebSocketHandler: Scene AI WebSocket error:", event);
            if (onErrorCallback) onErrorCallback(event);
        };
        return true; 
    }

    function sendMessage(payload) {
        if (sceneWebSocket && sceneWebSocket.readyState === WebSocket.OPEN) {
            try {
                const messageString = JSON.stringify(payload);
                sceneWebSocket.send(messageString);
                console.log("SceneWebSocketHandler: Message sent:", payload);
                
                // Track AI interaction
                if (window.trackAIInteraction) {
                    const interactionType = payload.action || payload.type || 'scene_generation';
                    const model = payload.model || 'unknown';
                    window.trackAIInteraction(interactionType, model);
                }
                
                return true;
            } catch (e) {
                console.error("SceneWebSocketHandler: Error stringifying payload for WebSocket:", e, payload);
                if (typeof showToast === 'function') showToast("Error preparing message for Scene AI.", "error");
                return false;
            }
        } else {
            console.warn("SceneWebSocketHandler: Scene WebSocket not open. Cannot send message.");
            if (typeof showToast === 'function') showToast("Scene AI connection not ready. Please wait or try reconnecting.", "warning");
            return false;
        }
    }

    function getReadyState() {
        if (sceneWebSocket) {
            return sceneWebSocket.readyState;
        }
        return WebSocket.CLOSED; 
    }

    function closeConnection(code, reason) {
        if (sceneWebSocket && sceneWebSocket.readyState === WebSocket.OPEN) {
            console.log(`SceneWebSocketHandler: Explicitly closing Scene WebSocket connection. Code: ${code}, Reason: ${reason}`);
            sceneWebSocket.close(code, reason);
        }
        sceneWebSocket = null; 
    }

    return {
        initialize: initialize,
        sendMessage: sendMessage,
        getReadyState: getReadyState,
        closeConnection: closeConnection
    };
})();