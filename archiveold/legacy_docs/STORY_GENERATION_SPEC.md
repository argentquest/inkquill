# Story Generation Feature - Technical Specification

## Overview
This feature allows authenticated users to automatically generate comprehensive story outlines by selecting world elements (characters, locations, lore items) and using AI to create a structured three-act narrative following the Hero's Journey framework.

## User Flow
1. User navigates to world hierarchy screen
2. User clicks "Generate New Story" button 
3. Modal popup appears showing all world elements for selection
4. User selects desired elements (max 4 characters, 3 locations, 2 lore items)
5. User specifies story parameters:
   - **Story Genre** (dropdown: Fantasy Adventure, Sci-Fi Thriller, Mystery Drama, etc.)
   - **Story Tone** (dropdown: Hopeful, Dark, Whimsical, Gritty, Humorous, etc.)
   - **Conflict Type** (dropdown: Character vs. Self, Character vs. Society, Character vs. Nature, etc.)
6. User chooses AI model for generation
7. User clicks "Generate Story"
8. AI creates JSON story outline using selected elements and specified parameters
9. System creates complete story structure in database
10. User is redirected to story detail page

## Database Changes

### Stories Table - New Fields
Add the following optional fields to the existing `stories` table:

```sql
ALTER TABLE stories ADD COLUMN story_genre VARCHAR(100);
ALTER TABLE stories ADD COLUMN story_tone VARCHAR(100); 
ALTER TABLE stories ADD COLUMN primary_conflict_type VARCHAR(100);
```

**Field Descriptions:**
- `story_genre`: Primary genre (e.g., "Sci-Fi Adventure", "Fantasy Drama")
- `story_tone`: Overall tone (e.g., "Whimsical", "Gritty", "Hopeful") 
- `primary_conflict_type`: Main conflict type (e.g., "Character vs. Self", "Character vs. Society")

### No Schema Changes Required
- Acts and Scenes tables already support the generated content
- Generated descriptions will populate `act_summary` and `scene_summary` fields
- Point of view information will be stored in scene summaries

### Prompts Table - New Option Types
Add new prompt records to manage dropdown options:

**Story Genre Options** (`prompt_type = "story_genre"`):
```sql
INSERT INTO prompts (title, prompt_type, content, reason_to_use, age_target, is_active) VALUES
('Fantasy Adventure', 'story_genre', 'Fantasy Adventure', 'Epic quests with magic, mythical creatures, and heroic journeys in imaginary worlds', 'ALL_AGES', true),
('Sci-Fi Thriller', 'story_genre', 'Sci-Fi Thriller', 'Suspenseful stories featuring advanced technology, space exploration, or dystopian futures', 'ALL_AGES', true),
('Mystery Drama', 'story_genre', 'Mystery Drama', 'Character-driven narratives centered around solving puzzles, crimes, or uncovering secrets', 'ALL_AGES', true),
('Romance Comedy', 'story_genre', 'Romance Comedy', 'Light-hearted love stories with humor, misunderstandings, and happy endings', 'ALL_AGES', true),
-- etc.
```

**Story Tone Options** (`prompt_type = "story_tone"`):
```sql
INSERT INTO prompts (title, prompt_type, content, reason_to_use, age_target, is_active) VALUES
('Hopeful', 'story_tone', 'Hopeful', 'Creates an optimistic atmosphere where characters overcome challenges with positive outcomes', 'ALL_AGES', true),
('Dark', 'story_tone', 'Dark', 'Establishes a serious, grim mood exploring difficult themes and moral ambiguity', 'ALL_AGES', true),
('Whimsical', 'story_tone', 'Whimsical', 'Brings playful, imaginative elements with unexpected twists and magical realism', 'ALL_AGES', true),
('Gritty', 'story_tone', 'Gritty', 'Raw, realistic portrayal of harsh realities and tough character choices', 'ALL_AGES', true),
-- etc.
```

