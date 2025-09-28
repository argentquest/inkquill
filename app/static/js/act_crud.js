// /ai_rag_story_app/app/static/js/act_crud.js

/**
 * act_crud.js
 * -----------
 * Handles client-side interactions for managing Act entities.
 * Relies on a global escapeHtml function from utils.js.
 */

"use strict";

document.addEventListener('DOMContentLoaded', () => {
    // ... (rest of the file remains the same, just the escapeHtml function is removed) ...

    const API_BASE_URL = "/api/v1"; 
    const actsListContainer = document.getElementById('acts-list-container');

    if (actsListContainer) {
        actsListContainer.addEventListener('click', async (event) => {
            const deleteButton = event.target.closest('.delete-act-btn');
            const generateScenesButton = event.target.closest('.generate-scenes-btn');
            const compileScenesButton = event.target.closest('.compile-scenes-to-act-btn'); 

            if (deleteButton) {
                await handleDeleteAct(deleteButton);
            } else if (generateScenesButton) {
                await handleGenerateScenes(generateScenesButton);
            } else if (compileScenesButton) {
                await handleCompileScenes(compileScenesButton);
            }
        });

        const actCards = actsListContainer.querySelectorAll('.act-card[data-act-id]');
        actCards.forEach(card => {
            const actId = card.dataset.actId;
            const generateBtn = card.querySelector('.generate-scenes-btn');
            const storyId = generateBtn ? generateBtn.dataset.storyId : null; 
            const scenesContainer = document.getElementById(`scenes-for-act-${actId}`);
            const noScenesMessageEl = scenesContainer ? scenesContainer.querySelector('.no-scenes-message') : null;
            const statusElement = document.getElementById(`generate-scenes-status-${actId}`); 
            if (actId && storyId && scenesContainer) {
                fetchAndDisplayScenes(actId, storyId, scenesContainer, noScenesMessageEl, statusElement);
            }
        });
    }

    async function fetchAndDisplayScenes(actId, storyId, scenesContainerElement, noScenesMsgElement, statusMsgElement) {
        if (!actId || !scenesContainerElement) {
            console.error("Act CRUD JS (fetchAndDisplayScenes): Missing actId or scenesContainerElement for Act ID:", actId);
            return;
        }

        scenesContainerElement.innerHTML = '<div class="text-center p-3"><span class="spinner-border spinner-border-sm"></span> Loading scenes...</div>';
        
        try {
            const fetchUrl = `${API_BASE_URL}/acts/${actId}/scenes/`;
            const response = await fetch(fetchUrl, { credentials: 'include' });
            if (!response.ok) {
                throw new Error(`Failed to fetch scenes: ${response.status}`);
            }
            const scenes = await response.json();
            scenesContainerElement.innerHTML = '';

            if (scenes.length > 0) {
                if (noScenesMsgElement) noScenesMsgElement.style.display = 'none';
                const sceneCardsContainer = document.createElement('div');
                sceneCardsContainer.className = 'row row-cols-1 row-cols-md-2 g-3 mt-2';
                scenes.forEach(scene => {
                    // Calculate background color and text color if scene has a story class
                    let cardHeaderStyle = '';
                    let buttonClasses = 'btn btn-primary btn-sm';
                    let deleteButtonClasses = 'btn btn-primary btn-sm';
                    
                    if (scene.story_class && scene.story_class.color) {
                        const brightness = getBrightness(scene.story_class.color);
                        const textColor = brightness > 128 ? '#000000' : '#ffffff';
                        
                        // Convert hex to rgba with 10% opacity for header background
                        const hexColor = scene.story_class.color;
                        const r = parseInt(hexColor.slice(1, 3), 16);
                        const g = parseInt(hexColor.slice(3, 5), 16);
                        const b = parseInt(hexColor.slice(5, 7), 16);
                        const headerBgColor = `rgba(${r}, ${g}, ${b}, 0.1)`;
                        
                        cardHeaderStyle = `style="background-color: ${headerBgColor}; border-bottom: 2px solid ${scene.story_class.color};"`;
                        
                        // Button styles remain consistent regardless of brightness
                        buttonClasses = 'btn btn-primary btn-sm';
                        deleteButtonClasses = 'btn btn-primary btn-sm';
                    }
                    
                    // Story class badge HTML
                    const storyClassBadge = scene.story_class ? `
                        <span class="badge story-class-badge ms-2" 
                              style="background-color: ${scene.story_class.color || 'var(--primary-color)'}; 
                                     color: ${scene.story_class.color ? (getBrightness(scene.story_class.color) > 128 ? '#000000' : '#ffffff') : 'white'};">
                            ${escapeHtml(scene.story_class.name)}
                        </span>
                    ` : '';
                    
                    // Parse scene elements from plot_points
                    let sceneElements = { characters: [], locations: [], lore_items: [] };
                    if (scene.plot_points) {
                        try {
                            sceneElements = JSON.parse(scene.plot_points);
                        } catch (e) {
                            // Fallback to characters_present if plot_points is not JSON
                            if (scene.characters_present) {
                                sceneElements.characters = scene.characters_present.split(', ').filter(c => c.trim());
                            }
                        }
                    } else if (scene.characters_present) {
                        sceneElements.characters = scene.characters_present.split(', ').filter(c => c.trim());
                    }
                    
                    // Generate elements HTML
                    const elementsHTML = generateSceneElementsHTML(sceneElements);
                    
                    // Generate thumbnail HTML
                    const thumbnailHTML = scene.image_url 
                        ? `<img src="${scene.image_url}" alt="${escapeHtml(scene.title) || 'Untitled Scene'} thumbnail" class="thumbnail-128">`
                        : `<div class="thumbnail-placeholder">
                               <div>
                                   <i class="fas fa-theater-masks mb-1" style="font-size: 24px;"></i><br>
                                   <small>No Image</small>
                               </div>
                           </div>`;

                    const sceneCardHTML = `
                        <div class="col">
                            <div class="card shadow-sm scene-card h-100" data-scene-id="${scene.id}">
                                <div class="card-header py-2 d-flex justify-content-between align-items-center" ${cardHeaderStyle}>
                                    <h6 class="card-title mb-0">
                                        <a href="/ui/scenes/${scene.id}/edit" class="text-decoration-none" 
                                           style="color: inherit;">
                                            <i class="fas fa-theater-masks me-1" style="font-size: 0.875rem;"></i>
                                            Scene ${escapeHtml(scene.scene_number)}: ${escapeHtml(scene.title) || 'Untitled Scene'}
                                        </a>
                                        ${storyClassBadge}
                                    </h6>
                                    <div class="d-flex gap-2">
                                        <a href="/ui/scenes/${scene.id}/edit" class="${buttonClasses}"
                                           data-bs-toggle="tooltip" data-bs-placement="bottom" 
                                           title="Open scene editor to develop content and edit scene details">
                                            <i class="fas fa-edit"></i>
                                        </a>
                                        <button class="${deleteButtonClasses} delete-scene-btn" data-scene-id="${scene.id}" data-act-id="${actId}"
                                                data-bs-toggle="tooltip" data-bs-placement="bottom" 
                                                title="Permanently delete this scene">
                                            <i class="fas fa-trash-alt"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="card-body d-flex flex-column">
                                    <div class="d-flex gap-3 mb-3">
                                        <!-- Scene Thumbnail -->
                                        <div>
                                            ${thumbnailHTML}
                                        </div>
                                        
                                        <!-- Scene Content -->
                                        <div class="flex-grow-1">
                                            ${scene.summary ? `<p class="card-text small mb-2"><strong>Summary:</strong> ${escapeHtml(scene.summary)}</p>` : '<p class="card-text text-muted small mb-2"><em>No summary available</em></p>'}
                                            ${elementsHTML}
                                        </div>
                                    </div>
                                    <div class="mt-auto">
                                        <small class="text-muted d-block">
                                            <i class="fas fa-clock me-1"></i>Updated: ${scene.updated_at ? new Date(scene.updated_at).toLocaleDateString() : 'N/A'}
                                        </small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    sceneCardsContainer.insertAdjacentHTML('beforeend', sceneCardHTML);
                });
                scenesContainerElement.appendChild(sceneCardsContainer);
                
                // Initialize tooltips for newly added scene cards
                const newTooltipElements = sceneCardsContainer.querySelectorAll('[data-bs-toggle="tooltip"]');
                newTooltipElements.forEach(tooltipTriggerEl => {
                    new bootstrap.Tooltip(tooltipTriggerEl);
                });
            } else {
                if (noScenesMsgElement) {
                    noScenesMsgElement.textContent = "No scenes have been generated or found for this act yet.";
                    noScenesMsgElement.style.display = 'block';
                }
            }
        } catch (error) {
            console.error(`Error fetching/displaying scenes for Act ID ${actId}:`, error);
            scenesContainerElement.innerHTML = '<p class="text-danger p-2">Failed to load scenes.</p>';
        }
    }

    async function handleDeleteAct(deleteButton) {
        const actId = deleteButton.dataset.actId;
        const storyId = deleteButton.dataset.storyId;
        
        if (!actId) {
            console.error("Act CRUD JS: Delete act button missing data-act-id.");
            if (typeof showToast === 'function') {
                showToast("Could not determine which act to delete.", "error");
            }
            return;
        }

        if (confirm("Are you sure you want to delete this act? This action cannot be undone.")) {
            const originalButtonHTML = deleteButton.innerHTML;
            deleteButton.disabled = true;
            deleteButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Deleting...`;

            try {
                const response = await fetch(`${API_BASE_URL}/acts/${actId}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });

                if (response.status === 204) {
                    if (typeof showToast === 'function') {
                        showToast('Act deleted successfully!', "success");
                    }
                    // Remove the act card from the DOM
                    const actCard = deleteButton.closest('.act-card');
                    if (actCard) {
                        actCard.remove();
                    }
                    // Optionally reload the page to refresh act numbering
                    setTimeout(() => window.location.reload(), 1000);
                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const detail = errorData?.detail || `Failed to delete act (Status: ${response.status})`;
                    console.error(`Failed to delete act ${actId}:`, detail);
                    if (typeof showToast === 'function') {
                        showToast(`Error deleting act: ${detail}`, "error");
                    }
                    deleteButton.disabled = false;
                    deleteButton.innerHTML = originalButtonHTML;
                }
            } catch (error) {
                console.error('Error deleting act:', error);
                if (typeof showToast === 'function') {
                    showToast('An error occurred while trying to delete the act.', "error");
                }
                deleteButton.disabled = false;
                deleteButton.innerHTML = originalButtonHTML;
            }
        }
    }

    async function handleGenerateScenes(generateButton) {
        const actId = generateButton.dataset.actId;
        const storyId = generateButton.dataset.storyId;
        
        if (!actId) {
            console.error("Act CRUD JS: Generate scenes button missing data-act-id.");
            if (typeof showToast === 'function') {
                showToast("Could not determine which act to generate scenes for.", "error");
            }
            return;
        }

        const originalButtonHTML = generateButton.innerHTML;
        const statusElement = document.getElementById(`generate-scenes-status-${actId}`);
        
        generateButton.disabled = true;
        generateButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating...`;
        
        if (statusElement) {
            statusElement.style.display = 'block';
            statusElement.innerHTML = '<span class="text-info">AI is analyzing the act content and generating scenes...</span>';
        }

        try {
            const response = await fetch(`${API_BASE_URL}/acts/${actId}/scenes/generate-scenes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include'
            });

            if (response.status === 202) {
                const result = await response.json();
                if (typeof showToast === 'function') {
                    showToast('Scene generation started! Scenes will appear shortly.', "success");
                }
                
                if (statusElement) {
                    statusElement.innerHTML = '<span class="text-success">Scene generation in progress. Refreshing in 3 seconds...</span>';
                }
                
                // Refresh the scenes list with multiple retries
                let retryCount = 0;
                const maxRetries = 3;
                const baseDelay = 3000; // 3 seconds base delay
                
                const refreshScenes = async () => {
                    const scenesContainer = document.getElementById(`scenes-for-act-${actId}`);
                    const noScenesMessage = scenesContainer ? scenesContainer.querySelector('.no-scenes-message') : null;
                    
                    if (scenesContainer) {
                        await fetchAndDisplayScenes(actId, storyId, scenesContainer, noScenesMessage, statusElement);
                        
                        // Check if scenes were actually loaded
                        const loadedScenes = scenesContainer.querySelectorAll('.scene-card');
                        if (loadedScenes.length === 0 && retryCount < maxRetries) {
                            retryCount++;
                            if (statusElement) {
                                statusElement.innerHTML = `<span class="text-info">Waiting for scenes to be generated... (Attempt ${retryCount}/${maxRetries})</span>`;
                            }
                            // Exponential backoff: 3s, 6s, 12s
                            setTimeout(refreshScenes, baseDelay * Math.pow(2, retryCount - 1));
                            return;
                        }
                    }
                    
                    generateButton.disabled = false;
                    generateButton.innerHTML = originalButtonHTML;
                    
                    if (statusElement) {
                        const currentSceneCount = scenesContainer.querySelectorAll('.scene-card').length;
                        if (currentSceneCount === 0) {
                            statusElement.innerHTML = '<span class="text-warning">Scene generation completed but scenes may take a moment to appear. Please refresh the page if scenes don\'t show up.</span>';
                            setTimeout(() => {
                                statusElement.style.display = 'none';
                            }, 15000);
                        } else {
                            statusElement.innerHTML = `<span class="text-success">Successfully generated ${currentSceneCount} scene${currentSceneCount > 1 ? 's' : ''}!</span>`;
                            setTimeout(() => {
                                statusElement.style.display = 'none';
                            }, 5000);
                        }
                    }
                };
                
                setTimeout(refreshScenes, baseDelay);
                
            } else {
                const errorData = await response.json().catch(() => ({}));
                let detail = errorData?.detail || `Failed to generate scenes (Status: ${response.status})`;
                
                if (response.status === 400 && detail.includes('no content')) {
                    detail = "Act has no content to generate scenes from. Please add content to the act first.";
                }
                
                console.error(`Failed to generate scenes for act ${actId}:`, detail);
                if (typeof showToast === 'function') {
                    showToast(`Error generating scenes: ${detail}`, "error", 7000);
                }
                
                generateButton.disabled = false;
                generateButton.innerHTML = originalButtonHTML;
                
                if (statusElement) {
                    statusElement.innerHTML = `<span class="text-danger">Error: ${detail}</span>`;
                    setTimeout(() => {
                        statusElement.style.display = 'none';
                    }, 5000);
                }
            }
        } catch (error) {
            console.error('Error generating scenes:', error);
            if (typeof showToast === 'function') {
                showToast('An error occurred while trying to generate scenes.', "error");
            }
            
            generateButton.disabled = false;
            generateButton.innerHTML = originalButtonHTML;
            
            if (statusElement) {
                statusElement.innerHTML = '<span class="text-danger">Network error occurred.</span>';
                setTimeout(() => {
                    statusElement.style.display = 'none';
                }, 5000);
            }
        }
    }

    async function handleCompileScenes(compileButton) {
        const actId = compileButton.dataset.actId;
        
        if (!actId) {
            console.error("Act CRUD JS: Compile scenes button missing data-act-id.");
            if (typeof showToast === 'function') {
                showToast("Could not determine which act to compile scenes for.", "error");
            }
            return;
        }

        if (!confirm("This will overwrite the current act content with compiled scenes. Are you sure?")) {
            return;
        }

        const originalButtonHTML = compileButton.innerHTML;
        compileButton.disabled = true;
        compileButton.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Compiling...`;

        try {
            // This would need an API endpoint for compiling scenes - placeholder for now
            if (typeof showToast === 'function') {
                showToast('Scene compilation feature coming soon!', "info");
            }
            
            compileButton.disabled = false;
            compileButton.innerHTML = originalButtonHTML;
        } catch (error) {
            console.error('Error compiling scenes:', error);
            if (typeof showToast === 'function') {
                showToast('An error occurred while trying to compile scenes.', "error");
            }
            
            compileButton.disabled = false;
            compileButton.innerHTML = originalButtonHTML;
        }
    }

    function getBrightness(hexColor) {
        // Convert hex to RGB and calculate brightness
        const r = parseInt(hexColor.substr(1, 2), 16);
        const g = parseInt(hexColor.substr(3, 2), 16);
        const b = parseInt(hexColor.substr(5, 2), 16);
        return (r * 299 + g * 587 + b * 114) / 1000;
    }
    
    // Helper function to generate scene elements HTML
    function generateSceneElementsHTML(sceneElements) {
        if (!sceneElements || (!sceneElements.characters?.length && !sceneElements.locations?.length && !sceneElements.lore_items?.length)) {
            return '';
        }
        
        let elementsHTML = '<div class="scene-elements mt-2 mb-2">';
        
        // Characters
        if (sceneElements.characters?.length) {
            elementsHTML += '<div class="element-group mb-1">';
            elementsHTML += '<small class="text-muted d-block mb-1"><i class="fas fa-users me-1"></i>Characters</small>';
            elementsHTML += '<div class="element-badges">';
            sceneElements.characters.forEach(char => {
                elementsHTML += `<span class="badge bg-primary me-1 mb-1" style="font-size: 0.7rem;">${escapeHtml(char)}</span>`;
            });
            elementsHTML += '</div></div>';
        }
        
        // Locations
        if (sceneElements.locations?.length) {
            elementsHTML += '<div class="element-group mb-1">';
            elementsHTML += '<small class="text-muted d-block mb-1"><i class="fas fa-map-marker-alt me-1"></i>Locations</small>';
            elementsHTML += '<div class="element-badges">';
            sceneElements.locations.forEach(loc => {
                elementsHTML += `<span class="badge bg-success me-1 mb-1" style="font-size: 0.7rem;">${escapeHtml(loc)}</span>`;
            });
            elementsHTML += '</div></div>';
        }
        
        // Lore Items
        if (sceneElements.lore_items?.length) {
            elementsHTML += '<div class="element-group mb-1">';
            elementsHTML += '<small class="text-muted d-block mb-1"><i class="fas fa-scroll me-1"></i>Lore Items</small>';
            elementsHTML += '<div class="element-badges">';
            sceneElements.lore_items.forEach(lore => {
                elementsHTML += `<span class="badge bg-warning text-dark me-1 mb-1" style="font-size: 0.7rem;">${escapeHtml(lore)}</span>`;
            });
            elementsHTML += '</div></div>';
        }
        
        elementsHTML += '</div>';
        return elementsHTML;
    }

     // <<< MODIFICATION: The local escapeHtml function is REMOVED from here. >>>
});