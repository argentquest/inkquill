// /ai_rag_story_app/app/static/js/document_upload.js

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Document Upload JavaScript loaded (with Job Polling).");

    const uploadForm = document.getElementById('document-upload-form');
    const fileInput = document.getElementById('document-file-input');
    const uploadButton = document.getElementById('upload-button');
    const uploadStatusMessageElement = document.getElementById('upload-status-message');
    const documentsListContainer = document.getElementById('uploaded-documents-list');

    const API_BASE_URL = "/api/v1";

    const MAX_FILE_SIZE_MB = 50;
    const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
    const ALLOWED_MIME_TYPES = [
        "application/pdf",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];

    let jobPollingIntervals = {};

    function stopPolling(jobId) {
        if (jobPollingIntervals[jobId]) {
            clearInterval(jobPollingIntervals[jobId]);
            delete jobPollingIntervals[jobId];
        }
    }

    async function pollJobStatus(jobId) {
        stopPolling(jobId);

        const statusCell = document.querySelector(`.job-status-cell[data-job-id="${jobId}"]`);
        if (!statusCell) return;

        const apiUrl = `${API_BASE_URL}/worlds/import/job-status/${jobId}`;

        jobPollingIntervals[jobId] = setInterval(async () => {
            try {
                const response = await fetch(apiUrl, { credentials: 'include' });
                if (response.status === 404) {
                    statusCell.innerHTML = `<span class="badge bg-warning">Job not found</span>`;
                    stopPolling(jobId);
                    return;
                }
                if (!response.ok) {
                    statusCell.innerHTML = `<span class="badge bg-danger">Status Error</span>`;
                    stopPolling(jobId);
                    return;
                }
                const job = await response.json();

                let statusClass = 'bg-secondary';
                if (job.state === 'RUNNING') statusClass = 'bg-info';
                else if (job.state === 'COMPLETED') statusClass = 'bg-success';
                else if (job.state === 'FAILED') statusClass = 'bg-danger';

                statusCell.innerHTML = `<span class="badge ${statusClass}">${job.status_message || job.state}</span>`;

                if (job.state === "COMPLETED" || job.state === "FAILED") {
                    stopPolling(jobId);
                    setTimeout(() => window.location.reload(), 2000);
                }
            } catch (error) {
                console.error("Polling error for job " + jobId, error);
                statusCell.innerHTML = `<span class="badge bg-danger">Network Error</span>`;
                stopPolling(jobId);
            }
        }, 5000);
    }

    if (uploadForm && fileInput && uploadButton && uploadStatusMessageElement) {
        uploadForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const file = fileInput.files ? fileInput.files[0] : null;
            if (!file) {
                showToast("Please select a file.", "warning");
                return;
            }

            if (file.size > MAX_FILE_SIZE_BYTES) {
                showToast(`File size exceeds the ${MAX_FILE_SIZE_MB}MB limit.`, "error");
                return;
            }

            const formData = new FormData(uploadForm);

            uploadButton.disabled = true;
            uploadButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Uploading...`;

            const apiUrl = `${API_BASE_URL}/documents/upload`;

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                });

                // --- BEGIN FIX ---
                // The key is to handle the response here in the JavaScript
                // instead of letting the browser navigate to the JSON response.
                if (response.ok) { // Check for 2xx status codes
                    const result = await response.json();
                    
                    // Track document upload
                    if (window.trackFeatureUse) {
                        window.trackFeatureUse('document_management', 'document_uploaded');
                    }
                    
                    showToast(result.message || `"${file.name}" submitted successfully! Refreshing...`, "success");

                    // Reload the page after a short delay to show the new job processing.
                    setTimeout(() => {
                        window.location.reload();
                    }, 2000); // Reload after 2 seconds

                } else {
                    // Handle server-side errors (e.g., 400, 500)
                    const errorData = await response.json().catch(() => ({}));
                    showToast(`Upload failed: ${errorData.detail || 'Server error'}`, "error");
                    uploadButton.disabled = false;
                    uploadButton.innerHTML = `<i class="fas fa-upload me-2"></i> Upload Document`;
                }
                // --- END FIX ---
            } catch (error) {
                // Handle network errors
                showToast('Upload failed due to a network error.', "error");
                uploadButton.disabled = false;
                uploadButton.innerHTML = `<i class="fas fa-upload me-2"></i> Upload Document`;
            }
            // The 'finally' block is removed because the button state is now handled
            // within the success/error blocks of the try/catch. This ensures the
            // button remains disabled during the `setTimeout` waiting period.
        });
    }
});