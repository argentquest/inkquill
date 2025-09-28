// Image Generation Modal Module
// This module provides easy integration of the image generation modal

class ImageGenerationModalManager {
    constructor() {
        this.modal = null;
        this.initialized = false;
    }

    // Initialize the modal manager
    init() {
        if (this.initialized) return;
        
        // Check if modal HTML is already in the page
        if (!document.getElementById('imageGenerationModal')) {
            console.error('Image generation modal HTML not found. Please include the partial template.');
            return;
        }
        
        this.initialized = true;
        console.log('Image Generation Modal Manager initialized');
    }

    // Show the modal for a specific entity
    showModal(entityType, entityId, defaultPrompt = '', callback = null) {
        this.init();
        
        if (!this.initialized) {
            console.error('Modal manager not initialized');
            return;
        }

        // Initialize and show the modal
        window.imageGenerationModal = new ImageGenerationModal(
            entityType,
            entityId,
            defaultPrompt,
            callback
        );
        
        window.imageGenerationModal.show();
    }

    // Helper method for story entities
    showForStory(storyId, defaultPrompt = '', callback = null) {
        this.showModal('story', storyId, defaultPrompt, callback);
    }

    // Helper method for act entities
    showForAct(actId, defaultPrompt = '', callback = null) {
        this.showModal('act', actId, defaultPrompt, callback);
    }

    // Helper method for scene entities
    showForScene(sceneId, defaultPrompt = '', callback = null) {
        this.showModal('scene', sceneId, defaultPrompt, callback);
    }

    // Helper method for character entities
    showForCharacter(characterId, defaultPrompt = '', callback = null) {
        this.showModal('character', characterId, defaultPrompt, callback);
    }

    // Helper method for location entities
    showForLocation(locationId, defaultPrompt = '', callback = null) {
        this.showModal('location', locationId, defaultPrompt, callback);
    }

    // Helper method for lore item entities
    showForLoreItem(loreItemId, defaultPrompt = '', callback = null) {
        this.showModal('lore_item', loreItemId, defaultPrompt, callback);
    }
}

// Create global instance
window.imageGenerationModalManager = new ImageGenerationModalManager();

// Convenience functions for easy integration
window.showImageGenerationModal = function(entityType, entityId, defaultPrompt = '', callback = null) {
    window.imageGenerationModalManager.showModal(entityType, entityId, defaultPrompt, callback);
};

window.showStoryImageModal = function(storyId, defaultPrompt = '', callback = null) {
    window.imageGenerationModalManager.showForStory(storyId, defaultPrompt, callback);
};

window.showActImageModal = function(actId, defaultPrompt = '', callback = null) {
    window.imageGenerationModalManager.showForAct(actId, defaultPrompt, callback);
};

window.showSceneImageModal = function(sceneId, defaultPrompt = '', callback = null) {
    window.imageGenerationModalManager.showForScene(sceneId, defaultPrompt, callback);
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageGenerationModalManager;
}