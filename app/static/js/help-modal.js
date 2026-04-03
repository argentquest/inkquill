/* ========================================================================
   HELP MODAL FUNCTIONALITY
   Quick Start guide modal system with dynamic content loading
   ======================================================================== */

class HelpModalManager {
  constructor() {
    this.modal = null;
    this.modalContent = null;
    this.modalTitle = null;
    this.modalBody = null;
    this.isInitialized = false;
    this.currentTopic = null;
    
    this.init();
  }

  init() {
    this.createModal();
    this.bindEvents();
    this.isInitialized = true;
    
    // Expose global function for opening modals
    window.openHelpModal = (topic) => this.openModal(topic);
    window.closeHelpModal = () => this.closeModal();
  }

  createModal() {
    // Check if modal already exists
    if (document.getElementById('quickStartHelpModal')) {
      this.modal = document.getElementById('quickStartHelpModal');
      this.modalContent = this.modal.querySelector('.help-modal-content');
      this.modalTitle = this.modal.querySelector('.help-modal-title');
      this.modalBody = this.modal.querySelector('.help-modal-body');
      this.topicSelect = this.modal.querySelector('#helpTopicSelect');
      return;
    }

    // Create modal HTML
    const modalHTML = `
      <div id="quickStartHelpModal" class="help-modal">
        <div class="help-modal-content">
          <div class="help-modal-header">
            <h2 class="help-modal-title">
              <span class="help-modal-icon">
                <i class="fas fa-question-circle"></i>
              </span>
              Quick Start Guide
            </h2>
            <div class="help-topic-navigation">
              <select id="helpTopicSelect" class="help-topic-select" onchange="window.helpModalManager.switchTopic(this.value)">
                <option value="">Browse Help Topics...</option>
                <optgroup label="Getting Started">
                  <option value="introduction">📚 Help & User Guide</option>
                  <option value="quick_start">🚀 Quick Start Tutorial</option>
                  <option value="register">👤 Registration Guide</option>
                  <option value="dashboard">🏠 Dashboard Overview</option>
                </optgroup>
                <optgroup label="World Building">
                  <option value="world_list">🌍 World Management</option>
                  <option value="world_detail">🌎 World Details</option>
                  <option value="world_builder">🔮 World Builder Wizard</option>
                  <option value="import_book">📚 Import from Book</option>
                </optgroup>
                <optgroup label="Characters & Lore">
                  <option value="character_detail">👤 Characters</option>
                  <option value="character_generator">👥 Character Generator</option>
                  <option value="location_detail">📍 Locations</option>
                  <option value="lore_item_detail">📜 Lore Items</option>
                </optgroup>
                <optgroup label="Writing & Stories">
                  <option value="story_detail">📖 Story Creation</option>
                  <option value="story_list">📚 Story Management</option>
                  <option value="basic_story_editor">✍️ Basic Story Editor</option>
                  <option value="act_editor">✍️ Act Editor</option>
                  <option value="scene_editor">🎬 Scene Editor</option>
                  <option value="story_classes">🎭 Story Classes</option>
                </optgroup>
                <optgroup label="Tools & Resources">
                  <option value="prompts">💬 Prompt Library</option>
                  <option value="documents">📁 Document Manager</option>
                  <option value="world_chat">💭 AI Chat Gallery</option>
                  <option value="public_chat">🌐 Public Chat Settings</option>
                  <option value="billing">💳 Billing & Credits</option>
                </optgroup>
                <optgroup label="Community">
                  <option value="forum">🗣️ Community Forum</option>
                  <option value="published_stories">📖 Published Stories</option>
                </optgroup>
              </select>
            </div>
            <button class="help-modal-close" onclick="closeHelpModal()" aria-label="Close help modal">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="help-modal-body">
            <div class="help-modal-loading">
              <div class="help-modal-spinner"></div>
              <span style="margin-left: var(--space-3);">Loading help content...</span>
            </div>
          </div>
        </div>
      </div>
    `;

    // Add modal to document
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Get references
    this.modal = document.getElementById('quickStartHelpModal');
    this.modalContent = this.modal.querySelector('.help-modal-content');
    this.modalTitle = this.modal.querySelector('.help-modal-title');
    this.modalBody = this.modal.querySelector('.help-modal-body');
    this.topicSelect = this.modal.querySelector('#helpTopicSelect');
  }

