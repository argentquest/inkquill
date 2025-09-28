// /ai_rag_story_app/app/static/js/world_chat_context_loader.js
"use strict";

const WorldChatContextLoader = (() => {
    const API_BASE_URL = "/api/v1/world-chat";
    
    let worldId = null;
    let callbacks = {};
    let worldContext = null;
    
    function init(worldIdParam, callbacksParam) {
        worldId = worldIdParam;
        callbacks = callbacksParam || {};
        setupElementListeners();
    }
    
    function setupElementListeners() {
        // Set up click listeners for element lists
        const charactersList = document.getElementById('characters-list');
        const locationsList = document.getElementById('locations-list');
        const loreList = document.getElementById('lore-list');
        
        if (charactersList) {
            charactersList.addEventListener('click', (e) => handleElementClick(e, 'character'));
        }
        if (locationsList) {
            locationsList.addEventListener('click', (e) => handleElementClick(e, 'location'));
        }
        if (loreList) {
            loreList.addEventListener('click', (e) => handleElementClick(e, 'lore_item'));
        }
    }
    
    async function loadWorldContext() {
        try {
            const response = await fetch(`${API_BASE_URL}/world-context/${worldId}`, {
                credentials: 'include'
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            worldContext = await response.json();
            
            if (callbacks.onContextLoaded) {
                callbacks.onContextLoaded(worldContext);
            }
            
            populateElementLists();
            displayWorldImage();
            
        } catch (error) {
            console.error("ContextLoader: Error loading world context:", error);
            if (callbacks.onError) callbacks.onError("Failed to load world context");
        }
    }
    
    function populateElementLists() {
        if (!worldContext) return;
        
        populateCharactersList(worldContext.characters);
        populateLocationsList(worldContext.locations);
        populateLoreList(worldContext.lore_items);
    }
    
    function populateCharactersList(characters) {
        const list = document.getElementById('characters-list');
        if (!list) return;
        
        if (!characters || characters.length === 0) {
            list.innerHTML = '<div class="text-muted small">No characters found</div>';
            return;
        }
        
        const items = characters.map(character => {
            const description = character.description || 'No description available';
            const truncatedDescription = description.length > 100 ? description.substring(0, 100) + '...' : description;
            
            const imageHtml = character.image_url 
                ? `<img src="${escapeHtml(character.image_url)}" alt="${escapeHtml(character.name || 'Character')}" class="element-list-img">`
                : `<div class="element-list-icon"><i class="fas fa-user-secret text-secondary"></i></div>`;
            
            return `
                <div class="element-item d-flex align-items-start" data-element-id="${character.id}" data-element-type="character">
                    <div class="element-thumbnail me-3 flex-shrink-0">
                        ${imageHtml}
                    </div>
                    <div class="element-content flex-grow-1 min-width-0">
                        <div class="element-item-name">${escapeHtml(character.name || 'Unnamed Character')}</div>
                        <div class="element-item-type text-muted small">${escapeHtml(truncatedDescription)}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        list.innerHTML = items;
    }
    
    function populateLocationsList(locations) {
        const list = document.getElementById('locations-list');
        if (!list) return;
        
        if (!locations || locations.length === 0) {
            list.innerHTML = '<div class="text-muted small">No locations found</div>';
            return;
        }
        
        const items = locations.map(location => {
            const description = location.description || 'No description available';
            const truncatedDescription = description.length > 100 ? description.substring(0, 100) + '...' : description;
            
            const imageHtml = location.image_url 
                ? `<img src="${escapeHtml(location.image_url)}" alt="${escapeHtml(location.name || 'Location')}" class="element-list-img">`
                : `<div class="element-list-icon"><i class="fas fa-map-marked-alt text-secondary"></i></div>`;
            
            return `
                <div class="element-item d-flex align-items-start" data-element-id="${location.id}" data-element-type="location">
                    <div class="element-thumbnail me-3 flex-shrink-0">
                        ${imageHtml}
                    </div>
                    <div class="element-content flex-grow-1 min-width-0">
                        <div class="element-item-name">${escapeHtml(location.name || 'Unnamed Location')}</div>
                        <div class="element-item-type text-muted small">${escapeHtml(truncatedDescription)}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        list.innerHTML = items;
    }
    
    function populateLoreList(loreItems) {
        const list = document.getElementById('lore-list');
        if (!list) return;
        
        if (!loreItems || loreItems.length === 0) {
            list.innerHTML = '<div class="text-muted small">No lore items found</div>';
            return;
        }
        
        const items = loreItems.map(lore => {
            const description = lore.description || 'No description available';
            const truncatedDescription = description.length > 100 ? description.substring(0, 100) + '...' : description;
            
            const imageHtml = lore.image_url 
                ? `<img src="${escapeHtml(lore.image_url)}" alt="${escapeHtml(lore.title || 'Lore Item')}" class="element-list-img">`
                : `<div class="element-list-icon"><i class="fas fa-scroll text-secondary"></i></div>`;
            
            return `
                <div class="element-item d-flex align-items-start" data-element-id="${lore.id}" data-element-type="lore_item">
                    <div class="element-thumbnail me-3 flex-shrink-0">
                        ${imageHtml}
                    </div>
                    <div class="element-content flex-grow-1 min-width-0">
                        <div class="element-item-name">${escapeHtml(lore.title || 'Untitled Lore')}</div>
                        <div class="element-item-type text-muted small">${escapeHtml(truncatedDescription)}</div>
                    </div>
                </div>
            `;
        }).join('');
        
        list.innerHTML = items;
    }
    
    function handleElementClick(event, elementType) {
        const elementItem = event.target.closest('.element-item');
        if (!elementItem) return;
        
        // Clear previous selections
        document.querySelectorAll('.element-item.selected').forEach(item => {
            item.classList.remove('selected');
        });
        
        // Select clicked item
        elementItem.classList.add('selected');
        
        const elementId = parseInt(elementItem.dataset.elementId);
        const elementData = getElementData(elementType, elementId);
        
        if (callbacks.onElementSelected) {
            callbacks.onElementSelected(elementType, elementId, elementData);
        }
        
        console.log(`Selected ${elementType}:`, elementId, elementData);
    }
    
    function getElementData(elementType, elementId) {
        if (!worldContext) return null;
        
        let collection;
        switch (elementType) {
            case 'character':
                collection = worldContext.characters;
                break;
            case 'location':
                collection = worldContext.locations;
                break;
            case 'lore_item':
                collection = worldContext.lore_items;
                break;
            default:
                return null;
        }
        
        return collection.find(item => item.id === elementId);
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function displayWorldImage() {
        const worldImageCard = document.getElementById('world-image-card');
        const worldImage = document.getElementById('world-image');
        
        if (!worldImageCard || !worldImage || !worldContext || !worldContext.world) {
            return;
        }
        
        // Check if world has an image URL
        const imageUrl = worldContext.world.image_url;
        if (imageUrl) {
            worldImage.src = imageUrl;
            worldImage.alt = worldContext.world.name || 'World Image';
            worldImageCard.style.display = 'block';
            console.log('World image displayed:', imageUrl);
        } else {
            worldImageCard.style.display = 'none';
            console.log('No world image available');
        }
    }
    
    return {
        init,
        loadWorldContext,
        getWorldContext: () => worldContext
    };
})();