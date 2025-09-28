// /ai_rag_story_app/app/static/js/world_chat_main.js
"use strict";

const WorldChatMain = (() => {
    const API_BASE_URL = "/api/v1";
    
    let currentWorldId = null;
    let currentSessionId = null;
    let currentUserId = null;
    
    // Module references
    let sessionManager = null;
    let contextLoader = null;
    let messageHandler = null;
    
    // DOM elements
    let elements = {};
    
    function init() {
        try {
            console.log("WorldChatMain: Initializing...");
            
            // Get context from hidden inputs
            currentWorldId = document.getElementById('world-id')?.value;
            currentUserId = document.getElementById('current-user-id')?.value;
            
            if (!currentWorldId) {
                console.error("WorldChatMain: No world ID found");
                showError("World ID not found. Please navigate to a valid world.");
                return;
            }
            
            // Cache DOM elements
            cacheElements();
            
            // Initialize modules
            initializeModules();
            
            // Set up event listeners
            setupEventListeners();
            
            // Load initial data
            loadInitialData();
            
            console.log("WorldChatMain: Initialization complete");
            
        } catch (error) {
            console.error("WorldChatMain: Initialization error:", error);
            showError("Failed to initialize chat interface");
        }
    }
    
    function cacheElements() {
        elements = {
            // Session management
            newSessionBtn: document.getElementById('new-session-btn'),
            clearConversationBtn: document.getElementById('clear-conversation-btn'),
            sessionDropdown: document.getElementById('session-dropdown-menu'),
            sessionTitle: document.getElementById('session-title'),
            sessionTimestamp: document.getElementById('session-timestamp'),
            currentSessionIdInput: document.getElementById('current-session-id'),
            
            // Chat interface
            chatMessages: document.getElementById('chat-messages'),
            messageInput: document.getElementById('message-input'),
            sendBtn: document.getElementById('send-btn'),
            typingIndicator: document.getElementById('typing-indicator'),
            
            // AI model selection
            aiModelSelect: document.getElementById('ai-model-config-select'),
            
            // Context panel
            charactersCount: document.getElementById('characters-count'),
            locationsCount: document.getElementById('locations-count'),
            storiesCount: document.getElementById('stories-count'),
            charactersList: document.getElementById('characters-list'),
            locationsList: document.getElementById('locations-list'),
            loreList: document.getElementById('lore-list'),
            
            // Chat suggestions
            suggestionsArea: document.getElementById('suggestions-area'),
            chatSuggestions: document.getElementById('chat-suggestions'),
            
            // World image
            worldImageCard: document.getElementById('world-image-card'),
            worldImage: document.getElementById('world-image'),
            
            // Statistics
            inputTokens: document.getElementById('input-tokens'),
            outputTokens: document.getElementById('output-tokens'),
            totalTokens: document.getElementById('total-tokens'),
            callCost: document.getElementById('call-cost'),
            modelName: document.getElementById('model-name'),
            durationMs: document.getElementById('duration-ms')
        };
        
        // Validate required elements
        const requiredElements = ['chatMessages', 'messageInput', 'sendBtn'];
        for (const elementName of requiredElements) {
            if (!elements[elementName]) {
                throw new Error(`Required element not found: ${elementName}`);
            }
        }
    }
    
    function initializeModules() {
        // Initialize session manager
        if (typeof WorldChatSessionManager !== 'undefined') {
            sessionManager = WorldChatSessionManager;
            sessionManager.init(currentWorldId, {
                onSessionCreated: handleSessionCreated,
                onSessionLoaded: handleSessionLoaded,
                onSessionDeleted: handleSessionDeleted,
                onError: showError
            });
        }
        
        // Initialize context loader
        if (typeof WorldChatContextLoader !== 'undefined') {
            contextLoader = WorldChatContextLoader;
            contextLoader.init(currentWorldId, {
                onContextLoaded: handleContextLoaded,
                onElementSelected: handleElementSelected,
                onError: showError
            });
        }
        
        // Initialize message handler
        if (typeof WorldChatMessageHandler !== 'undefined') {
            messageHandler = WorldChatMessageHandler;
            messageHandler.init(currentWorldId, {
                onMessageSent: handleMessageSent,
                onResponseReceived: handleResponseReceived,
                onError: showError
            });
        }
        
        console.log("WorldChatMain: Modules initialized");
    }
    
    function setupEventListeners() {
        // New session button
        if (elements.newSessionBtn) {
            elements.newSessionBtn.addEventListener('click', handleNewSessionClick);
        }
        
        // Clear conversation button
        if (elements.clearConversationBtn) {
            elements.clearConversationBtn.addEventListener('click', handleClearConversationClick);
        }
        
        // Message input
        if (elements.messageInput) {
            elements.messageInput.addEventListener('input', handleMessageInputChange);
            elements.messageInput.addEventListener('keydown', handleMessageInputKeydown);
        }
        
        // Send button
        if (elements.sendBtn) {
            elements.sendBtn.addEventListener('click', handleSendButtonClick);
        }
        
        // Chat suggestions (use event delegation since buttons are loaded dynamically)
        if (elements.chatSuggestions) {
            elements.chatSuggestions.addEventListener('click', handleSuggestionClick);
        }
        
        console.log("WorldChatMain: Event listeners set up");
    }
    
    async function loadInitialData() {
        try {
            // Load chat suggestions
            await loadChatSuggestions();
            
            // Load AI models
            if (typeof AIModelSelector !== 'undefined' && elements.aiModelSelect) {
                await AIModelSelector.loadAndPopulateModels(elements.aiModelSelect);
            }
            
            // Load world context
            if (contextLoader) {
                await contextLoader.loadWorldContext();
            }
            
            // Load existing sessions
            if (sessionManager) {
                await sessionManager.loadSessions();
            }
            
            console.log("WorldChatMain: Initial data loaded");
            
        } catch (error) {
            console.error("WorldChatMain: Error loading initial data:", error);
            showError("Failed to load initial data");
        }
    }
    
    async function loadChatSuggestions() {
        try {
            console.log('WorldChatMain: Loading chat suggestions...');
            const response = await fetch('/api/v1/world-chat/chat/samples');
            console.log('WorldChatMain: Chat samples response:', response.status, response.statusText);
            
            if (response.ok) {
                const samples = await response.json();
                console.log('WorldChatMain: Chat samples data:', samples);
                
                if (samples && samples.length > 0) {
                    elements.chatSuggestions.innerHTML = samples.map(sample => `
                        <button type="button" 
                                class="btn btn-outline-primary btn-sm suggestion-btn" 
                                data-suggestion="${sample.prompt_text}"
                                data-bs-toggle="tooltip" 
                                data-bs-placement="top" 
                                title="${sample.prompt_text}">
                            ${sample.title}
                        </button>
                    `).join('');
                    
                    console.log('WorldChatMain: Chat suggestions loaded successfully');
                    
                    // Initialize Bootstrap tooltips
                    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                    tooltipTriggerList.map(function (tooltipTriggerEl) {
                        return new bootstrap.Tooltip(tooltipTriggerEl);
                    });
                } else {
                    console.log('WorldChatMain: No chat samples found');
                    elements.chatSuggestions.innerHTML = '<small class="text-muted">No suggestions available</small>';
                }
            } else {
                console.error('WorldChatMain: Failed to load chat samples:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('WorldChatMain: Error loading chat suggestions:', error);
            // Fallback to empty suggestions if loading fails
            if (elements.chatSuggestions) {
                elements.chatSuggestions.innerHTML = '<small class="text-muted">Suggestions unavailable</small>';
            }
        }
    }
    
    // Event handlers
    async function handleNewSessionClick() {
        try {
            if (sessionManager) {
                await sessionManager.createNewSession();
            }
        } catch (error) {
            console.error("WorldChatMain: Error creating new session:", error);
            showError("Failed to create new session");
        }
    }
    
    function handleClearConversationClick() {
        if (confirm("Are you sure you want to clear the current conversation?")) {
            clearChatMessages();
            updateSessionTitle("New Conversation");
            updateSessionTimestamp("Just started");
            currentSessionId = null;
            if (elements.currentSessionIdInput) {
                elements.currentSessionIdInput.value = "";
            }
        }
    }
    
    function handleMessageInputChange() {
        const hasText = elements.messageInput.value.trim().length > 0;
        elements.sendBtn.disabled = !hasText;
    }
    
    function handleMessageInputKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendButtonClick();
        }
    }
    
    function handleSuggestionClick(event) {
        if (event.target.classList.contains('suggestion-btn')) {
            const suggestion = event.target.getAttribute('data-suggestion');
            if (suggestion && elements.messageInput) {
                elements.messageInput.value = suggestion;
                elements.messageInput.focus();
                // Auto-resize the textarea if needed
                if (elements.messageInput.style) {
                    elements.messageInput.style.height = 'auto';
                    elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 120) + 'px';
                }
                // Enable send button
                handleMessageInputChange();
            }
        }
    }
    
    async function handleSendButtonClick() {
        const message = elements.messageInput.value.trim();
        if (!message) return;
        
        try {
            // Ensure we have a session
            if (!currentSessionId && sessionManager) {
                currentSessionId = await sessionManager.createNewSession();
            }
            
            if (!currentSessionId) {
                throw new Error("No active session");
            }
            
            // Clear input immediately
            elements.messageInput.value = "";
            elements.sendBtn.disabled = true;
            
            // Send message
            if (messageHandler) {
                await messageHandler.sendMessage(currentSessionId, message, {
                    aiModelConfigId: elements.aiModelSelect?.value || null
                });
            }
            
        } catch (error) {
            console.error("WorldChatMain: Error sending message:", error);
            showError("Failed to send message");
        }
    }
    
    // Module callbacks
    function handleSessionCreated(sessionId, sessionData) {
        currentSessionId = sessionId;
        if (elements.currentSessionIdInput) {
            elements.currentSessionIdInput.value = sessionId;
        }
        updateSessionTitle(sessionData.title);
        updateSessionTimestamp("Just now");
        clearChatMessages();
        console.log("WorldChatMain: Session created:", sessionId);
    }
    
    function handleSessionLoaded(sessionId, sessionData) {
        currentSessionId = sessionId;
        if (elements.currentSessionIdInput) {
            elements.currentSessionIdInput.value = sessionId;
        }
        updateSessionTitle(sessionData.title);
        updateSessionTimestamp(formatTimestamp(sessionData.updated_at));
        loadSessionMessages(sessionData.messages || []);
        console.log("WorldChatMain: Session loaded:", sessionId);
    }
    
    function handleSessionDeleted(sessionId) {
        if (currentSessionId === sessionId) {
            currentSessionId = null;
            if (elements.currentSessionIdInput) {
                elements.currentSessionIdInput.value = "";
            }
            updateSessionTitle("New Conversation");
            updateSessionTimestamp("Just started");
            clearChatMessages();
        }
        console.log("WorldChatMain: Session deleted:", sessionId);
    }
    
    function handleContextLoaded(contextData) {
        updateWorldStats(contextData);
        console.log("WorldChatMain: Context loaded");
    }
    
    function handleElementSelected(elementType, elementId, elementData) {
        // Could add element-specific context to the next message
        console.log("WorldChatMain: Element selected:", elementType, elementId);
    }
    
    function handleMessageSent(message) {
        addMessageToChat("user", message);
        showTypingIndicator(true);
    }
    
    function handleResponseReceived(response, fullData) {
        showTypingIndicator(false);
        addMessageToChat("assistant", response);
        updateSessionTimestamp("Just now");
        
        // Update statistics if available
        if (fullData && fullData.call_stats) {
            updateStatistics(fullData.call_stats);
        }
    }
    
    // UI helper functions
    function updateSessionTitle(title) {
        if (elements.sessionTitle) {
            elements.sessionTitle.textContent = title;
        }
    }
    
    function updateSessionTimestamp(timestamp) {
        if (elements.sessionTimestamp) {
            elements.sessionTimestamp.textContent = timestamp;
        }
    }
    
    function clearChatMessages() {
        if (elements.chatMessages) {
            elements.chatMessages.innerHTML = `
                <div class="text-center text-muted py-5">
                    <i class="fas fa-magic fa-3x mb-3"></i>
                    <h5>Ready to Chat!</h5>
                    <p>Ask me anything about your world. I'm here to help you explore and develop your creative universe.</p>
                </div>
            `;
        }
    }
    
    function loadSessionMessages(messages) {
        clearChatMessages();
        if (messages && messages.length > 0) {
            messages.forEach(message => {
                addMessageToChat(message.role, message.content);
            });
        }
    }
    
    function addMessageToChat(role, content) {
        if (!elements.chatMessages) return;
        
        // Remove welcome message if it exists
        const welcomeMessage = elements.chatMessages.querySelector('.text-center.text-muted');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${role}`;
        
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const roleIcon = role === 'user' ? 'fas fa-user' : 'fas fa-robot';
        const roleName = role === 'user' ? 'You' : 'AI Assistant';
        
        messageDiv.innerHTML = `
            <div class="chat-message-header">
                <i class="${roleIcon} me-1"></i>
                <span>${roleName}</span>
                <span class="chat-message-time ms-2">${timestamp}</span>
            </div>
            <div class="chat-message-bubble">
                <div class="chat-message-content">${formatMessageContent(content)}</div>
            </div>
        `;
        
        elements.chatMessages.appendChild(messageDiv);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }
    
    function showTypingIndicator(show) {
        if (elements.typingIndicator) {
            elements.typingIndicator.style.display = show ? 'block' : 'none';
        }
    }
    
    function updateStatistics(callStats) {
        // Update token counts
        if (elements.inputTokens && callStats.input_tokens !== undefined) {
            elements.inputTokens.textContent = callStats.input_tokens.toLocaleString();
        }
        if (elements.outputTokens && callStats.output_tokens !== undefined) {
            elements.outputTokens.textContent = callStats.output_tokens.toLocaleString();
        }
        if (elements.totalTokens && callStats.total_tokens !== undefined) {
            elements.totalTokens.textContent = callStats.total_tokens.toLocaleString();
        }
        
        // Update cost (convert USD to Coins: 1 USD = 100 Coins)
        if (elements.callCost && callStats.cost !== undefined) {
            const costInCoins = callStats.cost * 100;
            elements.callCost.textContent = costInCoins.toFixed(2);
        }
        
        // Update model name
        if (elements.modelName && callStats.model_name) {
            elements.modelName.textContent = callStats.model_name;
        }
        
        // Update duration
        if (elements.durationMs && callStats.duration_ms !== undefined) {
            const seconds = (callStats.duration_ms / 1000).toFixed(2);
            elements.durationMs.textContent = `${seconds}s`;
        }
    }
    
    function updateWorldStats(contextData) {
        if (elements.charactersCount) {
            elements.charactersCount.textContent = contextData.characters?.length || 0;
        }
        if (elements.locationsCount) {
            elements.locationsCount.textContent = contextData.locations?.length || 0;
        }
        if (elements.storiesCount) {
            elements.storiesCount.textContent = contextData.stories?.length || 0;
        }
    }
    
    function showError(message) {
        console.error("WorldChatMain Error:", message);
        if (typeof showToast === 'function') {
            showToast(message, "error");
        } else {
            alert(message);
        }
    }
    
    function formatTimestamp(timestamp) {
        try {
            return new Date(timestamp).toLocaleString();
        } catch {
            return timestamp;
        }
    }
    
    function formatMessageContent(text) {
        // Basic HTML escaping first
        const div = document.createElement('div');
        div.textContent = text;
        let escaped = div.innerHTML;
        
        // Convert markdown-style formatting to HTML
        escaped = escaped
            // Bold text: **text** -> <strong>text</strong>
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic text: *text* -> <em>text</em>
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Convert literal \n\n to double line breaks
            .replace(/\\n\\n/g, '<br><br>')
            // Convert literal \n to single line break
            .replace(/\\n/g, '<br>')
            // Convert actual double newlines to paragraph breaks
            .replace(/\n\n/g, '</p><p>')
            // Convert actual single newlines to line breaks
            .replace(/\n/g, '<br>')
            // Wrap in paragraph tags if there's content
            .replace(/^(.+)$/s, '<p>$1</p>')
            // Clean up empty paragraphs
            .replace(/<p><\/p>/g, '');
        
        return escaped;
    }
    
    // Public API
    return {
        init,
        getCurrentSessionId: () => currentSessionId,
        getCurrentWorldId: () => currentWorldId
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    WorldChatMain.init();
});