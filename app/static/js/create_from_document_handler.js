"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("CreateFromDocumentHandler: Initializing with Job Polling.");

    const importForm = document.getElementById('create-from-doc-form');
    const worldNameInput = document.getElementById('new_world_name');
    const fileInput = document.getElementById('document_file');
    const processButton = document.getElementById('create-from-doc-button');
    const statusArea = document.getElementById('import-status-area');
    const statusMessageText = document.getElementById('import-status-message-text');
    const linkArea = document.getElementById('imported-world-link-area');
    const viewLink = document.getElementById('view-imported-world-link');

    const API_BASE_URL = "/api/v1";

    // Note: Model selection removed - now using hardcoded GPT-4.1 Mini

    if (!importForm || !processButton || !statusArea || !worldNameInput || !fileInput) {
        console.error("CreateFromDocumentHandler: One or more critical page elements are missing.");
        return;
    }

    let pollingInterval = null;

    function stopPolling() {
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
            console.log("Polling stopped.");
        }
    }

    async function pollJobStatus(jobId) {
        stopPolling(); // Stop any previous polling just in case

        const apiUrl = `${API_BASE_URL}/worlds/import/job-status/${jobId}`;
        
        pollingInterval = setInterval(async () => {
            try {
                const response = await fetch(apiUrl, { credentials: 'include' });
                
                if (!response.ok) {
                    stopPolling();
                    const errorText = await response.text();
                    statusMessageText.textContent = `Error checking job status (HTTP ${response.status}). Please check server logs.`;
                    statusArea.className = 'import-status-area error alert alert-danger mt-3';
                    console.error("Polling failed with status:", response.status, "Response:", errorText);
                    return;
                }

                const job = await response.json();
                
                // Update UI with the latest status
                let statusClass = 'processing alert-info';
                if (job.state === 'COMPLETED') statusClass = 'success alert-success';
                if (job.state === 'FAILED') statusClass = 'error alert-danger';
                
                statusArea.className = `import-status-area ${statusClass} mt-3`;
                statusMessageText.innerHTML = `<strong>Status:</strong> ${job.state} - ${job.status_message || 'Working...'}`;
                
                if (job.state === "COMPLETED" || job.state === "FAILED") {
                    stopPolling();
                    processButton.disabled = false;
                    processButton.innerHTML = `<i class="fas fa-magic me-2"></i> Analyze & Create World`;
                    
                    if (job.state === "COMPLETED") {
                        statusMessageText.innerHTML = `<strong>Success!</strong> ${job.result_message || 'World created and elements imported.'}`;
                        if (job.world_id) {
                            viewLink.href = `/ui/worlds/${job.world_id}`;
                            viewLink.textContent = `View Newly Created World`;
                            linkArea.style.display = 'block';
                        }
                    } else { // FAILED
                        statusMessageText.innerHTML = `<strong>Failed:</strong> ${job.result_message || 'An unknown error occurred during processing.'}`;
                    }
                }

            } catch (error) {
                console.error("Polling network error for job " + jobId, error);
                statusMessageText.textContent = "Error checking job status due to a network issue.";
                statusArea.className = 'import-status-area error alert alert-danger mt-3';
                stopPolling();
            }
        }, 5000); // Poll every 5 seconds
    }

    importForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const worldName = worldNameInput.value.trim();
        const file = fileInput.files ? fileInput.files[0] : null;

        if (!worldName) {
            if (typeof showToast === 'function') showToast("Please enter a name for the new world.", "warning");
            worldNameInput.focus();
            return;
        }
        if (!file) {
            if (typeof showToast === 'function') showToast("Please select a document file to upload.", "warning");
            fileInput.focus();
            return;
        }

        processButton.disabled = true;
        processButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Submitting Job...`;
        statusArea.style.display = 'block';
        statusArea.className = 'import-status-area processing alert alert-info mt-3';
        statusMessageText.innerHTML = `Submitting job to create world "<strong>${worldName}</strong>"...`;
        linkArea.style.display = 'none';

        const formData = new FormData(importForm);
        
        // Note: Model selection removed - backend now uses hardcoded GPT-4.1 Mini
        
        const submitUrl = `${API_BASE_URL}/worlds/import/create-from-document`;

        try {
            const response = await fetch(submitUrl, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            const result = await response.json();

            if (response.ok && result.job_id) {
                showToast("Job submitted successfully! Now tracking progress.", "success");
                pollJobStatus(result.job_id); // Start polling
                importForm.reset();
            } else {
                statusArea.className = 'import-status-area error alert alert-danger mt-3';
                statusMessageText.textContent = `Error: ${result.detail || "Could not start import job."}`;
                processButton.disabled = false;
                processButton.innerHTML = `<i class="fas fa-magic me-2"></i> Analyze & Create World`;
            }
        } catch (error) {
            console.error('CreateFromDocumentHandler: Network error:', error);
            statusArea.className = 'import-status-area error alert alert-danger mt-3';
            statusMessageText.textContent = "A network error occurred. Please check your connection and try again.";
            processButton.disabled = false;
            processButton.innerHTML = `<i class="fas fa-magic me-2"></i> Analyze & Create World`;
        }
    });
});