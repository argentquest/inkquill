// Analytics Tracking Implementation Examples
// This file shows how to implement enhanced Google Analytics tracking throughout the application

// ============================================
// 1. STORY MANAGEMENT TRACKING
// ============================================

// Track story creation
function trackStoryCreation(storyData) {
    if (window.trackStoryAction) {
        window.trackStoryAction('create', storyData.id, storyData.title);
    }
    
    // Track additional details
    if (window.trackFeatureUse) {
        window.trackFeatureUse('story_creation', 'complete', {
            world_id: storyData.world_id,
            has_description: !!storyData.short_description,
            initial_acts: storyData.acts_count || 0
        });
    }
}

// Track story deletion (add to story_crud.js after successful deletion)
function trackStoryDeletion(storyId, storyTitle) {
    if (window.trackStoryAction) {
        window.trackStoryAction('delete', storyId, storyTitle);
    }
}

// Track story publishing
function trackStoryPublishing(storyId, storyTitle, wordCount) {
    if (window.trackStoryAction) {
        window.trackStoryAction('publish', storyId, storyTitle);
    }
    
    if (window.trackFeatureUse) {
        window.trackFeatureUse('story_publishing', 'complete', {
            word_count: wordCount,
            has_images: true,
            publish_time: new Date().toISOString()
        });
    }
}

// ============================================
// 2. AI INTERACTION TRACKING
// ============================================

// Track AI content generation
function trackAIContentGeneration(responseData) {
    if (window.trackAIInteraction) {
        window.trackAIInteraction(
            'content_generation',
            responseData.model || 'gpt-4',
            responseData.total_tokens,
            responseData.estimated_cost
        );
    }
}

// Track AI scene writing assistance
function trackAISceneAssistance(sceneId, tokens) {
    if (window.trackAIInteraction) {
        window.trackAIInteraction('scene_assistance', 'gpt-4', tokens);
    }
    
    if (window.trackFeatureUse) {
        window.trackFeatureUse('ai_scene_writer', 'assist', {
            scene_id: sceneId,
            suggestion_accepted: true
        });
    }
}

// ============================================
// 3. IMAGE GENERATION TRACKING
// ============================================

// Track image generation (add to image generation function)
function trackImageGenerationStart(elementType, elementId, prompt) {
    if (window.trackImageGeneration) {
        window.trackImageGeneration(elementType, elementId, prompt);
    }
}

// Track image generation completion
function trackImageGenerationComplete(elementType, success, generationTime) {
    if (window.trackFeatureUse) {
        window.trackFeatureUse('image_generation', success ? 'success' : 'failure', {
            element_type: elementType,
            generation_time_ms: generationTime,
            model: 'dall-e-3'
        });
    }
}

// ============================================
// 4. WORLD BUILDING TRACKING
// ============================================

// Track world creation
function trackWorldCreation(worldData) {
    if (window.trackWorldAction) {
        window.trackWorldAction('create', worldData.id, worldData.name);
    }
}

// Track book import
function trackBookImport(worldId, worldName, bookTitle, importStats) {
    if (window.trackWorldAction) {
        window.trackWorldAction('import_from_book', worldId, worldName);
    }
    
    if (window.trackFeatureUse) {
        window.trackFeatureUse('book_import', 'complete', {
            book_title: bookTitle,
            characters_imported: importStats.characters || 0,
            locations_imported: importStats.locations || 0,
            lore_items_imported: importStats.lore_items || 0
        });
    }
}

// ============================================
// 5. USER ENGAGEMENT TRACKING
// ============================================

// Track feature discovery
function trackFeatureDiscovery(featureName) {
    if (window.trackFeatureUse) {
        window.trackFeatureUse(featureName, 'discover', {
            first_time: !localStorage.getItem(`feature_used_${featureName}`)
        });
        localStorage.setItem(`feature_used_${featureName}`, 'true');
    }
}

// Track user preferences
function trackUserPreference(preferenceName, value) {
    if (window.trackFeatureUse) {
        window.trackFeatureUse('user_preferences', 'change', {
            preference: preferenceName,
            value: value
        });
    }
}

