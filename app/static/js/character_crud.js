// /story_app/app/static/js/character_crud.js

/**
 * character_crud.js
 * -----------------
 * Handles client-side interactions for managing Character entities,
 * primarily focusing on deletion from the character list page (within a world).
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Character CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1";

    // Event delegation on the container for the characters list.
    // character_list_for_world.html uses <div id="characters-list-container">
    const charactersListContainer = document.getElementById('characters-list-container');

    if (charactersListContainer) {
        console.log("Character CRUD JS: Event listener being attached to characters-list-container.");
        charactersListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-character-btn');

            if (deleteButton) {
                const characterId = deleteButton.dataset.characterId;
                const characterName = deleteButton.dataset.characterName || "this character";
                console.log(`Character CRUD JS: Delete character button clicked. ID: ${characterId}, Name: ${characterName}`);
                event.preventDefault();

                if (!characterId) {
                    console.error("Character CRUD JS: Delete button missing data-character-id.");
                    if (typeof showToast === 'function') showToast("Could not determine which character to delete.", "error");
                    return;
                }

                if (confirm(`Are you sure you want to delete character "${characterName}" (ID: ${characterId})? This action cannot be undone.`)) {
                    const originalButtonHTML = deleteButton.innerHTML;
                    deleteButton.disabled = true;
                    deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

                    // API endpoint for deleting a character is /api/v1/characters/{character_id}
                    const apiUrl = `${API_BASE_URL}/characters/${characterId}`;
                    console.log(`Character CRUD JS: Delete API URL: ${apiUrl}`);

                    try {
                        const response = await fetch(apiUrl, {
                            method: 'DELETE',
                            credentials: 'include'
                        });

                        console.log(`Character CRUD JS: Delete API response status: ${response.status}`);
                        if (response.status === 204) {
                            // Track character deletion
                            if (window.trackFeatureUse) {
                                window.trackFeatureUse('world_building', 'character_deleted');
                            }
                            
                            if (typeof showToast === 'function') showToast(`Character "${characterName}" deleted successfully!`, "success");
                            const characterItemContainer = deleteButton.closest('.character-item-container');
                            if (characterItemContainer) {
                                characterItemContainer.remove();
                            } else {
                                console.warn("Character CRUD JS: Could not find character item's container to remove.");
                            }
                        } else {
                            const errorData = await response.json().catch(() => ({}));
                            let detail = errorData?.detail || `Failed to delete character (Status: ${response.status})`;
                            console.error(`Character CRUD JS: Failed to delete character ${characterId}:`, detail);
                            if (typeof showToast === 'function') showToast(`Error deleting character: ${detail}`, "error", 7000);
                            deleteButton.disabled = false;
                            deleteButton.innerHTML = originalButtonHTML;
                        }
                    } catch (error) {
                        console.error('Character CRUD JS: Error sending delete request:', error);
                        if (typeof showToast === 'function') showToast('An error occurred while trying to delete the character.', "error");
                        deleteButton.disabled = false;
                        deleteButton.innerHTML = originalButtonHTML;
                    }
                } else {
                    console.log(`Character CRUD JS: Deletion cancelled for character ID: ${characterId}`);
                }
            }
        });
    } else {
        console.warn("Character CRUD JS: Characters list container 'characters-list-container' not found.");
    }
    console.log("Character CRUD JS: Initialization complete.");
});
