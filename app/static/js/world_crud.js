// /ai_rag_story_app/app/static/js/world_crud.js

/**
 * world_crud.js
 * -------------
 * Handles client-side interactions for managing World entities,
 * primarily focusing on deletion from the world list page.
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("World CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1"; // Ensure this matches your API prefix

    // Using event delegation on the container for the worlds list.
    // world_list.html uses <div id="worlds-list-container">
    const worldsListContainer = document.getElementById('worlds-list-container');

    if (worldsListContainer) {
        console.log("World CRUD JS: Event listener being attached to worlds-list-container.");
        worldsListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-world-btn');

            if (deleteButton) {
                console.log("World CRUD JS: Delete world button clicked. ID:", deleteButton.dataset.worldId);
                event.preventDefault();
                const worldId = deleteButton.dataset.worldId;

                if (!worldId) {
                    console.error("World CRUD JS: Delete button missing data-world-id.");
                    if (typeof showToast === 'function') {
                        showToast("Could not determine which world to delete.", "error");
                    } else {
                        alert("Could not determine which world to delete.");
                    }
                    return;
                }

                if (confirm(`Are you sure you want to delete world ${worldId}? This will also delete all its characters, locations, lore items, and unlink any stories set in it.`)) {
                    const originalButtonHTML = deleteButton.innerHTML;
                    deleteButton.disabled = true;
                    deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

                    const apiUrl = `${API_BASE_URL}/worlds/${worldId}`;
                    console.log(`World CRUD JS: Delete API URL: ${apiUrl}`);

                    try {
                        const response = await fetch(apiUrl, {
                            method: 'DELETE',
                            credentials: 'include' // Important for auth cookies
                        });

                        console.log(`World CRUD JS: Delete API response status: ${response.status}`);
                        if (response.status === 204) { // No Content indicates successful deletion
                            // Track world deletion
                            if (window.trackFeatureUse) {
                                window.trackFeatureUse('world_management', 'world_deleted');
                            }
                            
                            if (typeof showToast === 'function') {
                                showToast('World deleted successfully!', "success");
                            } else {
                                alert('World deleted successfully!');
                            }
                            // Remove the world card from the DOM
                            const worldItemContainer = deleteButton.closest('.world-item-container');
                            if (worldItemContainer) {
                                worldItemContainer.remove();
                            } else {
                                console.warn("World CRUD JS: Could not find world item's container to remove.");
                                // Fallback to reload if direct DOM manipulation fails for some reason
                                // window.location.reload(); 
                            }
                        } else {
                            const errorData = await response.json().catch(() => ({}));
                            let detail = errorData?.detail || `Failed to delete world (Status: ${response.status})`;
                            console.error(`World CRUD JS: Failed to delete world ${worldId}:`, detail);
                            if (typeof showToast === 'function') {
                                showToast(`Error deleting world: ${detail}`, "error", 7000);
                            } else {
                                alert(`Error deleting world: ${detail}`);
                            }
                            deleteButton.disabled = false;
                            deleteButton.innerHTML = originalButtonHTML;
                        }
                    } catch (error) {
                        console.error('World CRUD JS: Error sending delete request for world:', error);
                        if (typeof showToast === 'function') {
                            showToast('An error occurred while trying to delete the world.', "error");
                        } else {
                            alert('An error occurred while trying to delete the world.');
                        }
                        deleteButton.disabled = false;
                        deleteButton.innerHTML = originalButtonHTML;
                    }
                } else {
                    console.log(`World CRUD JS: Deletion cancelled for world ID: ${worldId}`);
                }
            }
        });
    } else {
        console.warn("World CRUD JS: Worlds list container with id='worlds-list-container' not found.");
    }
    console.log("World CRUD JS: Initialization complete.");
});