// /story_app/app/static/js/world_importer_from_doc_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("WorldImporterFromDocHandler: DOMContentLoaded.");

    const importForm = document.getElementById('import-document-form');
    const fileInput = document.getElementById('document-file-input-import');
    const worldNameInput = document.getElementById('world-name-input');
    const generateButton = document.getElementById('generate-import-from-doc-button');
    const statusArea = document.getElementById('import-status-area');
    const statusMessageText = document.getElementById('import-status-message-text');
    const linkArea = document.getElementById('imported-world-link-area');
    const viewLink = document.getElementById('view-imported-world-link');
    const API_BASE_URL = "/api/v1";

    // Note: Model selection removed - now using hardcoded GPT-4.1 Mini

    if (!importForm || !fileInput || !worldNameInput || !generateButton || !statusArea || !statusMessageText || !linkArea || !viewLink) {
        console.error("WorldImporterFromDocHandler: One or more required HTML elements are missing.");
        if (generateButton) generateButton.disabled = true;
        return;
    }

    importForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        console.log("WorldImporterFromDocHandler: Form submitted.");

        const file = fileInput.files ? fileInput.files[0] : null;
        const worldName = worldNameInput.value.trim();
        
        if (!file) {
            showToast("Please select a file to upload.", "warning");
            return;
        }
        
        if (!worldName) {
            showToast("Please enter a world name.", "warning");
            return;
        }

        generateButton.disabled = true;
        const originalButtonHTML = generateButton.innerHTML;
        generateButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Analyzing & Importing...`;
        statusArea.className = 'import-status-area processing alert alert-info';
        statusMessageText.innerHTML = `Uploading and analyzing "<strong>${file.name}</strong>". This is a long process and may take several minutes. Please wait...`;
        statusArea.style.display = 'block';
        linkArea.style.display = 'none';

        // Note: Model selection removed - backend now uses hardcoded GPT-4.1 Mini
        const formData = new FormData();
        formData.append('file', file);
        formData.append('world_name', worldName);
        const apiUrl = `${API_BASE_URL}/worlds/import/create-from-document`;

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            const result = await response.json();

            if (response.ok && result.job_id) {
                statusArea.className = 'import-status-area success alert alert-success';
                statusMessageText.innerHTML = `<strong>Import Started!</strong><br>${result.message || 'Your document is being analyzed.'}<br><br>Document analysis typically takes 3-10 minutes depending on the file size. Please return to the <a href="/ui/worlds">My Worlds</a> page in a few minutes to see your newly imported world.`;
                showToast("Document import started! Check back in a few minutes.", "success", 8000);
                importForm.reset();
            } else {
                statusArea.className = 'import-status-area error alert alert-danger';
                const errorMessage = result.error || result.detail || "An unknown error occurred during import.";
                statusMessageText.textContent = `Error: ${errorMessage}`;
                showToast(`Import failed: ${errorMessage}`, "error", 10000);
            }
        } catch (error) {
            console.error('WorldImporterFromDocHandler: Network or unexpected error during import:', error);
            statusArea.className = 'import-status-area error alert alert-danger';
            statusMessageText.textContent = "A critical network error occurred. The request may have timed out. Please check the server logs and try again.";
            showToast("Import request failed. Check connection and server logs.", "error");
        } finally {
            generateButton.disabled = false;
            generateButton.innerHTML = originalButtonHTML;
        }
    });
});
