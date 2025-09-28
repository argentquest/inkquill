/* ========================================================================
   HELP PANEL FUNCTIONALITY
   Collapsible, resizable help panel system
   ======================================================================== */

class HelpPanelManager {
  constructor() {
    this.panel = null;
    this.header = null;
    this.content = null;
    this.title = null;
    this.isInitialized = false;
    this.isCollapsed = false;
    this.isDragging = false;
    this.isResizing = false;
    this.currentTopic = null;
    
    // Drag state
    this.dragOffset = { x: 0, y: 0 };
    this.startPos = { x: 0, y: 0 };
    
    // Panel state persistence
    this.panelState = this.loadPanelState();
    
    this.init();
  }

  init() {
    this.createPanel();
    this.bindEvents();
    this.isInitialized = true;
    
    // Expose global functions
    window.openHelpPanel = (topic) => this.openPanel(topic);
    window.closeHelpPanel = () => this.closePanel();
    window.toggleHelpPanel = () => this.togglePanel();
    
    // Apply saved panel state
    this.applyPanelState();
    
    // Check for URL parameters to auto-open help
    this.checkUrlParams();
  }

  createPanel() {
    // Check if panel already exists
    if (document.getElementById('helpPanel')) {
      this.panel = document.getElementById('helpPanel');
      this.header = this.panel.querySelector('.help-panel-header');
      this.content = this.panel.querySelector('.help-panel-content');
      this.title = this.panel.querySelector('.help-panel-title');
      this.topicSelect = this.panel.querySelector('#helpPanelTopicSelect');
      return;
    }

    // Create panel HTML
    const panelHTML = `
      <div id="helpPanel" class="help-panel">
        <div class="help-panel-header">
          <h3 class="help-panel-title">
            <span class="help-icon">
              <i class="fas fa-question-circle"></i>
            </span>
            Quick Help
          </h3>
          <div class="help-panel-controls">
            <button class="help-panel-btn" onclick="this.parentElement.parentElement.parentElement.classList.toggle('position-left')" title="Move Panel" aria-label="Move panel position">
              <i class="fas fa-arrows-alt"></i>
            </button>
            <button class="help-panel-btn" onclick="window.helpPanelManager.toggleCollapse()" title="Collapse/Expand" aria-label="Toggle collapse">
              <i class="fas fa-chevron-up"></i>
            </button>
            <button class="help-panel-btn" onclick="window.helpPanelManager.closePanel()" title="Close Panel" aria-label="Close help panel">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>
        <div class="help-panel-navigation">
          <select id="helpPanelTopicSelect" class="help-panel-topic-select" onchange="window.helpPanelManager.switchTopic(this.value)">
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
              <option value="world_builder_wizard">🔮 World Builder Wizard</option>
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
              <option value="act_editor">✍️ Act Editor</option>
              <option value="scene_editor">🎬 Scene Editor</option>
              <option value="story_classes">🎭 Story Classes</option>
            </optgroup>
            <optgroup label="Tools & Resources">
              <option value="prompts">💬 Prompt Library</option>
              <option value="documents">📁 Document Manager</option>
              <option value="world_chat">💭 World Chat</option>
              <option value="billing">💳 Billing & Credits</option>
            </optgroup>
            <optgroup label="Community">
              <option value="forum">🗣️ Community Forum</option>
              <option value="published_stories">📖 Published Stories</option>
            </optgroup>
          </select>
        </div>
        <div class="help-panel-content">
          <div class="help-panel-loading">
            <div class="help-panel-spinner"></div>
            <span>Loading help content...</span>
          </div>
        </div>
      </div>
    `;

    // Add panel to document
    document.body.insertAdjacentHTML('beforeend', panelHTML);
    
    // Get references
    this.panel = document.getElementById('helpPanel');
    this.header = this.panel.querySelector('.help-panel-header');
    this.content = this.panel.querySelector('.help-panel-content');
    this.title = this.panel.querySelector('.help-panel-title');
    this.topicSelect = this.panel.querySelector('#helpPanelTopicSelect');
    
    // Store reference globally
    window.helpPanelManager = this;
  }

