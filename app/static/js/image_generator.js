// /ai_rag_story_app/app/static/js/image_generator.js
"use strict";

document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-image-btn');
    if (!generateBtn) return;

    console.log("ImageGenerator.js: Initializing event listener.");

    generateBtn.addEventListener('click', async () => {
        const elementType = generateBtn.dataset.elementType;
        const elementId = generateBtn.dataset.elementId;
        const promptInput = document.getElementById('image_prompt_definition');
        const imageDisplay = document.getElementById('generated-image-display');
        const imageLink = document.getElementById('generated-image-link');
        const imageSpinner = document.getElementById('image-generation-spinner');
        const statusDisplay = document.getElementById('image-generation-status');
        const stylePromptSelect = document.getElementById('image_style_select');

        if (!elementType || !elementId || !promptInput || !imageDisplay || !imageLink || !imageSpinner || !statusDisplay) {
            console.error("Image generator: Missing one or more required page elements.");
            showToast("Cannot generate image, page is missing required elements.", "error");
            return;
        }

        const promptText = promptInput.value.trim();
        if (!promptText) {
            showToast("Please enter an image prompt first.", "warning");
            return;
        }
        
        const stylePromptText = stylePromptSelect ? stylePromptSelect.value : "";

        // UI Changes for Loading State
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Requesting...';
        imageSpinner.style.display = 'block';
        imageDisplay.style.display = 'none';
        imageLink.href = '#';
        imageLink.textContent = '';
        statusDisplay.textContent = 'Job submitted. Waiting for generation to start...';
        statusDisplay.style.display = 'block';

        const payload = {
            element_type: elementType,
            element_id: parseInt(elementId, 10),
            prompt_override: promptText,
            style_prompt: stylePromptText
        };

        try {
            const response = await fetch('/api/v1/images/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                credentials: 'include'
            });

            // Track AI interaction
            if (window.trackAIInteraction) {
                window.trackAIInteraction('image_generation', `dall_e_${elementType}`);
            }

            const result = await response.json();
            if (!response.ok) {
                throw new Error(result.detail || 'Failed to submit image generation job.');
            }

            const jobId = result.job_id;
            showToast("Image generation job started!", "info");
            
            // Track this job globally
            if (window.imageJobMonitor) {
                window.imageJobMonitor.addTrackedJob(jobId, elementType, elementId);
            }
            
            pollJobStatus(jobId);

        } catch (error) {
            console.error("Image generation error:", error);
            showToast(`Error: ${error.message}`, "error");
            resetUIAfterAction();
        }
    });

    function pollJobStatus(jobId) {
        const statusDisplay = document.getElementById('image-generation-status');
        const imageDisplay = document.getElementById('generated-image-display');
        const imageLink = document.getElementById('generated-image-link');
        const promptInput = document.getElementById('image_prompt_definition');

        const intervalId = setInterval(async () => {
            try {
                const response = await fetch(`/api/v1/images/job/${jobId}/status`, { credentials: 'include' });
                if (response.status >= 400) {
                    clearInterval(intervalId);
                    statusDisplay.textContent = `Error checking status (HTTP ${response.status}).`;
                    resetUIAfterAction();
                    return;
                }
                const job = await response.json();

                statusDisplay.textContent = `Status: ${job.state} - ${job.status_message || '...'}`;

                if (job.state === "COMPLETED") {
                    clearInterval(intervalId);
                    showToast("Image generated successfully!", "success");
                    statusDisplay.style.display = 'none';
                    
                    // Remove from global tracking
                    if (window.imageJobMonitor) {
                        window.imageJobMonitor.removeTrackedJob(jobId);
                    }
                    
                    // The result object now contains image metadata
                    if (job.result && job.result.blob_path) {
                        // Refresh the page or fetch updated element to get new image URL
                        window.location.reload();
                    } else {
                        // Fallback: refresh gallery to show new image
                        fetchAndRenderGallery();
                    }
                    resetUIAfterAction(); 
                } else if (job.state === "FAILED") {
                    clearInterval(intervalId);
                    showToast(`Image generation failed: ${job.status_message}`, "error");
                    statusDisplay.textContent = `Failed: ${job.status_message}`;
                    
                    // Remove from global tracking
                    if (window.imageJobMonitor) {
                        window.imageJobMonitor.removeTrackedJob(jobId);
                    }
                    
                    resetUIAfterAction();
                }

            } catch (error) {
                clearInterval(intervalId);
                console.error("Polling error:", error);
                statusDisplay.textContent = 'Polling failed due to a network error.';
                resetUIAfterAction();
            }
        }, 5000);
    }

    function resetUIAfterAction() {
        const generateBtn = document.getElementById('generate-image-btn');
        const imageSpinner = document.getElementById('image-generation-spinner');
        if (generateBtn) {
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic me-1"></i> Generate Image';
        }
        if (imageSpinner) {
            imageSpinner.style.display = 'none';
        }
    }

    function updateMainImage(imageUrl) {
        const imageDisplay = document.getElementById('generated-image-display');
        const imageLink = document.getElementById('generated-image-link');
        if(imageDisplay && imageLink && imageUrl) {
            imageDisplay.src = imageUrl;
            imageDisplay.style.display = 'block';
            imageLink.href = imageUrl;
            imageLink.textContent = "View Full Image";
        }
    }

    async function fetchAndRenderGallery() {
        const galleryContainer = document.getElementById('image-gallery-container');
        const elementId = document.getElementById('generate-image-btn')?.dataset.elementId;
        const elementType = document.getElementById('generate-image-btn')?.dataset.elementType;
        
        if (!galleryContainer || !elementId || !elementType) return;

        galleryContainer.innerHTML = '<div class="text-muted small">Loading versions...</div>';
        
        try {
            // Handle plural form for API URLs
            let elementTypePlural = elementType + 's';
            if (elementType === 'story') {
                elementTypePlural = 'stories';
            } else if (elementType === 'lore_item') {
                elementTypePlural = 'lore_items';
            }
            
            const apiUrl = `/api/v1/${elementTypePlural}/${elementId}/images`;
            const response = await fetch(apiUrl, { credentials: 'include' });
            if (!response.ok) throw new Error('Failed to fetch image gallery.');
            
            const images = await response.json();
            const mainImageDisplay = document.getElementById('generated-image-display');
            const mainImageSrc = mainImageDisplay ? mainImageDisplay.src : '';

            if (images.length > 0) {
                galleryContainer.innerHTML = images.map(img => {
                    const isActive = mainImageSrc && img.url && mainImageSrc === img.url;
                    return `
                        <div class="gallery-thumbnail ${isActive ? 'active' : ''}" data-image-id="${img.id}">
                            <img src="${img.url}" alt="Generated image version" loading="lazy">
                            <button class="btn btn-sm btn-primary set-current-btn" title="Set as current image" ${isActive ? 'disabled' : ''}>
                                <i class="fas fa-check"></i>
                            </button>
                        </div>
                    `;
                }).join('');
            } else {
                galleryContainer.innerHTML = '<p class="text-muted small">No image versions found.</p>';
            }
        } catch (error) {
            console.error("Error fetching image gallery:", error);
            galleryContainer.innerHTML = '<p class="text-danger small">Could not load versions.</p>';
        }
    }

    async function handleSetCurrentImage(imageId) {
        const elementId = document.getElementById('generate-image-btn')?.dataset.elementId;
        const elementType = document.getElementById('generate-image-btn')?.dataset.elementType;

        if (!elementId || !elementType) return;

        showToast("Setting new current image...", "info");

        try {
            // Handle plural form for API URLs
            let elementTypePlural = elementType + 's';
            if (elementType === 'story') {
                elementTypePlural = 'stories';
            } else if (elementType === 'lore_item') {
                elementTypePlural = 'lore_items';
            }
            
            const apiUrl = `/api/v1/${elementTypePlural}/${elementId}/set-current-image/${imageId}`;
            const response = await fetch(apiUrl, { method: 'POST', credentials: 'include' });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Failed to set current image.');
            }

            const updatedElement = await response.json();

            updateMainImage(updatedElement.image_url);
            showToast("Current image updated successfully!", "success");
            fetchAndRenderGallery();

        } catch (error) {
            console.error("Error setting current image:", error);
            showToast(error.message, "error");
        }
    }
    
    const galleryContainer = document.getElementById('image-gallery-container');
    if (galleryContainer) {
        galleryContainer.addEventListener('click', (event) => {
            const setCurrentBtn = event.target.closest('.set-current-btn');
            if (setCurrentBtn && !setCurrentBtn.disabled) {
                const galleryItem = setCurrentBtn.closest('.gallery-thumbnail');
                const imageId = galleryItem.dataset.imageId;
                if (imageId) {
                    handleSetCurrentImage(imageId);
                }
            }
        });
    }

    // Initial load on edit pages
    if (document.getElementById('generate-image-btn')?.dataset.elementId) {
        fetchAndRenderGallery();
    }
});