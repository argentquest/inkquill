// /ai_rag_story_app/app/static/js/story_crud.js

/**
 * story_crud.js
 * -------------
 * Handles client-side interactions for managing Story entities, including
 * deletion and the "Publish Story" functionality. Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {

    console.log("Story CRUD JavaScript loaded (with Publish Story functionality and Toasts).");

    const API_BASE_URL = "/api/v1"; 

    const eventDelegateContainer = document.querySelector('main.container') || document.body;
    console.log("Story CRUD JS: Event delegation container selected:", eventDelegateContainer);

    if (!eventDelegateContainer) {
        console.error("Story CRUD JS: Could not find a suitable event delegation container. Buttons might not work.");
        return; 
    }

    eventDelegateContainer.addEventListener('click', async (event) => {
        // console.log("Story CRUD JS: Click detected on eventDelegateContainer. Target:", event.target); 

        const deleteButton = event.target.closest('.delete-story-btn');
        const publishButton = event.target.closest('.publish-story-btn');

        // console.log("Story CRUD JS: Attempting to identify button. Delete button found:", !!deleteButton, "Publish button found:", !!publishButton);

        if (deleteButton) {
            console.log("Story CRUD JS: Delete button logic initiated.");
            event.preventDefault(); 
            const storyId = deleteButton.dataset.storyId;
            if (!storyId) { 
                console.error("Story CRUD JS: Delete button missing data-story-id.");
                showToast("Cannot determine which story to delete.", "error");
                return; 
            }
            if (confirm(`Are you sure you want to delete story ${storyId}? This will also delete all associated acts.`)) {
                const originalButtonText = deleteButton.textContent; // Store original text
                deleteButton.disabled = true; 
                deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;
                
                const apiUrl = `${API_BASE_URL}/stories/${storyId}`;
                console.log(`Story CRUD JS: Delete API URL: ${apiUrl}`);
                try {
                    const response = await fetch(apiUrl, { method: 'DELETE', credentials: 'include' });
                    console.log(`Story CRUD JS: Delete API response status: ${response.status}`);
                    if (response.status === 204) {
                        showToast('Story deleted successfully! Redirecting...', "success", 3000);
                        
                        // Track story deletion
                        if (window.trackStoryAction) {
                            // Try to get story title from the UI
                            const storyTitle = deleteButton.closest('.story-item')?.querySelector('.card-title')?.textContent?.trim() || 
                                             deleteButton.closest('tr')?.querySelector('.story-title')?.textContent?.trim() || 
                                             'Unknown Story';
                            window.trackStoryAction('delete', storyId, storyTitle);
                        }
                        
                        const storyItemContainer = deleteButton.closest('.story-item') || deleteButton.closest('.story-item-container') || deleteButton.closest('tr'); 
                        if (storyItemContainer && !window.location.pathname.includes(`/ui/stories/${storyId}`)) { // If on list page
                            storyItemContainer.remove();
                        } else { // If on detail page or item not easily removable, redirect
                             setTimeout(() => { window.location.href = '/ui/stories'; }, 1500);
                        }
                    } else {
                        const errorData = await response.json().catch(() => ({}));
                        let detail = errorData?.detail || `Failed with status ${response.status}`;
                        if (response.status === 401) detail = "Unauthorized. Please log in again.";
                        else if (response.status === 403) detail = "Forbidden. You do not have permission to delete this story.";
                        else if (response.status === 404) detail = "Story not found.";
                        showToast(`Error deleting story: ${detail}`, "error");
                        deleteButton.disabled = false; 
                        deleteButton.innerHTML = originalButtonText; // Restore original text
                    }
                } catch (error) {
                    console.error('Story CRUD JS: Error sending delete request:', error);
                    showToast('An error occurred while trying to delete the story.', "error");
                    deleteButton.disabled = false; 
                    deleteButton.innerHTML = originalButtonText; // Restore original text
                }
            } else {
                console.log("Story CRUD JS: Delete action cancelled by user.");
            }
        } else if (publishButton) {
            console.log("Story CRUD JS: Publish button logic initiated."); 
            event.preventDefault();
            const storyId = publishButton.dataset.storyId;
            const publishedStoryLinkArea = document.getElementById('published-story-link-area');
            const publishedStoryUrlElement = document.getElementById('published-story-url');
            const publishStatusMessageElement = document.getElementById('publish-status-message');

            // console.log("Story CRUD JS: Publish - LinkArea found?", !!publishedStoryLinkArea);
            // console.log("Story CRUD JS: Publish - UrlElement found?", !!publishedStoryUrlElement);
            // console.log("Story CRUD JS: Publish - StatusMessageElement found?", !!publishStatusMessageElement);

            if (!storyId) {
                console.error("Story CRUD JS: Publish button clicked, but data-story-id attribute is missing.");
                if (publishStatusMessageElement) {
                    publishStatusMessageElement.textContent = "Error: Could not determine which story to publish.";
                    publishStatusMessageElement.className = "alert alert-danger"; 
                } else {
                    showToast("Error: Could not determine which story to publish.", "error");
                }
                if (publishedStoryLinkArea) publishedStoryLinkArea.style.display = 'block'; 
                return;
            }

            console.log(`Story CRUD JS: Attempting to publish story ID: ${storyId}`);
            const originalButtonHTML = publishButton.innerHTML; 
            publishButton.disabled = true;
            publishButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Publishing...
            `;

            if (publishStatusMessageElement) {
                publishStatusMessageElement.textContent = "Publishing story, please wait...";
                publishStatusMessageElement.className = "alert alert-info"; 
                publishStatusMessageElement.style.display = 'block'; // Ensure it's visible
            }
            if (publishedStoryLinkArea) publishedStoryLinkArea.style.display = 'block'; // Ensure area is visible
            if (publishedStoryUrlElement) publishedStoryUrlElement.textContent = '';


            const apiUrl = `${API_BASE_URL}/stories/${storyId}/publish`;
            console.log(`Story CRUD JS: Publishing API URL: ${apiUrl}`); 

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST', 
                    headers: { /* No Content-Type needed if no body */ },
                    credentials: 'include' 
                });

                console.log(`Story CRUD JS: Publish API response status: ${response.status}`); 

                if (response.ok) { 
                    const result = await response.json(); 
                    console.log("Story CRUD JS: Publish successful:", result); 
                    
                    // Track story publishing
                    if (window.trackStoryAction) {
                        const storyTitle = publishButton.closest('.container')?.querySelector('h1')?.textContent?.trim() || 'Unknown Story';
                        window.trackStoryAction('publish', storyId, storyTitle);
                        
                        // Track additional publishing details
                        if (window.trackFeatureUse && result.word_count) {
                            window.trackFeatureUse('story_publishing', 'complete', {
                                word_count: result.word_count,
                                filename: result.filename,
                                has_url: !!result.published_url
                            });
                        }
                    }
                    
                    if (publishStatusMessageElement) {
                        publishStatusMessageElement.textContent = result.message || "Story published successfully!";
                        publishStatusMessageElement.className = "alert alert-success";
                    }
                    if (publishedStoryUrlElement && result.published_url) {
                        publishedStoryUrlElement.href = result.published_url;
                        publishedStoryUrlElement.innerHTML = '<i class="fas fa-external-link-alt me-1"></i>View Published Story';
                    }
                    showToast(result.message || "Story published!", "success", 7000); 
                } else {
                    const errorData = await response.json().catch(() => ({ detail: `Publishing failed with status ${response.status}` }));
                    let detail = errorData?.detail || `Failed to publish story (Status: ${response.status})`;
                     if (response.status === 401) detail = "Unauthorized. You may need to log in again.";
                     else if (response.status === 403) detail = "Forbidden. You do not have permission to publish this story.";
                     else if (response.status === 404) detail = "Story not found (or publish endpoint missing).";
                    console.error(`Story CRUD JS: Failed to publish story ${storyId}:`, detail);
                    if (publishStatusMessageElement) {
                        publishStatusMessageElement.textContent = `Error publishing story: ${detail}`;
                        publishStatusMessageElement.className = "alert alert-danger";
                    } else {
                        showToast(`Error publishing story: ${detail}`, "error");
                    }
                }
            } catch (error) {
                console.error('Story CRUD JS: Error sending publish request:', error);
                const networkErrorMsg = 'An error occurred while publishing. Please check your connection.';
                if (publishStatusMessageElement) {
                    publishStatusMessageElement.textContent = networkErrorMsg;
                    publishStatusMessageElement.className = "alert alert-danger";
                } else {
                    showToast(networkErrorMsg, "error");
                }
            } finally {
                publishButton.disabled = false;
                publishButton.innerHTML = originalButtonHTML; 
            }
        }
    });
    console.log("Story CRUD JS: Event listener attached to container.");
});