  bindEvents() {
    // Close modal when clicking outside
    this.modal.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.closeModal();
      }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modal.classList.contains('show')) {
        this.closeModal();
      }
    });

    // Prevent body scroll when modal is open
    this.modal.addEventListener('transitionend', (e) => {
      if (e.target === this.modal) {
        if (this.modal.classList.contains('show')) {
          document.body.style.overflow = 'hidden';
        } else {
          document.body.style.overflow = '';
        }
      }
    });
  }

  openModal(topic) {
    if (!this.isInitialized) {
      console.warn('Help modal not initialized');
      return;
    }

    this.currentTopic = topic;
    this.loadContent(topic);
    this.updateTopicSelect(topic);
    this.modal.classList.add('show');
    
    // Focus management for accessibility
    const closeButton = this.modal.querySelector('.help-modal-close');
    if (closeButton) {
      setTimeout(() => closeButton.focus(), 100);
    }

    // Track analytics if available
    if (window.trackFeatureUse) {
      window.trackFeatureUse('help_modal', 'open', { topic });
    }
  }

  switchTopic(topic) {
    if (!topic || topic === this.currentTopic) return;
    
    this.currentTopic = topic;
    this.loadContent(topic);
    
    // Track analytics if available
    if (window.trackFeatureUse) {
      window.trackFeatureUse('help_modal', 'switch_topic', { topic });
    }
  }

  updateTopicSelect(topic) {
    if (this.topicSelect) {
      this.topicSelect.value = topic || '';
    }
  }

  closeModal() {
    if (!this.modal) return;
    
    this.modal.classList.remove('show');
    this.currentTopic = null;
    
    // Return focus to trigger element if possible
    const activeElement = document.activeElement;
    if (activeElement && activeElement.blur) {
      activeElement.blur();
    }

    // Track analytics if available
    if (window.trackFeatureUse) {
      window.trackFeatureUse('help_modal', 'close');
    }
  }

  async loadContent(topic) {
    // Show loading state
    this.showLoading();
    
    // Update title based on topic
    this.updateTitle(topic);
    
    try {
      // Try to load content from static help directory first
      let response = await fetch(`/static/help/${topic}.html`);
      
      // Note: All help content is now in /static/help/ directory
      
      if (response.ok) {
        const htmlContent = await response.text();
        this.modalBody.innerHTML = htmlContent;
      } else {
        // Fallback to JavaScript content for topics that don't have HTML files yet
        const content = this.generateContent(topic);
        this.modalBody.innerHTML = content;
      }
    } catch (error) {
      console.error('Error loading help content:', error);
      // Fallback to JavaScript content
      const content = this.generateContent(topic);
      this.modalBody.innerHTML = content;
    }
  }

  showLoading() {
    this.modalBody.innerHTML = `
      <div class="help-modal-loading">
        <div class="help-modal-spinner"></div>
        <span style="margin-left: var(--space-3);">Loading help content...</span>
      </div>
    `;
  }

  updateTitle(topic) {
    const titles = {
      'introduction': 'Help & User Guide',
      'quick_start': 'Quick Start Tutorial',
      'world_list': 'World Management',
      'story_detail': 'Story Creation',
      'story_list': 'Story Management',
      'act_editor': 'Act Editor',
      'act_detail': 'Act Management',
      'scene_editor': 'Scene Editor',
      'character_detail': 'Characters',
      'character_list': 'Character Management',
      'character_generator': 'Character Generator',
      'location_detail': 'Locations',
      'location_list': 'Location Management',
      'lore_item_detail': 'Lore Items',
      'lore_item_list': 'Lore Management',
      'prompts': 'Prompt Library',
      'documents': 'Document Manager',
      'billing': 'Billing & Credits',
      'forum': 'Community Forum',
      'register': 'Registration Guide',
      'login': 'Login Help',
      'import_document': 'Document Import',
      'dashboard': 'Dashboard Guide',
      'user_guide': 'User Guide',
      'world_detail': 'World Details',
      'world_chat': 'AI Chat Gallery',
      'public_chat': 'AI World Chat',
      'basic_story_editor': 'Basic Story Editor',
      'news_updates': 'News & Updates',
      'community': 'Community'
    };

    const title = titles[topic] || 'Help & User Guide';
    const icon = this.getTopicIcon(topic);
    
    this.modalTitle.innerHTML = `
      <span class="help-modal-icon">
        <i class="${icon}"></i>
      </span>
      ${title}
    `;
  }

  getTopicIcon(topic) {
    const icons = {
      'quick_start': 'fas fa-rocket',
      'world_list': 'fas fa-globe',
      'story_detail': 'fas fa-book',
      'story_list': 'fas fa-book-open',
      'act_editor': 'fas fa-pen',
      'act_detail': 'fas fa-theater-masks',
      'scene_editor': 'fas fa-edit',
      'character_detail': 'fas fa-user',
      'character_list': 'fas fa-users',
      'character_generator': 'fas fa-user-plus',
      'location_detail': 'fas fa-map-marker-alt',
      'location_list': 'fas fa-map',
      'lore_item_detail': 'fas fa-scroll',
      'lore_item_list': 'fas fa-book-open',
      'prompts': 'fas fa-code',
      'documents': 'fas fa-file-alt',
      'billing': 'fas fa-credit-card',
      'forum': 'fas fa-comments',
      'register': 'fas fa-user-plus',
      'login': 'fas fa-sign-in-alt',
      'import_document': 'fas fa-upload',
      'dashboard': 'fas fa-tachometer-alt',
      'user_guide': 'fas fa-book-reader',
      'world_detail': 'fas fa-globe-americas',
      'news_updates': 'fas fa-newspaper',
      'community': 'fas fa-users'
    };

    return icons[topic] || 'fas fa-question-circle';
  }

  generateContent(topic) {
    const contentMap = {
      'world_list': this.getWorldListContent(),
      'story_detail': this.getStoryDetailContent(),
      'story_list': this.getStoryListContent(),
      'act_editor': this.getActEditorContent(),
      'act_detail': this.getActDetailContent(),
      'scene_editor': this.getSceneEditorContent(),
      'character_detail': this.getCharacterDetailContent(),
      'character_list': this.getCharacterListContent(),
      'character_generator': this.getCharacterGeneratorContent(),
      'location_detail': this.getLocationDetailContent(),
      'location_list': this.getLocationListContent(),
      'lore_item_detail': this.getLoreItemDetailContent(),
      'lore_item_list': this.getLoreItemListContent(),
      'prompts': this.getPromptsContent(),
      'documents': this.getDocumentsContent(),
      'billing': this.getBillingContent(),
      'forum': this.getForumContent(),
      'register': this.getRegisterContent(),
      'login': this.getLoginContent(),
      'world_builder': this.getWorldBuilderContent(),
      'world_detail': this.getWorldDetailContent(),
      'import_book': this.getImportBookContent(),
      'import_document': this.getImportDocumentContent(),
      'story_classes': this.getStoryClassesContent(),
      'world_chat': this.getWorldChatContent(),
      'published_stories': this.getPublishedStoriesContent(),
      'dashboard': this.getDashboardContent(),
      'user_guide': this.getUserGuideContent()
    };

    return contentMap[topic] || this.getDefaultContent();
  }

  getWorldListContent() {
    return `
      <div class="help-section">
        <h3>World Management Overview</h3>
        <p>Worlds are the foundation of your storytelling ecosystem. They contain all your characters, locations, lore items, and stories, creating a rich, interconnected narrative universe.</p>
        
        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Choose Creation Method</div>
              <div class="help-step-description">Use the <strong>World Builder Wizard</strong> for AI-guided creation, <strong>Import from Book</strong> to extract from literature, or <strong>Create New World</strong> for manual setup.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Populate Your World</div>
              <div class="help-step-description">Add <strong>Characters</strong> (with AI-generated images), <strong>Locations</strong> (with atmospheric descriptions), and <strong>Lore Items</strong> (customs, artifacts, organizations).</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Upload Reference Documents</div>
              <div class="help-step-description">Use the <strong>Document Manager</strong> to upload research files, character sheets, and reference materials that AI can use for context.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Start Writing Stories</div>
              <div class="help-step-description">Create stories in your world using the <strong>AI-assisted writing tools</strong> that leverage all your world elements for context.</div>
            </div>
          </div>
        </div>

        <h4>Advanced Features:</h4>
        <ul>
          <li><strong>World Chat:</strong> Chat with AI about your world to develop ideas</li>
          <li><strong>Hierarchy View:</strong> Visualize relationships between world elements</li>
          <li><strong>Context Integration:</strong> AI pulls context from your uploaded documents</li>
          <li><strong>Publishing:</strong> Share completed worlds and stories with the community</li>
          <li><strong>Version Control:</strong> Track changes and updates to your world</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-magic help-tip-icon"></i>
            World Builder Wizard
          </div>
          <div class="help-tip-content">
            The 20-question World Builder Wizard uses AI to generate a complete, coherent world with characters, locations, cultures, and conflicts. Perfect for getting started quickly!
          </div>
        </div>

        <div class="help-warning">
          <div class="help-warning-title">
            <i class="fas fa-coins help-warning-icon"></i>
            Credit Usage
          </div>
          <div class="help-warning-content">
            AI features (world generation, character creation, image generation) consume credits. Monitor your usage in the billing dashboard.
          </div>
        </div>

        <div class="help-actions">
          <a href="/ui/worlds" class="help-action-button">
            <i class="fas fa-globe"></i>
            My Worlds
          </a>
          <a href="/ui/worlds/create" class="help-action-button-secondary">
            <i class="fas fa-plus"></i>
            Create World
          </a>
          <a href="/ui/worlds/builder" class="help-action-button-secondary">
            <i class="fas fa-magic"></i>
            World Wizard
          </a>
        </div>
      </div>
    `;
  }

  getStoryDetailContent() {
    return `
      <div class="help-section">
        <h3>Story Creation & Management</h3>
        <p>Stories are structured narratives that take place in your worlds. The platform supports complete story lifecycle management from creation to publication.</p>
        
        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Choose Your World & Template</div>
              <div class="help-step-description">Select the world for context, choose a <strong>Story Class</strong> (genre template), and set your story's basic information and target audience.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Structure Your Story</div>
              <div class="help-step-description">Create <strong>Acts</strong> (major story sections) and break them into <strong>Scenes</strong>. Each scene focuses on a specific event or moment.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Write with AI Assistance</div>
              <div class="help-step-description">Use the <strong>real-time AI writing assistant</strong> that has access to your world's characters, locations, and lore for contextual suggestions.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Review & Publish</div>
              <div class="help-step-description">Edit your completed story, add cover art, set publication settings, and share with the community.</div>
            </div>
          </div>
        </div>

        <h4>Story Features:</h4>
        <ul>
          <li><strong>Story Classes:</strong> Genre-specific templates and guidance</li>
          <li><strong>Auto-save:</strong> Never lose your work with automatic saving</li>
          <li><strong>Version History:</strong> Track changes and revert to previous versions</li>
          <li><strong>Collaboration:</strong> Share drafts for feedback before publishing</li>
          <li><strong>Analytics:</strong> Track readership and engagement metrics</li>
          <li><strong>Export Options:</strong> Download in multiple formats (PDF, EPUB, etc.)</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-brain help-tip-icon"></i>
            AI Writing Assistant
          </div>
          <div class="help-tip-content">
            The AI assistant has full context of your world elements and can suggest plot developments, dialogue, character actions, and scene transitions that fit your established world.
          </div>
        </div>

        <div class="help-warning">
          <div class="help-warning-title">
            <i class="fas fa-clock help-warning-icon"></i>
            Best Practices
          </div>
          <div class="help-warning-content">
            Build your world elements (characters, locations, lore) before writing. The richer your world, the better the AI assistance. Use the Document Manager to upload reference materials.
          </div>
        </div>

        <div class="help-actions">
          <a href="/ui/stories" class="help-action-button">
            <i class="fas fa-book"></i>
            My Stories
          </a>
          <a href="/ui/stories/create" class="help-action-button-secondary">
            <i class="fas fa-plus"></i>
            Create Story
          </a>
          <a href="/published-stories" class="help-action-button-secondary">
            <i class="fas fa-eye"></i>
            Browse Published
          </a>
        </div>
      </div>
    `;
  }

  getActEditorContent() {
    return `
      <div class="help-section">
        <h3>Act Editor - Advanced AI Writing Interface</h3>
        <p>The Act Editor is a powerful, real-time AI-assisted writing environment with full access to your world's context and advanced collaboration features.</p>
        
        <h4>Interface Layout:</h4>
        <ul>
          <li><strong>Main Editor:</strong> Rich text editor with formatting tools and word count</li>
          <li><strong>AI Assistant Panel:</strong> Real-time suggestions and conversation</li>
          <li><strong>World Context Sidebar:</strong> Access to characters, locations, and lore</li>
          <li><strong>Scene Navigator:</strong> Quick access to scenes within the act</li>
        </ul>

        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Start Writing</div>
              <div class="help-step-description">Begin typing your act content. The AI monitors your writing and provides contextual suggestions in real-time.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Use AI Assistance</div>
              <div class="help-step-description">Click the AI panel to ask for plot suggestions, character development, or continuation help. The AI has full context of your world.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Reference World Elements</div>
              <div class="help-step-description">Use the sidebar to reference characters, locations, and lore. Click any element to insert details or ask AI about interactions.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Organize Scenes</div>
              <div class="help-step-description">Break your act into scenes using the scene navigator. Each scene can have its own focus and AI assistance.</div>
            </div>
          </div>
        </div>

        <h4>AI Features:</h4>
        <ul>
          <li><strong>Contextual Suggestions:</strong> AI analyzes your writing style and world context</li>
          <li><strong>Plot Development:</strong> Get suggestions for story progression and conflicts</li>
          <li><strong>Character Voice:</strong> AI maintains character consistency based on your profiles</li>
          <li><strong>World Consistency:</strong> Ensures details match your established world rules</li>
          <li><strong>Style Matching:</strong> AI adapts to your writing style and tone</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-robot help-tip-icon"></i>
            AI Conversation Tips
          </div>
          <div class="help-tip-content">
            Be specific with AI requests: "Help me write dialogue between Sarah and Marcus about the upcoming war" works better than "Help me write dialogue."
          </div>
        </div>

        <div class="help-warning">
          <div class="help-warning-title">
            <i class="fas fa-save help-warning-icon"></i>
            Auto-Save & WebSocket
          </div>
          <div class="help-warning-content">
            Your work auto-saves every few seconds via WebSocket connection. The AI assistance requires an active connection - watch for connection status indicators.
          </div>
        </div>

        <div class="help-actions">
          <button class="help-action-button" onclick="closeHelpModal()">
            <i class="fas fa-pen"></i>
            Start Writing
          </button>
        </div>
      </div>
    `;
  }

  getSceneEditorContent() {
    return `
      <div class="help-section">
        <h3>Scene Editor Guide</h3>
        <p>Scenes are the building blocks of your acts. Each scene should focus on a specific moment, conversation, or event in your story.</p>
        
        <h4>Editor Features:</h4>
        <ul>
          <li><strong>Real-time AI Assistance:</strong> Get writing suggestions as you type</li>
          <li><strong>World Context:</strong> AI has access to your world's characters and lore</li>
          <li><strong>Formatting Tools:</strong> Rich text editing with proper formatting</li>
          <li><strong>Word Count:</strong> Track your progress with live statistics</li>
        </ul>

        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Set the Scene</div>
              <div class="help-step-description">Start by establishing where and when the scene takes place.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Focus on Action</div>
              <div class="help-step-description">What happens in this scene? Keep it focused on one main event or conversation.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Use AI Assistance</div>
              <div class="help-step-description">When stuck, ask the AI for suggestions or to continue the narrative.</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  getCharacterDetailContent() {
    return `
      <div class="help-section">
        <h3>Character Management</h3>
        <p>Characters are the heart of your stories. Create detailed, memorable characters that will populate your worlds.</p>
        
        <h4>Character Information:</h4>
        <ul>
          <li><strong>Basic Details:</strong> Name, age, appearance, and role</li>
          <li><strong>Personality:</strong> Traits, motivations, and quirks</li>
          <li><strong>Background:</strong> History, relationships, and goals</li>
          <li><strong>AI Enhancement:</strong> Let AI help generate detailed descriptions</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-lightbulb help-tip-icon"></i>
            Character Development Tips
          </div>
          <div class="help-tip-content">
            <ul>
              <li>Give characters clear motivations and goals</li>
              <li>Include both strengths and flaws for realistic depth</li>
              <li>Consider how they relate to other characters</li>
              <li>Use the AI image generator to visualize your characters</li>
            </ul>
          </div>
        </div>

        <div class="help-actions">
          <button class="help-action-button" onclick="closeHelpModal()">
            <i class="fas fa-user-plus"></i>
            Create Character
          </button>
        </div>
      </div>
    `;
  }

  getLocationDetailContent() {
    return `
      <div class="help-section">
        <h3>Location Management</h3>
        <p>Locations provide the settings for your stories. Create rich, detailed environments that enhance your narrative.</p>
        
        <h4>Location Elements:</h4>
        <ul>
          <li><strong>Physical Description:</strong> What does the location look like?</li>
          <li><strong>Atmosphere:</strong> What's the mood and feeling of this place?</li>
          <li><strong>History:</strong> What significant events happened here?</li>
          <li><strong>Inhabitants:</strong> Who lives or frequents this location?</li>
        </ul>

        <div class="help-warning">
          <div class="help-warning-title">
            <i class="fas fa-map-marker-alt help-warning-icon"></i>
            Location Tips
          </div>
          <div class="help-warning-content">
            Think about how locations connect to each other and how characters move between them. This helps create a cohesive world.
          </div>
        </div>
      </div>
    `;
  }

  getLoreItemDetailContent() {
    return `
      <div class="help-section">
        <h3>Lore Items Guide</h3>
        <p>Lore items are the cultural, historical, and magical elements that make your world unique. They include customs, artifacts, religions, and more.</p>
        
        <h4>Types of Lore Items:</h4>
        <ul>
          <li><strong>Artifacts:</strong> Magical items, weapons, or important objects</li>
          <li><strong>Customs:</strong> Cultural practices and traditions</li>
          <li><strong>Religions:</strong> Belief systems and deities</li>
          <li><strong>Organizations:</strong> Guilds, governments, and factions</li>
          <li><strong>Events:</strong> Historical moments that shaped your world</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-scroll help-tip-icon"></i>
            Lore Development
          </div>
          <div class="help-tip-content">
            Start with the most important elements that directly impact your stories, then expand the lore as needed. Quality over quantity!
          </div>
        </div>
      </div>
    `;
  }

  getPromptsContent() {
    return `
      <div class="help-section">
        <h3>Prompt Library</h3>
        <p>The prompt library contains templates and examples to help you get the most out of AI assistance in your writing.</p>
        
        <h4>How to Use Prompts:</h4>
        <ul>
          <li><strong>Browse Categories:</strong> Find prompts by type (character, plot, dialogue, etc.)</li>
          <li><strong>Customize Templates:</strong> Modify prompts to fit your specific needs</li>
          <li><strong>Save Favorites:</strong> Keep your most-used prompts handy</li>
          <li><strong>Create Your Own:</strong> Build custom prompts for recurring tasks</li>
        </ul>

        <div class="help-actions">
          <a href="/ui/prompts" class="help-action-button">
            <i class="fas fa-code"></i>
            Browse Prompts
          </a>
        </div>
      </div>
    `;
  }

  getDocumentsContent() {
    return `
      <div class="help-section">
        <h3>Document Manager</h3>
        <p>Upload and manage reference documents that the AI can use to enhance your writing with relevant context.</p>
        
        <h4>Supported Documents:</h4>
        <ul>
          <li><strong>Research Files:</strong> PDFs, Word docs, and text files</li>
          <li><strong>Reference Materials:</strong> Character sheets, world bibles, outlines</li>
          <li><strong>Style Guides:</strong> Writing samples and style references</li>
        </ul>

        <div class="help-warning">
          <div class="help-warning-title">
            <i class="fas fa-exclamation-triangle help-warning-icon"></i>
            File Guidelines
          </div>
          <div class="help-warning-content">
            Keep uploaded files focused and relevant. Large documents may take longer to process and could dilute the AI's focus.
          </div>
        </div>
      </div>
    `;
  }

  getBillingContent() {
    return `
      <div class="help-section">
        <h3>Billing & Credits</h3>
        <p>Understand how AI usage is tracked and billed in the platform.</p>
        
        <h4>Credit System:</h4>
        <ul>
          <li><strong>AI Operations:</strong> Each AI request consumes credits based on complexity</li>
          <li><strong>Usage Tracking:</strong> Monitor your credit consumption in real-time</li>
          <li><strong>Cost Transparency:</strong> See detailed breakdowns of AI costs</li>
          <li><strong>Flexible Plans:</strong> Choose a plan that fits your writing needs</li>
        </ul>

        <div class="help-actions">
          <a href="/ui/billing" class="help-action-button">
            <i class="fas fa-credit-card"></i>
            View Billing
          </a>
        </div>
      </div>
    `;
  }

  getForumContent() {
    return `
      <div class="help-section">
        <h3>Community Forum</h3>
        <p>Connect with other writers, share your work, and get feedback from the community.</p>
        
        <h4>Forum Features:</h4>
        <ul>
          <li><strong>Writing Discussions:</strong> Share tips and techniques</li>
          <li><strong>Feedback Exchange:</strong> Get critiques on your work</li>
          <li><strong>Showcase Stories:</strong> Share your completed works</li>
          <li><strong>AI Tips:</strong> Learn advanced AI assistance techniques</li>
        </ul>

        <div class="help-actions">
          <a href="/forum" class="help-action-button">
            <i class="fas fa-comments"></i>
            Visit Forum
          </a>
        </div>
      </div>
    `;
  }

  getRegisterContent() {
    return `
      <div class="help-section">
        <h3>Registration Guide</h3>
        <p>Create your account to unlock unlimited access to all platform features.</p>
        
        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Create Account</div>
              <div class="help-step-description">Sign up with your email address and create a secure password.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Verify Email</div>
              <div class="help-step-description">Check your email and click the verification link to activate your account.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Choose Plan</div>
              <div class="help-step-description">Select a subscription plan that fits your writing needs and budget.</div>
            </div>
          </div>
        </div>

        <div class="help-actions">
          <a href="/ui/register" class="help-action-button">
            <i class="fas fa-user-plus"></i>
            Register Now
          </a>
        </div>
      </div>
    `;
  }

  getWorldBuilderContent() {
    return `
      <div class="help-section">
        <h3>World Builder Wizard</h3>
        <p>The 20-question World Builder Wizard uses advanced AI to create complete, coherent fantasy or sci-fi worlds based on your preferences and creative input.</p>
        
        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Answer Creative Questions</div>
              <div class="help-step-description">The wizard asks about genre, themes, conflicts, magic systems, technology levels, and cultural elements you want in your world.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">AI Generates Your World</div>
              <div class="help-step-description">Based on your answers, AI creates detailed characters, locations, lore items, cultures, and conflicts that work together coherently.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Review & Customize</div>
              <div class="help-step-description">Edit any generated elements, add your own details, or regenerate specific parts you want to change.</div>
            </div>
          </div>
        </div>

        <h4>What Gets Generated:</h4>
        <ul>
          <li><strong>World Overview:</strong> History, geography, and major themes</li>
          <li><strong>Key Characters:</strong> Important figures with relationships and motivations</li>
          <li><strong>Major Locations:</strong> Cities, landmarks, and significant places</li>
          <li><strong>Cultural Elements:</strong> Religions, customs, organizations, and conflicts</li>
          <li><strong>Artifacts & Magic:</strong> Important items and magical/technological systems</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-lightbulb help-tip-icon"></i>
            Pro Tips
          </div>
          <div class="help-tip-content">
            Be specific in your answers - "medieval fantasy with political intrigue" gives better results than just "fantasy." You can always modify generated content later.
          </div>
        </div>
      </div>
    `;
  }

  getWorldDetailContent() {
    return `
      <div class="help-section">
        <h3>World Detail Management</h3>
        <p>The world detail page is your command center for managing all aspects of your created world, from characters to publication settings.</p>
        
        <h4>Main Sections:</h4>
        <ul>
          <li><strong>Overview:</strong> World description, statistics, and quick actions</li>
          <li><strong>Characters Tab:</strong> Manage all characters with AI generation options</li>
          <li><strong>Locations Tab:</strong> Create and organize geographical elements</li>
          <li><strong>Lore Tab:</strong> Cultural elements, artifacts, and world rules</li>
          <li><strong>Stories Tab:</strong> Stories set in this world</li>
          <li><strong>Documents Tab:</strong> Reference materials for AI context</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-comments help-tip-icon"></i>
            World Chat
          </div>
          <div class="help-tip-content">
            Use the World Chat feature to brainstorm with AI about your world. Ask questions about plot possibilities, character relationships, or world-building challenges.
          </div>
        </div>

        <div class="help-actions">
          <button class="help-action-button" onclick="closeHelpModal()">
            <i class="fas fa-edit"></i>
            Continue Editing
          </button>
        </div>
      </div>
    `;
  }

  getCharacterGeneratorContent() {
    return `
      <div class="help-section">
        <h3>AI Character Generator</h3>
        <p>Create detailed, unique characters with AI assistance, including personality, background, and AI-generated portrait images.</p>
        
        <h4>Generation Process:</h4>
        <ul>
          <li><strong>Basic Info:</strong> Name, age, role in your world</li>
          <li><strong>Appearance:</strong> Physical description with AI image generation</li>
          <li><strong>Personality:</strong> Traits, motivations, fears, and quirks</li>
          <li><strong>Background:</strong> History, relationships, and goals</li>
          <li><strong>World Integration:</strong> How they fit into your specific world</li>
        </ul>

        <div class="help-warning">
          <div class="help-warning-title">
            <i class="fas fa-image help-warning-icon"></i>
            Image Generation
          </div>
          <div class="help-warning-content">
            AI image generation uses additional credits. You can generate multiple variations and choose the best one. Images are permanently saved to your character.
          </div>
        </div>
      </div>
    `;
  }

  getImportBookContent() {
    return `
      <div class="help-section">
        <h3>Import World from Book</h3>
        <p>Extract detailed world information from existing literature to create comprehensive worlds based on published works or your own writing.</p>
        
        <div class="help-steps">
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Upload or Paste Text</div>
              <div class="help-step-description">Upload a book file (PDF, EPUB, TXT) or paste text directly from your source material.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">AI Analysis</div>
              <div class="help-step-description">AI analyzes the text to identify characters, locations, relationships, and world-building elements.</div>
            </div>
          </div>
          <div class="help-step">
            <div class="help-step-number"></div>
            <div class="help-step-content">
              <div class="help-step-title">Review & Refine</div>
              <div class="help-step-description">Edit extracted information, add missing details, and organize elements into your world structure.</div>
            </div>
          </div>
        </div>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-copyright help-tip-icon"></i>
            Copyright Notice
          </div>
          <div class="help-tip-content">
            Only use this feature with texts you own the rights to or public domain works. Respect copyright laws and don't use copyrighted material without permission.
          </div>
        </div>
      </div>
    `;
  }

  getStoryClassesContent() {
    return `
      <div class="help-section">
        <h3>Story Classes & Templates</h3>
        <p>Story Classes provide genre-specific templates, writing guidance, and AI assistance tailored to different types of narratives.</p>
        
        <h4>Available Classes:</h4>
        <ul>
          <li><strong>Epic Fantasy:</strong> Large-scale adventure with magic and heroes</li>
          <li><strong>Urban Fantasy:</strong> Modern settings with supernatural elements</li>
          <li><strong>Science Fiction:</strong> Future technology and space exploration</li>
          <li><strong>Mystery/Thriller:</strong> Investigation and suspense-driven plots</li>
          <li><strong>Romance:</strong> Character relationships and emotional journeys</li>
          <li><strong>Horror:</strong> Fear, tension, and supernatural threats</li>
          <li><strong>Literary Fiction:</strong> Character-driven, literary storytelling</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-brain help-tip-icon"></i>
            AI Assistance
          </div>
          <div class="help-tip-content">
            Each Story Class trains the AI assistant with genre-specific knowledge, tropes, pacing, and storytelling techniques appropriate for that type of story.
          </div>
        </div>
      </div>
    `;
  }

  getWorldChatContent() {
    return `
      <div class="help-section">
        <h3>World Chat - AI Brainstorming</h3>
        <p>Chat with AI about your world to develop ideas, explore plot possibilities, and solve world-building challenges.</p>
        
        <h4>Chat Features:</h4>
        <ul>
          <li><strong>Full Context:</strong> AI knows all your world elements</li>
          <li><strong>Brainstorming:</strong> Generate new ideas and possibilities</li>
          <li><strong>Problem Solving:</strong> Work through plot holes or inconsistencies</li>
          <li><strong>Character Development:</strong> Explore character relationships and arcs</li>
          <li><strong>Plot Planning:</strong> Develop story ideas that fit your world</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-comments help-tip-icon"></i>
            Effective Questions
          </div>
          <div class="help-tip-content">
            Ask specific questions like "What would happen if Sarah discovered Marcus is working for the enemy?" rather than general questions like "What should happen next?"
          </div>
        </div>
      </div>
    `;
  }

  getPublishedStoriesContent() {
    return `
      <div class="help-section">
        <h3>Published Stories Gallery</h3>
        <p>Browse and discover stories published by the community, or publish your own completed works for others to enjoy.</p>
        
        <h4>Features:</h4>
        <ul>
          <li><strong>Community Gallery:</strong> Browse stories by genre, rating, and popularity</li>
          <li><strong>Reading Interface:</strong> Clean, distraction-free reading experience</li>
          <li><strong>Ratings & Reviews:</strong> Community feedback and recommendations</li>
          <li><strong>Author Profiles:</strong> Follow your favorite writers</li>
          <li><strong>Collections:</strong> Curated story collections and series</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-star help-tip-icon"></i>
            Publishing Your Work
          </div>
          <div class="help-tip-content">
            Complete stories can be published with custom cover art, descriptions, and content ratings. You maintain full control over your published content.
          </div>
        </div>
      </div>
    `;
  }

  getDashboardContent() {
    return `
      <div class="help-section">
        <h3>Dashboard Overview</h3>
        <p>Your personal dashboard provides quick access to all your creative projects and recent activity.</p>
        
        <h4>Dashboard Sections:</h4>
        <ul>
          <li><strong>Quick Actions:</strong> Create new worlds, stories, or characters</li>
          <li><strong>Recent Activity:</strong> Your latest edits and creations</li>
          <li><strong>Project Statistics:</strong> Word counts, completion status</li>
          <li><strong>Community Feed:</strong> Latest published stories and news</li>
          <li><strong>Credit Balance:</strong> Monitor your AI usage and billing</li>
        </ul>

        <div class="help-actions">
          <a href="/ui/worlds/create" class="help-action-button">
            <i class="fas fa-plus"></i>
            Create World
          </a>
          <a href="/ui/worlds/builder" class="help-action-button-secondary">
            <i class="fas fa-magic"></i>
            World Wizard
          </a>
        </div>
      </div>
    `;
  }

  getDefaultContent() {
    return `
      <div class="help-section">
        <h3>AI Storytelling Assistant</h3>
        <p>Welcome to the most advanced AI-powered world-building and storytelling platform! Create rich, detailed worlds and compelling stories with cutting-edge AI assistance.</p>
        
        <h4>Platform Features:</h4>
        <ul>
          <li><strong>World Builder Wizard:</strong> 20-question AI world generation</li>
          <li><strong>Real-time Writing Assistant:</strong> Context-aware AI help as you write</li>
          <li><strong>Character Generator:</strong> AI-created characters with generated portraits</li>
          <li><strong>Document Integration:</strong> Upload reference materials for AI context</li>
          <li><strong>Community Publishing:</strong> Share your stories with readers</li>
          <li><strong>Import from Literature:</strong> Extract worlds from existing books</li>
        </ul>

        <div class="help-tip">
          <div class="help-tip-title">
            <i class="fas fa-rocket help-tip-icon"></i>
            Getting Started
          </div>
          <div class="help-tip-content">
            New users should start with the World Builder Wizard to create their first world, then explore the AI writing tools to create their first story.
          </div>
        </div>

        <div class="help-actions">
          <a href="/ui/worlds/builder" class="help-action-button">
            <i class="fas fa-magic"></i>
            Start World Wizard
          </a>
          <a href="/ui/user-guide" class="help-action-button-secondary">
            <i class="fas fa-book"></i>
            Full User Guide
          </a>
        </div>
      </div>
    `;
  }
}

// Initialize the help modal system when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.helpModalManager = new HelpModalManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = HelpModalManager;
}
