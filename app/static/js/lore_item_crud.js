// /ai_rag_story_app/app/static/js/lore_item_crud.js

/**
 * lore_item_crud.js
 * -----------------
 * Handles client-side interactions for managing LoreItem entities,
 * primarily focusing on deletion from the lore item list page (within a world).
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("LoreItem CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1";

    const loreItemsListContainer = document.getElementById('lore-items-list-container');

    if (loreItemsListContainer) {
        console.log("LoreItem CRUD JS: Event listener being attached to lore-items-list-container.");
        loreItemsListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-lore-item-btn');

            if (deleteButton) {
                const loreItemId = deleteButton.dataset.loreItemId;
                const loreItemTitle = deleteButton.dataset.loreItemTitle || "this lore item";
                console.log(`LoreItem CRUD JS: Delete lore item button clicked. ID: ${loreItemId}, Title: ${loreItemTitle}`);
                event.preventDefault();

                if (!loreItemId) {
                    console.error("LoreItem CRUD JS: Delete button missing data-lore-item-id.");
                    if (typeof showToast === 'function') showToast("Could not determine which lore item to delete.", "error");
                    return;
                }

                if (confirm(`Are you sure you want to delete lore item "${loreItemTitle}" (ID: ${loreItemId})? This action cannot be undone.`)) {
                    const originalButtonHTML = deleteButton.innerHTML;
                    deleteButton.disabled = true;
                    deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

                    const apiUrl = `${API_BASE_URL}/lore-items/${loreItemId}`;
                    console.log(`LoreItem CRUD JS: Delete API URL: ${apiUrl}`);

                    try {
                        const response = await fetch(apiUrl, {
                            method: 'DELETE',
                            credentials: 'include'
                        });

                        console.log(`LoreItem CRUD JS: Delete API response status: ${response.status}`);
                        if (response.status === 204) {
                            if (typeof showToast === 'function') showToast(`Lore item "${loreItemTitle}" deleted successfully!`, "success");
                            const loreItemContainer = deleteButton.closest('.lore-item-container');
                            if (loreItemContainer) {
                                loreItemContainer.remove();
                            } else {
                                console.warn("LoreItem CRUD JS: Could not find lore item's container to remove.");
                            }
                        } else {
                            const errorData = await response.json().catch(() => ({}));
                            let detail = errorData?.detail || `Failed to delete lore item (Status: ${response.status})`;
                            console.error(`LoreItem CRUD JS: Failed to delete lore item ${loreItemId}:`, detail);
                            if (typeof showToast === 'function') showToast(`Error deleting lore item: ${detail}`, "error", 7000);
                            deleteButton.disabled = false;
                            deleteButton.innerHTML = originalButtonHTML;
                        }
                    } catch (error) {
                        console.error('LoreItem CRUD JS: Error sending delete request:', error);
                        if (typeof showToast === 'function') showToast('An error occurred while trying to delete the lore item.', "error");
                        deleteButton.disabled = false;
                        deleteButton.innerHTML = originalButtonHTML;
                    }
                } else {
                    console.log(`LoreItem CRUD JS: Deletion cancelled for lore item ID: ${loreItemId}`);
                }
            }
        });
    } else {
        console.warn("LoreItem CRUD JS: Lore items list container 'lore-items-list-container' not found.");
    }
    console.log("LoreItem CRUD JS: Initialization complete.");
});