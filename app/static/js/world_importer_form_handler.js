// /story_app/app/static/js/world_importer_form_handler.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const importForm = document.getElementById('import-book-form');
    const bookTitleInput = document.getElementById('book_title_input');
    const generateImportButton = document.getElementById('generate-import-button');
    const importStatusArea = document.getElementById('import-status-area');
    const importStatusMessageText = document.getElementById('import-status-message-text');
    const importedWorldLinkArea = document.getElementById('imported-world-link-area');
    const viewImportedWorldLink = document.getElementById('view-imported-world-link');
    const modelSelector = document.getElementById('ai-model-config-select-import');

    const API_BASE_URL = "/api/v1";

    // Initialize AI model selector
    if (typeof AIModelSelector !== 'undefined') {
        AIModelSelector.initialize('ai-model-config-select-import');
    } else {
        console.warn("WorldImporterFormHandler: AIModelSelector not loaded.");
    }

    if (!importForm || !bookTitleInput || !generateImportButton || !importStatusArea || !importStatusMessageText || !viewImportedWorldLink || !importedWorldLinkArea) {
        console.error("WorldImporterFormHandler: One or more required HTML elements are missing.");
        if (generateImportButton) generateImportButton.disabled = true;
        return;
    }

    importForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const bookTitle = bookTitleInput.value.trim();
        if (!bookTitle) {
            if (typeof showToast === 'function') showToast("Please enter a book title.", "warning");
            return;
        }

        generateImportButton.disabled = true;
        const originalButtonHTML = generateImportButton.innerHTML;
        generateImportButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Generating & Importing...`;
        importStatusArea.className = 'import-status-area processing alert alert-info';
        importStatusMessageText.innerHTML = `Processing request for "<strong>${bookTitle}</strong>"... This may take a minute or more.`;
        importStatusArea.style.display = 'block';
        importedWorldLinkArea.style.display = 'none';

        // Get selected model ID
        const selectedModelId = modelSelector && modelSelector.value ? parseInt(modelSelector.value, 10) : null;
        
        const payload = { 
            book_title: bookTitle,
            model_config_id: selectedModelId
        };
        const apiUrl = `${API_BASE_URL}/worlds/import-from-book-title`;

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                credentials: 'include'
            });

            // Track AI interaction
            if (window.trackAIInteraction) {
                window.trackAIInteraction('world_import_from_book', 'gpt_world_generation');
            }

            const result = await response.json();

            if (response.ok && result.job_id) {
                importStatusArea.className = 'import-status-area success alert alert-success';
                importStatusMessageText.innerHTML = `<strong>Import Started!</strong><br>${result.message || 'Your world is being generated.'}<br><br>This process typically takes 2-5 minutes. Please return to the <a href="/ui/worlds">My Worlds</a> page in a few minutes to see your newly imported world.`;
                showToast("World import started! Check back in a few minutes.", "success", 8000);
                
                // Reset the form
                bookTitleInput.value = '';
                generateImportButton.disabled = false;
                generateImportButton.innerHTML = originalButtonHTML;

            } else {
                importStatusArea.className = 'import-status-area error alert alert-danger';
                const errorMessage = result.error || result.detail || "An unknown error occurred during import.";
                importStatusMessageText.textContent = `Error: ${errorMessage}`;
                showToast(`Import failed: ${errorMessage}`, "error", 10000);
                generateImportButton.disabled = false;
                generateImportButton.innerHTML = originalButtonHTML;
            }
        } catch (error) {
            console.error('WorldImporterFormHandler: Network or unexpected error during import:', error);
            importStatusArea.className = 'import-status-area error alert alert-danger';
            importStatusMessageText.textContent = "A network error occurred. Please check your connection and try again.";
            showToast("Import request failed. Check connection and server logs.", "error");
            generateImportButton.disabled = false;
            generateImportButton.innerHTML = originalButtonHTML;
        }
    });
});
