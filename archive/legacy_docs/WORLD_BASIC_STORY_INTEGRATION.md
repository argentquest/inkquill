# World Basic Story Integration - Technical Specifications

## Overview

Integration of Basic Story Editor functionality within existing worlds, allowing users to create AI-generated stories that automatically incorporate world context and extract new elements back into the world.

## Feature Requirements

### Core Functionality
- **Story Type**: New "World Basic Story" classification
- **Context Integration**: Automatic inclusion of world element summaries + Context content
- **Element Extraction**: Auto-create new characters/locations from generated stories
- **Element Linking**: Auto-link stories to both new and existing world elements
- **No Constraints**: Remove length/structure limitations from regular Basic Stories

### User Experience
- **Access**: "Create World Basic Story" button near existing "Create Story" on world pages
- **Permissions**: No special permissions required - follows world visibility rules
- **Organization**: World Basic Stories listed alongside Advanced Stories in world views
- **Visibility**: Stories inherit world's collaboration level visibility settings

### AI Configuration
- **Model Selection**: Use world's preferred AI model settings when available
- **Fallback**: Default to standard Basic Story AI configuration if world has no preferences
- **Context Injection**: Prepend world context to story generation prompts

## Technical Implementation

### Database Schema Changes

#### Story Model Updates
```sql
-- Add new story type enum value
ALTER TYPE story_type_enum ADD VALUE 'world_basic';

-- Story table already has world_id and user_id, no changes needed
```

#### World AI Model Settings
```sql
-- Add AI model preferences to worlds table (if not already exists)
ALTER TABLE worlds ADD COLUMN preferred_ai_model VARCHAR(100);
ALTER TABLE worlds ADD COLUMN ai_model_settings JSONB;
```

### API Endpoints

#### New World Basic Story Creation
```
POST /api/v1/worlds/{world_id}/basic-stories
```

**Request Body:**
```json
{
  "title": "Story title",
  "initial_prompt": "User's story prompt",
  "ai_instructions": "Additional AI instructions (optional)"
}
```

**Response:**
```json
{
  "story_id": 123,
  "world_id": 456,
  "story_type": "world_basic",
  "generated_content": "...",
  "extracted_elements": {
    "characters": [{"name": "New Character", "id": 789}],
    "locations": [{"name": "New Location", "id": 790}]
  },
  "linked_elements": {
    "existing_characters": [{"name": "Existing Character", "id": 100}],
    "existing_locations": [{"name": "Existing Location", "id": 101}]
  }
}
```

### Service Layer Architecture

#### WorldBasicStoryService
```python
class WorldBasicStoryService:
    async def create_world_basic_story(
        self, 
        world_id: int, 
        user_id: int, 
        story_prompt: str,
        db: AsyncSession
    ) -> WorldBasicStoryResult:
        # 1. Validate user permissions
        # 2. Fetch world context
        # 3. Build AI prompt with world context
        # 4. Generate story via AI service
        # 5. Extract new elements
        # 6. Link existing elements
        # 7. Create story record
        # 8. Return complete result
```

#### World Context Builder
```python
class WorldContextBuilder:
    async def build_context_prompt(self, world_id: int, db: AsyncSession) -> str:
        # Fetch world elements
        world = await self.get_world_with_elements(world_id, db)
        
        # Build context sections
        context_parts = [
            "WORLD CONTEXT - Use this information if relevant to the story:",
            f"World: {world.name}",
            f"Description: {world.description}",
            "",
            "CHARACTERS:",
            *[f"- {char.name}: {char.description}" for char in world.characters],
            "",
            "LOCATIONS:", 
            *[f"- {loc.name}: {loc.description}" for loc in world.locations],
            "",
            "LORE:",
            *[f"- {lore.title}: {lore.description}" for lore in world.lore_items],
            "",
            "Context CONTEXT:",
            await self.get_context_context(world_id),
            "",
            "INSTRUCTIONS: Use the above world context when relevant. You may introduce new characters and locations that fit the world."
        ]
        
        return "\n".join(context_parts)
```

#### Element Extraction Service
```python
class ElementExtractionService:
    async def extract_elements_from_story(
        self, 
        story_content: str, 
        world_id: int,
        db: AsyncSession
    ) -> ExtractedElements:
        # Use AI to identify new characters and locations
        # Check against existing world elements
        # Handle name conflicts with modified names
        # Create new world elements
        # Return extraction results
```

