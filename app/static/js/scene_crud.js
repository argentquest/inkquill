// /ai_rag_story_app/app/static/js/scene_crud.js

/**
 * scene_crud.js
 * -------------
 * Handles client-side interactions for managing Scene entities, primarily focusing on
 * deletion from the story detail page (where scenes are listed under acts).
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Scene CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1"; // Ensure this matches your API prefix

    // Event delegation will be attached to a common ancestor of all scene lists.
    // Since scenes are listed under acts, and acts are in 'acts-list-container',
    // we can use that or a higher-level container like 'main.container'.
    // Using 'acts-list-container' is more specific if it always exists when scenes are shown.
    const actsAndScenesContainer = document.getElementById('acts-list-container') || document.querySelector('main.container') || document.body;
    
    console.log("Scene CRUD JS: Event delegation container selected:", actsAndScenesContainer);

    if (!actsAndScenesContainer) {
        console.error("Scene CRUD JS: Could not find a suitable event delegation container for scene actions.");
        return; 
    }

    actsAndScenesContainer.addEventListener('click', async (event) => {
        const deleteSceneButton = event.target.closest('.delete-scene-btn');

        if (deleteSceneButton) {
            console.log("Scene CRUD JS: Delete scene button clicked. Scene ID:", deleteSceneButton.dataset.sceneId, "Act ID:", deleteSceneButton.dataset.actId);
            event.preventDefault();
            const sceneId = deleteSceneButton.dataset.sceneId;
            const actId = deleteSceneButton.dataset.actId; // Useful for context or UI updates

            if (!sceneId) {
                console.error("Scene CRUD JS: Delete scene button missing data-scene-id.");
                if (typeof showToast === 'function') {
                    showToast("Could not determine which scene to delete.", "error");
                } else {
                    alert("Could not determine which scene to delete.");
                }
                return;
            }

            if (confirm(`Are you sure you want to delete scene ${sceneId}? This action cannot be undone.`)) {
                const originalButtonHTML = deleteSceneButton.innerHTML;
                deleteSceneButton.disabled = true;
                deleteSceneButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

                // The API endpoint for deleting a scene is /api/v1/scenes/{scene_id}
                const apiUrl = `${API_BASE_URL}/scenes/${sceneId}`;
                console.log(`Scene CRUD JS: Delete API URL: ${apiUrl}`);

                try {
                    const response = await fetch(apiUrl, {
                        method: 'DELETE',
                        headers: {
                            // 'X-CSRF-Token': getCsrfToken(), // If using CSRF
                        },
                        credentials: 'include' // Important for auth cookies
                    });

                    console.log(`Scene CRUD JS: Delete API response status: ${response.status}`);
                    if (response.status === 204) { // No Content indicates successful deletion
                        if (typeof showToast === 'function') {
                            showToast('Scene deleted successfully!', "success");
                        } else {
                            alert('Scene deleted successfully!');
                        }
                        // Remove the scene card from the DOM
                        const sceneCard = deleteSceneButton.closest('.col') || deleteSceneButton.closest('.scene-card') || deleteSceneButton.closest('.list-group-item');
                        if (sceneCard) {
                            sceneCard.remove();
                            // Check if the parent container (e.g., for actId) is now empty
                            const scenesContainerForAct = document.getElementById(`scenes-for-act-${actId}`);
                            if (scenesContainerForAct && scenesContainerForAct.querySelectorAll('.col, .scene-card, .list-group-item').length === 0) {
                                const noScenesMsg = scenesContainerForAct.querySelector('.no-scenes-message');
                                if (noScenesMsg) {
                                    noScenesMsg.textContent = "No scenes generated for this act yet.";
                                    noScenesMsg.style.display = 'block';
                                }
                            }
                        } else {
                            console.warn("Scene CRUD JS: Could not find scene card element to remove from UI.");
                        }
                    } else {
                        const errorData = await response.json().catch(() => ({})); 
                        let detail = errorData?.detail || `Failed to delete scene (Status: ${response.status})`;
                        if (response.status === 401) {
                            detail = "Unauthorized. Please log in again.";
                        } else if (response.status === 403) {
                            detail = "Forbidden. You do not have permission to delete this scene.";
                        } else if (response.status === 404) {
                            detail = "Scene not found.";
                        }
                        console.error(`Scene CRUD JS: Failed to delete scene ${sceneId}:`, detail);
                        if (typeof showToast === 'function') {
                            showToast(`Error deleting scene: ${detail}`, "error", 7000);
                        } else {
                            alert(`Error deleting scene: ${detail}`);
                        }
                        deleteSceneButton.disabled = false;
                        deleteSceneButton.innerHTML = originalButtonHTML;
                    }
                } catch (error) {
                    console.error('Scene CRUD JS: Error sending delete request for scene:', error);
                    if (typeof showToast === 'function') {
                        showToast('An error occurred while trying to delete the scene. Please check your connection.', "error");
                    } else {
                        alert('An error occurred while trying to delete the scene. Please check your connection.');
                    }
                    deleteButton.disabled = false;
                    deleteButton.innerHTML = originalButtonHTML;
                }
            } else {
                console.log(`Scene CRUD JS: Deletion cancelled for scene ID: ${sceneId}`);
            }
        }
        // Add logic for '.edit-scene-btn' if it requires JS beyond navigation
        // For now, the "Edit Scene" button in story_detail.html is a simple <a> link.
    });
    console.log("Scene CRUD JS: Initialization complete.");
});