  bindEvents() {
    // Drag functionality
    this.header.addEventListener('mousedown', (e) => this.startDrag(e));
    this.header.addEventListener('touchstart', (e) => this.startDrag(e), { passive: false });
    
    document.addEventListener('mousemove', (e) => this.drag(e));
    document.addEventListener('touchmove', (e) => this.drag(e), { passive: false });
    
    document.addEventListener('mouseup', () => this.endDrag());
    document.addEventListener('touchend', () => this.endDrag());
    
    // Prevent text selection during drag
    this.header.addEventListener('selectstart', (e) => e.preventDefault());
    
    // Resize observer to save state
    if (window.ResizeObserver) {
      const resizeObserver = new ResizeObserver(() => {
        if (!this.isDragging && !this.isResizing) {
          this.savePanelState();
        }
      });
      resizeObserver.observe(this.panel);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.key === 'F1') {
        e.preventDefault();
        this.togglePanel();
      }
      if (e.key === 'Escape' && this.panel.classList.contains('show')) {
        this.closePanel();
      }
    });
    
    // Handle window resize for mobile responsiveness
    window.addEventListener('resize', () => {
      this.handleWindowResize();
    });
  }

  startDrag(e) {
    // Don't drag if clicking on control buttons
    if (e.target.closest('.help-panel-btn')) return;
    
    this.isDragging = true;
    this.panel.classList.add('dragging');
    
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    const rect = this.panel.getBoundingClientRect();
    this.dragOffset = {
      x: clientX - rect.left,
      y: clientY - rect.top
    };
    
    // Prevent default to avoid text selection
    e.preventDefault();
  }

  drag(e) {
    if (!this.isDragging) return;
    
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    if (!clientX || !clientY) return;
    
    let newX = clientX - this.dragOffset.x;
    let newY = clientY - this.dragOffset.y;
    
    // Constrain to viewport
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    const panelWidth = this.panel.offsetWidth;
    const panelHeight = this.panel.offsetHeight;
    
    newX = Math.max(0, Math.min(newX, viewportWidth - panelWidth));
    newY = Math.max(0, Math.min(newY, viewportHeight - panelHeight));
    
    // Apply position
    this.panel.style.left = newX + 'px';
    this.panel.style.top = newY + 'px';
    this.panel.style.right = 'auto';
    
    e.preventDefault();
  }

  endDrag() {
    if (!this.isDragging) return;
    
    this.isDragging = false;
    this.panel.classList.remove('dragging');
    
    // Save new position
    this.savePanelState();
  }

  openPanel(topic) {
    if (!this.isInitialized) {
      console.warn('Help panel not initialized');
      return;
    }

    this.currentTopic = topic;
    this.loadContent(topic);
    this.updateTopicSelect(topic);
    this.panel.classList.add('show');
    
    // Focus management for accessibility
    const collapseButton = this.panel.querySelector('.help-panel-btn');
    if (collapseButton) {
      setTimeout(() => collapseButton.focus(), 100);
    }

    // Track analytics if available
    if (window.trackFeatureUse) {
      window.trackFeatureUse('help_panel', 'open', { topic });
    }
  }

  switchTopic(topic) {
    if (!topic || topic === this.currentTopic) return;
    
    this.currentTopic = topic;
    this.loadContent(topic);
    
    // Track analytics if available
    if (window.trackFeatureUse) {
      window.trackFeatureUse('help_panel', 'switch_topic', { topic });
    }
  }

  updateTopicSelect(topic) {
    if (this.topicSelect) {
      this.topicSelect.value = topic || '';
    }
  }

  closePanel() {
    if (!this.panel) return;
    
    this.panel.classList.remove('show');
    this.currentTopic = null;
    
    // Track analytics if available
    if (window.trackFeatureUse) {
      window.trackFeatureUse('help_panel', 'close');
    }
  }

  togglePanel() {
    if (this.panel.classList.contains('show')) {
      this.closePanel();
    } else {
      this.openPanel(this.currentTopic || 'dashboard');
    }
  }

  toggleCollapse() {
    this.isCollapsed = !this.isCollapsed;
    this.panel.classList.toggle('collapsed', this.isCollapsed);
    
    // Update collapse button icon
    const collapseBtn = this.panel.querySelector('.help-panel-btn i.fa-chevron-up, .help-panel-btn i.fa-chevron-down');
    if (collapseBtn) {
      collapseBtn.className = this.isCollapsed ? 'fas fa-chevron-down' : 'fas fa-chevron-up';
    }
    
    this.savePanelState();
  }

  async loadContent(topic) {
    // Show loading state
    this.showLoading();
    
    // Update title based on topic
    this.updateTitle(topic);
    
    try {
      // Try to load content from static help directory
      let response = await fetch(`/static/help/${topic}.html`);
      
      if (response.ok) {
        const htmlContent = await response.text();
        this.content.innerHTML = htmlContent;
      } else {
        // Fallback to default content
        this.content.innerHTML = this.getDefaultContent(topic);
      }
    } catch (error) {
      console.error('Error loading help content:', error);
      this.content.innerHTML = this.getDefaultContent(topic);
    }
  }

  showLoading() {
    this.content.innerHTML = `
      <div class="help-panel-loading">
        <div class="help-panel-spinner"></div>
        <span>Loading help content...</span>
      </div>
    `;
  }

  updateTitle(topic) {
    const titles = {
      'introduction': 'Help & User Guide',
      'quick_start': 'Quick Start Tutorial',
      'dashboard': 'Dashboard Help',
      'world_list': 'World Management',
      'world_builder_wizard': 'World Builder Wizard',
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
      'user_guide': 'User Guide',
      'login': 'Login Help',
      'register': 'Registration Help',
      'world_detail': 'World Building',
      'import_book': 'Import from Book',
      'import_document': 'Import Documents'
    };

    const title = titles[topic] || 'Quick Help';
    this.title.innerHTML = `
      <span class="help-icon">
        <i class="fas fa-question-circle"></i>
      </span>
      ${title}
    `;
  }

  getDefaultContent(topic) {
    return `
      <div class="help-section">
        <h3><i class="fas fa-info-circle help-icon"></i> Help Content</h3>
        <p>Help content for <strong>${topic}</strong> is being loaded...</p>
        <div class="help-tip">
          <i class="fas fa-lightbulb"></i>
          <strong>Tip:</strong> You can resize this panel by dragging the bottom-right corner, or collapse it using the chevron button.
        </div>
        <div class="help-actions">
          <button class="btn btn-sm btn-primary" onclick="window.helpPanelManager.loadContent('user_guide')">
            <i class="fas fa-book"></i> User Guide
          </button>
          <button class="btn btn-sm btn-outline-primary" onclick="window.helpPanelManager.loadContent('dashboard')">
            <i class="fas fa-home"></i> Dashboard Help
          </button>
        </div>
      </div>
    `;
  }

  handleWindowResize() {
    // Ensure panel stays within viewport bounds
    const rect = this.panel.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    if (rect.right > viewportWidth) {
      this.panel.style.left = (viewportWidth - rect.width) + 'px';
    }
    if (rect.bottom > viewportHeight) {
      this.panel.style.top = (viewportHeight - rect.height) + 'px';
    }
  }

  savePanelState() {
    const state = {
      width: this.panel.offsetWidth,
      height: this.panel.offsetHeight,
      left: this.panel.offsetLeft,
      top: this.panel.offsetTop,
      isCollapsed: this.isCollapsed,
      topic: this.currentTopic
    };
    
    localStorage.setItem('helpPanelState', JSON.stringify(state));
  }

  loadPanelState() {
    try {
      const saved = localStorage.getItem('helpPanelState');
      return saved ? JSON.parse(saved) : {};
    } catch (e) {
      return {};
    }
  }

  applyPanelState() {
    if (!this.panelState) return;
    
    const { width, height, left, top, isCollapsed } = this.panelState;
    
    if (width) this.panel.style.width = width + 'px';
    if (height) this.panel.style.height = height + 'px';
    if (left !== undefined) this.panel.style.left = left + 'px';
    if (top !== undefined) this.panel.style.top = top + 'px';
    
    if (isCollapsed) {
      this.isCollapsed = true;
      this.panel.classList.add('collapsed');
      const collapseBtn = this.panel.querySelector('.help-panel-btn i.fa-chevron-up');
      if (collapseBtn) {
        collapseBtn.className = 'fas fa-chevron-down';
      }
    }
  }

  checkUrlParams() {
    const urlParams = new URLSearchParams(window.location.search);
    const helpTopic = urlParams.get('help');
    const showHelp = urlParams.get('show_help');
    
    // If help parameter exists, open help panel with that topic
    if (helpTopic) {
      setTimeout(() => {
        this.openPanel(helpTopic);
      }, 500); // Small delay to ensure page is fully loaded
    }
    // If show_help=true, open with default help for current page
    else if (showHelp === 'true' || showHelp === '1') {
      setTimeout(() => {
        // Try to detect current page and show appropriate help
        const currentHelp = this.detectCurrentPageHelp();
        this.openPanel(currentHelp);
      }, 500);
    }
  }

  detectCurrentPageHelp() {
    const path = window.location.pathname;
    
    // Map common URL patterns to help topics
    if (path.includes('/worlds/') && path.includes('/builder')) {
      return 'world_builder_wizard';
    } else if (path.includes('/worlds/') && path.includes('/generator/character')) {
      return 'character_generator';
    } else if (path.includes('/worlds/') && !path.includes('/stories/')) {
      return 'world_detail';
    } else if (path.includes('/stories/') && path.includes('/acts/') && path.includes('/edit')) {
      return 'act_editor';
    } else if (path.includes('/stories/') && path.includes('/scenes/') && path.includes('/edit')) {
      return 'scene_editor';
    } else if (path.includes('/stories/') && !path.includes('/acts/')) {
      return 'story_detail';
    } else if (path.includes('/characters/')) {
      return 'character_detail';
    } else if (path.includes('/locations/')) {
      return 'location_detail';
    } else if (path.includes('/lore_items/')) {
      return 'lore_item_detail';
    } else if (path === '/' || path === '/dashboard') {
      return 'dashboard';
    } else if (path.includes('/worlds')) {
      return 'world_list';
    } else if (path.includes('/stories')) {
      return 'story_list';
    }
    
    // Default fallback
    return 'dashboard';
  }
}

// Initialize help panel when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.helpPanelManager = new HelpPanelManager();
});

// Backwards compatibility - redirect modal calls to panel
window.openHelpModal = (topic) => {
  if (window.helpPanelManager) {
    window.helpPanelManager.openPanel(topic);
  }
};

window.closeHelpModal = () => {
  if (window.helpPanelManager) {
    window.helpPanelManager.closePanel();
  }
};