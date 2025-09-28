// Story Wizard JavaScript

class StoryWizard {
    constructor() {
        this.sessionId = document.getElementById('session-id').value;
        this.currentPhase = 1;
        this.currentStep = 1;
        this.isGenerating = false;
        this.storyData = {};
        this.jsonData = {};
        
        this.initializeElements();
        this.attachEventListeners();
        this.updateProgressBar();
    }

    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chat-messages');
        this.userMessage = document.getElementById('user-message');
        this.sendButton = document.getElementById('send-button');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.aiModelSelect = document.getElementById('ai-model-select');
        
        // Progress elements
        this.currentPhaseEl = document.getElementById('current-phase-name');
        this.currentStepEl = document.getElementById('current-step');
        this.totalStepsEl = document.getElementById('total-steps');
        
        // Story panel elements
        this.storyAccumulation = document.getElementById('story-accumulation');
        this.generateReportBtn = document.getElementById('generate-report-btn');
        
        // AI Debug elements
        this.aiPromptText = document.getElementById('ai-prompt-text');
        this.aiResponseText = document.getElementById('ai-response-text');
        
        console.log('AI Debug elements:', {
            aiPromptText: this.aiPromptText,
            aiResponseText: this.aiResponseText
        });
        
        // Modal elements
        this.reportModal = new bootstrap.Modal(document.getElementById('storyReportModal'));
        this.reportContent = document.getElementById('story-report-content');
        this.createStoryBtn = document.getElementById('create-story-btn');
    }

    attachEventListeners() {
        // Send message
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.userMessage.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Generate report
        this.generateReportBtn.addEventListener('click', () => this.generateReport());

        // Export options
        document.getElementById('download-text-btn').addEventListener('click', () => this.downloadText());
        document.getElementById('download-json-btn').addEventListener('click', () => this.downloadJSON());
        document.getElementById('copy-report-btn').addEventListener('click', () => this.copyReport());
        document.getElementById('print-report-btn').addEventListener('click', () => this.printReport());
        
        // Create story
        this.createStoryBtn.addEventListener('click', () => this.createStory());
    }

    async sendMessage() {
        const message = this.userMessage.value.trim();
        if (!message || this.isGenerating) return;

        this.isGenerating = true;
        this.sendButton.disabled = true;
        this.typingIndicator.classList.remove('d-none');

        // Add user message to chat
        this.addMessage(message, 'user');
        this.userMessage.value = '';

        try {
            const response = await fetch('/api/story-wizard/process-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_data: {
                        session_id: this.sessionId,
                        phase: this.currentPhase,
                        step: this.currentStep,
                        conversation: this.getConversationHistory(),
                        story_data: this.storyData
                    },
                    message: message,
                    ai_model_id: this.aiModelSelect.value || null
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                // Add wizard response
                this.addMessage(data.response, 'wizard');

                // Update AI debug info
                this.updateAIDebugInfo(data);

                // Update progress
                this.currentPhase = data.phase;
                this.currentStep = data.step;
                this.updateProgressBar();

                // Update story data
                this.updateStoryData(data.story_data);

                // Check if complete
                if (data.is_complete) {
                    this.generateReportBtn.classList.remove('d-none');
                    this.showCompletionMessage();
                }
            } else {
                throw new Error(data.detail || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to send message. Please try again.');
        } finally {
            this.isGenerating = false;
            this.sendButton.disabled = false;
            this.typingIndicator.classList.add('d-none');
        }
    }

    addMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'wizard' 
            ? '<i class="fas fa-hat-wizard"></i>'
            : '<i class="fas fa-user"></i>';

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Parse content for paragraphs
        const paragraphs = content.split('\n').filter(p => p.trim());
        messageContent.innerHTML = paragraphs.map(p => `<p>${this.escapeHtml(p)}</p>`).join('');

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateProgressBar() {
        // Update phase indicators
        document.querySelectorAll('.progress-phase').forEach(phase => {
            const phaseId = parseInt(phase.dataset.phase);
            phase.classList.remove('active', 'completed');
            
            if (phaseId < this.currentPhase) {
                phase.classList.add('completed');
            } else if (phaseId === this.currentPhase) {
                phase.classList.add('active');
            }
        });

        // Update phase name and step
        const phaseNames = {
            1: "Core Spark & Protagonist",
            2: "World & Call to Adventure",
            3: "Conflict, Stakes & Supporting Cast",
            4: "Climax, Resolution & Theme"
        };
        
        const phaseTotalSteps = {
            1: 2, 2: 2, 3: 3, 4: 2
        };

        this.currentPhaseEl.textContent = `Phase ${this.currentPhase}: ${phaseNames[this.currentPhase]}`;
        this.currentStepEl.textContent = this.currentStep;
        this.totalStepsEl.textContent = phaseTotalSteps[this.currentPhase];
    }

    updateStoryData(data) {
        this.storyData = data;
        this.jsonData = data; // Store for export

        // Update each section based on the data
        this.updateSection('section-core', data, ['core_concept', 'genre', 'mood_atmosphere']);
        this.updateSection('section-protagonist', data.protagonist || {}, ['name', 'age', 'defining_characteristic']);
        this.updateSection('section-setting', data.setting || {}, ['primary_location']);
        this.updateSection('section-conflict', data.antagonist || {}, ['description']);
        this.updateSection('section-relationships', data, ['key_relationships']);
        this.updateSection('section-climax', data.plot_points || {}, ['climax_description']);
        this.updateSection('section-theme', data, ['theme']);
    }

    updateSection(sectionId, data, fields) {
        const section = document.getElementById(sectionId);
        if (!section) return;

        const content = section.querySelector('.section-content');
        const hasData = fields.some(field => data[field] && data[field] !== '');

        if (hasData) {
            content.classList.add('filled');
            let html = '';
            
            fields.forEach(field => {
                if (data[field]) {
                    if (Array.isArray(data[field])) {
                        html += `<ul>${data[field].map(item => `<li>${this.formatItem(item)}</li>`).join('')}</ul>`;
                    } else if (typeof data[field] === 'object') {
                        html += this.formatObject(data[field]);
                    } else {
                        html += `<p><strong>${this.formatFieldName(field)}:</strong> ${data[field]}</p>`;
                    }
                }
            });
            
            content.innerHTML = html || '<p class="placeholder-text">Will be filled as you progress...</p>';
        }
    }

    formatFieldName(field) {
        return field
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    formatItem(item) {
        if (typeof item === 'object') {
            return item.name || item.description || JSON.stringify(item);
        }
        return item;
    }

    formatObject(obj) {
        let html = '<ul>';
        Object.entries(obj).forEach(([key, value]) => {
            if (value) {
                html += `<li><strong>${this.formatFieldName(key)}:</strong> ${value}</li>`;
            }
        });
        html += '</ul>';
        return html;
    }

    updateAIDebugInfo(data) {
        console.log('Updating AI debug info with data:', data);
        
        // Check if elements exist
        if (!this.aiPromptText) {
            console.error('AI Prompt text element not found');
            return;
        }
        if (!this.aiResponseText) {
            console.error('AI Response text element not found');
            return;
        }

        // Update AI prompt display
        if (data.ai_prompt) {
            console.log('Setting AI prompt from data:', data.ai_prompt.substring(0, 100) + '...');
            this.aiPromptText.textContent = data.ai_prompt;
        } else {
            console.log('No ai_prompt in data, building representation');
            // Build a representation of what was likely sent
            const prompt = this.buildPromptRepresentation(data);
            this.aiPromptText.textContent = prompt;
        }

        // Update AI response display
        if (data.response) {
            console.log('Setting AI response:', data.response.substring(0, 100) + '...');
            this.aiResponseText.textContent = data.response;
        } else {
            console.log('No response in data');
        }

        // Store for potential debugging
        this.lastAIInteraction = {
            prompt: this.aiPromptText.textContent,
            response: data.response,
            phase: data.phase,
            step: data.step,
            timestamp: new Date().toISOString()
        };
        
        console.log('AI debug info updated successfully');
    }

    buildPromptRepresentation(data) {
        // Build a representation of the likely prompt structure
        const phaseNames = {
            1: "Core Spark & Protagonist",
            2: "World & Call to Adventure", 
            3: "Conflict, Stakes & Supporting Cast",
            4: "Climax, Resolution & Theme"
        };

        // Get the last user message from the conversation
        const lastUserMessage = this.getLastUserMessage();

        let prompt = `Story Wizard Chat Prompt
Phase: ${data.phase} - ${phaseNames[data.phase] || 'Unknown Phase'}
Step: ${data.step}

Context from previous story data:
${JSON.stringify(data.story_data || {}, null, 2)}

User Message: ${lastUserMessage}

[Full system prompt would be generated here with guidance for the AI]`;

        return prompt;
    }

    getLastUserMessage() {
        // Get the last message that was sent by the user
        const userMessages = document.querySelectorAll('.user-message .message-content');
        if (userMessages.length > 0) {
            return userMessages[userMessages.length - 1].textContent.trim();
        }
        return '[No user message found]';
    }

    async generateReport() {
        try {
            const response = await fetch('/ui/story-wizard/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.displayReport(data.text_report);
                this.jsonData = data.json_report;
                this.reportModal.show();
            } else {
                throw new Error(data.detail || 'Failed to generate report');
            }
        } catch (error) {
            console.error('Error generating report:', error);
            this.showError('Failed to generate report. Please try again.');
        }
    }

    displayReport(textReport) {
        // Convert text report to HTML
        const lines = textReport.split('\n');
        let html = '';
        
        lines.forEach(line => {
            if (line.startsWith('Story Text Frame:')) {
                html += `<h1>${line}</h1>`;
            } else if (line.match(/^[A-Z].*:$/) && line.length > 20) {
                html += `<h2>${line.replace(':', '')}</h2>`;
            } else if (line.startsWith('-')) {
                if (!html.endsWith('</ul>')) html += '<ul>';
                html += `<li>${line.substring(1).trim()}</li>`;
                if (!lines[lines.indexOf(line) + 1]?.startsWith('-')) html += '</ul>';
            } else if (line.trim()) {
                if (line.includes(':') && line.split(':')[0].length < 30) {
                    const [label, ...rest] = line.split(':');
                    html += `<p><strong>${label}:</strong>${rest.join(':')}</p>`;
                } else {
                    html += `<p>${line}</p>`;
                }
            }
        });
        
        this.reportContent.innerHTML = html;
    }

    downloadText() {
        const content = this.reportContent.innerText;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'story-frame.txt';
        a.click();
        URL.revokeObjectURL(url);
    }

    downloadJSON() {
        const content = JSON.stringify(this.jsonData, null, 2);
        const blob = new Blob([content], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'story-frame.json';
        a.click();
        URL.revokeObjectURL(url);
    }

    copyReport() {
        const content = this.reportContent.innerText;
        navigator.clipboard.writeText(content).then(() => {
            this.showSuccess('Report copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showError('Failed to copy report');
        });
    }

    printReport() {
        window.print();
    }

    async createStory() {
        try {
            // Create a basic story with the generated data
            const response = await fetch('/stories/basic/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: this.jsonData.story_title || 'Untitled Story',
                    short_description: this.jsonData.theme || 'Created with Story Wizard'
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.story_id) {
                // Navigate to the story editor with the wizard data
                window.location.href = `/ui/basic-story/${data.story_id}/edit?wizard_data=true`;
                
                // Store wizard data in sessionStorage for the editor to pick up
                sessionStorage.setItem('wizardStoryData', JSON.stringify(this.jsonData));
            }
        } catch (error) {
            console.error('Error creating story:', error);
            this.showError('Failed to create story. Please try again.');
        }
    }

    showCompletionMessage() {
        this.addMessage(
            "Congratulations! You've completed your story framework. Click 'Generate Story Report' to see your complete story outline.",
            'wizard'
        );
    }

    showError(message) {
        // Show error toast or alert
        alert(message); // Replace with better notification system
    }

    showSuccess(message) {
        // Show success toast
        alert(message); // Replace with better notification system
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    getConversationHistory() {
        const messages = [];
        const messageElements = this.chatMessages.querySelectorAll('.message');
        
        messageElements.forEach(msg => {
            const isUser = msg.classList.contains('user-message');
            const content = msg.querySelector('.message-content').innerText;
            
            messages.push({
                role: isUser ? 'user' : 'assistant',
                content: content,
                timestamp: new Date().toISOString()
            });
        });
        
        return messages;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new StoryWizard();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
});