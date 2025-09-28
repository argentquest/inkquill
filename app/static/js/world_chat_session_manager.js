// /ai_rag_story_app/app/static/js/world_chat_session_manager.js
"use strict";

const WorldChatSessionManager = (() => {
    const API_BASE_URL = "/api/v1/world-chat";
    
    let worldId = null;
    let callbacks = {};
    
    function init(worldIdParam, callbacksParam) {
        worldId = worldIdParam;
        callbacks = callbacksParam || {};
        setupSessionDropdownListeners();
    }
    
    function setupSessionDropdownListeners() {
        const dropdown = document.getElementById('session-dropdown-menu');
        if (dropdown) {
            dropdown.addEventListener('click', handleSessionDropdownClick);
        }
    }
    
    async function loadSessions() {
        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${worldId}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            populateSessionDropdown(data.sessions);
            
        } catch (error) {
            console.error("SessionManager: Error loading sessions:", error);
            if (callbacks.onError) callbacks.onError("Failed to load sessions");
        }
    }
    
    async function createNewSession() {
        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${worldId}`, {
                method: 'POST',
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const session = await response.json();
            
            if (callbacks.onSessionCreated) {
                callbacks.onSessionCreated(session.id, session);
            }
            
            await loadSessions(); // Refresh dropdown
            return session.id;
            
        } catch (error) {
            console.error("SessionManager: Error creating session:", error);
            if (callbacks.onError) callbacks.onError("Failed to create new session");
            throw error;
        }
    }
    
    async function loadSession(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${worldId}/${sessionId}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const session = await response.json();
            
            if (callbacks.onSessionLoaded) {
                callbacks.onSessionLoaded(session.id, session);
            }
            
            return session;
            
        } catch (error) {
            console.error("SessionManager: Error loading session:", error);
            if (callbacks.onError) callbacks.onError("Failed to load session");
            throw error;
        }
    }
    
    async function deleteSession(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/sessions/${worldId}/${sessionId}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            if (callbacks.onSessionDeleted) {
                callbacks.onSessionDeleted(sessionId);
            }
            
            await loadSessions(); // Refresh dropdown
            
        } catch (error) {
            console.error("SessionManager: Error deleting session:", error);
            if (callbacks.onError) callbacks.onError("Failed to delete session");
        }
    }
    
    function populateSessionDropdown(sessions) {
        const dropdown = document.getElementById('session-dropdown-menu');
        if (!dropdown) return;
        
        if (!sessions || sessions.length === 0) {
            dropdown.innerHTML = '<li><span class="dropdown-item-text text-muted">No saved sessions</span></li>';
            return;
        }
        
        const items = sessions.map(session => `
            <li>
                <div class="session-item" data-session-id="${session.id}">
                    <div class="session-item-title">${escapeHtml(session.title)}</div>
                    <div class="session-item-time">${formatTimestamp(session.updated_at)}</div>
                </div>
            </li>
        `).join('');
        
        dropdown.innerHTML = items + `
            <li><hr class="dropdown-divider"></li>
            <li><button class="dropdown-item text-danger" id="clear-all-sessions">
                <i class="fas fa-trash me-2"></i>Clear All Sessions
            </button></li>
        `;
    }
    
    async function handleSessionDropdownClick(event) {
        const sessionItem = event.target.closest('.session-item');
        const clearAllBtn = event.target.closest('#clear-all-sessions');
        
        if (sessionItem) {
            const sessionId = parseInt(sessionItem.dataset.sessionId);
            await loadSession(sessionId);
        } else if (clearAllBtn) {
            if (confirm("Are you sure you want to delete all chat sessions?")) {
                // Implementation would need to delete all sessions
                console.log("Clear all sessions requested");
            }
        }
    }
    
    function formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch {
            return timestamp;
        }
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    return {
        init,
        loadSessions,
        createNewSession,
        loadSession,
        deleteSession
    };
})();