**Conflict Type Options** (`prompt_type = "story_conflict"`):
```sql
INSERT INTO prompts (title, prompt_type, content, reason_to_use, age_target, is_active) VALUES
('Character vs. Self', 'story_conflict', 'Character vs. Self', 'Internal struggles with personal demons, difficult decisions, or identity crises', 'ALL_AGES', true),
('Character vs. Society', 'story_conflict', 'Character vs. Society', 'Protagonist challenges social norms, unjust systems, or cultural expectations', 'ALL_AGES', true),
('Character vs. Nature', 'story_conflict', 'Character vs. Nature', 'Survival stories against natural disasters, wilderness, or environmental forces', 'ALL_AGES', true),
-- etc.
```

This approach allows admins to manage available options through the existing prompts interface.

## API Endpoint

### GET /api/v1/prompts/story-options

**Authentication:** Required (logged-in users only)

**Purpose:** Fetch available options for story generation dropdowns

**Response:**
```json
{
  "genres": [
    {
      "id": 1, 
      "title": "Fantasy Adventure", 
      "content": "Fantasy Adventure",
      "reason_to_use": "Epic quests with magic, mythical creatures, and heroic journeys in imaginary worlds"
    },
    {
      "id": 2, 
      "title": "Sci-Fi Thriller", 
      "content": "Sci-Fi Thriller",
      "reason_to_use": "Suspenseful stories featuring advanced technology, space exploration, or dystopian futures"
    }
  ],
  "tones": [
    {
      "id": 10, 
      "title": "Hopeful", 
      "content": "Hopeful",
      "reason_to_use": "Creates an optimistic atmosphere where characters overcome challenges with positive outcomes"
    },
    {
      "id": 11, 
      "title": "Dark", 
      "content": "Dark",
      "reason_to_use": "Establishes a serious, grim mood exploring difficult themes and moral ambiguity"
    }
  ],
  "conflicts": [
    {
      "id": 20, 
      "title": "Character vs. Self", 
      "content": "Character vs. Self",
      "reason_to_use": "Internal struggles with personal demons, difficult decisions, or identity crises"
    },
    {
      "id": 21, 
      "title": "Character vs. Society", 
      "content": "Character vs. Society",
      "reason_to_use": "Protagonist challenges social norms, unjust systems, or cultural expectations"
    }
  ]
}
```

### POST /api/v1/worlds/{world_id}/stories/generate

**Authentication:** Required (logged-in users only)

**Request Body:**
```json
{
  "selected_characters": [1, 3, 7], // Array of character IDs (max 4)
  "selected_locations": [2, 5],     // Array of location IDs (max 3)  
  "selected_lore_items": [1],       // Array of lore item IDs (max 2)
  "story_genre": "Fantasy Adventure", // User-selected genre
  "story_tone": "Hopeful",           // User-selected tone
  "primary_conflict_type": "Character vs. Society", // User-selected conflict
  "ai_model_config_id": 5           // ID of AI model to use
}
```

**Response (Success):**
```json
{
  "success": true,
  "story_id": 123,
  "generated_outline": {
    "title": "The Crystal of Eldara",
    "story_genre": "Fantasy Adventure",
    "story_tone": "Hopeful",
    "primary_conflict_type": "Character vs. Society",
    "acts_created": 3,
    "scenes_created": 14,
    "characters_used": ["Lyra", "Gareth", "Elder Mara"],
    "locations_used": ["Crystal Caverns", "Village of Thornhaven"],
    "lore_items_used": ["Ancient Crystal"]
  },
  "summary": "Created story 'The Crystal of Eldara' with 3 acts and 14 scenes"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid JSON generated by AI",
  "partial_data": {
    "story_id": 123,
    "created_acts": 2,
    "created_scenes": 8
  },
  "message": "Story partially created. Please review and complete manually."
}
```

**Error Handling:**
- Malformed JSON: Parse valid portions, create partial story, notify user
- Database errors: Rollback transaction, return error
- AI service errors: Return error with retry option
- Missing world elements: Return validation error

## AI Integration

### New Plugin: StoryStructurePlugin

**Location:** `app/services/ai/plugins/story_structure_plugin.py`

**Function:** `generate_story_outline`

**Semantic Kernel Integration:**
```python
@kernel_function(
    description="Generate a comprehensive story outline using world elements",
    name="generate_story_outline"
)
async def generate_story_outline(
    self,
    characters: str,  # JSON string of character objects
    locations: str,   # JSON string of location objects  
    lore_items: str   # JSON string of lore item objects
) -> str:
```

**Prompt File:** `/app/prompts/system/story_generation.txt` (already created)

