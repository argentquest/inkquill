// /ai_rag_story_app/app/static/js/story_class_crud.js

/**
 * story_class_crud.js
 * ------------------
 * Handles client-side interactions for managing Story Class entities.
 * Includes color picker functionality and CRUD operations.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = "/api/v1";
    
    // Elements
    const storyClassesGrid = document.getElementById('story-classes-grid');
    const noClassesMessage = document.getElementById('no-classes-message');
    const storyClassModal = document.getElementById('storyClassModal');
    const storyClassForm = document.getElementById('story-class-form');
    const deleteClassModal = document.getElementById('deleteClassModal');
    const confirmDeleteBtn = document.getElementById('confirm-delete-class');
    
    // Form elements
    const classIdInput = document.getElementById('story-class-id');
    const classNameInput = document.getElementById('story-class-name');
    const classDescInput = document.getElementById('story-class-description');
    const classColorInput = document.getElementById('story-class-color');
    const classColorTextInput = document.getElementById('story-class-color-text');
    const colorPreviewCard = document.getElementById('color-preview-card');
    const modalTitle = document.getElementById('storyClassModalLabel');
    const submitButton = storyClassForm.querySelector('button[type="submit"]');
    const submitButtonText = submitButton.querySelector('.button-text');
    const submitButtonSpinner = submitButton.querySelector('.spinner-border');
    
    let currentClassId = null;
    let deleteClassId = null;

    // Initialize
    loadStoryClasses();
    setupEventListeners();

    function setupEventListeners() {
        // Color picker synchronization
        classColorInput.addEventListener('input', (e) => {
            const color = e.target.value;
            classColorTextInput.value = color;
            updateColorPreview(color);
        });

        classColorTextInput.addEventListener('input', (e) => {
            const color = e.target.value;
            if (isValidHexColor(color)) {
                classColorInput.value = color;
                updateColorPreview(color);
            }
        });

        // Form submission
        storyClassForm.addEventListener('submit', handleFormSubmit);

        // Modal events
        storyClassModal.addEventListener('show.bs.modal', () => {
            if (!currentClassId) {
                resetForm();
            }
        });

        // Delete confirmation
        confirmDeleteBtn.addEventListener('click', handleDeleteClass);

        // Grid click events (delegated)
        storyClassesGrid.addEventListener('click', (e) => {
            const editBtn = e.target.closest('.edit-class-btn');
            const deleteBtn = e.target.closest('.delete-class-btn');

            if (editBtn) {
                const classId = parseInt(editBtn.dataset.classId);
                editStoryClass(classId);
            } else if (deleteBtn) {
                const classId = parseInt(deleteBtn.dataset.classId);
                const className = deleteBtn.dataset.className;
                showDeleteConfirmation(classId, className);
            }
        });
    }

    function isValidHexColor(color) {
        return /^#[0-9A-Fa-f]{6}$/.test(color);
    }

    function updateColorPreview(color) {
        if (isValidHexColor(color)) {
            colorPreviewCard.style.backgroundColor = color;
            
            // Adjust text color based on background brightness
            const brightness = getBrightness(color);
            colorPreviewCard.style.color = brightness > 128 ? '#000000' : '#ffffff';
        }
    }

    function getBrightness(hexColor) {
        // Convert hex to RGB and calculate brightness
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        return (r * 299 + g * 587 + b * 114) / 1000;
    }

    async function loadStoryClasses() {
        try {
            // Build URL with world context
            let url = `${API_BASE_URL}/story-classes/`;
            const params = new URLSearchParams();
            
            // Get world context from window object (set by template)
            if (window.storyClassContext) {
                if (window.storyClassContext.worldId) {
                    params.append('world_id', window.storyClassContext.worldId);
                } else if (window.storyClassContext.storyId) {
                    params.append('story_id', window.storyClassContext.storyId);
                }
            }
            
            if (params.toString()) {
                url += '?' + params.toString();
            }

            const response = await fetch(url, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to load story classes: ${response.status}`);
            }

            const storyClasses = await response.json();
            displayStoryClasses(storyClasses);

        } catch (error) {
            console.error('Error loading story classes:', error);
            if (typeof showToast === 'function') {
                showToast('Failed to load story classes', 'error');
            }
        }
    }

    function displayStoryClasses(storyClasses) {
        if (!storyClasses || storyClasses.length === 0) {
            storyClassesGrid.style.display = 'none';
            noClassesMessage.style.display = 'block';
            return;
        }

        storyClassesGrid.style.display = 'block';
        noClassesMessage.style.display = 'none';

        storyClassesGrid.innerHTML = storyClasses.map(storyClass => {
            const brightness = getBrightness(storyClass.color);
            const textColor = brightness > 128 ? '#000000' : '#ffffff';
            
            return `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="card h-100" style="background-color: ${storyClass.color}; color: ${textColor};">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title mb-0">${escapeHtml(storyClass.name)}</h5>
                                <div class="dropdown">
                                    <button class="btn btn-sm btn-outline-light" type="button" data-bs-toggle="dropdown" 
                                            style="border-color: ${textColor}; color: ${textColor};">
                                        <i class="fas fa-ellipsis-v"></i>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li>
                                            <a class="dropdown-item edit-class-btn" href="#" data-class-id="${storyClass.id}">
                                                <i class="fas fa-edit me-2"></i>Edit
                                            </a>
                                        </li>
                                        <li>
                                            <a class="dropdown-item text-danger delete-class-btn" href="#" 
                                               data-class-id="${storyClass.id}" data-class-name="${escapeHtml(storyClass.name)}">
                                                <i class="fas fa-trash me-2"></i>Delete
                                            </a>
                                        </li>
                                    </ul>
                                </div>
                            </div>
                            
                            ${storyClass.description ? `
                                <p class="card-text small mb-2">${escapeHtml(storyClass.description)}</p>
                            ` : ''}
                            
                            <div class="mt-auto">
                                <small class="text-white-50">
                                    Color: ${storyClass.color.toUpperCase()}
                                </small>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    function resetForm() {
        currentClassId = null;
        classIdInput.value = '';
        classNameInput.value = '';
        classDescInput.value = '';
        classColorInput.value = '#007bff';
        classColorTextInput.value = '#007bff';
        updateColorPreview('#007bff');
        modalTitle.textContent = 'Create Story Class';
        submitButtonText.textContent = 'Create Class';
        
        // Clear validation states
        [classNameInput, classDescInput, classColorTextInput].forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
        });
    }

    async function editStoryClass(classId) {
        try {
            const response = await fetch(`${API_BASE_URL}/story-classes/${classId}`, {
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error(`Failed to load story class: ${response.status}`);
            }

            const storyClass = await response.json();
            
            // Populate form
            currentClassId = classId;
            classIdInput.value = classId;
            classNameInput.value = storyClass.name;
            classDescInput.value = storyClass.description || '';
            classColorInput.value = storyClass.color;
            classColorTextInput.value = storyClass.color;
            updateColorPreview(storyClass.color);
            
            modalTitle.textContent = 'Edit Story Class';
            submitButtonText.textContent = 'Update Class';
            
            // Show modal
            const modal = new bootstrap.Modal(storyClassModal);
            modal.show();

        } catch (error) {
            console.error('Error loading story class:', error);
            if (typeof showToast === 'function') {
                showToast('Failed to load story class details', 'error');
            }
        }
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(storyClassForm);
        const data = {
            name: formData.get('name').trim(),
            description: formData.get('description').trim() || null,
            color: formData.get('color').toUpperCase()
        };

        // Validation
        if (!data.name) {
            classNameInput.classList.add('is-invalid');
            return;
        }

        if (!isValidHexColor(data.color)) {
            classColorTextInput.classList.add('is-invalid');
            return;
        }

        // Show loading state
        submitButton.disabled = true;
        submitButtonSpinner.style.display = 'inline-block';

        try {
            let url = currentClassId 
                ? `${API_BASE_URL}/story-classes/${currentClassId}`
                : `${API_BASE_URL}/story-classes/`;
            
            // Add world context for creation
            if (!currentClassId) {
                const params = new URLSearchParams();
                if (window.storyClassContext) {
                    if (window.storyClassContext.worldId) {
                        params.append('world_id', window.storyClassContext.worldId);
                    } else if (window.storyClassContext.storyId) {
                        params.append('story_id', window.storyClassContext.storyId);
                    }
                }
                if (params.toString()) {
                    url += '?' + params.toString();
                }
            }
            
            const method = currentClassId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            const result = await response.json();
            
            if (typeof showToast === 'function') {
                showToast(
                    currentClassId ? 'Story class updated successfully!' : 'Story class created successfully!',
                    'success'
                );
            }

            // Close modal and reload
            const modal = bootstrap.Modal.getInstance(storyClassModal);
            modal.hide();
            await loadStoryClasses();

        } catch (error) {
            console.error('Error saving story class:', error);
            if (typeof showToast === 'function') {
                showToast(`Error saving story class: ${error.message}`, 'error');
            }
        } finally {
            // Reset loading state
            submitButton.disabled = false;
            submitButtonSpinner.style.display = 'none';
        }
    }

    function showDeleteConfirmation(classId, className) {
        deleteClassId = classId;
        document.getElementById('delete-class-name').textContent = className;
        
        const modal = new bootstrap.Modal(deleteClassModal);
        modal.show();
    }

    async function handleDeleteClass() {
        if (!deleteClassId) return;

        const spinner = confirmDeleteBtn.querySelector('.spinner-border');
        confirmDeleteBtn.disabled = true;
        spinner.style.display = 'inline-block';

        try {
            const response = await fetch(`${API_BASE_URL}/story-classes/${deleteClassId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}`);
            }

            if (typeof showToast === 'function') {
                showToast('Story class deleted successfully!', 'success');
            }

            // Close modal and reload
            const modal = bootstrap.Modal.getInstance(deleteClassModal);
            modal.hide();
            await loadStoryClasses();

        } catch (error) {
            console.error('Error deleting story class:', error);
            if (typeof showToast === 'function') {
                showToast(`Error deleting story class: ${error.message}`, 'error');
            }
        } finally {
            confirmDeleteBtn.disabled = false;
            spinner.style.display = 'none';
            deleteClassId = null;
        }
    }
});