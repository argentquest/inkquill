// /story_app/app/static/js/document_crud.js

/**
 * document_crud.js
 * ----------------
 * Handles client-side interactions for managing UploadedDocument entities,
 * primarily focusing on deletion from the document manager page.
 * Uses showToast() for notifications.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Document CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1"; // Ensure this matches your API prefix

    // Using event delegation on the container for the documents list.
    // The document_manager.html template uses <tbody id="uploaded-documents-list">
    const documentsListContainer = document.getElementById('uploaded-documents-list');

    if (documentsListContainer) {
        console.log("Document CRUD JS: Event listener being attached to uploaded-documents-list.");
        documentsListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-document-btn');

            if (deleteButton) {
                console.log("Document CRUD JS: Delete document button clicked. ID:", deleteButton.dataset.documentId);
                event.preventDefault();
                const documentId = deleteButton.dataset.documentId;

                if (!documentId) {
                    console.error("Document CRUD JS: Delete button missing data-document-id.");
                    // Assuming showToast is globally available from notifications.js
                    if (typeof showToast === 'function') {
                        showToast("Could not determine which document to delete.", "error");
                    } else {
                        alert("Could not determine which document to delete.");
                    }
                    return;
                }

                if (confirm(`Are you sure you want to delete document record ${documentId}? This will also attempt to delete the file from storage and its entries from the search index if the backend is configured to do so.`)) {
                    const originalButtonHTML = deleteButton.innerHTML; // Store original HTML
                    deleteButton.disabled = true;
                    deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

                    const apiUrl = `${API_BASE_URL}/documents/${documentId}`; // Assuming this is your delete endpoint
                    console.log(`Document CRUD JS: Delete API URL: ${apiUrl}`);

                    try {
                        const response = await fetch(apiUrl, {
                            method: 'DELETE',
                            headers: {
                                // 'X-CSRF-Token': getCsrfToken(), // If using CSRF
                            },
                            credentials: 'include' // Important for auth cookies
                        });

                        console.log(`Document CRUD JS: Delete API response status: ${response.status}`);
                        if (response.status === 204) { // No Content indicates successful deletion
                            // Track document deletion
                            if (window.trackFeatureUse) {
                                window.trackFeatureUse('document_management', 'document_deleted');
                            }
                            
                            if (typeof showToast === 'function') {
                                showToast('Document record deleted successfully!', "success");
                            } else {
                                alert('Document record deleted successfully!');
                            }
                            deleteButton.closest('tr').remove(); // Remove the table row from the DOM
                        } else {
                            const errorData = await response.json().catch(() => ({})); 
                            let detail = errorData?.detail || `Failed to delete document (Status: ${response.status})`;
                            if (response.status === 401) {
                                detail = "Unauthorized. Please log in again.";
                            } else if (response.status === 403) {
                                detail = "Forbidden. You do not have permission to delete this document record.";
                            } else if (response.status === 404) {
                                detail = "Document record not found.";
                            }
                            console.error(`Document CRUD JS: Failed to delete document ${documentId}:`, detail);
                            if (typeof showToast === 'function') {
                                showToast(`Error deleting document: ${detail}`, "error", 7000);
                            } else {
                                alert(`Error deleting document: ${detail}`);
                            }
                            deleteButton.disabled = false;
                            deleteButton.innerHTML = originalButtonHTML;
                        }
                    } catch (error) {
                        console.error('Document CRUD JS: Error sending delete request for document:', error);
                        if (typeof showToast === 'function') {
                            showToast('An error occurred while trying to delete the document. Please check your connection.', "error");
                        } else {
                            alert('An error occurred while trying to delete the document. Please check your connection.');
                        }
                        deleteButton.disabled = false;
                        deleteButton.innerHTML = originalButtonHTML;
                    }
                } else {
                    console.log(`Document CRUD JS: Deletion cancelled for document ID: ${documentId}`);
                }
            }
        });
    } else {
        console.warn("Document CRUD JS: Documents list container with id='uploaded-documents-list' not found. Delete functionality for documents might not work.");
    }
    console.log("Document CRUD JS: Initialization complete.");
});