// ============================================
// 6. ERROR TRACKING
// ============================================

// Track application errors
function trackApplicationError(error, context) {
    if (window.trackError) {
        window.trackError(error.message || error, context);
    }
}

// Track API errors
function trackAPIError(endpoint, statusCode, errorMessage) {
    if (window.trackError) {
        window.trackError(`API Error: ${statusCode} - ${errorMessage}`, endpoint);
    }
}

// ============================================
// 7. PAGE VIEW TRACKING WITH CONTEXT
// ============================================

// Track story editor page view
function trackStoryEditorView(storyId, storyTitle, wordCount) {
    if (window.trackPageView) {
        window.trackPageView('Story Editor', {
            story_id: storyId,
            story_title: storyTitle,
            word_count: wordCount,
            edit_session_start: new Date().toISOString()
        });
    }
}

// Track world detail page view
function trackWorldDetailView(worldId, worldName, elementCounts) {
    if (window.trackPageView) {
        window.trackPageView('World Detail', {
            world_id: worldId,
            world_name: worldName,
            character_count: elementCounts.characters || 0,
            location_count: elementCounts.locations || 0,
            lore_count: elementCounts.lore_items || 0
        });
    }
}

// ============================================
// 8. IMPLEMENTATION HELPERS
// ============================================

// Wrapper function to safely call tracking functions
function safeTrack(trackingFunction, ...args) {
    try {
        if (typeof trackingFunction === 'function') {
            trackingFunction(...args);
        }
    } catch (error) {
        console.error('Tracking error:', error);
    }
}

// Batch tracking for multiple events
function batchTrack(events) {
    events.forEach(event => {
        safeTrack(event.fn, ...event.args);
    });
}

// ============================================
// 9. INTEGRATION EXAMPLES
// ============================================

// Example: Integrate with story deletion in story_crud.js
/*
// Add after line 54 in story_crud.js:
if (window.trackStoryAction) {
    // Get story title from the card/row if available
    const storyTitle = deleteButton.closest('.story-item')?.querySelector('.story-title')?.textContent || 'Unknown';
    window.trackStoryAction('delete', storyId, storyTitle);
}
*/

// Example: Integrate with story publishing
/*
// Add after successful publish in story_crud.js:
if (window.trackStoryAction && result.word_count) {
    window.trackStoryAction('publish', storyId, 'Story Title');
    window.trackFeatureUse('story_publishing', 'complete', {
        word_count: result.word_count,
        publish_url: result.published_url
    });
}
*/

// Example: Integrate with AI interactions
/*
// Add to WebSocket message handler in ai_scene_writing.js:
if (data.usage && window.trackAIInteraction) {
    window.trackAIInteraction(
        'scene_assistance',
        data.model || 'gpt-4',
        data.usage.total_tokens,
        data.usage.estimated_cost
    );
}
*/

// ============================================
// 10. DEBUGGING UTILITIES
// ============================================

// Enable debug mode for development
function enableAnalyticsDebug() {
    window.gtag_debug_mode = true;
    console.log('Analytics debug mode enabled');
}

// Log all tracking calls for debugging
function logTrackingCall(eventName, parameters) {
    if (window.gtag_debug_mode) {
        console.log('Analytics Event:', eventName, parameters);
    }
}

// Test tracking implementation
function testAnalyticsTracking() {
    console.log('Testing Analytics Tracking...');
    
    // Test each tracking function
    const tests = [
        () => trackFeatureUse('test_feature', 'test_action'),
        () => trackStoryAction('test_create', 999, 'Test Story'),
        () => trackAIInteraction('test_ai', 'gpt-4', 100, 0.01),
        () => trackWorldAction('test_create', 999, 'Test World'),
        () => trackImageGeneration('test_type', 999, 'test prompt'),
        () => trackPageView('Test Page', { test_param: 'test_value' }),
        () => trackError('Test error', 'test_source')
    ];
    
    tests.forEach((test, index) => {
        try {
            test();
            console.log(`✓ Test ${index + 1} passed`);
        } catch (error) {
            console.error(`✗ Test ${index + 1} failed:`, error);
        }
    });
    
    console.log('Analytics testing complete');
}