# Tabler UI Components Library

This directory contains reusable Tabler UI components extracted from the main Tabler library for easy integration into our application.

## Available Components

### Core Components

#### Modals (`/modals/`)
- **base_modal.html** - Flexible base modal with customizable content
- **confirmation_modal.html** - Confirmation dialogs with danger/warning modes
- **success_modal.html** - Success notification modals

#### Cards (`/cards/`)
- **basic_card.html** - Standard card with header, body, and footer
- **status_card.html** - Cards with status indicators and metrics
- **action_card.html** - Interactive cards with hover effects and actions

#### Forms (`/forms/`)
- **input.html** - Text inputs with icons, validation, and styling
- **textarea.html** - Multi-line text areas with character counting
- **select.html** - Dropdown selects with option handling

#### Buttons (`/buttons/`)
- **button.html** - Flexible buttons with icons, colors, and states
- **button_group.html** - Grouped button collections

#### Alerts (`/alerts/`)
- **alert.html** - Notification alerts with icons and actions

### UI Elements

#### Navigation (`/navigation/`)
- **breadcrumb.html** - Breadcrumb navigation trails

#### Progress (`/progress/`)
- **progress_bar.html** - Progress indicators with colors and animations

#### Badges (`/badges/`)
- **badge.html** - Status badges with icons and colors

## Usage Examples

### Basic Components
```html
<!-- Modal -->
{% include "components/modals/base_modal.html" 
   modal_id="my-modal" 
   title="Modal Title" 
   content="Modal content here" 
   show_footer=true %}

<!-- Card -->
{% include "components/cards/basic_card.html" 
   title="Card Title" 
   content="Card content" 
   footer="Card footer" %}

<!-- Form Input -->
{% include "components/forms/input.html" 
   name="email" 
   label="Email Address" 
   type="email" 
   icon="email" 
   required=true %}

<!-- Button -->
{% include "components/buttons/button.html" 
   text="Save" 
   color="primary" 
   icon="save" %}

<!-- Alert -->
{% include "components/alerts/alert.html" 
   type="success" 
   title="Success!" 
   message="Operation completed successfully." %}
```

### Advanced Components
```html
<!-- Status Card -->
{% include "components/cards/status_card.html" 
   title="Active Users" 
   value="2,847" 
   status="success" 
   change="+12%" 
   change_color="success" 
   change_icon="up" %}

<!-- Action Card -->
{% include "components/cards/action_card.html" 
   title="Create Story" 
   description="Start writing your story" 
   icon="edit" 
   action_url="/stories/new" %}

<!-- Confirmation Modal -->
{% include "components/modals/confirmation_modal.html" 
   modal_id="confirm-delete" 
   title="Delete Item?" 
   message="This action cannot be undone." 
   danger_mode=true %}

<!-- Progress Bar -->
{% include "components/progress/progress_bar.html" 
   value=75 
   color="primary" 
   show_text=true %}

<!-- Badge -->
{% include "components/badges/badge.html" 
   text="New" 
   color="success" 
   icon="star" %}
```

## Component Parameters

### Common Parameters
- `class` - Additional CSS classes
- `id` - Element ID
- `attrs` - Additional HTML attributes

### Modal Parameters
- `modal_id` - Modal ID (required)
- `title` - Modal title
- `size` - Modal size (sm, lg, xl, full-width)
- `content`/`body` - Modal content
- `show_footer` - Show footer section
- `center_content` - Center modal content
- `status_color` - Status bar color

### Card Parameters
- `title` - Card title
- `subtitle` - Card subtitle
- `content`/`body` - Card content
- `footer` - Card footer content
- `actions` - Header actions
- `header_class`, `body_class`, `footer_class` - Section-specific classes

### Form Parameters
- `name` - Input name
- `label` - Input label
- `type` - Input type
- `placeholder` - Placeholder text
- `required` - Required field
- `icon` - Input icon
- `hint` - Help text

### Button Parameters
- `text` - Button text
- `color` - Button color (primary, secondary, success, etc.)
- `icon` - Button icon
- `size` - Button size (sm, lg)
- `outline` - Outline style
- `block` - Full width
- `loading` - Loading state

## Source Reference

All components are based on Tabler UI examples from:
- `/tabler-main/preview/pages/` - Component examples
- `/tabler-main/shared/includes/` - Component templates  
- `/tabler-main/core/scss/ui/` - Component styles
- GitHub: https://github.com/tabler/tabler

## Integration with Existing Code

These components can be used alongside the existing interview system and other application features. The components follow Tabler's design system and are compatible with Bootstrap 5.