#### Element Linking Service
```python
class ElementLinkingService:
    async def link_story_elements(
        self,
        story_id: int,
        story_content: str,
        world_id: int,
        db: AsyncSession
    ) -> LinkedElements:
        # Identify mentions of existing world elements
        # Create story-element associations
        # Return linking results
```

### Frontend Integration

#### World Page Updates
```typescript
// Add World Basic Story creation button
interface WorldPageProps {
  world: World;
  canCreateStories: boolean;
}

const WorldBasicStoryButton = ({ worldId }: { worldId: number }) => {
  const handleCreateWorldBasicStory = async () => {
    // Open World Basic Story creation modal
    // Similar to regular Basic Story flow but with world context
  };
  
  return (
    <button 
      onClick={handleCreateWorldBasicStory}
      className="btn btn-primary"
    >
      <i className="fas fa-magic me-2"></i>
      Create World Basic Story
    </button>
  );
};
```

#### Story Creation Modal
```typescript
// Modified Basic Story creation flow
interface WorldBasicStoryModalProps {
  worldId: number;
  onSuccess: (story: Story) => void;
}

const WorldBasicStoryModal = ({ worldId, onSuccess }: WorldBasicStoryModalProps) => {
  // Similar to BasicStoryModal but:
  // - Include world context preview
  // - Show world AI model being used
  // - Display extracted/linked elements after generation
};
```

### Story Display Integration

#### Story List Component Updates
```typescript
// Add World Basic Story type indicator
const StoryTypeIndicator = ({ story }: { story: Story }) => {
  if (story.story_type === 'world_basic') {
    return (
      <span className="badge bg-info">
        <i className="fas fa-magic me-1"></i>
        World Basic Story
      </span>
    );
  }
  // ... other story types
};
```

#### Story Detail View
```typescript
// Show extracted/linked elements for World Basic Stories
const WorldBasicStoryDetails = ({ story }: { story: Story }) => {
  return (
    <div className="world-basic-story-details">
      <h5>World Elements</h5>
      <div className="extracted-elements">
        <h6>New Elements Created:</h6>
        {story.extracted_elements?.map(element => (
          <ElementLink key={element.id} element={element} />
        ))}
      </div>
      <div className="linked-elements">
        <h6>World Elements Referenced:</h6>
        {story.linked_elements?.map(element => (
          <ElementLink key={element.id} element={element} />
        ))}
      </div>
    </div>
  );
};
```

## Implementation Phases

### Phase 1: Core Infrastructure
1. Database schema updates
2. World Basic Story service creation
3. Basic API endpoint implementation
4. World context builder service

### Phase 2: AI Integration
1. Element extraction service with AI
2. Element linking service
3. Context content integration
4. Conflict resolution for duplicate names

### Phase 3: Frontend Integration
1. World page UI updates
2. Story creation modal adaptation
3. Story list display updates
4. Element linking visualization

### Phase 4: Polish & Optimization
1. Performance optimization for large worlds
2. Enhanced element extraction accuracy
3. User experience refinements
4. Analytics and monitoring

## Success Metrics

- **Usage**: Number of World Basic Stories created per world
- **Quality**: User satisfaction with element extraction accuracy
- **Engagement**: Time spent reading World Basic Stories vs regular stories
- **Content Growth**: New world elements created through World Basic Stories
- **Performance**: Story generation time with world context

## Technical Considerations

### Performance
- **Context Size**: Large worlds may generate very long prompts
- **Caching**: Cache world context for repeated story generations
- **Context Optimization**: Efficient retrieval of relevant world content

### Data Integrity
- **Element Conflicts**: Robust handling of name conflicts
- **Association Accuracy**: High precision in element linking
- **Content Validation**: Ensure generated content fits world themes

### Scalability
- **Concurrent Generation**: Handle multiple simultaneous story generations
- **Database Performance**: Efficient queries for world context building
- **AI Rate Limits**: Manage AI service usage for popular worlds

---

*This integration bridges the gap between simple story generation and complex world-building, providing users with an easy entry point to contribute meaningful content to existing worlds.*
