# Enhanced Google Analytics Tracking Guide

This document explains the enhanced Google Analytics tracking implementation that includes user ID tracking and detailed event tracking.

## Overview

The enhanced tracking system provides:
- **User ID Tracking**: Automatically tracks authenticated users with their unique ID
- **User Properties**: Tracks user type (admin/regular), account creation date, and active status
- **Enhanced Event Tracking**: Detailed tracking for specific user actions
- **Custom Parameters**: Ability to add custom data to any tracking event
- **Privacy-First**: Respects consent mode and anonymizes data when required

## Automatic User Tracking

When a user is authenticated, the following information is automatically tracked:

```javascript
// Automatically included in all events for authenticated users:
user_id: '123',                    // Unique user ID
user_properties: {
  user_type: 'regular',           // or 'admin'
  account_created: '2024-01-15',  // Account creation date
  is_active: true                 // Account status
}
```

## Available Tracking Functions

### 1. Authentication Events

```javascript
// Track login
trackAuthEvent('login', 'email');
trackAuthEvent('login', 'google');

// Track registration
trackAuthEvent('signup', 'email');

// Track logout
trackAuthEvent('logout', 'manual');
```

### 2. Feature Usage

```javascript
// Basic usage
trackFeatureUse('story_editor', 'open');
trackFeatureUse('world_builder', 'create');

// With additional data
trackFeatureUse('image_gallery', 'view', {
  gallery_size: 10,
  filter_applied: true,
  view_mode: 'grid'
});
```

### 3. AI Interactions

```javascript
// Track AI usage with detailed metrics
trackAIInteraction('story_generation', 'gpt-4', 1500, 0.045);
// Parameters: type, model, token_count, estimated_cost

trackAIInteraction('character_description', 'gpt-3.5-turbo', 250, 0.001);
trackAIInteraction('image_generation', 'dall-e-3', null, 0.040);
```

### 4. Story Management

```javascript
// Track story-related actions
trackStoryAction('create', storyId, 'My Epic Adventure');
trackStoryAction('publish', storyId, storyTitle);
trackStoryAction('delete', storyId, storyTitle);
trackStoryAction('share', storyId, storyTitle);
```

### 5. World Building

```javascript
// Track world-related actions
trackWorldAction('create', worldId, 'Fantasy Realm');
trackWorldAction('import_from_book', worldId, worldName);
trackWorldAction('add_character', worldId, worldName);
trackWorldAction('enable_chat', worldId, worldName);
```

### 6. Image Generation

```javascript
// Track image generation events
trackImageGeneration('character', characterId, promptText);
trackImageGeneration('scene', sceneId, promptText);
trackImageGeneration('location', locationId, promptText);
```

### 7. Custom Page Views

```javascript
// Track page views with custom parameters
trackPageView('Story Editor', {
  story_id: 123,
  word_count: 5000,
  edit_mode: 'collaborative'
});

trackPageView('World Map', {
  world_id: 456,
  location_count: 25,
  zoom_level: 3
});
```

### 8. Error Tracking

```javascript
// Track errors for debugging
trackError('Failed to save story', 'story_editor');
trackError('API timeout', 'ai_service');
trackError('Image upload failed', 'media_manager');
```

## Implementation Examples

### In Story Editor

```javascript
// When user opens story editor
trackFeatureUse('story_editor', 'open', {
  story_id: storyId,
  acts_count: actsCount,
  scenes_count: scenesCount
});

// When user saves
trackStoryAction('save', storyId, storyTitle);

// When AI is used
trackAIInteraction('content_suggestion', 'gpt-4', response.tokens, response.cost);
```

### In World Builder

```javascript
// When creating a world
trackWorldAction('create', world.id, world.name);

// When importing from book
trackFeatureUse('book_import', 'complete', {
  book_title: bookTitle,
  characters_imported: characterCount,
  locations_imported: locationCount
});
```

### In Image Generation

```javascript
// When generating an image
trackImageGeneration(elementType, elementId, prompt);

// Track the completion
trackFeatureUse('image_generation', 'complete', {
  element_type: elementType,
  generation_time: generationTime,
  model_used: 'dall-e-3'
});
```

## Privacy Considerations

1. **User ID Hashing**: Consider hashing user IDs before sending to GA for additional privacy
2. **Consent Mode**: All tracking respects the user's consent preferences
3. **Data Minimization**: Only track necessary data for analytics purposes
4. **IP Anonymization**: Enabled when consent mode is active

## Best Practices

1. **Consistent Naming**: Use consistent event names and categories
2. **Meaningful Labels**: Use descriptive labels that will be useful in reports
3. **Value Tracking**: Use the value parameter for metrics that can be aggregated
4. **Error Handling**: Wrap tracking calls in try-catch blocks for production
5. **Testing**: Test tracking in GA DebugView before deploying

## Custom Dimensions Setup (GA4)

To fully utilize this tracking, set up these custom dimensions in GA4:

1. **User Dimensions**:
   - user_type (scope: User)
   - account_created (scope: User)
   
2. **Event Dimensions**:
   - story_id (scope: Event)
   - world_id (scope: Event)
   - ai_model (scope: Event)
   - element_type (scope: Event)
   - action_type (scope: Event)

## Debugging

Enable debug mode to see tracking calls in console:

```javascript
// Add to your code for debugging
window.gtag_debug_mode = true;
```

View real-time data in Google Analytics:
1. Go to Reports → Realtime
2. Use DebugView for detailed event inspection
3. Check User Explorer for user-level data

## Compliance

Remember to:
1. Update your privacy policy to mention enhanced tracking
2. Ensure GDPR/CCPA compliance with user consent
3. Provide users with opt-out mechanisms
4. Document what data is collected and why