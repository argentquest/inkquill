# Help Button Integration Guide

This guide shows how to add contextual help buttons to any page in the application.

## Quick Reference

### Basic Usage
```html
{% include 'partials/_help_button.html' with help_topic='page_name' %}
```

### Full Options
```html
{% include 'partials/_help_button.html' with 
   help_topic='world_list',
   position='fixed',
   size='lg',
   tooltip='Get help with world management',
   classes='custom-class',
   with_text=true
%}
```

## Available Help Topics

### Core Features
- `dashboard` - Main dashboard overview
- `world_list` - World management page
- `world_detail` - Individual world view
- `world_builder` - World Builder Wizard
- `story_detail` - Story management
- `act_editor` - Act writing interface
- `scene_editor` - Scene writing interface

### Content Creation
- `character_detail` - Character management
- `character_generator` - AI character creation
- `location_detail` - Location management  
- `lore_item_detail` - Lore item management
- `import_book` - Import from literature
- `story_classes` - Story templates

### Tools & Features
- `documents` - Document manager
- `prompts` - Prompt library
- `world_chat` - AI brainstorming
- `published_stories` - Community gallery
- `billing` - Credits and billing
- `forum` - Community forum
- `register` - Registration guide

## Implementation Examples

### 1. Dashboard Page
```html
<!-- Fixed help button (recommended for complex pages) -->
{% include 'partials/_help_button.html' with 
   help_topic='dashboard',
   position='fixed',
   tooltip='Get help with the dashboard'
%}
```

### 2. World Management Page
```html
<!-- In page header -->
<div class="page-header d-flex justify-content-between align-items-center">
    <h1>My Worlds</h1>
    {% include 'partials/_help_button.html' with 
       help_topic='world_list',
       position='inline',
       tooltip='Learn about world management'
    %}
</div>
```

### 3. Writing Editor Pages
```html
<!-- In editor toolbar -->
<div class="editor-toolbar">
    <div class="toolbar-group">
        <!-- other toolbar buttons -->
        {% include 'partials/_help_button.html' with 
           help_topic='act_editor',
           size='sm',
           tooltip='Writing help'
        %}
    </div>
</div>
```

### 4. Form Pages
```html
<!-- In card header -->
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5>Create New Character</h5>
        {% include 'partials/_help_button.html' with 
           help_topic='character_detail',
           size='sm',
           tooltip='Character creation help'
        %}
    </div>
    <div class="card-body">
        <!-- form content -->
    </div>
</div>
```

### 5. Mobile-Responsive Help Button
```html
<!-- With text on desktop, icon-only on mobile -->
{% include 'partials/_help_button.html' with 
   help_topic='world_builder',
   with_text=true,
   tooltip='World Builder Wizard help'
%}
```

## Page-Specific Recommendations

### Complex Pages (Editors, Dashboards)
- Use `position='fixed'` for persistent help access
- Consider larger size (`size='lg'`) for visibility

### List/Management Pages  
- Place in page header with `position='inline'`
- Use standard size with descriptive tooltip

### Form Pages
- Include in card headers or form titles
- Use small size (`size='sm'`) to avoid overwhelming the form

### Modal/Dialog Pages
- Place in modal header with `position='absolute'`
- Ensure help content is concise for modal context

## CSS Classes and Customization

### Position Classes
- `help-button-fixed` - Fixed bottom-right position
- `help-button-absolute` - Absolute positioned (for headers)
- Default: inline with content flow

### Size Classes  
- `help-button-sm` - Small (28px)
- Default - Medium (36px)
- `help-button-lg` - Large (44px)

### Style Variants
- `help-button-primary` - Primary brand color
- `help-button-secondary` - Subtle secondary style
- `help-button-ghost` - Transparent background

### Custom Styling
```html
{% include 'partials/_help_button.html' with 
   help_topic='custom_page',
   classes='help-button-primary my-custom-class'
%}
```

## Accessibility Features

The help button component includes:
- Proper ARIA labels and roles
- Keyboard navigation support  
- Screen reader announcements
- High contrast mode support
- Reduced motion respect

## Best Practices

1. **One help button per page** - Avoid multiple help buttons that might confuse users
2. **Consistent placement** - Use fixed position for complex pages, inline for simple ones
3. **Descriptive tooltips** - Help users understand what help they'll get
4. **Context-specific topics** - Use the most relevant help topic for each page
5. **Mobile consideration** - Test help button placement on mobile devices

## Content Management

Help content is managed in `/app/static/js/help-modal.js`. To add new help topics:

1. Add the topic to the `contentMap` in `generateContent()`
2. Create a corresponding `getYourTopicContent()` method
3. Add appropriate icon in `getTopicIcon()` method
4. Update title mapping in `updateTitle()` method

## Testing

Always test help buttons:
- Click functionality opens the correct help content
- Responsive behavior on different screen sizes  
- Accessibility with keyboard navigation
- Theme compatibility (light/dark modes)