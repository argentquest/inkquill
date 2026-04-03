// /story_app/app/static/js/location_crud.js

/**
 * location_crud.js
 * -----------------
 * Handles client-side interactions for managing Location entities,
 * primarily focusing on deletion from the location list page (within a world).
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Location CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1";

    const locationsListContainer = document.getElementById('locations-list-container');

    if (locationsListContainer) {
        console.log("Location CRUD JS: Event listener being attached to locations-list-container.");
        locationsListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-location-btn');

            if (deleteButton) {
                const locationId = deleteButton.dataset.locationId;
                const locationName = deleteButton.dataset.locationName || "this location";
                console.log(`Location CRUD JS: Delete location button clicked. ID: ${locationId}, Name: ${locationName}`);
                event.preventDefault();

                if (!locationId) {
                    console.error("Location CRUD JS: Delete button missing data-location-id.");
                    if (typeof showToast === 'function') showToast("Could not determine which location to delete.", "error");
                    return;
                }

                if (confirm(`Are you sure you want to delete location "${locationName}" (ID: ${locationId})? This action cannot be undone.`)) {
                    const originalButtonHTML = deleteButton.innerHTML;
                    deleteButton.disabled = true;
                    deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

                    const apiUrl = `${API_BASE_URL}/locations/${locationId}`;
                    console.log(`Location CRUD JS: Delete API URL: ${apiUrl}`);

                    try {
                        const response = await fetch(apiUrl, {
                            method: 'DELETE',
                            credentials: 'include'
                        });

                        console.log(`Location CRUD JS: Delete API response status: ${response.status}`);
                        if (response.status === 204) {
                            if (typeof showToast === 'function') showToast(`Location "${locationName}" deleted successfully!`, "success");
                            const locationItemContainer = deleteButton.closest('.location-item-container');
                            if (locationItemContainer) {
                                locationItemContainer.remove();
                            } else {
                                console.warn("Location CRUD JS: Could not find location item's container to remove.");
                            }
                        } else {
                            const errorData = await response.json().catch(() => ({}));
                            let detail = errorData?.detail || `Failed to delete location (Status: ${response.status})`;
                            console.error(`Location CRUD JS: Failed to delete location ${locationId}:`, detail);
                            if (typeof showToast === 'function') showToast(`Error deleting location: ${detail}`, "error", 7000);
                            deleteButton.disabled = false;
                            deleteButton.innerHTML = originalButtonHTML;
                        }
                    } catch (error) {
                        console.error('Location CRUD JS: Error sending delete request:', error);
                        if (typeof showToast === 'function') showToast('An error occurred while trying to delete the location.', "error");
                        deleteButton.disabled = false;
                        deleteButton.innerHTML = originalButtonHTML;
                    }
                } else {
                    console.log(`Location CRUD JS: Deletion cancelled for location ID: ${locationId}`);
                }
            }
        });
    } else {
        console.warn("Location CRUD JS: Locations list container 'locations-list-container' not found.");
    }
    console.log("Location CRUD JS: Initialization complete.");
});
