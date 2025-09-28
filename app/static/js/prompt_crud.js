// /ai_rag_story_app/app/static/js/prompt_crud.js

/**
 * prompt_crud.js
 * --------------
 * Handles client-side interactions for managing Prompt entities, including
 * deletion and the new "Quick Use" feature.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    console.log("Prompt CRUD JS: DOMContentLoaded - Script initialized.");

    const API_BASE_URL = "/api/v1";
    const promptsListContainer = document.getElementById('prompts-list-container');

    // --- New elements for "Use Prompt" Modal ---
    const usePromptModalElement = document.getElementById('usePromptModal');
    const usePromptModal = usePromptModalElement ? new bootstrap.Modal(usePromptModalElement) : null;
    const storySelect = document.getElementById('use-prompt-story-select');
    const actSelect = document.getElementById('use-prompt-act-select');
    const modalContentStorage = document.getElementById('use-prompt-modal-content-storage');
    const goToEditorBtn = document.getElementById('use-prompt-go-to-editor-btn');
    const modalErrorDiv = document.getElementById('use-prompt-modal-error');
    
    if (promptsListContainer) {
        promptsListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-prompt-btn');
            const useButton = event.target.closest('.use-prompt-btn');

            if (deleteButton) {
                // ... (existing delete logic remains unchanged) ...
                event.preventDefault();
                const promptId = deleteButton.dataset.promptId;
                if (!promptId) {
                    showToast("Could not determine which prompt to delete.", "error");
                    return;
                }
                if (confirm(`Are you sure you want to delete prompt ${promptId}? This action cannot be undone.`)) {
                    const originalButtonHTML = deleteButton.innerHTML;
                    deleteButton.disabled = true;
                    deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm"></span>`;
                    try {
                        const response = await fetch(`${API_BASE_URL}/prompts/${promptId}`, { method: 'DELETE', credentials: 'include' });
                        if (response.status === 204) {
                            showToast('Prompt deleted successfully!', "success");
                            deleteButton.closest('tr').remove();
                        } else {
                            const errorData = await response.json().catch(() => ({}));
                            showToast(`Error deleting prompt: ${errorData.detail || 'Unknown error'}`, "error");
                            deleteButton.disabled = false;
                            deleteButton.innerHTML = originalButtonHTML;
                        }
                    } catch (error) {
                        showToast('An error occurred while deleting the prompt.', "error");
                        deleteButton.disabled = false;
                        deleteButton.innerHTML = originalButtonHTML;
                    }
                }
            } else if (useButton && usePromptModal) {
                // --- NEW "Use Prompt" LOGIC ---
                event.preventDefault();
                const promptContent = useButton.dataset.promptContent;
                if (modalContentStorage) modalContentStorage.value = promptContent;

                // Reset modal state
                if (modalErrorDiv) modalErrorDiv.style.display = 'none';
                if (actSelect) {
                    actSelect.innerHTML = '<option value="">-- Select a story first --</option>';
                    actSelect.disabled = true;
                }
                if (goToEditorBtn) goToEditorBtn.disabled = true;

                // Fetch stories and populate dropdown
                if (storySelect) {
                    storySelect.innerHTML = '<option value="">Loading stories...</option>';
                    try {
                        const response = await fetch(`${API_BASE_URL}/stories/`);
                        if (!response.ok) throw new Error('Failed to fetch stories.');
                        const stories = await response.json();
                        storySelect.innerHTML = '<option value="">-- Select a story --</option>';
                        if (stories.length > 0) {
                            stories.forEach(story => {
                                const option = document.createElement('option');
                                option.value = story.id;
                                option.textContent = story.title;
                                storySelect.appendChild(option);
                            });
                        } else {
                            storySelect.innerHTML = '<option value="">No stories found.</option>';
                        }
                    } catch (error) {
                        console.error("Error fetching stories for modal:", error);
                        if(modalErrorDiv) {
                            modalErrorDiv.textContent = "Could not load your stories.";
                            modalErrorDiv.style.display = 'block';
                        }
                        storySelect.innerHTML = '<option value="">Error loading stories</option>';
                    }
                }
                usePromptModal.show();
            }
        });
    }

    // --- NEW Event Listeners for Modal ---
    if (storySelect && actSelect) {
        storySelect.addEventListener('change', async () => {
            const storyId = storySelect.value;
            actSelect.innerHTML = '<option value="">Loading acts...</option>';
            actSelect.disabled = true;
            if (goToEditorBtn) goToEditorBtn.disabled = true;

            if (!storyId) {
                actSelect.innerHTML = '<option value="">-- Select a story first --</option>';
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/stories/${storyId}/acts`);
                if (!response.ok) throw new Error('Failed to fetch acts.');
                const acts = await response.json();
                actSelect.innerHTML = '<option value="">-- Select an act --</option>';
                if (acts.length > 0) {
                    acts.forEach(act => {
                        const option = document.createElement('option');
                        option.value = act.id;
                        option.textContent = `Act ${act.act_number}: ${act.title}`;
                        actSelect.appendChild(option);
                    });
                    actSelect.disabled = false;
                } else {
                    actSelect.innerHTML = '<option value="">No acts found in this story.</option>';
                }
            } catch (error) {
                console.error("Error fetching acts for modal:", error);
                if(modalErrorDiv) {
                    modalErrorDiv.textContent = "Could not load acts for the selected story.";
                    modalErrorDiv.style.display = 'block';
                }
                actSelect.innerHTML = '<option value="">Error loading acts</option>';
            }
        });
    }

    if (actSelect && goToEditorBtn) {
        actSelect.addEventListener('change', () => {
            goToEditorBtn.disabled = !actSelect.value;
        });
    }

    if (goToEditorBtn && storySelect && actSelect && modalContentStorage) {
        goToEditorBtn.addEventListener('click', () => {
            const storyId = storySelect.value;
            const actId = actSelect.value;
            const promptContent = modalContentStorage.value;

            if (storyId && actId && promptContent) {
                // Use localStorage to pass the prompt content
                localStorage.setItem('prefillAIPrompt', promptContent);
                // Redirect to the Act Editor
                window.location.href = `/ui/stories/${storyId}/acts/${actId}/edit-content`;
            } else {
                showToast("Please select both a story and an act.", "warning");
            }
        });
    }

});