**Model Configuration:**
- Use user-selected AI model
- Recommended settings: temperature=0.3, max_tokens=4000 for structured output
- JSON mode enabled if available on the model

## Frontend Implementation

### Modal Component: StoryGenerationModal

**Location:** Add to existing hierarchy page (`/app/templates/pages/world_hierarchy.html`)

**Modal Structure:**
```html
<div class="modal fade" id="storyGenerationModal">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5>Generate New Story</h5>
      </div>
      <div class="modal-body">
        <!-- Element Selection Sections -->
        <div class="selection-section">
          <h6>Characters (Select up to 4)</h6>
          <div class="element-grid">
            <!-- Character checkboxes with names/descriptions -->
          </div>
        </div>
        
        <div class="selection-section">
          <h6>Locations (Select up to 3)</h6>
          <div class="element-grid">
            <!-- Location checkboxes -->
          </div>
        </div>
        
        <div class="selection-section">
          <h6>Lore Items (Select up to 2)</h6>
          <div class="element-grid">
            <!-- Lore item checkboxes -->
          </div>
        </div>
        
        <div class="story-parameters">
          <h6>Story Parameters</h6>
          <div class="row">
            <div class="col-md-4">
              <label for="story-genre-select">Genre</label>
              <select id="story-genre-select" class="form-select" required>
                <option value="">Select Genre...</option>
                <!-- Populated from prompts table with prompt_type="story_genre" -->
              </select>
            </div>
            <div class="col-md-4">
              <label for="story-tone-select">Tone</label>
              <select id="story-tone-select" class="form-select" required>
                <option value="">Select Tone...</option>
                <!-- Populated from prompts table with prompt_type="story_tone" -->
              </select>
            </div>
            <div class="col-md-4">
              <label for="conflict-type-select">Primary Conflict</label>
              <select id="conflict-type-select" class="form-select" required>
                <option value="">Select Conflict...</option>
                <!-- Populated from prompts table with prompt_type="story_conflict" -->
              </select>
            </div>
          </div>
        </div>
        
        <div class="model-selection">
          <h6>AI Model</h6>
          <select id="ai-model-select" class="form-select" required>
            <!-- Populated from user's available models -->
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary" id="generate-story-btn">Generate Story</button>
      </div>
    </div>
  </div>
</div>
```

**JavaScript Functions:**
- `openStoryGenerationModal()` - Initialize and show modal
- `loadWorldElements()` - Fetch characters/locations/lore for current world
- `loadStoryOptions()` - Fetch genre/tone/conflict options from prompts table
- `validateSelection()` - Enforce limits (4/3/2) and required story parameters
- `generateStory()` - Call API endpoint with selected elements and parameters
- `handleGenerationResult()` - Process response and redirect

### Trigger Button
Add to world hierarchy page:
```html
<button type="button" class="btn btn-success" onclick="openStoryGenerationModal()">
  <i class="fas fa-magic"></i> Generate New Story
</button>
```

## Backend Implementation

### Service Layer

**Location:** `app/services/story_generation_service.py`

**Key Functions:**
```python
async def generate_story_from_elements(
    world_id: int,
    selected_characters: List[int],
    selected_locations: List[int], 
    selected_lore_items: List[int],
    ai_model_config_id: int,
    user_id: int
) -> Dict[str, Any]:
    """
    Main orchestration function that:
    1. Fetches world elements from database
    2. Calls AI service for story generation  
    3. Parses and validates JSON response
    4. Creates story/acts/scenes in database
    5. Returns result summary
    """

async def create_story_structure_from_json(
    outline_json: Dict[str, Any],
    world_id: int,
    user_id: int
) -> int:
    """
    Creates complete story structure in database from AI-generated JSON
    """

async def parse_and_validate_outline(
    ai_response: str
) -> Tuple[Dict[str, Any], List[str]]:
    """
    Parses AI response, validates structure, returns outline and errors
    """
```

### Router

**Location:** `app/routers/stories.py`

**Endpoint Implementation:**
```python
@router.post("/api/v1/worlds/{world_id}/stories/generate")
async def generate_story_outline(
    world_id: int,
    request: StoryGenerationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new story from selected world elements
    """
```

