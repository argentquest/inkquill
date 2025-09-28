# Basic/Advanced Story System Design Document

## Overview

This document outlines the design and implementation plan for introducing a two-tier story system: Basic Stories (simple, quick-start) and Advanced Stories (full world-building features). This system allows users to start writing immediately with Basic Stories and upgrade to Advanced Stories when they need world-building capabilities.

## Background - Design Q&A Sessions

### Question 1: Story Creation Flow
**Q:** When a user wants to create a Basic Story (without a world), what should the initial creation experience look like?

**A:** Simplified form with just story title and description (no genre/tone fields)

---

### Question 2: Shadow World Implementation
**Q:** For the shadow world that gets created automatically with a Basic Story:
- Should it be completely hidden from the user?
- Should it have a generic name?
- Should these shadow worlds be marked with a special flag/type in the database?

**A:** 
- Completely hidden from the user
- Will need a way to change story mode from basic to advanced
- Shadow worlds should not be visible in the list of worlds

---

### Question 3: Upgrading from Basic to Advanced
**Q:** When a user upgrades their Basic Story to Advanced mode:
- Should the hidden shadow world become visible and editable?
- Should they have the option to create a brand new world or convert the shadow world?
- Should they be able to link their story to an existing world?

**A:** 
- Yes, shadow world becomes visible and editable
- No new world creation option
- No linking to existing worlds

---

### Question 4: UI/UX Differentiation
**Q:** How should Basic and Advanced stories be distinguished in the UI?

**A:** All of the following:
- Visual indicator (badge/icon) on story cards/lists
- Different menu options (hiding world-related features)
- Different story detail page appearance

---

### Question 5: Feature Restrictions
**Q:** What features should be disabled/hidden for Basic Stories?

**A:** 
- Character management (disabled)
- Location management (disabled)
- Hierarchy view (disabled)
- AI prompts should not receive world information (leave blank)
- Lore items (enabled)
- World chat (enabled)

---

### Question 6: Database Design
**Q:** For implementing this system, should we add fields to track story type and shadow worlds?

**A:** Both:
- Add `story_type` field to Story model ('basic' or 'advanced')
- Add `is_shadow` boolean field to World model

---

### Question 7: Migration Strategy
**Q:** How should we handle existing data?

**A:** 
- All existing stories marked as 'advanced'
- All existing worlds marked as `is_shadow = false`
- Create database migration for these defaults

---

### Question 8: Story Creation Entry Points
**Q:** Where should users be able to create a Basic Story from?

**A:** 
- "Start Writing" button on main dashboard
- Toggle on existing story creation form (Basic vs Advanced mode)
- Two separate menu items: "Create Basic Story" and "Create Advanced Story"

---

### Question 9: Advanced Mode Features
**Q:** Which features should become available when upgrading to Advanced?

**A:** All of the following:
- Multiple acts
- World detail page access
- Character/Location creation
- World-building wizard/tools
- Story hierarchy view
- Generate world elements from story content

---

### Question 10: Basic Story Limitations
**Q:** Should Basic Stories have any content limits?

**A:** No limits - let them write as much as they want

---

### Question 11: Shadow World Naming
**Q:** How should world naming work during upgrade?

**A:** 
- Default name like "[Story Title] World"
- Prompt users to name world during upgrade
- World name editable after upgrade
- No undo upgrade option

---

### Question 12: Story List Display
**Q:** How should Basic and Advanced stories be displayed in lists?

**A:** Mixed together with visual badges/indicators

---

### Question 13: AI Context Handling
**Q:** How should AI features work for Basic Stories?

**A:** 
- AI assistance works without world context
- No AI features completely disabled
- AI prompts modified to work without world context
- Basic-specific AI features (like "Suggest what happens next")

---

### Question 14: Publishing and Sharing
**Q:** Can Basic Stories be published/shared?

**A:** 
- Basic Stories are publishable like Advanced Stories
- Same publishing process
- Show differently in gallery with badge
- Readers can see if it's Basic vs Advanced

---

### Question 15: Data Migration Edge Cases
**Q:** Any special edge cases for migration?

**A:** No need to worry about edge cases

---

### Question 16: User Experience Flow
**Q:** What should new users see first?

**A:** 
- "Start Writing" as most prominent call-to-action
- No onboarding for Basic vs Advanced
- No notifications to existing users
- Homepage emphasizes quick writing but introduces Advanced Stories

---

### Question 17: Story Templates
**Q:** Should Basic Stories have templates?

**A:** 
- Primary option: blank slate
- Optional genre-based templates via dropdown

---

### Question 18: Navigation and Menu Structure
**Q:** How should navigation adapt?

**A:** 
- "My Stories" shows both types mixed
- "My Worlds" visible even if only Basic Stories
- Tooltips/help text for menu items
- Menu dynamically changes based on user content

---

### Question 19: Analytics and Tracking
**Q:** Should we track usage differently?

**A:** No special analytics for now

---

### Question 20: Future Expansion
**Q:** Future features to consider?

**A:** 
- No downgrade from Advanced to Basic
- Document import as Basic Stories (yes)
- Collaborative Basic Stories (yes)
- Basic Story series (yes)

---

## Additional Requirements

### Default Act Creation
- Basic Stories automatically create Act 1
- User directed straight to act editor after story creation
- Act numbers hidden when only 1 act exists
- Act numbers shown when 2+ acts exist

## Implementation Design

### 1. Database Schema Changes

