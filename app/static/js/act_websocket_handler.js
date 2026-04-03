// /story_app/app/static/js/act_websocket_handler.js
"use strict";

const ActWebSocketHandler = (() => {
    let actWebSocket = null;
    let onMessageCallback = null;
    let onOpenCallback = null;
    let onCloseCallback = null;
    let onErrorCallback = null;
    
    const API_BASE_URL = "/api/v1"; // Assuming this is consistent

    async function getWSTicket() {
        console.log("ActWebSocketHandler: Requesting WebSocket ticket...");
        try {
            const response = await fetch(`${API_BASE_URL}/auth/ws-ticket`, { 
                method: 'GET', 
                credentials: 'include' 
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail || `Failed to get WebSocket ticket: ${response.status}`;
                console.error("ActWebSocketHandler: Failed to fetch WebSocket ticket -", detail);
                if (typeof showToast === 'function') showToast(`Error getting AI auth ticket: ${detail}`, "error");
                return null;
            }
            const data = await response.json();
            console.log("ActWebSocketHandler: WebSocket ticket received.");
            return data.ticket;
        } catch (error) {
            console.error("ActWebSocketHandler: Error fetching WebSocket ticket:", error);
            if (typeof showToast === 'function') showToast("Network error getting AI auth ticket.", "error");
            return null;
        }
    }

    async function initialize(storyId, actId, msgCallback, openCallback, closeCallback, errorCallback) {
        if (!storyId || !actId) {
            console.error("ActWebSocketHandler: Story ID or Act ID is missing. Cannot initialize WebSocket.");
            if (typeof showToast === 'function') showToast("Cannot connect to AI: Missing critical context.", "error");
            if (errorCallback) errorCallback(new Error("Missing storyId or actId for WebSocket."));
            return false;
        }

        onMessageCallback = msgCallback;
        onOpenCallback = openCallback;
        onCloseCallback = closeCallback;
        onErrorCallback = errorCallback;

        const ticket = await getWSTicket();
        if (!ticket) {
            console.error("ActWebSocketHandler: No WebSocket ticket obtained. Cannot connect.");
            if (typeof showToast === 'function') showToast("AI Authentication failed. AI features disabled.", "error");
            if (errorCallback) errorCallback(new Error("Failed to obtain WebSocket ticket."));
            return false;
        }

        const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
        const wsURL = `${wsScheme}://${window.location.host}/ws/stories/${storyId}/acts/${actId}/generate?ticket=${encodeURIComponent(ticket)}`;
        
        console.log(`ActWebSocketHandler: Attempting to connect to Act AI WebSocket: ${wsURL}`);

        if (actWebSocket && (actWebSocket.readyState === WebSocket.OPEN || actWebSocket.readyState === WebSocket.CONNECTING)) {
            console.log("ActWebSocketHandler: WebSocket already open or connecting.");
            return true; 
        }

        try {
            actWebSocket = new WebSocket(wsURL);
        } catch (e) {
            console.error("ActWebSocketHandler: Error creating WebSocket object:", e);
            if (typeof showToast === 'function') showToast("Error initializing AI connection.", "error");
            if (onErrorCallback) onErrorCallback(e);
            return false;
        }
        
        actWebSocket.onopen = (event) => {
            console.log("ActWebSocketHandler: Act AI WebSocket connected.");
            if (onOpenCallback) onOpenCallback(event);
        };
        
        actWebSocket.onmessage = (event) => {
            let messageData;
            try {
                messageData = JSON.parse(event.data);
                console.log("ActWebSocketHandler: Received message - Type:", messageData.type);
                if (onMessageCallback) onMessageCallback(messageData);
            } catch (e) {
                console.error("ActWebSocketHandler: Non-JSON WebSocket message received or parse error:", event.data, e);
                // Optionally, pass raw non-JSON data to a different callback or handle specific non-JSON messages
                if (onMessageCallback) onMessageCallback({ type: "raw_text_error", data: event.data, error: e.message });
            }
        };
        
        actWebSocket.onclose = (event) => {
            console.warn(`ActWebSocketHandler: Act AI WebSocket closed. Code: ${event.code}, Reason: '${event.reason}', Clean: ${event.wasClean}`);
            if (onCloseCallback) onCloseCallback(event);
            actWebSocket = null; // Clear instance on close
        };
        
        actWebSocket.onerror = (event) => {
            console.error("ActWebSocketHandler: Act AI WebSocket error:", event);
            if (onErrorCallback) onErrorCallback(event);
            // Note: The 'onclose' event will usually follow an 'onerror' event.
        };
        return true; // Indicates an attempt to connect was made
    }

    function sendMessage(payload) {
        if (actWebSocket && actWebSocket.readyState === WebSocket.OPEN) {
            try {
                const messageString = JSON.stringify(payload);
                actWebSocket.send(messageString);
                console.log("ActWebSocketHandler: Message sent:", payload);
                
                // Track AI interaction
                if (window.trackAIInteraction) {
                    const interactionType = payload.action || payload.type || 'act_generation';
                    const model = payload.model || 'unknown';
                    window.trackAIInteraction(interactionType, model);
                }
                
                return true;
            } catch (e) {
                console.error("ActWebSocketHandler: Error stringifying payload for WebSocket:", e, payload);
                if (typeof showToast === 'function') showToast("Error preparing message for AI.", "error");
                return false;
            }
        } else {
            console.warn("ActWebSocketHandler: WebSocket not open. Cannot send message.");
            if (typeof showToast === 'function') showToast("AI connection not ready. Please wait or try reconnecting.", "warning");
            return false;
        }
    }

    function getReadyState() {
        if (actWebSocket) {
            return actWebSocket.readyState;
        }
        return WebSocket.CLOSED; // Or another appropriate constant if WebSocket is null
    }

    function closeConnection(code, reason) {
        if (actWebSocket && actWebSocket.readyState === WebSocket.OPEN) {
            console.log(`ActWebSocketHandler: Explicitly closing WebSocket connection. Code: ${code}, Reason: ${reason}`);
            actWebSocket.close(code, reason);
        }
        actWebSocket = null; // Ensure it's nulled out
    }

    return {
        initialize: initialize,
        sendMessage: sendMessage,
        getReadyState: getReadyState,
        closeConnection: closeConnection
    };
})();
