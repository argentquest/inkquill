// /ai_rag_story_app/app/static/js/story_chat.js

class StoryChatInterface {
    constructor(storyId, containerId) {
        this.storyId = storyId;
        this.containerId = containerId;
        this.currentSessionId = null;
        this.websocket = null;
        this.isConnected = false;
        this.messageQueue = [];
        
        this.init();
    }
    
    async init() {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error(`Story chat container not found: ${this.containerId}`);
            return;
        }
        
        await this.renderInterface();
        await this.loadSessions();
    }
    
    async renderInterface() {
        this.container.innerHTML = `
            <div class="story-chat-interface">
                <!-- Chat Sessions Sidebar -->
                <div class="chat-sidebar">
                    <div class="sidebar-header">
                        <h5><i class="fas fa-comments me-2"></i>Story Discussions</h5>
                        <button class="btn btn-sm btn-primary" onclick="storyChatInterface.showNewSessionModal()">
                            <i class="fas fa-plus"></i> New Chat
                        </button>
                    </div>
                    <div class="sessions-list" id="sessions-list">
                        <!-- Sessions will be loaded here -->
                    </div>
                </div>
                
                <!-- Chat Area -->
                <div class="chat-area">
                    <div class="chat-header" id="chat-header" style="display: none;">
                        <div class="session-info">
                            <h6 id="session-title">Select a chat session</h6>
                            <small class="text-muted" id="session-focus"></small>
                        </div>
                        <div class="chat-actions">
                            <button class="btn btn-sm btn-outline-danger" onclick="storyChatInterface.deleteCurrentSession()">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    
                    <div class="chat-messages" id="chat-messages">
                        <div class="welcome-message">
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-robot fa-3x mb-3"></i>
                                <h5>Start a conversation about your story</h5>
                                <p>Select an existing chat session or create a new one to begin discussing your story with AI.</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="chat-input-area" id="chat-input-area" style="display: none;">
                        <div class="input-group">
                            <textarea class="form-control" id="message-input" 
                                      placeholder="Ask about your story, discuss plot ideas, or get writing advice..."
                                      rows="2"></textarea>
                            <button class="btn btn-primary" id="send-button" onclick="storyChatInterface.sendMessage()">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        
                        <!-- Target Element Selection -->
                        <div class="mt-2">
                            <small class="text-muted">Focus on specific story element:</small>
                            <select class="form-select form-select-sm" id="target-element-select" style="width: auto; display: inline-block;">
                                <option value="">General discussion</option>
                                <option value="story">Entire story</option>
                                <!-- Acts and scenes will be populated dynamically -->
                            </select>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- New Session Modal -->
            <div class="modal fade" id="newSessionModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Start New Chat Session</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="new-session-form">
                                <div class="mb-3">
                                    <label for="session-title-input" class="form-label">Chat Title</label>
                                    <input type="text" class="form-control" id="session-title-input" 
                                           placeholder="e.g., Plot Development, Character Discussion">
                                </div>
                                <div class="mb-3">
                                    <label for="session-description-input" class="form-label">Description (Optional)</label>
                                    <textarea class="form-control" id="session-description-input" rows="2"
                                              placeholder="What do you want to discuss about your story?"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="session-focus-input" class="form-label">Focus Area</label>
                                    <select class="form-select" id="session-focus-input">
                                        <option value="general">General Discussion</option>
                                        <option value="plot">Plot Development</option>
                                        <option value="characters">Character Development</option>
                                        <option value="world">World Building</option>
                                        <option value="themes">Themes & Messages</option>
                                        <option value="structure">Story Structure</option>
                                        <option value="writing">Writing Techniques</option>
                                    </select>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="storyChatInterface.createSession()">
                                Start Chat
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Enter key to send message
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }
    
    async loadSessions() {
        try {
            const response = await fetch(`/story-chat/stories/${this.storyId}/sessions`);
            if (!response.ok) throw new Error('Failed to load sessions');
            
            const sessions = await response.json();
            this.renderSessions(sessions);
            
        } catch (error) {
            console.error('Error loading chat sessions:', error);
            this.showError('Failed to load chat sessions');
        }
    }
    
    renderSessions(sessions) {
        const sessionsList = document.getElementById('sessions-list');
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = `
                <div class="text-center text-muted py-3">
                    <i class="fas fa-comment-dots mb-2"></i>
                    <p class="small">No chat sessions yet.<br>Create one to start talking about your story!</p>
                </div>
            `;
            return;
        }
        
        sessionsList.innerHTML = sessions.map(session => `
            <div class="session-item ${session.id === this.currentSessionId ? 'active' : ''}" 
                 onclick="storyChatInterface.selectSession(${session.id})">
                <div class="session-title">${session.title}</div>
                <div class="session-focus">${session.focus_area || 'general'}</div>
                <div class="session-date">${new Date(session.updated_at).toLocaleDateString()}</div>
            </div>
        `).join('');
    }
    
    async selectSession(sessionId) {
        try {
            this.currentSessionId = sessionId;
            
            // Update UI
            document.querySelectorAll('.session-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.closest('.session-item').classList.add('active');
            
            // Load session messages
            const response = await fetch(`/story-chat/stories/${this.storyId}/sessions/${sessionId}`);
            if (!response.ok) throw new Error('Failed to load session');
            
            const session = await response.json();
            this.renderChatSession(session);
            
            // Connect WebSocket
            await this.connectWebSocket(sessionId);
            
        } catch (error) {
            console.error('Error selecting session:', error);
            this.showError('Failed to load chat session');
        }
    }
    
    renderChatSession(session) {
        // Update header
        document.getElementById('chat-header').style.display = 'flex';
        document.getElementById('session-title').textContent = session.title;
        document.getElementById('session-focus').textContent = session.focus_area || 'General discussion';
        
        // Show input area
        document.getElementById('chat-input-area').style.display = 'block';
        
        // Render messages
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = '';
        
        session.messages.forEach(message => {
            this.addMessageToChat(message.role, message.content, false);
        });
        
        this.scrollToBottom();
    }
    
    async connectWebSocket(sessionId) {
        if (this.websocket) {
            this.websocket.close();
        }
        
        try {
            // Get WebSocket ticket
            const response = await fetch('/api/v1/auth/ws-ticket', { method: 'POST' });
            if (!response.ok) throw new Error('Failed to get WebSocket ticket');
            
            const { ticket } = await response.json();
            
            // Connect to WebSocket
            const wsUrl = `ws://localhost:8000/story-chat/ws/stories/${this.storyId}/sessions/${sessionId}/chat?ticket=${ticket}`;
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                console.log('Story chat WebSocket connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                this.isConnected = false;
                console.log('Story chat WebSocket disconnected');
            };
            
            this.websocket.onerror = (error) => {
                console.error('Story chat WebSocket error:', error);
                this.showError('Connection error');
            };
            
        } catch (error) {
            console.error('Error connecting WebSocket:', error);
            this.showError('Failed to connect to chat');
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'session_info':
                console.log('Session info received:', data.session);
                break;
                
            case 'response_start':
                this.currentResponseElement = this.addMessageToChat('assistant', '', true);
                break;
                
            case 'text_chunk':
                if (this.currentResponseElement) {
                    const contentDiv = this.currentResponseElement.querySelector('.message-content');
                    contentDiv.textContent += data.content;
                    this.scrollToBottom();
                }
                break;
                
            case 'response_complete':
                this.currentResponseElement = null;
                this.scrollToBottom();
                break;
                
            case 'error':
                this.showError(data.message);
                break;
                
            case 'pong':
                // Handle ping response
                break;
        }
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const content = messageInput.value.trim();
        
        if (!content || !this.isConnected) return;
        
        // Get target element
        const targetSelect = document.getElementById('target-element-select');
        const [targetElement, targetElementId] = targetSelect.value.split(':');
        
        // Add user message to chat
        this.addMessageToChat('user', content, false);
        messageInput.value = '';
        
        // Send via WebSocket
        this.websocket.send(JSON.stringify({
            type: 'send_message',
            content: content,
            target_element: targetElement || null,
            target_element_id: targetElementId ? parseInt(targetElementId) : null
        }));
        
        this.scrollToBottom();
    }
    
    addMessageToChat(role, content, isStreaming = false) {
        const messagesContainer = document.getElementById('chat-messages');
        
        // Remove welcome message if present
        const welcomeMessage = messagesContainer.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message ${isStreaming ? 'streaming' : ''}`;
        
        const icon = role === 'user' ? 'fas fa-user' : 'fas fa-robot';
        const messageClass = role === 'user' ? 'bg-primary text-white' : 'bg-light';
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <i class="${icon}"></i>
                <span class="message-role">${role === 'user' ? 'You' : 'AI Assistant'}</span>
                <span class="message-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content ${messageClass}">${content}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showNewSessionModal() {
        const modal = new bootstrap.Modal(document.getElementById('newSessionModal'));
        modal.show();
    }
    
    async createSession() {
        const title = document.getElementById('session-title-input').value.trim();
        const description = document.getElementById('session-description-input').value.trim();
        const focus = document.getElementById('session-focus-input').value;
        
        if (!title) {
            this.showError('Please enter a chat title');
            return;
        }
        
        try {
            const response = await fetch(`/story-chat/stories/${this.storyId}/sessions`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    description: description || null,
                    focus_area: focus
                })
            });
            
            if (!response.ok) throw new Error('Failed to create session');
            
            const session = await response.json();
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('newSessionModal'));
            modal.hide();
            
            // Clear form
            document.getElementById('new-session-form').reset();
            
            // Reload sessions and select new one
            await this.loadSessions();
            await this.selectSession(session.id);
            
        } catch (error) {
            console.error('Error creating session:', error);
            this.showError('Failed to create chat session');
        }
    }
    
    async deleteCurrentSession() {
        if (!this.currentSessionId) return;
        
        if (!confirm('Are you sure you want to delete this chat session? This cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`/story-chat/stories/${this.storyId}/sessions/${this.currentSessionId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('Failed to delete session');
            
            // Close WebSocket
            if (this.websocket) {
                this.websocket.close();
            }
            
            // Reset UI
            this.currentSessionId = null;
            document.getElementById('chat-header').style.display = 'none';
            document.getElementById('chat-input-area').style.display = 'none';
            document.getElementById('chat-messages').innerHTML = `
                <div class="welcome-message">
                    <div class="text-center text-muted py-5">
                        <i class="fas fa-robot fa-3x mb-3"></i>
                        <h5>Chat session deleted</h5>
                        <p>Select another session or create a new one to continue.</p>
                    </div>
                </div>
            `;
            
            // Reload sessions
            await this.loadSessions();
            
        } catch (error) {
            console.error('Error deleting session:', error);
            this.showError('Failed to delete chat session');
        }
    }
    
    showError(message) {
        // Use existing toast system if available
        if (window.showToast) {
            window.showToast('error', message);
        } else {
            alert(message);
        }
    }
}

// Global instance variable
let storyChatInterface = null;