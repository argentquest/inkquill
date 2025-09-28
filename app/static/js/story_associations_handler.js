// /ai_rag_story_app/app/static/js/story_associations_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("StoryAssociationsHandler: Initializing (v.syntax_fix)");

    const storyIdElement = document.getElementById('story-id-for-associations');
    const worldIdElement = document.getElementById('world-id-for-associations');

    if (!storyIdElement || !storyIdElement.value) {
        console.error("StoryAssociationsHandler: CRITICAL - Story ID element not found or empty.");
        return;
    }

    const STORY_ID = storyIdElement.value;
    const WORLD_ID = worldIdElement ? worldIdElement.value : null;
    const API_BASE_URL = "/api/v1";

    if (!WORLD_ID) {
        console.warn("StoryAssociationsHandler: WARNING - No WORLD_ID found. Linking features disabled.");
    }

    const elementTypesConfig = {
        character: {
            listContainerId: 'linked-characters-list',
            noElementsMessageClass: 'no-linked-elements-message-char',
            modalId: 'linkCharacterModal',
            selectId: 'select-world-character',
            roleInputId: 'character-role-in-story',
            linkButtonId: 'confirm-link-character-btn',
            fetchWorldElementsUrl: WORLD_ID ? `${API_BASE_URL}/worlds/${WORLD_ID}/characters` : null,
            fetchLinkedElementsUrl: `${API_BASE_URL}/stories/${STORY_ID}/characters`,
            linkApiUrl: `${API_BASE_URL}/stories/${STORY_ID}/characters`,
            unlinkApiUrlBase: `${API_BASE_URL}/stories/${STORY_ID}/characters`,
            idField: 'character_id', nameField: 'name', roleField: 'role_in_story', linkedElementName: 'character', iconClass: 'fa-user-secret'
        },
        location: {
            listContainerId: 'linked-locations-list',
            noElementsMessageClass: 'no-linked-elements-message-loc',
            modalId: 'linkLocationModal',
            selectId: 'select-world-location',
            roleInputId: 'location-significance-to-story',
            linkButtonId: 'confirm-link-location-btn',
            fetchWorldElementsUrl: WORLD_ID ? `${API_BASE_URL}/worlds/${WORLD_ID}/locations` : null,
            fetchLinkedElementsUrl: `${API_BASE_URL}/stories/${STORY_ID}/locations`,
            linkApiUrl: `${API_BASE_URL}/stories/${STORY_ID}/locations`,
            unlinkApiUrlBase: `${API_BASE_URL}/stories/${STORY_ID}/locations`,
            idField: 'location_id', nameField: 'name', roleField: 'significance_to_story', linkedElementName: 'location', iconClass: 'fa-map-marked-alt'
        },
        lore_item: {
            listContainerId: 'linked-lore-items-list',
            noElementsMessageClass: 'no-linked-elements-message-lore',
            modalId: 'linkLoreItemModal',
            selectId: 'select-world-lore-item',
            roleInputId: 'lore-item-relevance-to-story',
            linkButtonId: 'confirm-link-lore-item-btn',
            fetchWorldElementsUrl: WORLD_ID ? `${API_BASE_URL}/worlds/${WORLD_ID}/lore-items` : null,
            fetchLinkedElementsUrl: `${API_BASE_URL}/stories/${STORY_ID}/lore-items`,
            linkApiUrl: `${API_BASE_URL}/stories/${STORY_ID}/lore-items`,
            unlinkApiUrlBase: `${API_BASE_URL}/stories/${STORY_ID}/lore-items`,
            idField: 'lore_item_id', nameField: 'title', roleField: 'relevance_to_story', linkedElementName: 'lore item', iconClass: 'fa-scroll'
        }
    };

    // --- FIX: Using the correct escapeHtml function ---
    function escapeHtml(unsafe) {
        if (unsafe === null || typeof unsafe === 'undefined') return '';
        return String(unsafe)
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
    // --- END FIX ---

    async function fetchData(url, errorMessagePrefix) {
        if (!url) {
            console.warn(`StoryAssociationsHandler: FetchData: URL is null for ${errorMessagePrefix}.`);
            return null;
        }
        try {
            const response = await fetch(url, { credentials: 'include' });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const detail = errorData.detail || response.statusText;
                if (typeof showToast === 'function') showToast(`${errorMessagePrefix}: ${detail}`, "error");
                return null;
            }
            return await response.json();
        } catch (error) {
            console.error(`StoryAssociationsHandler: Network error during fetchData for ${errorMessagePrefix}:`, error);
            if (typeof showToast === 'function') showToast(`Network error fetching data.`, "error");
            return null;
        }
    }

    async function loadCharacterRoles() {
        try {
            const response = await fetch('/api/v1/prompts/character-roles', { credentials: 'include' });
            if (!response.ok) {
                console.warn('Failed to load character roles:', response.statusText);
                return [];
            }
            return await response.json();
        } catch (error) {
            console.error('Error loading character roles:', error);
            return [];
        }
    }

    async function populateCharacterRoleSelect() {
        const roleSelect = document.getElementById('character-role-in-story');
        const roleDescription = document.getElementById('role-description');
        
        if (!roleSelect) return;
        
        // Clear existing options except the first one
        while (roleSelect.children.length > 1) {
            roleSelect.removeChild(roleSelect.lastChild);
        }
        
        const roles = await loadCharacterRoles();
        
        roles.forEach(role => {
            const option = document.createElement('option');
            option.value = role.title;
            option.textContent = role.title;
            option.dataset.description = role.reason_to_use || '';
            roleSelect.appendChild(option);
        });
        
        // Add event listener to show role description
        roleSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption && selectedOption.dataset.description) {
                roleDescription.textContent = selectedOption.dataset.description;
                roleDescription.style.display = 'block';
            } else {
                roleDescription.style.display = 'none';
            }
        });
    }

    async function populateWorldElementSelect(elementType) {
        const config = elementTypesConfig[elementType];
        const selectElement = document.getElementById(config.selectId);
        if (!selectElement) return;

        if (!config.fetchWorldElementsUrl) {
            selectElement.innerHTML = `<option value="">-- No world assigned --</option>`;
            selectElement.disabled = false;
            return;
        }

        selectElement.innerHTML = `<option value="">Loading...</option>`;
        selectElement.disabled = true;

        const worldElements = await fetchData(config.fetchWorldElementsUrl, `Failed to fetch ${elementType}s`);
        
        selectElement.innerHTML = `<option value="">-- Select a ${config.linkedElementName} --</option>`;
        if (worldElements && worldElements.length > 0) {
            worldElements.forEach(element => {
                const option = document.createElement('option');
                option.value = element.id;
                option.textContent = `${escapeHtml(element[config.nameField])} (ID: ${element.id})`;
                selectElement.appendChild(option);
            });
            selectElement.disabled = false;
        } else {
            selectElement.innerHTML = `<option value="">-- No ${config.linkedElementName}s found --</option>`;
            selectElement.disabled = false;
        }
    }

    function renderLinkedElements(elementType, linkedElements) {
        const config = elementTypesConfig[elementType];
        const listContainer = document.getElementById(config.listContainerId);
        const noElementsMsgElement = listContainer ? listContainer.querySelector(`.${config.noElementsMessageClass}`) : null;

        if (!listContainer) return;
        
        listContainer.querySelectorAll('.list-group-item:not(.' + config.noElementsMessageClass + ')').forEach(item => item.remove());

        if (linkedElements && linkedElements.length > 0) {
            if (noElementsMsgElement) noElementsMsgElement.style.display = 'none';
            linkedElements.forEach(item => {
                const elementName = escapeHtml(item[config.nameField] || `Unnamed`);
                const roleText = escapeHtml(item[config.roleField] || 'N/A');
                
                let imageHtml = '';
                if (item.image_url) {
                    imageHtml = `<img src="${item.image_url}" alt="${elementName}" class="element-list-img">`;
                } else {
                    imageHtml = `<div class="element-list-icon"><i class="fas ${config.iconClass} text-secondary"></i></div>`;
                }
                
                let editUrl = `/ui/worlds/${elementType}s/${item.id}/edit`;
                if (elementType === 'lore_item') {
                     editUrl = `/ui/worlds/lore-items/${item.id}/edit`;
                } else if (elementType === 'character') {
                    editUrl = `/ui/worlds/characters/${item.id}/edit`;
                } else if (elementType === 'location') {
                    editUrl = `/ui/worlds/locations/${item.id}/edit`;
                }
                
                let locationInfo = '';
                if ((elementType === 'character' || elementType === 'lore_item') && item.current_location) {
                    const locationName = escapeHtml(item.current_location.name || 'Unknown Location');
                    locationInfo = `<small class="text-muted d-block"><i class="fas fa-map-marker-alt me-1"></i>Located at: ${locationName}</small>`;
                }
                
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-start';
                li.dataset.elementId = item.id;
                li.innerHTML = `
                    ${imageHtml}
                    <div class="ms-2 me-auto">
                        <div class="fw-bold">
                            <a href="${editUrl}" class="text-decoration-none" title="Edit ${config.linkedElementName}">
                                ${elementName}
                            </a>
                        </div>
                        <small class="text-muted">Role: ${roleText}</small>
                        ${locationInfo}
                    </div>
                    <button class="btn btn-sm btn-danger unlink-element-btn" data-element-type="${elementType}" data-element-id="${item.id}" title="Unlink this ${config.linkedElementName}">
                        <i class="fas fa-trash"></i>
                    </button>
                `;
                listContainer.appendChild(li);
            });
        } else {
            if (noElementsMsgElement) {
                noElementsMsgElement.textContent = `No ${config.linkedElementName}s currently linked.`;
                noElementsMsgElement.style.display = 'block';
            }
        }
    }

    async function handleLinkElement(elementType) {
        const config = elementTypesConfig[elementType];
        const selectElement = document.getElementById(config.selectId);
        const roleInputElement = document.getElementById(config.roleInputId);
        const modalElement = document.getElementById(config.modalId);
        
        const elementToLinkId = selectElement.value;
        const roleOrSignificance = roleInputElement.value.trim();

        if (!elementToLinkId) {
            if (typeof showToast === 'function') showToast(`Please select a ${config.linkedElementName} to link.`, "warning");
            return;
        }

        const payload = {};
        payload[config.idField] = parseInt(elementToLinkId, 10);
        payload[config.roleField] = roleOrSignificance || null;
        
        try {
            const response = await fetch(config.linkApiUrl, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload), credentials: 'include'
            });

            if (response.ok) {
                if (typeof showToast === 'function') showToast(`${config.linkedElementName} linked successfully!`, "success");
                const updatedLinkedElements = await fetchData(config.fetchLinkedElementsUrl, `Failed to refresh linked ${elementType}s`);
                renderLinkedElements(elementType, updatedLinkedElements || []);
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) modal.hide();
            } else {
                const errorData = await response.json().catch(() => ({}));
                if (typeof showToast === 'function') showToast(`Error linking: ${errorData.detail || 'Unknown error'}`, "error");
            }
        } catch (error) {
            if (typeof showToast === 'function') showToast(`Network error linking element.`, "error");
        }
    }
    
    async function handleUnlinkElement(elementType, elementIdToUnlink) {
        const config = elementTypesConfig[elementType];
        if (!confirm(`Are you sure you want to unlink this ${config.linkedElementName}?`)) return;
        
        const unlinkUrl = `${config.unlinkApiUrlBase}/${elementIdToUnlink}`;
        try {
            const response = await fetch(unlinkUrl, { method: 'DELETE', credentials: 'include' });
            if (response.ok) {
                if (typeof showToast === 'function') showToast(`${config.linkedElementName} unlinked successfully.`, "success");
                const updatedLinkedElements = await fetchData(config.fetchLinkedElementsUrl, `Failed to refresh linked ${elementType}s`);
                renderLinkedElements(elementType, updatedLinkedElements || []);
            } else {
                const errorData = await response.json().catch(() => ({}));
                if (typeof showToast === 'function') showToast(`Error unlinking: ${errorData.detail || 'Unknown error'}`, "error");
            }
        } catch (error) {
            if (typeof showToast === 'function') showToast(`Network error unlinking element.`, "error");
        }
    }

    async function initializePage() {
        if (!WORLD_ID) {
            console.warn("No World ID found for this story. Association features will be disabled.");
            return;
        }

        Object.keys(elementTypesConfig).forEach(type => {
            const config = elementTypesConfig[type];
            const modalElement = document.getElementById(config.modalId);
            const linkButton = document.getElementById(config.linkButtonId);
            const listContainer = document.getElementById(config.listContainerId);

            if (modalElement) {
                modalElement.addEventListener('show.bs.modal', () => {
                    populateWorldElementSelect(type);
                    // Load character roles for character linking modal
                    if (type === 'character') {
                        populateCharacterRoleSelect();
                    }
                });
            }

            if (linkButton) {
                linkButton.addEventListener('click', () => handleLinkElement(type));
            }

            if (listContainer) {
                listContainer.addEventListener('click', (event) => {
                    const unlinkBtn = event.target.closest('.unlink-element-btn');
                    if (unlinkBtn && unlinkBtn.dataset.elementType === type) {
                        handleUnlinkElement(type, unlinkBtn.dataset.elementId);
                    }
                });
            }
        });

        for (const elementType in elementTypesConfig) {
             const config = elementTypesConfig[elementType];
            const linkedElements = await fetchData(config.fetchLinkedElementsUrl, `Failed to fetch linked ${elementType}s`);
            renderLinkedElements(elementType, linkedElements || []);
        }
    }

    initializePage();
});