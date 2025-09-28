// World Hierarchy Tree View JavaScript
console.log('World Hierarchy JavaScript file loaded!');

class WorldHierarchyManager {
    constructor() {
        this.selectedNode = null;
        this.contextMenu = document.getElementById('context-menu');
        this.detailsPanel = document.getElementById('element-details');
        
        this.init();
    }
    
    init() {
        // Set up event listeners
        this.setupTreeInteractions();
        this.setupContextMenu();
        
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        
        // Collapse all nodes by default
        this.collapseAllNodes();
        
        // Hide context menu when clicking elsewhere
        document.addEventListener('click', (e) => {
            if (!this.contextMenu.contains(e.target)) {
                this.hideContextMenu();
            }
        });
        
        // Prevent context menu on right click elsewhere
        document.addEventListener('contextmenu', (e) => {
            if (!e.target.closest('.tree-node-header') && !e.target.closest('.element-card')) {
                e.preventDefault();
            }
        });
    }
    
    setupTreeInteractions() {
        // Handle expand/collapse
        document.querySelectorAll('.expand-icon').forEach(icon => {
            console.log('Setting up expand icon:', icon);
            icon.addEventListener('click', (e) => {
                e.stopPropagation();
                console.log('Expand icon clicked:', icon);
                this.toggleNode(icon);
            });
        });
        
        // Handle node selection
        document.querySelectorAll('.tree-node-header').forEach(header => {
            header.addEventListener('click', (e) => {
                if (!e.target.classList.contains('expand-icon')) {
                    this.selectNode(header);
                }
            });
            
            // Right-click context menu
            header.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.selectNode(header);
                this.showContextMenu(e.clientX, e.clientY, header);
            });
        });

        // Handle element card interactions
        document.querySelectorAll('.element-card').forEach(card => {
            // Click selection
            card.addEventListener('click', (e) => {
                this.selectCard(card);
            });
            
            // Right-click context menu
            card.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                this.selectCard(card);
                this.showContextMenu(e.clientX, e.clientY, card);
            });
        });
    }
    
    setupContextMenu() {
        document.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleContextAction(action);
                this.hideContextMenu();
            });
        });
    }
    
    expandAllNodes() {
        // Find all expand icons and ensure they're in expanded state
        document.querySelectorAll('.expand-icon').forEach(icon => {
            if (icon.classList.contains('collapsed')) {
                icon.classList.remove('collapsed');
                icon.classList.add('expanded');
            }
        });
        
        // Find all tree-children and ensure they're visible
        document.querySelectorAll('.tree-children').forEach(children => {
            if (children.classList.contains('collapsed')) {
                children.classList.remove('collapsed');
            }
        });
        
        console.log('All nodes expanded');
    }
    
    collapseAllNodes() {
        // Find all expand icons (except the world root) and collapse them
        document.querySelectorAll('.expand-icon').forEach(icon => {
            // Skip the world root node (level 0)
            const header = icon.closest('.tree-node-header');
            const level = header.dataset.level;
            
            if (level !== '0') { // Don't collapse the world root
                if (icon.classList.contains('expanded')) {
                    icon.classList.remove('expanded');
                    icon.classList.add('collapsed');
                }
            }
        });
        
        // Find all tree-children (except world's direct children) and hide them
        document.querySelectorAll('.tree-children').forEach(children => {
            const parentHeader = children.previousElementSibling;
            const level = parentHeader ? parentHeader.dataset.level : null;
            
            if (level !== '0') { // Don't collapse world's direct children
                if (!children.classList.contains('collapsed')) {
                    children.classList.add('collapsed');
                }
            }
        });
        
        console.log('All nodes collapsed (except world root)');
    }
    
    toggleNode(expandIcon) {
        const isExpanded = expandIcon.classList.contains('expanded');
        const treeNode = expandIcon.closest('.tree-node');
        const children = treeNode.querySelector(':scope > .tree-children');
        
        if (children) {
            if (isExpanded) {
                expandIcon.classList.remove('expanded');
                expandIcon.classList.add('collapsed');
                children.classList.add('collapsed');
            } else {
                expandIcon.classList.remove('collapsed');
                expandIcon.classList.add('expanded');
                children.classList.remove('collapsed');
            }
        }
    }
    
    selectNode(nodeHeader) {
        // Remove previous selection
        if (this.selectedNode) {
            this.selectedNode.classList.remove('selected');
        }
        
        // Set new selection
        nodeHeader.classList.add('selected');
        this.selectedNode = nodeHeader;
        
        // Load details for selected node
        this.loadNodeDetails(nodeHeader);
    }

    selectCard(card) {
        // Remove previous selection
        if (this.selectedNode) {
            this.selectedNode.classList.remove('selected');
        }
        
        // Remove card selections
        document.querySelectorAll('.element-card.selected').forEach(c => {
            c.classList.remove('selected');
        });
        
        // Set new selection
        card.classList.add('selected');
        this.selectedNode = card;
        
        // Load details for selected card
        this.loadCardDetails(card);
    }
    
    loadNodeDetails(nodeHeader) {
        const treeNode = nodeHeader.closest('.tree-node');
        const nodeType = treeNode.dataset.type;
        const nodeId = treeNode.dataset.id;
        
        // Show quick edit form for editable elements
        this.showQuickEditForm(nodeType, nodeId);
        
        // For acts and scenes, show tabbed interface
        if (nodeType === 'act' || nodeType === 'scene') {
            this.showTabbedDetails(nodeType, nodeId);
        } else {
            // For other elements, clear tabbed details and show regular details
            this.clearAllDetails();
            
            let detailsHtml = '';
            
            switch (nodeType) {
                case 'world':
                    detailsHtml = this.createWorldDetails();
                    break;
                case 'story':
                    detailsHtml = this.createStoryDetails(nodeId);
                    break;
                case 'character':
                    detailsHtml = this.createCharacterDetails(nodeId);
                    break;
                case 'location':
                    detailsHtml = this.createLocationDetails(nodeId);
                    break;
                case 'lore_item':
                    detailsHtml = this.createLoreItemDetails(nodeId);
                    break;
                default:
                    detailsHtml = '<div class="details-empty"><p>Unknown element type</p></div>';
            }
            
            // Hide empty state and show regular details
            document.querySelector('.details-empty').style.display = 'none';
            
            // Create a temporary container for regular details
            const regularDetails = document.createElement('div');
            regularDetails.innerHTML = detailsHtml;
            regularDetails.id = 'regular-details';
            
            // Clear any existing regular details and add new ones
            const existingRegular = document.getElementById('regular-details');
            if (existingRegular) {
                existingRegular.remove();
            }
            
            document.getElementById('element-details').appendChild(regularDetails);
        }
    }

    loadCardDetails(card) {
        const nodeType = card.dataset.type;
        const nodeId = card.dataset.id;
        
        // Show quick edit form for editable elements
        this.showQuickEditForm(nodeType, nodeId);
        
        // For scenes, show tabbed interface
        if (nodeType === 'scene') {
            this.showTabbedDetails(nodeType, nodeId);
        } else {
            // For other elements, clear tabbed details and show regular details
            this.clearAllDetails();
            
            let detailsHtml = '';
            
            switch (nodeType) {
                case 'character':
                    detailsHtml = this.createCharacterDetails(nodeId);
                    break;
                case 'location':
                    detailsHtml = this.createLocationDetails(nodeId);
                    break;
                case 'lore_item':
                    detailsHtml = this.createLoreItemDetails(nodeId);
                    break;
                default:
                    detailsHtml = '<div class="details-empty"><p>Unknown element type</p></div>';
            }
            
            // Hide empty state and show regular details
            document.querySelector('.details-empty').style.display = 'none';
            
            // Create a temporary container for regular details
            const regularDetails = document.createElement('div');
            regularDetails.innerHTML = detailsHtml;
            regularDetails.id = 'regular-details';
            
            // Clear any existing regular details and add new ones
            const existingRegular = document.getElementById('regular-details');
            if (existingRegular) {
                existingRegular.remove();
            }
            
            document.getElementById('element-details').appendChild(regularDetails);
        }
    }
    
    isSceneEditingActive() {
        const tabbedDetails = document.getElementById('tabbed-details');
        return tabbedDetails && tabbedDetails.style.display !== 'none';
    }
    
    createWorldDetails() {
        // Get world data from the DOM
        const worldNode = document.querySelector('[data-type="world"]');
        const worldId = worldNode ? worldNode.dataset.id : 'Unknown';
        const worldName = worldNode ? worldNode.querySelector('.node-title')?.textContent || 'Unknown World' : 'Unknown World';
        const worldDescription = worldNode ? worldNode.querySelector('.tree-node-header')?.getAttribute('title') || 'No description available' : 'No description available';
        
        // Create initial HTML with loading state
        const loadingHtml = `
            <div class="details-title">
                <i class="fas fa-globe me-2"></i>World Details
            </div>
            <div class="details-description">
                <p><strong>Name:</strong> ${worldName}</p>
                <p><strong>Description:</strong> ${worldDescription}</p>
                <p><strong>Created:</strong> <span class="loading-placeholder">Loading...</span></p>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary btn-sm" onclick="hierarchyManager.viewElement('world', '${worldId}')">
                    <i class="fas fa-eye me-1"></i>View World
                </button>
                <button class="btn btn-outline-secondary btn-sm ms-2" onclick="hierarchyManager.editElement('world', '${worldId}')">
                    <i class="fas fa-edit me-1"></i>Edit World
                </button>
            </div>
        `;
        
        // Try to fetch full world data if we have an ID
        if (worldId !== 'Unknown') {
            setTimeout(() => this.loadFullWorldDetails(worldId), 100);
        }
        
        return loadingHtml;
    }
    
    async loadFullWorldDetails(worldId) {
        try {
            const response = await fetch(`/api/v1/worlds/${worldId}`);
            if (response.ok) {
                const worldData = await response.json();
                
                // Update the created date if it exists
                const loadingPlaceholder = document.querySelector('.loading-placeholder');
                if (loadingPlaceholder && worldData.created_at) {
                    const createdDate = new Date(worldData.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    });
                    loadingPlaceholder.textContent = createdDate;
                } else if (loadingPlaceholder) {
                    loadingPlaceholder.textContent = 'Unknown';
                }
            }
        } catch (error) {
            console.error('Error loading world details:', error);
            const loadingPlaceholder = document.querySelector('.loading-placeholder');
            if (loadingPlaceholder) {
                loadingPlaceholder.textContent = 'Unknown';
            }
        }
    }
    
    createStoryDetails(storyId) {
        // Stories don't show detailed info in the hierarchy view
        return `
            <div class="details-empty text-center py-4">
                <i class="fas fa-book fa-2x mb-3 text-muted"></i>
                <p class="text-muted">Select an act or scene to view details</p>
                <p class="small text-muted">Stories are managed through the main story pages</p>
            </div>
        `;
    }
    
    createActDetails(actId) {
        // TODO: Fetch act details via API
        return `
            <div class="details-title">
                <i class="fas fa-theater-masks me-2"></i>Act Details
            </div>
            <div class="details-description">
                <p>Act details will be loaded here...</p>
                <p><em>Feature coming soon</em></p>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary btn-sm" onclick="hierarchyManager.viewElement('act', ${actId})">
                    <i class="fas fa-eye me-1"></i>View Act
                </button>
                <button class="btn btn-outline-secondary btn-sm ms-2" onclick="hierarchyManager.editElement('act', ${actId})">
                    <i class="fas fa-edit me-1"></i>Edit Act
                </button>
            </div>
        `;
    }
    
    createCharacterDetails(characterId) {
        const isSceneEditing = this.isSceneEditingActive();
        
        let html = `
            <div class="details-title">
                <i class="fas fa-user me-2"></i>Character Details
            </div>
        `;
        
        // Only show action buttons when NOT in scene editing mode
        if (!isSceneEditing) {
            html += `
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm" onclick="hierarchyManager.viewElement('character', ${characterId})">
                        <i class="fas fa-eye me-1"></i>View Character
                    </button>
                    <button class="btn btn-outline-secondary btn-sm ms-2" onclick="hierarchyManager.editElement('character', ${characterId})">
                        <i class="fas fa-edit me-1"></i>Edit Character
                    </button>
                </div>
            `;
        }
        
        return html;
    }
    
    createLocationDetails(locationId) {
        const isSceneEditing = this.isSceneEditingActive();
        
        let html = `
            <div class="details-title">
                <i class="fas fa-map-marker-alt me-2"></i>Location Details
            </div>
            <div class="details-description">
                <p>Location details will be loaded here...</p>
                <p><em>Feature coming soon</em></p>
            </div>
        `;
        
        // Only show action buttons when NOT in scene editing mode
        if (!isSceneEditing) {
            html += `
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm" onclick="hierarchyManager.viewElement('location', ${locationId})">
                        <i class="fas fa-eye me-1"></i>View Location
                    </button>
                    <button class="btn btn-outline-secondary btn-sm ms-2" onclick="hierarchyManager.editElement('location', ${locationId})">
                        <i class="fas fa-edit me-1"></i>Edit Location
                    </button>
                </div>
            `;
        }
        
        return html;
    }
    
    createLoreItemDetails(loreItemId) {
        const isSceneEditing = this.isSceneEditingActive();
        
        let html = `
            <div class="details-title">
                <i class="fas fa-scroll me-2"></i>Lore Item Details
            </div>
            <div class="details-description">
                <p>Lore item details will be loaded here...</p>
                <p><em>Feature coming soon</em></p>
            </div>
        `;
        
        // Only show action buttons when NOT in scene editing mode
        if (!isSceneEditing) {
            html += `
                <div class="mt-3">
                    <button class="btn btn-primary btn-sm" onclick="hierarchyManager.viewElement('lore_item', ${loreItemId})">
                        <i class="fas fa-eye me-1"></i>View Lore Item
                    </button>
                    <button class="btn btn-outline-secondary btn-sm ms-2" onclick="hierarchyManager.editElement('lore_item', ${loreItemId})">
                        <i class="fas fa-edit me-1"></i>Edit Lore Item
                    </button>
                </div>
            `;
        }
        
        return html;
    }
    
    createSceneDetails(sceneId) {
        // Scenes now use the tabbed interface, this method should not be called
        return `
            <div class="details-empty text-center py-4">
                <i class="fas fa-film fa-2x mb-3 text-muted"></i>
                <p class="text-muted">This scene should be displayed in the tabbed interface</p>
            </div>
        `;
    }
    
    showContextMenu(x, y, element) {
        let nodeType, nodeId;
        let actualElement;
        
        // Check if it's a tree node or element card
        if (element.classList.contains('element-card')) {
            nodeType = element.dataset.type;
            nodeId = element.dataset.id;
            actualElement = element;
        } else {
            const treeNode = element.closest('.tree-node');
            nodeType = treeNode.dataset.type;
            nodeId = treeNode.dataset.id;
            actualElement = treeNode;
        }
        
        // Update context menu options based on node type and element
        this.updateContextMenuOptions(nodeType, actualElement);
        
        // Position context menu
        this.contextMenu.style.left = x + 'px';
        this.contextMenu.style.top = y + 'px';
        this.contextMenu.style.display = 'block';
        
        // Store current node for context actions
        this.contextMenu.dataset.nodeType = nodeType;
        this.contextMenu.dataset.nodeId = nodeId;
        
        // Adjust position if menu goes off screen
        const rect = this.contextMenu.getBoundingClientRect();
        if (rect.right > window.innerWidth) {
            this.contextMenu.style.left = (x - rect.width) + 'px';
        }
        if (rect.bottom > window.innerHeight) {
            this.contextMenu.style.top = (y - rect.height) + 'px';
        }
    }
    
    updateContextMenuOptions(nodeType, element) {
        // Hide all creation options first
        const createStory = this.contextMenu.querySelector('[data-action="create-story"]');
        const createAct = this.contextMenu.querySelector('[data-action="create-act"]');
        const createScene = this.contextMenu.querySelector('[data-action="create-scene"]');
        const createSeparator = this.contextMenu.querySelector('.context-menu-create-separator');
        const associateItem = this.contextMenu.querySelector('[data-action="associate"]');
        const rolesItem = this.contextMenu.querySelector('[data-action="edit-roles"]');
        const removeAssociationItem = this.contextMenu.querySelector('[data-action="remove-association"]');
        const deleteItem = this.contextMenu.querySelector('[data-action="delete"]');
        
        // Hide all by default
        createStory.style.display = 'none';
        createAct.style.display = 'none';
        createScene.style.display = 'none';
        createSeparator.style.display = 'none';
        associateItem.style.display = 'none';
        rolesItem.style.display = 'none';
        removeAssociationItem.style.display = 'none';
        deleteItem.style.display = 'none';
        
        // Show options based on node type
        switch (nodeType) {
            case 'world':
                createStory.style.display = 'block';
                createSeparator.style.display = 'block';
                break;
            case 'story':
                createAct.style.display = 'block';
                createSeparator.style.display = 'block';
                associateItem.style.display = 'block';
                break;
            case 'act':
                createScene.style.display = 'block';
                createSeparator.style.display = 'block';
                associateItem.style.display = 'block';
                break;
            case 'scene':
                associateItem.style.display = 'block';
                break;
            case 'character':
            case 'location':
            case 'lore_item':
                rolesItem.style.display = 'block';
                // Use the passed element to check context
                if (element) {
                    // Check if it's inside a story, act, or scene container
                    const storyContainer = element.closest('[data-type="story"]');
                    const actContainer = element.closest('[data-type="act"]');
                    const sceneContainer = element.closest('[data-type="scene"]');
                    
                    if (storyContainer || actContainer || sceneContainer) {
                        // Show remove association for associated elements
                        removeAssociationItem.style.display = 'block';
                    } else {
                        // Show delete for unassociated elements (in Available sections)
                        deleteItem.style.display = 'block';
                    }
                }
                break;
        }
    }
    
    hideContextMenu() {
        this.contextMenu.style.display = 'none';
    }
    
    handleContextAction(action) {
        const nodeType = this.contextMenu.dataset.nodeType;
        const nodeId = this.contextMenu.dataset.nodeId;
        
        switch (action) {
            case 'view':
                this.viewElement(nodeType, nodeId);
                break;
            case 'edit':
                this.editElement(nodeType, nodeId);
                break;
            case 'associate':
                this.manageAssociations(nodeType, nodeId);
                break;
            case 'edit-roles':
                this.editElementRoles(nodeType, nodeId);
                break;
            case 'create-story':
                this.createNewStory(nodeId);
                break;
            case 'create-act':
                this.createNewAct(nodeId);
                break;
            case 'create-scene':
                this.createNewScene(nodeId);
                break;
            case 'remove-association':
                this.removeAssociation(nodeType, nodeId);
                break;
            case 'delete':
                this.deleteElement(nodeType, nodeId);
                break;
        }
    }
    
    viewElement(nodeType, nodeId) {
        const worldId = document.querySelector('[data-type="world"]').dataset.id;
        let url = '';
        
        switch (nodeType) {
            case 'world':
                url = `/ui/worlds/${nodeId}`;
                break;
            case 'story':
                url = `/ui/stories/${nodeId}`;
                break;
            case 'act':
                url = `/ui/acts/${nodeId}`;
                break;
            case 'scene':
                url = `/ui/scenes/${nodeId}`;
                break;
            case 'character':
                url = `/ui/worlds/${worldId}/characters/${nodeId}`;
                break;
            case 'location':
                url = `/ui/worlds/${worldId}/locations/${nodeId}`;
                break;
            case 'lore_item':
                url = `/ui/worlds/${worldId}/lore-items/${nodeId}`;
                break;
            default:
                console.error('Unknown element type:', nodeType);
                return;
        }
        
        window.location.href = url;
    }
    
    editElement(nodeType, nodeId) {
        const worldId = document.querySelector('[data-type="world"]').dataset.id;
        let url = '';
        
        switch (nodeType) {
            case 'world':
                url = `/ui/worlds/${nodeId}/edit`;
                break;
            case 'story':
                url = `/ui/stories/${nodeId}/edit`;
                break;
            case 'act':
                url = `/ui/acts/${nodeId}/edit`;
                break;
            case 'scene':
                url = `/ui/scenes/${nodeId}/edit`;
                break;
            case 'character':
                url = `/ui/worlds/characters/${nodeId}/edit`;
                break;
            case 'location':
                url = `/ui/worlds/locations/${nodeId}/edit`;
                break;
            case 'lore_item':
                url = `/ui/worlds/lore-items/${nodeId}/edit`;
                break;
            default:
                console.error('Unknown element type:', nodeType);
                return;
        }
        
        window.location.href = url;
    }
    
    createNewStory(worldId) {
        // Navigate to the story creation form for this world using correct route
        window.location.href = `/ui/worlds/${worldId}/stories/new`;
    }
    
    createNewAct(storyId) {
        // Navigate to the act creation form for this story using correct route
        window.location.href = `/ui/stories/${storyId}/acts/new`;
    }
    
    createNewScene(actId) {
        // Navigate to the scene creation form for this act
        // Note: Scene creation requires both story_id and act_id, need to get story_id
        const actNode = document.querySelector(`[data-type="act"][data-id="${actId}"]`);
        if (actNode) {
            // Find the parent story node by traversing up the DOM
            let currentElement = actNode;
            while (currentElement) {
                // Look for parent story container
                const storyContainer = currentElement.closest('.tree-node[data-type="story"]');
                if (storyContainer) {
                    const storyId = storyContainer.dataset.id;
                    window.location.href = `/ui/stories/${storyId}/acts/${actId}/scenes/new`;
                    return;
                }
                currentElement = currentElement.parentElement;
            }
        }
        
        console.error('Could not find parent story for act:', actId);
        this.showToast('Could not determine parent story for this act.', 'error');
    }
    
    manageAssociations(nodeType, nodeId) {
        console.log('Manage associations for', nodeType, nodeId);
        if (nodeType === 'story' || nodeType === 'act' || nodeType === 'scene') {
            this.openAssociationModal(nodeType, nodeId);
        } else if (nodeType === 'character' || nodeType === 'location' || nodeType === 'lore_item') {
            this.openElementAssociationModal(nodeType, nodeId);
        } else {
            alert(`Association management not yet available for ${nodeType}`);
        }
    }
    
    async deleteElement(nodeType, nodeId) {
        // Only allow deletion for characters, locations, and lore items
        if (!['character', 'location', 'lore_item'].includes(nodeType)) {
            return;
        }
        
        // Get element name for confirmation
        const element = document.querySelector(`[data-type="${nodeType}"][data-id="${nodeId}"]`);
        const elementName = element ? element.querySelector('.node-title')?.textContent.trim() || 
                                     element.querySelector('.element-card-title')?.textContent.trim() || 
                                     nodeType : nodeType;
        
        // Show confirmation dialog
        const confirmMessage = `Are you sure you want to permanently delete "${elementName}"?\n\nThis action cannot be undone and will remove the ${nodeType.replace('_', ' ')} from the world completely.`;
        if (!confirm(confirmMessage)) {
            return;
        }
        
        // Prepare API endpoint
        let endpoint = '';
        
        switch (nodeType) {
            case 'character':
                endpoint = `/api/v1/characters/${nodeId}`;
                break;
            case 'location':
                endpoint = `/api/v1/locations/${nodeId}`;
                break;
            case 'lore_item':
                endpoint = `/api/v1/lore-items/${nodeId}`;
                break;
        }
        
        try {
            // Make DELETE request
            const response = await fetch(endpoint, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Remove element from DOM
                element.remove();
                
                // Show success message
                this.showToast(`${nodeType.replace('_', ' ')} deleted successfully`, 'success');
                
                // Clear details panel if this element was selected
                if (this.selectedNode === element) {
                    this.selectedNode = null;
                    this.updateDetailsPanel(null);
                }
            } else {
                // Only try to parse JSON if there's content
                let errorMessage = 'Failed to delete element';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    // If JSON parsing fails, use status text
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('Error deleting element:', error);
            this.showToast(`Failed to delete ${nodeType.replace('_', ' ')}: ${error.message}`, 'error');
        }
    }
    
    temporarilyDisableUnsavedChangesWarning() {
        // Check if there's a content editor with unsaved changes
        if (window.contentEditor) {
            // Force clear unsaved changes to avoid the popup
            window.contentEditor.hasUnsavedChanges = false;
            // Also update the UI to reflect this change
            if (typeof window.contentEditor.updateUI === 'function') {
                window.contentEditor.updateUI();
            }
        }
    }
    
    clearUnsavedChanges() {
        // Public method to clear unsaved changes
        if (window.contentEditor) {
            window.contentEditor.hasUnsavedChanges = false;
            if (typeof window.contentEditor.updateUI === 'function') {
                window.contentEditor.updateUI();
            }
            this.showToast('Unsaved changes cleared', 'info');
        }
    }
    
    async removeAssociation(nodeType, nodeId) {
        // Only allow removal for characters, locations, and lore items
        if (!['character', 'location', 'lore_item'].includes(nodeType)) {
            return;
        }
        
        // Get element info
        const element = document.querySelector(`[data-type="${nodeType}"][data-id="${nodeId}"]`);
        if (!element) return;
        
        const elementName = element.querySelector('.node-title')?.textContent.trim() || 
                           element.querySelector('.element-card-title')?.textContent.trim() || 
                           nodeType;
        
        // Find the container (story, act, or scene)
        const storyContainer = element.closest('[data-type="story"]');
        const actContainer = element.closest('[data-type="act"]');
        const sceneContainer = element.closest('[data-type="scene"]');
        
        let containerType = '';
        let containerId = '';
        let containerName = '';
        
        if (sceneContainer) {
            containerType = 'scene';
            containerId = sceneContainer.dataset.id;
            containerName = sceneContainer.querySelector('.node-title')?.textContent || 'this scene';
        } else if (actContainer) {
            containerType = 'act';
            containerId = actContainer.dataset.id;
            containerName = actContainer.querySelector('.node-title')?.textContent || 'this act';
        } else if (storyContainer) {
            containerType = 'story';
            containerId = storyContainer.dataset.id;
            containerName = storyContainer.querySelector('.node-title')?.textContent || 'this story';
        } else {
            this.showToast('Could not determine association container', 'error');
            return;
        }
        
        // Show confirmation dialog
        const confirmMessage = `Are you sure you want to remove "${elementName}" from ${containerName}?\n\nThe ${nodeType.replace('_', ' ')} will not be deleted, only the association will be removed.`;
        if (!confirm(confirmMessage)) {
            return;
        }
        
        // Prepare API endpoint based on container and element type
        let endpoint = `/api/v1/associations/${containerType}/${containerId}/${nodeType}/${nodeId}`;
        
        try {
            // Make DELETE request
            const response = await fetch(endpoint, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Remove element from DOM
                element.remove();
                
                // Show success message
                this.showToast(`${nodeType.replace('_', ' ')} removed from ${containerType} successfully`, 'success');
                
                // Clear details panel if this element was selected
                if (this.selectedNode === element) {
                    this.selectedNode = null;
                    this.updateDetailsPanel(null);
                }
            } else {
                // Only try to parse JSON if there's content
                let errorMessage = 'Failed to remove association';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch (e) {
                    // If JSON parsing fails, use status text
                    errorMessage = response.statusText || errorMessage;
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('Error removing association:', error);
            this.showToast(`Failed to remove association: ${error.message}`, 'error');
        }
    }
    
    openAssociationModal(containerType, containerId) {
        // Use the existing modal from the HTML template
        const modal = document.getElementById('associationModal');
        
        // Store container info in modal
        modal.dataset.containerType = containerType;
        modal.dataset.containerId = containerId;
        
        // Update modal title
        const modalLabel = document.getElementById('associationModalLabel');
        modalLabel.innerHTML = `<i class="fas fa-link me-2"></i>Manage ${containerType.charAt(0).toUpperCase() + containerType.slice(1)} Associations`;
        
        // Initialize Bootstrap modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Load current associations
        this.loadAssociations(containerType, containerId);
        
        // Set up save button
        const saveBtn = document.getElementById('saveAssociationsBtn');
        saveBtn.onclick = () => this.saveAssociations(containerType, containerId);
    }
    
    createAssociationModal(containerType, containerId) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'associationModal';
        modal.tabIndex = -1;
        modal.setAttribute('aria-labelledby', 'associationModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        modal.setAttribute('data-container-type', containerType);
        modal.setAttribute('data-container-id', containerId);
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="associationModalLabel">
                            <i class="fas fa-link me-2"></i>Manage ${containerType.charAt(0).toUpperCase() + containerType.slice(1)} Associations
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-users me-2"></i>Characters</h6>
                                <div id="characterAssociations" class="association-list">
                                    <div class="text-center text-muted">
                                        <div class="spinner-border spinner-border-sm" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                        Loading...
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-map-marker-alt me-2"></i>Locations</h6>
                                <div id="locationAssociations" class="association-list">
                                    <div class="text-center text-muted">
                                        <div class="spinner-border spinner-border-sm" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                        Loading...
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="row mt-3">
                            <div class="col-12">
                                <h6><i class="fas fa-scroll me-2"></i>Lore Items</h6>
                                <div id="loreItemAssociations" class="association-list">
                                    <div class="text-center text-muted">
                                        <div class="spinner-border spinner-border-sm" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                        </div>
                                        Loading...
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>Close
                        </button>
                        <button type="button" class="btn btn-primary" onclick="hierarchyManager.saveAssociations('${containerType}', ${containerId})">
                            <i class="fas fa-save me-1"></i>Save Changes
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    async loadAssociations(containerType, containerId) {
        try {
            // Load current associations from API
            const apiUrl = `/api/v1/associations/${containerType}/${containerId}/all`;
            console.log('Loading associations from:', apiUrl);
            
            const response = await fetch(apiUrl);
            
            if (response.ok) {
                const associations = await response.json();
                console.log('Associations loaded:', associations);
                this.renderAssociations(associations, containerType, containerId);
            } else {
                console.error('Failed to load associations. Status:', response.status, 'Response:', await response.text());
                throw new Error('Failed to load associations');
            }
            
        } catch (error) {
            console.error('Error loading associations:', error);
            // Fall back to showing available elements for association
            this.loadAvailableElements(containerType, containerId);
        }
    }
    
    renderAssociations(associations, containerType, containerId) {
        // Load all available elements first
        this.loadAvailableElements(containerType, containerId).then(() => {
            // Then mark existing associations and add their roles
            this.markExistingAssociations(associations);
        });
    }
    
    markExistingAssociations(associations) {
        // Mark character associations
        if (associations.characters) {
            associations.characters.forEach(assoc => {
                // Check if character object exists
                if (!assoc.character) {
                    console.warn('Character object missing in association:', assoc);
                    return;
                }
                
                const checkbox = document.getElementById(`char_${assoc.character.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    const tagsContainer = document.getElementById(`char_tags_${assoc.character.id}`);
                    const roleInput = document.getElementById(`char_roles_${assoc.character.id}`);
                    const notesTextarea = document.getElementById(`char_notes_${assoc.character.id}`);
                    
                    if (tagsContainer && assoc.roles) {
                        this.displayRoleTags(tagsContainer, assoc.roles, roleInput);
                    }
                    if (notesTextarea && assoc.notes) {
                        notesTextarea.value = assoc.notes;
                    }
                }
            });
        }
        
        // Mark location associations
        if (associations.locations) {
            associations.locations.forEach(assoc => {
                // Check if location object exists
                if (!assoc.location) {
                    console.warn('Location object missing in association:', assoc);
                    return;
                }
                
                const checkbox = document.getElementById(`loc_${assoc.location.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    const tagsContainer = document.getElementById(`loc_tags_${assoc.location.id}`);
                    const roleInput = document.getElementById(`loc_roles_${assoc.location.id}`);
                    const notesTextarea = document.getElementById(`loc_notes_${assoc.location.id}`);
                    
                    if (tagsContainer && assoc.roles) {
                        this.displayRoleTags(tagsContainer, assoc.roles, roleInput);
                    }
                    if (notesTextarea && assoc.notes) {
                        notesTextarea.value = assoc.notes;
                    }
                }
            });
        }
        
        // Mark lore item associations
        if (associations.lore_items) {
            associations.lore_items.forEach(assoc => {
                // Check if lore_item object exists
                if (!assoc.lore_item) {
                    console.warn('Lore item object missing in association:', assoc);
                    return;
                }
                
                const checkbox = document.getElementById(`lore_${assoc.lore_item.id}`);
                if (checkbox) {
                    checkbox.checked = true;
                    const tagsContainer = document.getElementById(`lore_tags_${assoc.lore_item.id}`);
                    const roleInput = document.getElementById(`lore_roles_${assoc.lore_item.id}`);
                    const notesTextarea = document.getElementById(`lore_notes_${assoc.lore_item.id}`);
                    
                    if (tagsContainer && assoc.roles) {
                        this.displayRoleTags(tagsContainer, assoc.roles, roleInput);
                    }
                    if (notesTextarea && assoc.notes) {
                        notesTextarea.value = assoc.notes;
                    }
                }
            });
        }
    }
    
    async loadAvailableElements(containerType, containerId) {
        // Load all available elements that can be associated
        // This will show all world elements with checkboxes to create associations
        const worldId = document.querySelector('[data-type="world"]').dataset.id;
        console.log('Loading available elements for', containerType, containerId, 'from world', worldId);
        
        try {
            const [charactersRes, locationsRes, loreItemsRes] = await Promise.all([
                fetch(`/api/v1/worlds/${worldId}/characters`),
                fetch(`/api/v1/worlds/${worldId}/locations`),
                fetch(`/api/v1/worlds/${worldId}/lore-items`)
            ]);
            
            if (!charactersRes.ok || !locationsRes.ok || !loreItemsRes.ok) {
                console.error('Failed to load elements:', {
                    characters: charactersRes.status,
                    locations: locationsRes.status,
                    loreItems: loreItemsRes.status
                });
                throw new Error('Failed to load world elements');
            }
            
            const characters = await charactersRes.json();
            const locations = await locationsRes.json();
            const loreItems = await loreItemsRes.json();
            
            console.log('Loaded elements:', { characters: characters.length, locations: locations.length, loreItems: loreItems.length });
            
            this.renderAvailableElements({ characters, locations, loreItems });
            
        } catch (error) {
            console.error('Error loading available elements:', error);
            this.showAssociationError('Failed to load available elements for association');
        }
    }
    
    renderAvailableElements(elements) {
        console.log('Rendering available elements:', elements);
        
        const characterContainer = document.getElementById('characterAssociations');
        const locationContainer = document.getElementById('locationAssociations');
        const loreItemContainer = document.getElementById('loreItemAssociations');
        
        console.log('Container elements found:', {
            characterContainer: !!characterContainer,
            locationContainer: !!locationContainer,
            loreItemContainer: !!loreItemContainer
        });
        
        // Render characters
        if (characterContainer) {
            console.log('Rendering', elements.characters.length, 'characters');
            characterContainer.innerHTML = elements.characters.map(char => `
            <div class="association-item">
                <div class="association-item-header">
                    <input class="form-check-input me-2" type="checkbox" value="${char.id}" id="char_${char.id}">
                    <div class="association-thumbnail default-character${char.image_url ? ' has-image' : ''}"
                         ${char.image_url ? `style="background-image: url('${char.image_url}');"` : ''}></div>
                    <label class="form-check-label" for="char_${char.id}">
                        ${char.name}
                    </label>
                </div>
                <div class="role-input-container">
                    <div class="role-tags" id="char_tags_${char.id}"></div>
                    <input type="text" 
                           class="form-control form-control-sm role-input" 
                           placeholder="Add role..." 
                           id="char_roles_${char.id}"
                           data-element-type="character"
                           data-element-id="${char.id}">
                    <div class="role-suggestions" id="char_suggestions_${char.id}" style="display: none;"></div>
                    <textarea class="form-control form-control-sm note-field-fixed mt-2" 
                              placeholder="Notes (optional)..." 
                              id="char_notes_${char.id}"></textarea>
                </div>
            </div>
        `).join('');
        } else {
            console.error('Character container not found');
        }
        
        // Render locations
        if (locationContainer) {
            console.log('Rendering', elements.locations.length, 'locations');
            locationContainer.innerHTML = elements.locations.map(loc => `
            <div class="association-item">
                <div class="association-item-header">
                    <input class="form-check-input me-2" type="checkbox" value="${loc.id}" id="loc_${loc.id}">
                    <div class="association-thumbnail default-location${loc.image_url ? ' has-image' : ''}"
                         ${loc.image_url ? `style="background-image: url('${loc.image_url}');"` : ''}></div>
                    <label class="form-check-label" for="loc_${loc.id}">
                        ${loc.name}
                    </label>
                </div>
                <div class="role-input-container">
                    <div class="role-tags" id="loc_tags_${loc.id}"></div>
                    <input type="text" 
                           class="form-control form-control-sm role-input" 
                           placeholder="Add role..." 
                           id="loc_roles_${loc.id}"
                           data-element-type="location"
                           data-element-id="${loc.id}">
                    <div class="role-suggestions" id="loc_suggestions_${loc.id}" style="display: none;"></div>
                    <textarea class="form-control form-control-sm note-field-fixed mt-2" 
                              placeholder="Notes (optional)..." 
                              id="loc_notes_${loc.id}"></textarea>
                </div>
            </div>
        `).join('');
        } else {
            console.error('Location container not found');
        }
        
        // Render lore items
        if (loreItemContainer) {
            console.log('Rendering', elements.loreItems.length, 'lore items');
            loreItemContainer.innerHTML = elements.loreItems.map(item => `
            <div class="association-item">
                <div class="association-item-header">
                    <input class="form-check-input me-2" type="checkbox" value="${item.id}" id="lore_${item.id}">
                    <div class="association-thumbnail default-lore${item.image_url ? ' has-image' : ''}"
                         ${item.image_url ? `style="background-image: url('${item.image_url}');"` : ''}></div>
                    <label class="form-check-label" for="lore_${item.id}">
                        ${item.title}
                    </label>
                </div>
                <div class="role-input-container">
                    <div class="role-tags" id="lore_tags_${item.id}"></div>
                    <input type="text" 
                           class="form-control form-control-sm role-input" 
                           placeholder="Add role..." 
                           id="lore_roles_${item.id}"
                           data-element-type="lore_item"
                           data-element-id="${item.id}">
                    <div class="role-suggestions" id="lore_suggestions_${item.id}" style="display: none;"></div>
                    <textarea class="form-control form-control-sm note-field-fixed mt-2" 
                              placeholder="Notes (optional)..." 
                              id="lore_notes_${item.id}"></textarea>
                </div>
            </div>
        `).join('');
        } else {
            console.error('Lore item container not found');
        }
        
        // Initialize role management after rendering
        this.initializeRoleManagement();
    }
    
    initializeRoleManagement() {
        console.log('Initializing role management...');
        const modal = document.getElementById('associationModal');
        const containerType = modal.dataset.containerType;
        console.log('Container type:', containerType);
        
        // Set up role input handlers
        const roleInputs = document.querySelectorAll('.role-input');
        console.log('Found', roleInputs.length, 'role inputs');
        
        roleInputs.forEach(input => {
            const elementType = input.dataset.elementType;
            const elementId = input.dataset.elementId;
            const prefix = elementType === 'character' ? 'char' : elementType === 'location' ? 'loc' : 'lore';
            const tagsContainer = document.getElementById(`${prefix}_tags_${elementId}`);
            const suggestionsContainer = document.getElementById(`${prefix}_suggestions_${elementId}`);
            
            // Only initialize empty roles if container doesn't already have roles
            const existingTags = tagsContainer.querySelectorAll('.role-tag');
            if (existingTags.length === 0) {
                const existingRoles = [];
                this.displayRoleTags(tagsContainer, existingRoles, input);
            }
            
            // Handle input events
            input.addEventListener('focus', async () => {
                const suggestions = await this.fetchRoleSuggestions(containerType, elementType);
                this.showRoleSuggestions(suggestionsContainer, suggestions, input, tagsContainer);
            });
            
            input.addEventListener('blur', (e) => {
                // Hide suggestions after a delay to allow clicking
                setTimeout(() => {
                    suggestionsContainer.style.display = 'none';
                }, 200);
            });
            
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ',') {
                    e.preventDefault();
                    const role = input.value.trim();
                    if (role) {
                        this.addRoleTag(tagsContainer, role, input);
                        input.value = '';
                    }
                }
            });
        });
    }
    
    async fetchRoleSuggestions(containerType, elementType) {
        try {
            const response = await fetch(`/api/v1/associations/roles/${containerType}/${elementType}`);
            if (!response.ok) throw new Error('Failed to fetch role suggestions');
            const data = await response.json();
            return data.predefined_roles || [];
        } catch (error) {
            console.error('Error fetching role suggestions:', error);
            return [];
        }
    }
    
    showRoleSuggestions(container, suggestions, input, tagsContainer) {
        const currentTags = Array.from(tagsContainer.querySelectorAll('.role-tag')).map(tag => 
            tag.textContent.replace('×', '').trim().toLowerCase()
        );
        
        // Filter out already selected roles
        const availableSuggestions = suggestions.filter(role => 
            !currentTags.includes(role.toLowerCase())
        );
        
        if (availableSuggestions.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.innerHTML = availableSuggestions.map(role => `
            <div class="role-suggestion-item" data-role="${role}">${role}</div>
        `).join('');
        
        container.style.display = 'block';
        
        // Add click handlers to suggestions
        container.querySelectorAll('.role-suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const role = item.dataset.role;
                this.addRoleTag(tagsContainer, role, input);
                input.value = '';
                container.style.display = 'none';
            });
        });
    }
    
    displayRoleTags(container, roles, input) {
        container.innerHTML = roles.map(role => this.createRoleTagHTML(role)).join('');
        this.attachTagRemoveHandlers(container, input);
    }
    
    addRoleTag(container, role, input) {
        const normalizedRole = role.trim().toLowerCase();
        
        // Check if already exists
        const existingTags = Array.from(container.querySelectorAll('.role-tag')).map(tag => 
            tag.textContent.replace('×', '').trim().toLowerCase()
        );
        
        if (existingTags.includes(normalizedRole)) {
            return;
        }
        
        // Add new tag
        const tagHtml = this.createRoleTagHTML(role);
        container.insertAdjacentHTML('beforeend', tagHtml);
        this.attachTagRemoveHandlers(container, input);
    }
    
    createRoleTagHTML(role) {
        return `
            <span class="role-tag">
                ${role}
                <span class="role-tag-remove" data-role="${role}">×</span>
            </span>
        `;
    }
    
    attachTagRemoveHandlers(container, input) {
        container.querySelectorAll('.role-tag-remove').forEach(removeBtn => {
            removeBtn.onclick = (e) => {
                e.stopPropagation();
                removeBtn.parentElement.remove();
            };
        });
    }
    
    showAssociationError(message) {
        ['characterAssociations', 'locationAssociations', 'loreItemAssociations'].forEach(id => {
            const container = document.getElementById(id);
            if (container) {
                container.innerHTML = `<div class="alert alert-warning">${message}</div>`;
            }
        });
    }
    
    async saveAssociations(containerType, containerId) {
        const modal = document.getElementById('associationModal');
        const saveBtn = document.getElementById('saveAssociationsBtn');
        const originalText = saveBtn.innerHTML;
        
        // Show saving state
        saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Saving...';
        saveBtn.disabled = true;
        
        try {
            const associations = this.collectAssociationData();
            const results = [];
            
            // Save each association
            for (const association of associations) {
                const { elementType, elementId, roles, notes } = association;
                
                const response = await fetch(`/api/v1/associations/${containerType}/${containerId}/${elementType}/${elementId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        roles: roles,
                        notes: notes
                    })
                });
                
                if (!response.ok) {
                    throw new Error(`Failed to save association for ${elementType} ${elementId}`);
                }
                
                results.push(await response.json());
            }
            
            // Close modal and refresh page
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();
            
            this.showToast('Associations saved successfully!', 'success');
            
            // Temporarily disable unsaved changes warning and reload
            this.temporarilyDisableUnsavedChangesWarning();
            setTimeout(() => {
                window.location.reload();
            }, 500);
            
        } catch (error) {
            console.error('Error saving associations:', error);
            this.showToast('Failed to save associations. Please try again.', 'error');
        } finally {
            // Restore button
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
    }
    
    collectAssociationData() {
        const associations = [];
        
        // Collect character associations
        document.querySelectorAll('#characterAssociations .association-item').forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {
                const elementId = checkbox.value;
                const tagsContainer = item.querySelector('.role-tags');
                const notesTextarea = document.getElementById(`char_notes_${elementId}`);
                const roles = Array.from(tagsContainer.querySelectorAll('.role-tag')).map(tag => 
                    tag.textContent.replace('×', '').trim()
                );
                const notes = notesTextarea ? notesTextarea.value.trim() : null;
                
                associations.push({
                    elementType: 'character',
                    elementId: elementId,
                    roles: roles,
                    notes: notes || null
                });
            }
        });
        
        // Collect location associations
        document.querySelectorAll('#locationAssociations .association-item').forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {
                const elementId = checkbox.value;
                const tagsContainer = item.querySelector('.role-tags');
                const notesTextarea = document.getElementById(`loc_notes_${elementId}`);
                const roles = Array.from(tagsContainer.querySelectorAll('.role-tag')).map(tag => 
                    tag.textContent.replace('×', '').trim()
                );
                const notes = notesTextarea ? notesTextarea.value.trim() : null;
                
                associations.push({
                    elementType: 'location',
                    elementId: elementId,
                    roles: roles,
                    notes: notes || null
                });
            }
        });
        
        // Collect lore item associations
        document.querySelectorAll('#loreItemAssociations .association-item').forEach(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            if (checkbox && checkbox.checked) {
                const elementId = checkbox.value;
                const tagsContainer = item.querySelector('.role-tags');
                const notesTextarea = document.getElementById(`lore_notes_${elementId}`);
                const roles = Array.from(tagsContainer.querySelectorAll('.role-tag')).map(tag => 
                    tag.textContent.replace('×', '').trim()
                );
                const notes = notesTextarea ? notesTextarea.value.trim() : null;
                
                associations.push({
                    elementType: 'lore_item',
                    elementId: elementId,
                    roles: roles,
                    notes: notes || null
                });
            }
        });
        
        return associations;
    }
    
    showToast(message, type = 'info') {
        // Create a simple toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }
    
    openElementAssociationModal(elementType, elementId) {
        alert(`Viewing associations for ${elementType} ${elementId} - Feature coming soon`);
    }
    
    editElementRoles(nodeType, nodeId) {
        // Only allow role editing for associated elements (characters, locations, lore_items)
        if (!['character', 'location', 'lore_item'].includes(nodeType)) {
            alert('Role editing is only available for characters, locations, and lore items.');
            return;
        }
        
        // Find the element in the hierarchy to get its current context
        const elementNode = document.querySelector(`[data-type="${nodeType}"][data-id="${nodeId}"]`);
        if (!elementNode) {
            alert('Could not find element in hierarchy.');
            return;
        }
        
        // Determine the parent container (story or act)
        const parentContainer = this.findParentContainer(elementNode);
        if (!parentContainer) {
            alert('Could not determine parent story or act for this element.');
            return;
        }
        
        this.openRoleEditModal(nodeType, nodeId, parentContainer.type, parentContainer.id);
    }
    
    findParentContainer(elementNode) {
        // Walk up the DOM to find the parent story or act
        let current = elementNode.parentElement;
        
        while (current) {
            // Look for a tree-node with story or act type
            const treeNode = current.querySelector('.tree-node[data-type="story"], .tree-node[data-type="act"]') ||
                            current.closest('.tree-node[data-type="story"], .tree-node[data-type="act"]');
            
            if (treeNode) {
                return {
                    type: treeNode.dataset.type,
                    id: treeNode.dataset.id
                };
            }
            
            current = current.parentElement;
        }
        
        return null;
    }
    
    openRoleEditModal(elementType, elementId, containerType, containerId) {
        // Use the existing modal from the HTML template
        const modal = document.getElementById('roleEditModal');
        
        // Store element and container info in modal
        modal.dataset.elementType = elementType;
        modal.dataset.elementId = elementId;
        modal.dataset.containerType = containerType;
        modal.dataset.containerId = containerId;
        
        // Update modal title
        const modalLabel = document.getElementById('roleEditModalLabel');
        const elementTypeName = elementType === 'lore_item' ? 'Lore Item' : elementType.charAt(0).toUpperCase() + elementType.slice(1);
        modalLabel.innerHTML = `<i class="fas fa-user-tag me-2"></i>Edit ${elementTypeName} Roles`;
        
        // Initialize Bootstrap modal
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        // Load current roles for this specific association
        this.loadElementRoles(elementType, elementId, containerType, containerId);
        
        // Set up save button
        const saveBtn = document.getElementById('saveRolesBtn');
        saveBtn.onclick = () => this.saveElementRoles(elementType, elementId, containerType, containerId);
    }
    
    createRoleEditModal(elementType, elementId, containerType, containerId) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'roleEditModal';
        modal.tabIndex = -1;
        modal.setAttribute('aria-labelledby', 'roleEditModalLabel');
        modal.setAttribute('aria-hidden', 'true');
        modal.setAttribute('data-element-type', elementType);
        modal.setAttribute('data-element-id', elementId);
        modal.setAttribute('data-container-type', containerType);
        modal.setAttribute('data-container-id', containerId);
        
        const elementTypeName = elementType === 'lore_item' ? 'Lore Item' : elementType.charAt(0).toUpperCase() + elementType.slice(1);
        
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="roleEditModalLabel">
                            <i class="fas fa-user-tag me-2"></i>Edit ${elementTypeName} Roles
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label class="form-label fw-bold">Element:</label>
                            <div id="elementInfo" class="text-muted">Loading...</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label fw-bold">Associated with:</label>
                            <div id="containerInfo" class="text-muted">Loading...</div>
                        </div>
                        <div class="mb-3">
                            <label for="roleInput" class="form-label fw-bold">Roles:</label>
                            <div id="roleTagsContainer" class="role-tags mb-2"></div>
                            <input type="text" 
                                   class="form-control" 
                                   id="roleInput" 
                                   placeholder="Add role (press Enter or comma to add)...">
                            <div id="roleSuggestions" class="role-suggestions" style="display: none;"></div>
                            <div class="form-text">Add roles to describe how this ${elementTypeName.toLowerCase()} is used in this ${containerType}.</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-1"></i>Cancel
                        </button>
                        <button type="button" class="btn btn-primary" onclick="hierarchyManager.saveElementRoles('${elementType}', ${elementId}, '${containerType}', ${containerId})">
                            <i class="fas fa-save me-1"></i>Save Roles
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    async loadElementRoles(elementType, elementId, containerType, containerId) {
        try {
            // Load element info
            const elementInfo = this.getElementInfoFromDOM(elementType, elementId);
            const elementInfoContainer = document.getElementById('roleEditElementInfo');
            elementInfoContainer.innerHTML = `<strong>${elementInfo.name}</strong><br><small class="text-muted">${elementType.charAt(0).toUpperCase() + elementType.slice(1)}</small>`;
            
            // Load existing association
            const response = await fetch(`/api/v1/associations/${containerType}/${containerId}/${elementType}/${elementId}`);
            
            let currentRoles = [];
            let currentNotes = '';
            if (response.ok) {
                const association = await response.json();
                currentRoles = association.roles || [];
                currentNotes = association.notes || '';
            }
            
            // Display current roles
            const tagsContainer = document.getElementById('roleTagsContainer');
            const roleInput = document.getElementById('roleInput');
            const notesTextarea = document.getElementById('roleNotes');
            
            this.displayRoleTags(tagsContainer, currentRoles, roleInput);
            if (notesTextarea) {
                notesTextarea.value = currentNotes;
            }
            
            // Set up role input functionality
            this.setupSingleRoleInput(containerType, elementType);
            
        } catch (error) {
            console.error('Error loading element roles:', error);
            const elementInfoContainer = document.getElementById('roleEditElementInfo');
            elementInfoContainer.innerHTML = '<span class="text-danger">Error loading element info</span>';
        }
    }
    
    getElementInfoFromDOM(elementType, elementId) {
        const element = document.querySelector(`[data-type="${elementType}"][data-id="${elementId}"] .node-title`);
        return {
            name: element ? element.textContent.trim() : `${elementType} ${elementId}`
        };
    }
    
    setupSingleRoleInput(containerType, elementType) {
        const roleInput = document.getElementById('roleInput');
        const tagsContainer = document.getElementById('roleTagsContainer');
        const suggestionsContainer = document.getElementById('roleSuggestions');
        
        // Clear any existing event listeners by cloning and replacing the element
        const newRoleInput = roleInput.cloneNode(true);
        roleInput.parentNode.replaceChild(newRoleInput, roleInput);
        
        // Handle input events on the new element
        newRoleInput.addEventListener('focus', async () => {
            const suggestions = await this.fetchRoleSuggestions(containerType, elementType);
            this.showRoleSuggestions(suggestionsContainer, suggestions, newRoleInput, tagsContainer);
        });
        
        newRoleInput.addEventListener('blur', (e) => {
            setTimeout(() => {
                suggestionsContainer.style.display = 'none';
            }, 200);
        });
        
        newRoleInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const role = newRoleInput.value.trim();
                if (role) {
                    this.addRoleTag(tagsContainer, role, newRoleInput);
                    newRoleInput.value = '';
                }
            }
        });
    }
    
    async saveElementRoles(elementType, elementId, containerType, containerId) {
        const modal = document.getElementById('roleEditModal');
        const saveButton = document.getElementById('saveRolesBtn');
        const originalText = saveButton.innerHTML;
        
        // Show saving state
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Saving...';
        saveButton.disabled = true;
        
        try {
            // Collect roles from tags
            const tagsContainer = document.getElementById('roleTagsContainer');
            const notesTextarea = document.getElementById('roleNotes');
            const roles = Array.from(tagsContainer.querySelectorAll('.role-tag')).map(tag => 
                tag.textContent.replace('×', '').trim()
            );
            const notes = notesTextarea ? notesTextarea.value.trim() : null;
            
            // Save the association
            const response = await fetch(`/api/v1/associations/${containerType}/${containerId}/${elementType}/${elementId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    roles: roles,
                    notes: notes || null
                })
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Failed to save roles: ${error}`);
            }
            
            // Close modal
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();
            
            // Temporarily disable unsaved changes warning and reload
            this.temporarilyDisableUnsavedChangesWarning();
            window.location.reload();
            
        } catch (error) {
            console.error('Error saving element roles:', error);
            this.showToast('Failed to save roles. Please try again.', 'error');
        } finally {
            // Restore button
            saveButton.innerHTML = originalText;
            saveButton.disabled = false;
        }
    }
    
    // === QUICK EDIT FORM ===
    
    async showQuickEditForm(nodeType, nodeId) {
        const quickEditContainer = document.getElementById('quick-edit-form');
        
        // Only show for editable elements
        const editableTypes = ['character', 'location', 'lore_item', 'story', 'act', 'scene'];
        
        if (!editableTypes.includes(nodeType)) {
            quickEditContainer.style.display = 'none';
            return;
        }
        
        // Show loading state
        quickEditContainer.innerHTML = this.createLoadingForm(nodeType);
        quickEditContainer.style.display = 'block';
        
        try {
            // Fetch element data from API
            const elementData = await this.fetchElementData(nodeType, nodeId);
            
            // Create quick edit form with real data
            quickEditContainer.innerHTML = this.createQuickEditForm(nodeType, nodeId, elementData);
            
            // Initialize tooltips for the newly created form
            this.initializeQuickEditTooltips(quickEditContainer);
        } catch (error) {
            console.error('Error loading element data:', error);
            quickEditContainer.innerHTML = this.createErrorForm(nodeType, 'Failed to load element data');
        }
    }
    
    async fetchElementData(nodeType, nodeId) {
        const endpoints = {
            'character': `/api/v1/characters/${nodeId}`,
            'location': `/api/v1/locations/${nodeId}`,
            'lore_item': `/api/v1/lore-items/${nodeId}`,
            'story': `/api/v1/stories/${nodeId}`,
            'act': `/api/v1/acts/${nodeId}`,
            'scene': `/api/v1/scenes/${nodeId}`
        };
        
        const endpoint = endpoints[nodeType];
        if (!endpoint) {
            throw new Error(`No API endpoint defined for type: ${nodeType}`);
        }
        
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${nodeType} data: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Normalize the data structure based on element type
        return this.normalizeElementData(nodeType, data);
    }
    
    normalizeElementData(nodeType, data) {
        let title, description, ai_summary = null;
        
        switch (nodeType) {
            case 'character':
            case 'location':
                title = data.name || '';
                description = data.description || '';
                break;
            case 'lore_item':
                title = data.title || '';
                description = data.content || '';
                break;
            case 'story':
                title = data.title || '';
                description = data.short_description || '';  // Writer's intent/summary
                ai_summary = data.ai_summary || null;
                break;
            case 'act':
                title = data.title || '';
                description = data.act_summary || '';  // Writer's intent/summary
                ai_summary = data.ai_summary || null;
                break;
            case 'scene':
                title = data.title || '';
                description = data.summary || '';  // Writer's intent/summary
                ai_summary = data.ai_summary || null;
                break;
            default:
                title = data.title || data.name || '';
                description = data.description || data.content || data.short_description || data.act_summary || data.summary || '';
        }
        
        return { title, description, ai_summary, rawData: data };
    }
    
    createLoadingForm(nodeType) {
        const typeDisplayName = this.getTypeDisplayName(nodeType);
        const iconClass = this.getTypeIconClass(nodeType);
        
        return `
            <div class="quick-edit-card">
                <div class="quick-edit-header">
                    <div class="quick-edit-icon ${iconClass}"></div>
                    Quick Edit ${typeDisplayName}
                </div>
                <div class="text-center py-3">
                    <div class="spinner-border spinner-border-sm me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    Loading ${typeDisplayName.toLowerCase()} data...
                </div>
            </div>
        `;
    }
    
    createErrorForm(nodeType, errorMessage) {
        const typeDisplayName = this.getTypeDisplayName(nodeType);
        const iconClass = this.getTypeIconClass(nodeType);
        
        return `
            <div class="quick-edit-card">
                <div class="quick-edit-header">
                    <div class="quick-edit-icon ${iconClass}"></div>
                    Quick Edit ${typeDisplayName}
                </div>
                <div class="text-center py-3 text-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${errorMessage}
                </div>
            </div>
        `;
    }
    
    getElementDataFromDOM(nodeType, nodeId) {
        // This method is now deprecated in favor of fetchElementData
        // Keeping for backward compatibility
        const element = document.querySelector(`[data-type="${nodeType}"][data-id="${nodeId}"]`);
        const titleElement = element ? element.querySelector('.node-title') : null;
        
        let title = '';
        let description = '';
        
        if (titleElement) {
            title = titleElement.textContent.trim();
            
            // Extract description from tooltip if available
            const headerElement = element.querySelector('.tree-node-header, .element-card');
            if (headerElement && headerElement.hasAttribute('title')) {
                description = headerElement.getAttribute('title');
            }
        }
        
        return { title, description };
    }
    
    createQuickEditForm(nodeType, nodeId, elementData) {
        const typeDisplayName = this.getTypeDisplayName(nodeType);
        const iconClass = this.getTypeIconClass(nodeType);
        
        // Determine field names, labels, and help text based on type
        let titleField = 'name';
        let titleLabel = 'Name';
        let titleHelpText = '';
        let descriptionLabel = 'Description';
        let descriptionPlaceholder = 'Brief description...';
        let descriptionHelpText = '';
        
        if (nodeType === 'story' || nodeType === 'act' || nodeType === 'scene') {
            titleField = 'title';
            titleLabel = 'Title';
            titleHelpText = `The main title for this ${nodeType}. Keep it descriptive and engaging for readers.`;
            descriptionLabel = 'Writer\'s Summary';
            descriptionPlaceholder = 'Your intent and summary for this ' + nodeType.toLowerCase() + '...';
            descriptionHelpText = `Your personal notes and intent for this ${nodeType}. This helps guide AI assistance and maintains your creative vision.`;
        } else if (nodeType === 'lore_item') {
            titleField = 'title';
            titleLabel = 'Title';
            titleHelpText = 'The name or title of this lore item. This should be clear and descriptive.';
            descriptionLabel = 'Content';
            descriptionPlaceholder = 'Brief content overview...';
            descriptionHelpText = 'A summary of this lore item\'s content, significance, or role in your world.';
        } else if (nodeType === 'character') {
            titleHelpText = 'The character\'s full name or primary identifier.';
            descriptionHelpText = 'Key details about this character\'s appearance, personality, background, and role in your world.';
        } else if (nodeType === 'location') {
            titleHelpText = 'The name of this location as it appears in your world.';
            descriptionHelpText = 'Important details about this location\'s appearance, atmosphere, significance, and role in your stories.';
        }
        
        return `
            <div class="quick-edit-card">
                <div class="quick-edit-header">
                    <div class="quick-edit-icon ${iconClass}"></div>
                    Quick Edit ${typeDisplayName}
                    <i class="fas fa-question-circle text-muted ms-auto" 
                       data-bs-toggle="tooltip" data-bs-placement="top"
                       title="Make quick edits to this ${nodeType}'s basic information. Changes will be saved immediately to your world."></i>
                </div>
                <form id="quickEditForm" onsubmit="return false;">
                    <input type="hidden" id="quickEditType" value="${nodeType}">
                    <input type="hidden" id="quickEditId" value="${nodeId}">
                    
                    <div class="quick-edit-form-group">
                        <label class="quick-edit-label" for="quickEditTitle">
                            ${titleLabel}:
                            <i class="fas fa-question-circle text-muted" 
                               data-bs-toggle="tooltip" data-bs-placement="top"
                               title="${titleHelpText}"></i>
                        </label>
                        <input type="text" 
                               id="quickEditTitle" 
                               name="${titleField}"
                               class="quick-edit-input" 
                               value="${this.escapeHtml(elementData.title)}"
                               maxlength="200">
                    </div>
                    
                    <div class="quick-edit-form-group">
                        <label class="quick-edit-label" for="quickEditDescription">
                            ${descriptionLabel}:
                            <i class="fas fa-question-circle text-muted" 
                               data-bs-toggle="tooltip" data-bs-placement="top"
                               title="${descriptionHelpText}"></i>
                        </label>
                        <textarea id="quickEditDescription" 
                                  name="description"
                                  class="quick-edit-input quick-edit-textarea" 
                                  maxlength="1000"
                                  placeholder="${descriptionPlaceholder}">${this.escapeHtml(elementData.description)}</textarea>
                    </div>
                    
                    ${(nodeType === 'story' || nodeType === 'act' || nodeType === 'scene') ? `
                    <div class="quick-edit-form-group">
                        <label class="quick-edit-label" for="quickEditAiSummary">
                            AI Summary:
                            <i class="fas fa-question-circle text-muted" 
                               data-bs-toggle="tooltip" data-bs-placement="top"
                               title="This field shows the AI-generated summary based on your content. It's automatically updated and cannot be directly edited."></i>
                        </label>
                        <textarea id="quickEditAiSummary" 
                                  name="ai_summary"
                                  class="quick-edit-input quick-edit-textarea" 
                                  maxlength="1000"
                                  placeholder="AI-generated summary..."
                                  readonly
                                  style="background-color: var(--tblr-bg-surface-secondary); cursor: not-allowed;">${this.escapeHtml(elementData.ai_summary || '')}</textarea>
                    </div>
                    ` : ''}
                    
                    <button type="button" 
                            class="quick-edit-save-btn" 
                            onclick="hierarchyManager.saveQuickEdit()"
                            data-bs-toggle="tooltip" data-bs-placement="top"
                            title="Save changes to this ${nodeType} and update the hierarchy view">
                        <i class="fas fa-save me-1"></i>Save Changes
                    </button>
                </form>
            </div>
        `;
    }
    
    initializeQuickEditTooltips(container) {
        // Initialize Bootstrap tooltips for all elements with data-bs-toggle="tooltip" in the form
        const tooltipElements = container.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipElements.forEach(element => {
            new bootstrap.Tooltip(element);
        });
    }
    
    getTypeDisplayName(nodeType) {
        const displayNames = {
            'character': 'Character',
            'location': 'Location',
            'lore_item': 'Lore Item',
            'story': 'Story',
            'act': 'Act',
            'scene': 'Scene'
        };
        return displayNames[nodeType] || nodeType;
    }
    
    getTypeIconClass(nodeType) {
        const iconClasses = {
            'character': 'default-character',
            'location': 'default-location',
            'lore_item': 'default-lore',
            'story': 'default-story',
            'act': 'default-act',
            'scene': 'default-scene'
        };
        return iconClasses[nodeType] || '';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text || '';
        return div.innerHTML;
    }
    
    async saveQuickEdit() {
        const form = document.getElementById('quickEditForm');
        const saveButton = form.querySelector('.quick-edit-save-btn');
        const originalText = saveButton.innerHTML;
        
        // Get form data
        const nodeType = document.getElementById('quickEditType').value;
        const nodeId = document.getElementById('quickEditId').value;
        const title = document.getElementById('quickEditTitle').value.trim();
        const description = document.getElementById('quickEditDescription').value.trim();
        
        // Get AI summary if it exists (only for story, act, scene)
        let aiSummary = null;
        const aiSummaryField = document.getElementById('quickEditAiSummary');
        if (aiSummaryField) {
            aiSummary = aiSummaryField.value.trim();
        }
        
        if (!title) {
            this.showToast('Title is required', 'error');
            return;
        }
        
        // Show saving state
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';
        saveButton.disabled = true;
        saveButton.classList.add('quick-edit-saving');
        
        try {
            // Determine API endpoint and field names
            const { endpoint, payload } = this.getQuickEditApiData(nodeType, nodeId, title, description, aiSummary);
            
            const response = await fetch(endpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Failed to save: ${error}`);
            }
            
            // Show success
            this.showToast('Changes saved successfully!', 'success');
            
            // Update the DOM to reflect changes
            this.updateElementInDOM(nodeType, nodeId, title, description);
            
        } catch (error) {
            console.error('Error saving quick edit:', error);
            this.showToast('Failed to save changes. Please try again.', 'error');
        } finally {
            // Restore button
            saveButton.innerHTML = originalText;
            saveButton.disabled = false;
            saveButton.classList.remove('quick-edit-saving');
        }
    }
    
    getQuickEditApiData(nodeType, nodeId, title, description, aiSummary = null) {
        let endpoint, payload;
        
        switch (nodeType) {
            case 'character':
                endpoint = `/api/v1/characters/${nodeId}`;
                payload = { name: title, description: description };
                break;
            case 'location':
                endpoint = `/api/v1/locations/${nodeId}`;
                payload = { name: title, description: description };
                break;
            case 'lore_item':
                endpoint = `/api/v1/lore-items/${nodeId}`;
                payload = { title: title, content: description };
                break;
            case 'story':
                endpoint = `/api/v1/stories/${nodeId}`;
                payload = { title: title, short_description: description };  // Writer's intent/summary
                if (aiSummary !== null) {
                    payload.ai_summary = aiSummary;
                }
                break;
            case 'act':
                endpoint = `/api/v1/acts/${nodeId}`;
                payload = { title: title, act_summary: description };  // Writer's intent/summary
                if (aiSummary !== null) {
                    payload.ai_summary = aiSummary;
                }
                break;
            case 'scene':
                endpoint = `/api/v1/scenes/${nodeId}`;
                payload = { title: title, summary: description };  // Writer's intent/summary
                if (aiSummary !== null) {
                    payload.ai_summary = aiSummary;
                }
                break;
            default:
                throw new Error(`Unsupported element type: ${nodeType}`);
        }
        
        return { endpoint, payload };
    }
    
    updateElementInDOM(nodeType, nodeId, title, description) {
        // Update the title in the hierarchy
        const element = document.querySelector(`[data-type="${nodeType}"][data-id="${nodeId}"]`);
        if (element) {
            const titleElement = element.querySelector('.node-title, .element-card-title');
            if (titleElement) {
                titleElement.textContent = title;
            }
            
            // Update tooltip with new description
            const tooltipElement = element.querySelector('.tree-node-header, .element-card');
            if (tooltipElement && description) {
                tooltipElement.setAttribute('title', description);
                // Reinitialize tooltip
                const tooltip = bootstrap.Tooltip.getInstance(tooltipElement);
                if (tooltip) {
                    tooltip.dispose();
                    new bootstrap.Tooltip(tooltipElement);
                }
            }
        }
    }
    
    async saveAssociations(containerType, containerId) {
        const modal = document.getElementById('associationModal');
        const saveButton = modal.querySelector('.btn-primary');
        const originalText = saveButton.innerHTML;
        
        // Show saving state
        saveButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Saving...';
        saveButton.disabled = true;
        
        try {
            // Collect all checked associations
            const associations = {
                characters: this.collectElementAssociations('char'),
                locations: this.collectElementAssociations('loc'),
                loreItems: this.collectElementAssociations('lore')
            };
            
            console.log('Saving associations:', associations);
            
            // Save each type of association
            const promises = [];
            
            // Save character associations
            associations.characters.forEach(assoc => {
                promises.push(this.saveElementAssociation(containerType, containerId, 'character', assoc.id, assoc.roles));
            });
            
            // Save location associations
            associations.locations.forEach(assoc => {
                promises.push(this.saveElementAssociation(containerType, containerId, 'location', assoc.id, assoc.roles));
            });
            
            // Save lore item associations
            associations.loreItems.forEach(assoc => {
                promises.push(this.saveElementAssociation(containerType, containerId, 'lore_item', assoc.id, assoc.roles));
            });
            
            await Promise.all(promises);
            
            // Close modal and refresh tree
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            bootstrapModal.hide();
            
            // Show success message
            this.showToast('Associations saved successfully!', 'success');
            
            // Temporarily disable unsaved changes warning and reload
            this.temporarilyDisableUnsavedChangesWarning();
            setTimeout(() => {
                window.location.reload();
            }, 500);
            
        } catch (error) {
            console.error('Error saving associations:', error);
            this.showToast('Failed to save associations. Please try again.', 'error');
        } finally {
            // Restore button
            saveButton.innerHTML = originalText;
            saveButton.disabled = false;
        }
    }
    
    collectElementAssociations(prefix) {
        const associations = [];
        const checkboxes = document.querySelectorAll(`input[type="checkbox"][id^="${prefix}_"]:checked`);
        
        checkboxes.forEach(checkbox => {
            const elementId = checkbox.value;
            const tagsContainer = document.getElementById(`${prefix}_tags_${elementId}`);
            
            // Collect roles from tags
            const roles = Array.from(tagsContainer.querySelectorAll('.role-tag')).map(tag => 
                tag.textContent.replace('×', '').trim()
            );
            
            // Include the association even if no roles are specified
            associations.push({
                id: parseInt(elementId),
                roles: roles
            });
        });
        
        return associations;
    }
    
    async saveElementAssociation(containerType, containerId, elementType, elementId, roles) {
        const response = await fetch(`/api/v1/associations/${containerType}/${containerId}/${elementType}/${elementId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roles: roles,
                notes: null
            })
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Failed to save ${elementType} association: ${error}`);
        }
        
        return response.json();
    }
    
    async showTabbedDetails(elementType, elementId) {
        try {
            // Fetch element data from API
            let endpoint, elementData;
            if (elementType === 'act') {
                endpoint = `/api/v1/acts/${elementId}`;
            } else if (elementType === 'scene') {
                endpoint = `/api/v1/scenes/${elementId}`;
            }
            
            const response = await fetch(endpoint);
            if (!response.ok) {
                throw new Error(`Failed to fetch ${elementType} data`);
            }
            
            elementData = await response.json();
            
            // Hide regular details and show tabbed interface
            document.querySelector('.details-empty').style.display = 'none';
            const tabbedDetails = document.getElementById('tabbed-details');
            tabbedDetails.style.display = 'block';
            
            // Update title
            const title = elementType === 'act' ? `Act ${elementData.act_number}: ${elementData.title}` 
                                                : `Scene ${elementData.scene_number}: ${elementData.title}`;
            document.getElementById('details-title').textContent = title;
            
            // Action buttons are no longer used since we simplified the interface
            
            // Skip populating info panel since it's hidden for acts and scenes
            
            // Load content into editor immediately since only content tab is shown
            if (window.contentEditor) {
                window.contentEditor.loadContent(elementType, elementId, elementData);
            }
            
        } catch (error) {
            console.error('Error loading tabbed details:', error);
            this.showToast('Failed to load element details', 'error');
        }
    }
    
    createElementInfoHtml(elementType, elementData) {
        let html = `
            <div class="mb-3">
                <strong>Title:</strong> ${elementData.title || 'Untitled'}
            </div>
        `;
        
        if (elementType === 'act') {
            html += `
                <div class="mb-3">
                    <strong>Act Number:</strong> ${elementData.act_number || 'N/A'}
                </div>
                <div class="mb-3">
                    <strong>Writer's Summary:</strong>
                    <div class="text-muted small">${elementData.act_summary || 'No summary provided'}</div>
                </div>
                <div class="mb-3">
                    <strong>AI Summary:</strong>
                    <div class="text-muted small">${elementData.ai_summary || 'No AI summary available'}</div>
                </div>
                <div class="mb-3">
                    <strong>Writer's Notes:</strong>
                    <div class="text-muted small">${elementData.writer_notes || 'No notes'}</div>
                </div>
            `;
        } else if (elementType === 'scene') {
            html += `
                <div class="mb-3">
                    <strong>Scene Number:</strong> ${elementData.scene_number || 'N/A'}
                </div>
                <div class="mb-3">
                    <strong>Writer's Summary:</strong>
                    <div class="text-muted small">${elementData.summary || 'No summary provided'}</div>
                </div>
                <div class="mb-3">
                    <strong>AI Summary:</strong>
                    <div class="text-muted small">${elementData.ai_summary || 'No AI summary available'}</div>
                </div>
                <div class="mb-3">
                    <strong>Word Count:</strong> ${elementData.word_count || 0} words
                </div>
            `;
        }
        
        if (elementData.created_at) {
            html += `
                <div class="mb-3">
                    <strong>Created:</strong> ${new Date(elementData.created_at).toLocaleString()}
                </div>
            `;
        }
        
        if (elementData.updated_at) {
            html += `
                <div class="mb-3">
                    <strong>Last Updated:</strong> ${new Date(elementData.updated_at).toLocaleString()}
                </div>
            `;
        }
        
        return html;
    }
    
    clearAllDetails() {
        // Hide tabbed details interface
        const tabbedDetails = document.getElementById('tabbed-details');
        if (tabbedDetails) {
            tabbedDetails.style.display = 'none';
        }
        
        // Clear action buttons
        const actionsContainer = document.getElementById('element-actions');
        if (actionsContainer) {
            actionsContainer.style.display = 'none';
            actionsContainer.innerHTML = '';
        }
        
        // Show empty state
        const emptyDetails = document.querySelector('.details-empty');
        if (emptyDetails) {
            emptyDetails.style.display = 'block';
        }
        
        // Clear content editor if it exists
        if (window.contentEditor) {
            window.contentEditor.clearEditor();
        }
        
        // Reset tabs to content tab (which is now first)
        const contentTab = document.getElementById('content-tab');
        if (contentTab) {
            contentTab.click();
        }
    }
    
    showToast(message, type = 'info') {
        // Create and show a Bootstrap toast
        const toastContainer = document.querySelector('.toast-container') || document.body;
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bootstrapToast = new bootstrap.Toast(toast);
        bootstrapToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toastContainer.removeChild(toast);
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing WorldHierarchyManager');
    window.hierarchyManager = new WorldHierarchyManager();
    console.log('WorldHierarchyManager initialized');
});