**Request/Response Models:**
```python
class StoryGenerationRequest(BaseModel):
    selected_characters: List[int] = Field(max_items=4)
    selected_locations: List[int] = Field(max_items=3)  
    selected_lore_items: List[int] = Field(max_items=2)
    ai_model_config_id: int

class StoryGenerationResponse(BaseModel):
    success: bool
    story_id: Optional[int] = None
    generated_outline: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    partial_data: Optional[Dict[str, Any]] = None
```

## Data Flow

### Generation Process
1. **Element Retrieval:** Fetch selected characters/locations/lore with full details
2. **Prompt Construction:** Build context strings for AI prompt template
3. **AI Generation:** Call Semantic Kernel with story generation function
4. **JSON Parsing:** Validate and parse AI response into structured data
5. **Database Creation:** Create story record with metadata fields
6. **Act Creation:** Create 3 act records with summaries from JSON
7. **Scene Creation:** Create all scene records with summaries and metadata
8. **Response:** Return story ID and generation summary

### Error Recovery
- **Partial JSON:** Extract valid acts/scenes, create what possible
- **Invalid Structure:** Log error, create basic story shell, notify user
- **Database Errors:** Full rollback, return error for retry
- **AI Timeout:** Return error with option to retry

## Content Mapping

### JSON to Database Mapping
- `title` → `stories.title`
- `story_genre` → `stories.story_genre` 
- `story_tone` → `stories.story_tone`
- `primary_conflict_type` → `stories.primary_conflict_type`
- `acts[].name` → `acts.title`
- `acts[].scenes[].description` → `scenes.scene_summary`
- `acts[].scenes[].point_of_view` → `scenes.scene_summary` (appended)
- `acts[].scenes[].protagonist_arc_note` → `scenes.scene_summary` (appended)

### Content vs Summary
- All generated text goes to summary fields, NOT content fields
- Content fields remain empty for user to write actual narrative
- Summary fields provide story structure and guidance

## Security & Validation

### Access Control
- Endpoint requires authentication (logged-in users only)
- Users can only generate stories for worlds they own
- Rate limiting: Max 5 story generations per hour per user

### Input Validation  
- World must exist and belong to user
- Selected elements must exist and belong to specified world
- Element limits enforced (4/3/2)
- AI model must be available to user

### Data Validation
- Generated JSON structure validation
- Character/location/lore usage validation
- Required fields presence validation
- Content length validation for database fields

## Testing Strategy

### Unit Tests
- JSON parsing and validation functions
- Database creation functions  
- Element selection validation
- Error handling scenarios

### Integration Tests
- Full generation workflow
- Database transaction rollback
- AI service integration
- API endpoint responses

### UI Tests
- Modal interaction and validation
- Element selection limits
- Error message display
- Success flow to story detail page

## Performance Considerations

### Database
- Use transactions for atomic story creation
- Batch insert acts and scenes for efficiency
- Index on new story metadata fields if needed

### AI Service
- Implement timeout handling (30 seconds)
- Retry logic for transient failures
- Token usage tracking and cost logging

### Frontend
- Lazy load world elements in modal
- Loading states during generation
- Optimistic UI updates where possible

## Future Enhancements

### Phase 2 Features
- Template-based story generation (different story structures)
- Character relationship mapping in generated stories
- Story revision and regeneration
- Export generated outlines to external formats

### Analytics
- Track popular element combinations
- Story generation success rates
- User engagement with generated vs manual stories
- AI model performance comparison

## Configuration

### Environment Variables
No new environment variables required - uses existing AI service configuration.

### Feature Flags
Consider adding feature flag for story generation:
```python
ENABLE_STORY_GENERATION = True  # In config.py
```

## Monitoring

### Logging
- Story generation requests and results
- AI service call duration and token usage
- JSON parsing failures and recovery attempts
- Database creation success/failure rates

### Metrics
- Generation completion rate
- Average generation time
- User adoption rate
- Generated story quality (user ratings)

---

## Implementation Priority

1. **Database migrations** - Add new fields to stories table
2. **Backend service** - Core generation logic and API endpoint  
3. **AI plugin** - Semantic Kernel integration
4. **Frontend modal** - Element selection UI
5. **Integration** - Connect all pieces and test end-to-end
6. **Polish** - Error handling, loading states, validation