#### Story Model Updates
```python
class Story(Base):
    # Existing fields...
    
    # New field
    story_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False, 
        default='advanced',
        server_default='advanced'
    )  # Values: 'basic', 'advanced'
```

#### World Model Updates
```python
class World(Base):
    # Existing fields...
    
    # New field
    is_shadow: Mapped[bool] = mapped_column(
        Boolean, 
        nullable=False, 
        default=False,
        server_default='false'
    )
```

### 2. Core Features by Story Type

#### Basic Story Features
- **Creation**: Minimal form (title, description)
- **Writing**: Direct to Act 1 editor
- **AI**: Context-free assistance
- **Publishing**: Full publishing capabilities with "Basic" badge
- **Restrictions**: No characters, locations, or hierarchy view

#### Advanced Story Features
- **All Basic features plus**:
- **World Building**: Full access to world, characters, locations, lore
- **Structure**: Multiple acts with visible numbering
- **AI**: Full context-aware assistance
- **Views**: Hierarchy view, world chat

### 3. User Interface Changes

#### Story Cards
- Visual badge indicating "Basic" or "Advanced"
- Different icon or color scheme
- Quick actions adapted to story type

#### Navigation Menu
- Dynamic based on user's content
- "My Worlds" hidden if user only has shadow worlds
- Tooltips explaining each section

#### Story Creation
- "Start Writing" button (prominent, leads to Basic)
- Toggle on creation form for Basic/Advanced
- Clear explanation of differences

#### Story Detail Page
- Basic: Simplified interface, upgrade prompt
- Advanced: Full feature set visible

### 4. Workflow Implementations

#### Basic Story Creation Flow
1. User clicks "Start Writing"
2. Enters title and description
3. System creates:
   - Story (type='basic')
   - Shadow world (is_shadow=true, name="[Title] World")
   - Act 1 (no number shown)
4. Redirects to act editor

#### Upgrade Flow (Basic → Advanced)
1. User clicks "Upgrade to Advanced"
2. Confirmation dialog explains changes
3. System updates:
   - Story type to 'advanced'
   - Shadow world becomes visible
4. Prompts user to name their world
5. Shows tour of newly available features

### 5. API Endpoints Updates

#### New Endpoints
- `POST /api/stories/basic` - Create Basic Story
- `POST /api/stories/{id}/upgrade` - Upgrade to Advanced
- `GET /api/stories?type=basic|advanced` - Filter by type

#### Modified Endpoints
- `GET /api/worlds` - Exclude shadow worlds by default
- `GET /api/stories` - Include story_type in response

### 6. Service Layer Changes

#### Story Service
- `create_basic_story()` - Creates story with shadow world
- `upgrade_to_advanced()` - Converts Basic to Advanced
- `get_story_features()` - Returns available features by type

#### World Service
- Update queries to filter out shadow worlds
- Add method to convert shadow world to regular

### 7. Frontend Components

#### New Components
- `BasicStoryForm` - Minimal creation form
- `StoryTypeBadge` - Visual indicator component
- `UpgradePrompt` - Upgrade UI component
- `FeatureGate` - Conditionally show/hide features

#### Updated Components
- `StoryCard` - Add type badge
- `Navigation` - Dynamic menu items
- `StoryDetail` - Conditional rendering by type

### 8. Migration Plan

#### Database Migration
```sql
-- Add story_type to stories
ALTER TABLE stories 
ADD COLUMN story_type VARCHAR(20) NOT NULL DEFAULT 'advanced';

-- Add is_shadow to worlds
ALTER TABLE worlds 
ADD COLUMN is_shadow BOOLEAN NOT NULL DEFAULT FALSE;

-- Update existing data
UPDATE stories SET story_type = 'advanced';
UPDATE worlds SET is_shadow = FALSE;
```

#### Rollout Strategy
1. Deploy database changes
2. Deploy backend with backward compatibility
3. Deploy frontend with feature flags
4. Enable features gradually
5. Monitor for issues

### 9. Testing Strategy

#### Unit Tests
- Story creation (Basic and Advanced)
- Upgrade mechanism
- Shadow world visibility
- Feature restrictions

#### Integration Tests
- Full Basic Story workflow
- Upgrade workflow
- World list filtering
- AI context handling

#### UI/UX Tests
- Story type badges display
- Navigation changes
- Feature visibility
- Upgrade prompts

### 10. Future Considerations

#### Phase 2 Features
- Document import as Basic Stories
- Collaborative editing for Basic Stories
- Basic Story series/connections
- Templates and prompts library

#### Potential Enhancements
- Story type conversion analytics
- Advanced story feature usage tracking
- Guided world-building after upgrade
- Progressive feature unlocking

## Success Metrics

### Primary Metrics
- New user activation (create first story)
- Time to first written content
- Basic to Advanced conversion rate
- User retention by story type

### Secondary Metrics
- Feature adoption post-upgrade
- Publishing rate by story type
- User satisfaction scores
- Support ticket volume

## Risks and Mitigations

### Technical Risks
- **Risk**: Migration failures on large databases
- **Mitigation**: Batch processing, rollback plan

### User Experience Risks
- **Risk**: User confusion about story types
- **Mitigation**: Clear UI indicators, helpful tooltips

### Business Risks
- **Risk**: Users staying in Basic mode too long
- **Mitigation**: Gentle upgrade prompts, feature teasers

## Conclusion

The Basic/Advanced Story system provides a low-friction entry point for new users while preserving the full power of the platform for advanced users. By hiding complexity initially and revealing it progressively, we can improve new user activation while maintaining the sophisticated features that power users love.