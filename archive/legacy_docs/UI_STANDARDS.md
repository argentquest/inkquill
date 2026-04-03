# UI Design Standards & Guidelines

**Version 1.0 | AI Storytelling Assistant | Tabler Premium Implementation**

---

## Table of Contents

1. [Overview](#overview)
2. [Mandatory Page Structure](#mandatory-page-structure)
3. [Container & Layout Standards](#container--layout-standards)
4. [Header Standards](#header-standards)
5. [Button Standards](#button-standards)
6. [Card Component Standards](#card-component-standards)
7. [Animation Standards](#animation-standards)
8. [Color & Theme Standards](#color--theme-standards)
9. [Form & Input Standards](#form--input-standards)
10. [Modal Standards](#modal-standards)
11. [Empty State Standards](#empty-state-standards)
12. [Typography Standards](#typography-standards)
13. [Spacing & Layout Rules](#spacing--layout-rules)
14. [Interactive Element Standards](#interactive-element-standards)
15. [Premium Feature Usage](#premium-feature-usage)
16. [Navigation Standards](#navigation-standards)
17. [Image & Media Standards](#image--media-standards)
18. [Implementation Requirements](#implementation-requirements)
19. [Code Examples](#code-examples)
20. [Common Patterns](#common-patterns)

---

## Overview

This document outlines the **mandatory** UI design standards for the AI Storytelling Assistant application. All UI development must follow these Tabler Premium design standards without exception.

### Key Principles
- **Consistency**: Every page follows the same visual patterns
- **Premium Feel**: Rich animations, gradients, and interactions
- **Accessibility**: Proper ARIA labels and keyboard navigation
- **Responsiveness**: Works flawlessly on all device sizes
- **Performance**: Smooth animations and fast interactions

---

## Mandatory Page Structure

Every page **MUST** follow this exact structure:

```html
<!-- Base Template Structure -->
{% extends "layouts/base.html" %}

{% block page_header %}
<!-- MANDATORY: Hero Header (see Header Standards) -->
<div class="page-header d-print-none" style="background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%); margin-top: calc(var(--tblr-gutter-x, 1.5rem) * 0.7); margin-bottom: 2rem;">
  <div class="container-fluid">
    <div class="row g-2 align-items-center text-white">
      <div class="col">
        <h2 class="page-title">
          <i class="fas fa-icon me-2"></i>Page Title
        </h2>
        <div class="page-subtitle">Descriptive subtitle</div>
        <div class="mt-2">
          <span class="badge bg-light text-dark">Status Badge</span>
        </div>
      </div>
      <div class="col-auto ms-auto d-print-none">
        <div class="btn-list">
          <button class="btn btn-light">
            <i class="fas fa-plus me-1"></i>Primary Action
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block content %}
<div class="page-body">
  <div class="container-fluid">
    <!-- Page content here -->
  </div>
</div>
{% endblock %}
```

---

## Container & Layout Standards

### 1. Container Rules
- **ALWAYS** use `container-fluid` (never `container-xl`)
- **NEVER** use fixed width containers
- **ALWAYS** ensure responsive design on mobile, tablet, and desktop

### 2. Grid System
```html
<!-- Standard page grid -->
<div class="container-fluid">
  <div class="row">
    <div class="col-12">
      <!-- Full width content -->
    </div>
  </div>
  
  <!-- Two column layout -->
  <div class="row">
    <div class="col-md-8">
      <!-- Main content -->
    </div>
    <div class="col-md-4">
      <!-- Sidebar content -->
    </div>
  </div>
</div>
```

### 3. Spacing
- Use Tabler CSS variables: `var(--tblr-gutter-x)`
- Consistent spacing with `mb-3`, `mt-3`, `p-3` classes
- Reduced top margins: `calc(var(--tblr-gutter-x, 1.5rem) * 0.7)`

---

## Header Standards

### MANDATORY: Every Page Must Have a Hero Header

**NO EXCEPTIONS** - All pages require gradient hero headers.

#### Standard Header Template
```html
<div class="page-header d-print-none" style="background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%); margin-top: calc(var(--tblr-gutter-x, 1.5rem) * 0.7); margin-bottom: 2rem;">
  <div class="container-fluid">
    <div class="row g-2 align-items-center text-white">
      <!-- Title Section -->
      <div class="col">
        <h2 class="page-title">
          <i class="fas fa-book me-2"></i>Page Title
        </h2>
        <div class="page-subtitle">
          Clear, descriptive subtitle explaining the page purpose
        </div>
        <div class="mt-2">
          <span class="badge bg-light text-dark">
            <i class="fas fa-info-circle me-1"></i>Status Info
          </span>
        </div>
      </div>
      
      <!-- Action Section -->
      <div class="col-auto ms-auto d-print-none">
        <div class="btn-list">
          <button class="btn btn-light" data-bs-toggle="tooltip" title="Help information">
            <i class="fas fa-question-circle me-1"></i>Help
          </button>
          <button class="btn btn-light">
            <i class="fas fa-plus me-1"></i>Primary Action
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
```

#### Header Requirements
- **Gradient Background**: `linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%)`
- **White Text**: All text must be white for contrast
- **Icon + Title**: FontAwesome icon with descriptive title
- **Subtitle**: Clear description of page purpose
- **Action Buttons**: Primary actions in header, not below content
- **Status Badges**: Use `bg-light text-dark` for readability

---

## Button Standards

### Button Hierarchy

#### 1. Help Buttons (MANDATORY STYLE)
```html
<button class="btn btn-warning" data-bs-toggle="tooltip" title="Get help with this feature">
  <i class="fas fa-question-circle me-1"></i>Help
</button>
```

#### 2. Primary Action Buttons
```html
<button class="btn btn-primary">
  <i class="fas fa-plus me-1"></i>Create New
</button>
```

#### 3. Header Buttons (on gradient backgrounds)
```html
<button class="btn btn-light">
  <i class="fas fa-cog me-1"></i>Settings
</button>
```

#### 4. Secondary Actions
```html
<button class="btn btn-outline-primary">
  <i class="fas fa-edit me-1"></i>Edit
</button>
```

### Button Requirements
- **Text Labels**: ALL buttons MUST have descriptive text, not just icons
- **Icon Spacing**: Always use `me-1` between icons and text
- **Tooltips**: All buttons must have helpful tooltips
- **Consistency**: Use the same button style for the same action type

### Button Groups
```html
<div class="btn-list">
  <button class="btn btn-primary">
    <i class="fas fa-save me-1"></i>Save
  </button>
  <button class="btn btn-outline-secondary">
    <i class="fas fa-times me-1"></i>Cancel
  </button>
</div>

<!-- Responsive button list -->
<div class="btn-list flex-wrap">
  <button class="btn btn-primary">Action 1</button>
  <button class="btn btn-outline-primary">Action 2</button>
  <button class="btn btn-outline-primary">Action 3</button>
</div>
```

---

## Card Component Standards

### Standard Card Structure
```html
<div class="card">
  <!-- Status bar for visual hierarchy -->
  <div class="card-status-top bg-primary"></div>
  
  <div class="card-header">
    <h3 class="card-title">
      <i class="fas fa-icon me-2"></i>Card Title
    </h3>
    <div class="card-actions">
      <button class="btn btn-primary btn-sm">
        <i class="fas fa-edit me-1"></i>Edit
      </button>
    </div>
  </div>
  
  <div class="card-body">
    <p class="text-secondary mb-3">Card description or content</p>
    
    <!-- Metadata section -->
    <div class="row g-2 mb-3">
      <div class="col-auto">
        <small class="text-muted">
          <i class="fas fa-calendar me-1"></i>Created: Jan 15, 2024
        </small>
      </div>
      <div class="col-auto">
        <small class="text-muted">
          <i class="fas fa-user me-1"></i>Author: John Doe
        </small>
      </div>
    </div>
  </div>
  
  <div class="card-footer">
    <div class="btn-list">
      <button class="btn btn-primary btn-sm">Primary Action</button>
      <button class="btn btn-outline-secondary btn-sm">Secondary</button>
    </div>
  </div>
</div>
```

### Hover Effects (REQUIRED)
```css
.card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid var(--tblr-border-color);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: var(--tblr-box-shadow-lg);
  border-color: var(--tblr-primary);
}

/* Animated top border */
.card-status-top {
  height: 3px;
  background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.card:hover .card-status-top {
  transform: scaleX(1);
}
```

### Card Variations

#### Card with Image
```html
<div class="card">
  <div class="card-img-top img-responsive img-responsive-1by1" 
       style="background-image: url('image.jpg'); background-size: cover; background-position: center;"></div>
  <div class="card-body">
    <h3 class="card-title">Title</h3>
    <p class="text-secondary">Description</p>
  </div>
</div>
```

#### Empty State Card
```html
<div class="card">
  <div class="card-body text-center">
    <div class="avatar avatar-xl bg-primary-lt mb-3">
      <i class="fas fa-plus fa-2x"></i>
    </div>
    <h3>No items yet</h3>
    <p class="text-secondary">Create your first item to get started</p>
    <button class="btn btn-primary">
      <i class="fas fa-plus me-1"></i>Create First Item
    </button>
  </div>
</div>
```

---

## Animation Standards

### Fade-in Animations
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate3d(0, 40px, 0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
}

.animate-fade-in {
  animation: fadeInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Staggered animations for lists */
.card:nth-child(1) { animation-delay: 0.1s; }
.card:nth-child(2) { animation-delay: 0.2s; }
.card:nth-child(3) { animation-delay: 0.3s; }
.card:nth-child(4) { animation-delay: 0.4s; }
```

### Hover Transitions
```css
.interactive-element {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.interactive-element:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}
```

### Loading States
```html
<!-- Tabler progress bar -->
<div class="progress progress-sm">
  <div class="progress-bar progress-bar-indeterminate"></div>
</div>

<!-- Card loading state -->
<div class="card">
  <div class="card-body">
    <div class="placeholder-glow">
      <span class="placeholder col-7"></span>
      <span class="placeholder col-4"></span>
      <span class="placeholder col-4"></span>
      <span class="placeholder col-6"></span>
    </div>
  </div>
</div>
```

---

## Color & Theme Standards

### CSS Variables (MANDATORY)
**NEVER** use hardcoded colors. **ALWAYS** use Tabler CSS variables.

```css
/* Primary colors */
var(--tblr-primary)     /* Main brand color */
var(--tblr-purple)      /* Secondary brand color */

/* Background colors */
var(--tblr-bg-surface)           /* Card backgrounds */
var(--tblr-bg-surface-secondary) /* Metadata sections */

/* Text colors */
var(--tblr-body-color)          /* Default text */
var(--tblr-text-secondary)      /* Secondary text */

/* Border colors */
var(--tblr-border-color)        /* Default borders */

/* Shadow variables */
var(--tblr-box-shadow)          /* Default shadow */
var(--tblr-box-shadow-lg)       /* Large shadow */
```

### Gradient Patterns
```css
/* Standard gradient */
background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%);

/* Subtle gradient overlay */
background: 
  radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
  radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
  linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%);
```

### Text Contrast Rules
```html
<!-- Light backgrounds -->
<div class="bg-light">
  <span class="text-dark">Dark text on light background</span>
</div>

<!-- Dark/gradient backgrounds -->
<div style="background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%);">
  <span class="text-white">White text on gradient background</span>
</div>

<!-- Badges on gradients -->
<div class="gradient-background">
  <span class="badge bg-light text-dark">Readable badge</span>
</div>
```

---

## Form & Input Standards

### Standard Form Layout
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Form Title</h3>
  </div>
  <div class="card-body">
    <form>
      <div class="mb-3">
        <label class="form-label required">Field Label</label>
        <input type="text" class="form-control" placeholder="Enter value...">
        <small class="form-hint">Helpful hint about this field</small>
      </div>
      
      <div class="mb-3">
        <label class="form-label">Optional Field</label>
        <textarea class="form-control" rows="3" placeholder="Enter description..."></textarea>
      </div>
      
      <div class="mb-3">
        <label class="form-label">Select Field</label>
        <select class="form-select">
          <option value="">Choose option...</option>
          <option value="1">Option 1</option>
          <option value="2">Option 2</option>
        </select>
      </div>
    </form>
  </div>
  <div class="card-footer">
    <div class="btn-list">
      <button class="btn btn-primary">
        <i class="fas fa-save me-1"></i>Save
      </button>
      <button class="btn btn-outline-secondary">
        <i class="fas fa-times me-1"></i>Cancel
      </button>
    </div>
  </div>
</div>
```

### Input States
```html
<!-- Success state -->
<input type="text" class="form-control is-valid" value="Valid input">
<div class="valid-feedback">Looks good!</div>

<!-- Error state -->
<input type="text" class="form-control is-invalid" value="Invalid input">
<div class="invalid-feedback">Please provide a valid value.</div>

<!-- Loading state -->
<div class="input-group">
  <input type="text" class="form-control" placeholder="Loading...">
  <span class="input-group-text">
    <div class="spinner-border spinner-border-sm" role="status"></div>
  </span>
</div>
```

### Floating Labels (Optional)
```html
<div class="form-floating mb-3">
  <input type="text" class="form-control" id="floatingInput" placeholder="Name">
  <label for="floatingInput">Full Name</label>
</div>
```

---

## Modal Standards

### Standard Modal Structure
```html
<div class="modal fade" id="exampleModal" tabindex="-1">
  <div class="modal-dialog modal-xl">
    <div class="modal-content">
      <!-- Enhanced gradient header -->
      <div class="modal-header text-white" style="background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%);">
        <h5 class="modal-title text-center w-100">
          <i class="fas fa-icon me-2"></i>Modal Title
        </h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      
      <div class="modal-body">
        <!-- Modal content -->
      </div>
      
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
          <i class="fas fa-times me-1"></i>Cancel
        </button>
        <button type="button" class="btn btn-primary">
          <i class="fas fa-save me-1"></i>Save Changes
        </button>
      </div>
    </div>
  </div>
</div>
```

### Modal Sizes
```html
<!-- Large modal -->
<div class="modal-dialog modal-xl">

<!-- Medium modal (default) -->
<div class="modal-dialog">

<!-- Small modal -->
<div class="modal-dialog modal-sm">

<!-- Full screen -->
<div class="modal-dialog modal-fullscreen">
```

---

## Empty State Standards

### Standard Empty State
```html
<div class="card">
  <div class="card-body text-center py-5">
    <div class="avatar avatar-xl bg-primary-lt mb-3">
      <i class="fas fa-inbox fa-2x"></i>
    </div>
    <h3 class="mb-3">No items found</h3>
    <p class="text-secondary mb-4">
      You haven't created any items yet. Get started by creating your first item.
    </p>
    <button class="btn btn-primary">
      <i class="fas fa-plus me-1"></i>Create First Item
    </button>
  </div>
</div>
```

### Loading Empty State
```html
<div class="card">
  <div class="card-body text-center py-5">
    <div class="spinner-border text-primary mb-3" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
    <h3 class="mb-3">Loading...</h3>
    <p class="text-secondary">Please wait while we fetch your data.</p>
  </div>
</div>
```

### Error Empty State
```html
<div class="card">
  <div class="card-body text-center py-5">
    <div class="avatar avatar-xl bg-danger-lt mb-3">
      <i class="fas fa-exclamation-triangle fa-2x"></i>
    </div>
    <h3 class="mb-3">Something went wrong</h3>
    <p class="text-secondary mb-4">
      We couldn't load your data. Please try again.
    </p>
    <button class="btn btn-primary">
      <i class="fas fa-refresh me-1"></i>Try Again
    </button>
  </div>
</div>
```

---

## Typography Standards

### Heading Hierarchy
```html
<h1 class="page-title">
  <i class="fas fa-icon me-2"></i>Main Page Title
</h1>

<h2 class="section-title">
  <i class="fas fa-icon me-2"></i>Section Title
</h2>

<h3 class="card-title">Card Title</h3>

<h4 class="subtitle">Subtitle</h4>
```

### Text Styles
```html
<!-- Primary text -->
<p class="text-body">Regular body text content.</p>

<!-- Secondary text -->
<p class="text-secondary">Secondary information or descriptions.</p>

<!-- Small text -->
<small class="text-muted">
  <i class="fas fa-clock me-1"></i>Last updated 2 hours ago
</small>

<!-- Emphasized text -->
<strong>Important information</strong>
<em>Emphasized text</em>
```

### Icon Usage
```html
<!-- Consistent icon sizing -->
<i class="fas fa-icon"></i>          <!-- Default size -->
<i class="fas fa-icon fa-lg"></i>     <!-- Large -->
<i class="fas fa-icon fa-2x"></i>     <!-- 2x size -->

<!-- Icon with text spacing -->
<i class="fas fa-user me-1"></i>User Profile
<span class="ms-2"><i class="fas fa-star"></i></span>
```

---

## Spacing & Layout Rules

### Margin Classes
```html
<!-- Standard margins -->
<div class="mb-3">Bottom margin</div>
<div class="mt-3">Top margin</div>
<div class="mx-3">Horizontal margins</div>
<div class="my-3">Vertical margins</div>

<!-- Responsive margins -->
<div class="mb-md-4 mb-2">Responsive bottom margin</div>
```

### Padding Classes
```html
<!-- Standard padding -->
<div class="p-3">All sides padding</div>
<div class="px-3">Horizontal padding</div>
<div class="py-3">Vertical padding</div>

<!-- Large padding for empty states -->
<div class="py-5">Large vertical padding</div>
```

### Layout Utilities
```html
<!-- Flexbox utilities -->
<div class="d-flex align-items-center justify-content-between">
  <span>Left content</span>
  <span>Right content</span>
</div>

<!-- Grid gaps -->
<div class="row g-3">Grid with gap</div>
<div class="row g-2">Small gap</div>
<div class="row g-4">Large gap</div>
```

---

## Interactive Element Standards

### Tooltips (MANDATORY)
```html
<button class="btn btn-primary" 
        data-bs-toggle="tooltip" 
        data-bs-placement="top" 
        title="This button performs the primary action">
  <i class="fas fa-save me-1"></i>Save
</button>
```

### Loading States
```html
<!-- Button loading state -->
<button class="btn btn-primary" disabled>
  <span class="spinner-border spinner-border-sm me-2" role="status"></span>
  Loading...
</button>

<!-- Card loading state -->
<div class="card">
  <div class="card-body">
    <div class="progress progress-sm mb-3">
      <div class="progress-bar progress-bar-indeterminate"></div>
    </div>
    <div class="placeholder-glow">
      <span class="placeholder col-7"></span>
      <span class="placeholder col-4"></span>
    </div>
  </div>
</div>
```

### Error Handling
```html
<!-- Error alert -->
<div class="alert alert-danger d-flex align-items-center" role="alert">
  <i class="fas fa-exclamation-triangle me-2"></i>
  <div>
    <strong>Error:</strong> Something went wrong. Please try again.
  </div>
</div>

<!-- Error state with retry -->
<div class="text-center py-4">
  <div class="avatar avatar-xl bg-danger-lt mb-3">
    <i class="fas fa-exclamation-triangle fa-2x"></i>
  </div>
  <h3>Failed to load</h3>
  <p class="text-secondary mb-3">Please check your connection and try again.</p>
  <button class="btn btn-primary" onclick="retryAction()">
    <i class="fas fa-refresh me-1"></i>Retry
  </button>
</div>
```

---

## Premium Feature Usage

### Status Bars
```html
<div class="card">
  <div class="card-status-top bg-success"></div> <!-- Green for success -->
  <div class="card-status-top bg-warning"></div> <!-- Yellow for warning -->
  <div class="card-status-top bg-danger"></div>  <!-- Red for error -->
  <div class="card-status-top bg-primary"></div> <!-- Blue for info -->
</div>
```

### Ribbons
```html
<div class="card">
  <div class="ribbon bg-red ribbon-top">
    <i class="fas fa-star"></i>
  </div>
  <div class="card-body">
    Card with ribbon
  </div>
</div>
```

### Enhanced Shadows
```html
<!-- Default shadow -->
<div class="shadow-sm">Light shadow</div>

<!-- Medium shadow -->
<div class="shadow">Medium shadow</div>

<!-- Large shadow -->
<div class="shadow-lg">Large shadow</div>

<!-- Custom Tabler shadows -->
<div style="box-shadow: var(--tblr-box-shadow-lg)">Tabler large shadow</div>
```

---

## Navigation Standards

### Breadcrumbs
```html
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item">
      <a href="/dashboard">
        <i class="fas fa-home me-1"></i>Dashboard
      </a>
    </li>
    <li class="breadcrumb-item">
      <a href="/stories">Stories</a>
    </li>
    <li class="breadcrumb-item active" aria-current="page">
      Edit Story
    </li>
  </ol>
</nav>
```

### Page Navigation
```html
<div class="d-flex justify-content-between align-items-center mb-3">
  <a href="/previous" class="btn btn-outline-primary">
    <i class="fas fa-arrow-left me-1"></i>Previous
  </a>
  
  <span class="text-secondary">Step 2 of 5</span>
  
  <a href="/next" class="btn btn-primary">
    Next<i class="fas fa-arrow-right ms-1"></i>
  </a>
</div>
```

---

## Image & Media Standards

### Responsive Images
```html
<!-- Card image with 1:1 aspect ratio -->
<div class="card">
  <div class="card-img-top img-responsive img-responsive-1by1" 
       style="background-image: url('image.jpg'); background-size: cover; background-position: center;">
  </div>
</div>

<!-- Card image with 16:9 aspect ratio -->
<div class="card">
  <div class="card-img-top img-responsive img-responsive-16by9" 
       style="background-image: url('image.jpg'); background-size: cover; background-position: center;">
  </div>
</div>
```

### Placeholder Images
```html
<!-- Avatar placeholder -->
<div class="avatar avatar-xl bg-primary-lt">
  <i class="fas fa-user fa-2x"></i>
</div>

<!-- Image placeholder -->
<div class="img-responsive img-responsive-1by1 bg-light d-flex align-items-center justify-content-center">
  <i class="fas fa-image fa-3x text-muted"></i>
</div>
```

---

## Implementation Requirements

### ✅ ALWAYS Do
- Check existing pages for pattern consistency before implementing new UI
- Use Tabler CSS variables instead of hardcoded colors
- Implement hover effects and animations for interactive elements
- Add descriptive text to buttons (not just icons)
- Include tooltips on all interactive elements
- Use the mandatory hero header on every page
- Follow the card hover effects pattern
- Use consistent spacing with Tabler classes

### ❌ NEVER Do
- Use basic Bootstrap components when Tabler Premium alternatives exist
- Create inconsistent button styling
- Forget to add descriptive text to buttons
- Use hardcoded colors instead of CSS variables
- Skip the mandatory hero header
- Use `container-xl` instead of `container-fluid`
- Ignore responsive design requirements

---

## Code Examples

### Complete Page Example
```html
{% extends "layouts/base.html" %}

{% block page_header %}
<div class="page-header d-print-none" style="background: linear-gradient(135deg, var(--tblr-primary) 0%, var(--tblr-purple) 100%); margin-top: calc(var(--tblr-gutter-x, 1.5rem) * 0.7); margin-bottom: 2rem;">
  <div class="container-fluid">
    <div class="row g-2 align-items-center text-white">
      <div class="col">
        <h2 class="page-title">
          <i class="fas fa-book me-2"></i>My Stories
        </h2>
        <div class="page-subtitle">
          Manage and create your stories
        </div>
        <div class="mt-2">
          <span class="badge bg-light text-dark">
            <i class="fas fa-list me-1"></i>{{ stories|length }} Stories
          </span>
        </div>
      </div>
      <div class="col-auto ms-auto d-print-none">
        <div class="btn-list">
          <button class="btn btn-warning" onclick="openHelpModal('stories-help')" data-bs-toggle="tooltip" title="Get help with stories">
            <i class="fas fa-question-circle me-1"></i>Help
          </button>
          <a href="/stories/create" class="btn btn-light">
            <i class="fas fa-plus me-1"></i>New Story
          </a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block content %}
<div class="page-body">
  <div class="container-fluid">
    {% if stories %}
    <div class="row row-cards">
      {% for story in stories %}
      <div class="col-sm-6 col-lg-4">
        <div class="card animate-fade-in">
          <div class="card-status-top bg-primary"></div>
          <div class="card-body">
            <h3 class="card-title">
              <i class="fas fa-book me-2"></i>{{ story.title }}
            </h3>
            <p class="text-secondary">{{ story.description }}</p>
            <div class="row g-2 mb-3">
              <div class="col-auto">
                <small class="text-muted">
                  <i class="fas fa-calendar me-1"></i>{{ story.created_at.strftime('%b %d, %Y') }}
                </small>
              </div>
            </div>
          </div>
          <div class="card-footer">
            <div class="btn-list">
              <a href="/stories/{{ story.id }}" class="btn btn-primary btn-sm">
                <i class="fas fa-edit me-1"></i>Edit
              </a>
              <button class="btn btn-outline-secondary btn-sm" onclick="viewStory({{ story.id }})">
                <i class="fas fa-eye me-1"></i>View
              </button>
            </div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center py-5">
            <div class="avatar avatar-xl bg-primary-lt mb-3">
              <i class="fas fa-book fa-2x"></i>
            </div>
            <h3 class="mb-3">No stories yet</h3>
            <p class="text-secondary mb-4">
              Create your first story to start your writing journey.
            </p>
            <a href="/stories/create" class="btn btn-primary">
              <i class="fas fa-plus me-1"></i>Create First Story
            </a>
          </div>
        </div>
      </div>
    </div>
    {% endif %}
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Add fade-in animation classes with stagger
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    card.style.animationDelay = `${index * 0.1}s`;
  });
});

function viewStory(storyId) {
  // Implementation for viewing story
  window.location.href = `/stories/${storyId}/view`;
}
</script>
{% endblock %}
```

---

## Common Patterns

### Dashboard Cards
```html
<div class="row row-cards">
  <div class="col-sm-6 col-lg-3">
    <div class="card">
      <div class="card-body">
        <div class="d-flex align-items-center">
          <div class="avatar bg-primary-lt me-3">
            <i class="fas fa-users"></i>
          </div>
          <div>
            <div class="small text-secondary">Total Users</div>
            <div class="h3 mb-0">1,234</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

### Action Cards
```html
<div class="card">
  <div class="card-body text-center">
    <div class="avatar avatar-lg bg-primary-lt mb-3">
      <i class="fas fa-plus fa-lg"></i>
    </div>
    <h3 class="card-title">Create New</h3>
    <p class="text-secondary">Start a new project</p>
    <button class="btn btn-primary">
      <i class="fas fa-plus me-1"></i>Get Started
    </button>
  </div>
</div>
```

### List Items
```html
<div class="list-group list-group-flush">
  <div class="list-group-item">
    <div class="row align-items-center">
      <div class="col-auto">
        <div class="avatar bg-primary-lt">
          <i class="fas fa-file"></i>
        </div>
      </div>
      <div class="col">
        <div class="fw-bold">Item Title</div>
        <div class="text-secondary small">Item description</div>
      </div>
      <div class="col-auto">
        <div class="btn-list">
          <button class="btn btn-primary btn-sm">Edit</button>
          <button class="btn btn-outline-secondary btn-sm">Delete</button>
        </div>
      </div>
    </div>
  </div>
</div>
```

---

**End of UI Standards Document**

This document serves as the complete reference for all UI development in the AI Storytelling Assistant. All developers must follow these standards to ensure consistency and quality across the application.

For questions or clarifications, refer to existing pages in the application that demonstrate these patterns in practice.