# Character Roles Using Prompts Table - Implementation Plan

## Overview
Transform the current free-text `role_in_story` field to use the prompts table for standardized, manageable character role options.

## Phase 1: Schema & Model Updates

### 1.1 Update PromptTypeEnum
**File:** `/app/models/prompt.py`

Add new enum values:
```python
class PromptTypeEnum(str, enum.Enum):
    # ... existing values ...
    CHARACTER_ROLE = "CHARACTER_ROLE"
    STORY_GENRE = "STORY_GENRE"  # For story generation
    STORY_TONE = "STORY_TONE"    # For story generation
    STORY_CONFLICT = "STORY_CONFLICT"  # For story generation
```

### 1.2 Update Association Tables
**Current state:** `role_in_story` is a simple String(255) field

**Option A: Keep as String (Recommended)**
- Store the prompt's `title` value in `role_in_story`
- Simple migration, no foreign key needed
- Flexible - allows custom roles if needed

**Option B: Add Foreign Key to Prompts**
```python
# In story_character_association table
Column("role_prompt_id", Integer, ForeignKey("prompts.id"), nullable=True)
```
- More rigid but enforces referential integrity
- Would need to handle prompt deletion

## Phase 2: Database Migration

### 2.1 Create Alembic Migration
```bash
alembic revision --autogenerate -m "Add character role prompt types and story metadata fields"
```

### 2.2 Migration Content
```python
def upgrade():
    # 1. Add story metadata fields
    op.add_column('stories', sa.Column('story_genre', sa.String(100), nullable=True))
    op.add_column('stories', sa.Column('story_tone', sa.String(100), nullable=True))
    op.add_column('stories', sa.Column('primary_conflict_type', sa.String(100), nullable=True))
    
    # 2. If using Option B (foreign key approach):
    # op.add_column('story_character_association', 
    #     sa.Column('role_prompt_id', sa.Integer(), 
    #     sa.ForeignKey('prompts.id'), nullable=True))

def downgrade():
    op.drop_column('stories', 'story_genre')
    op.drop_column('stories', 'story_tone')
    op.drop_column('stories', 'primary_conflict_type')
    # If Option B: op.drop_column('story_character_association', 'role_prompt_id')
```

## Phase 3: Seed Data

### 3.1 Character Role Prompts
```sql
INSERT INTO prompts (title, prompt_type, prompt_content, reason_to_use, age_target, is_active) VALUES
-- Primary Roles
('Protagonist', 'CHARACTER_ROLE', 'Protagonist', 'The main character driving the story forward, facing challenges and growing', 'ALL_AGES', true),
('Antagonist', 'CHARACTER_ROLE', 'Antagonist', 'The primary opposing force creating conflict for the protagonist', 'ALL_AGES', true),
('Deuteragonist', 'CHARACTER_ROLE', 'Deuteragonist', 'The second most important character, often a close ally or rival', 'ALL_AGES', true),

-- Supporting Roles
('Mentor', 'CHARACTER_ROLE', 'Mentor', 'Wise guide who provides advice, training, or magical gifts', 'ALL_AGES', true),
('Sidekick', 'CHARACTER_ROLE', 'Sidekick', 'Loyal companion providing support, comic relief, or assistance', 'ALL_AGES', true),
('Love Interest', 'CHARACTER_ROLE', 'Love Interest', 'Romantic partner or potential partner creating emotional stakes', 'ALL_AGES', true),
('Comic Relief', 'CHARACTER_ROLE', 'Comic Relief', 'Character providing humor and levity to balance serious moments', 'ALL_AGES', true),

-- Functional Roles
('Herald', 'CHARACTER_ROLE', 'Herald', 'Brings the call to adventure or important news that starts the journey', 'ALL_AGES', true),
('Threshold Guardian', 'CHARACTER_ROLE', 'Threshold Guardian', 'Tests the hero before allowing progress to the next stage', 'ALL_AGES', true),
('Shapeshifter', 'CHARACTER_ROLE', 'Shapeshifter', 'Character whose loyalty or nature is uncertain, creating doubt', 'ALL_AGES', true),
('Shadow', 'CHARACTER_ROLE', 'Shadow', 'Represents the dark side or repressed aspects of the protagonist', 'ALL_AGES', true),
('Trickster', 'CHARACTER_ROLE', 'Trickster', 'Catalyst for change through mischief, breaking rules and conventions', 'ALL_AGES', true),

-- Minor Roles
('Ally', 'CHARACTER_ROLE', 'Ally', 'Supporting character who helps the protagonist achieve goals', 'ALL_AGES', true),
('Minion', 'CHARACTER_ROLE', 'Minion', 'Subordinate of the antagonist carrying out orders', 'ALL_AGES', true),
('Victim', 'CHARACTER_ROLE', 'Victim', 'Character in need of rescue or protection, raising stakes', 'ALL_AGES', true),
('Witness', 'CHARACTER_ROLE', 'Witness', 'Observer who provides crucial information or testimony', 'ALL_AGES', true),
('Background Character', 'CHARACTER_ROLE', 'Background Character', 'Populates the world without significant story impact', 'ALL_AGES', true);
```

### 3.2 Story Generation Option Prompts
```sql
-- Story Genres
INSERT INTO prompts (title, prompt_type, prompt_content, reason_to_use, age_target, is_active) VALUES
('Fantasy Adventure', 'STORY_GENRE', 'Fantasy Adventure', 'Epic quests with magic, mythical creatures, and heroic journeys', 'ALL_AGES', true),
('Sci-Fi Thriller', 'STORY_GENRE', 'Sci-Fi Thriller', 'Suspenseful stories with advanced technology and futuristic settings', 'ALL_AGES', true),
('Mystery Drama', 'STORY_GENRE', 'Mystery Drama', 'Character-driven narratives centered on solving puzzles or crimes', 'ALL_AGES', true),
('Historical Fiction', 'STORY_GENRE', 'Historical Fiction', 'Stories set in authentic historical periods with period-accurate details', 'ALL_AGES', true),
('Urban Fantasy', 'STORY_GENRE', 'Urban Fantasy', 'Magic and supernatural elements in modern city settings', 'ALL_AGES', true);

-- Story Tones
INSERT INTO prompts (title, prompt_type, prompt_content, reason_to_use, age_target, is_active) VALUES
('Hopeful', 'STORY_TONE', 'Hopeful', 'Optimistic atmosphere where characters overcome challenges positively', 'ALL_AGES', true),
('Dark', 'STORY_TONE', 'Dark', 'Serious, grim mood exploring difficult themes and moral ambiguity', 'ALL_AGES', true),
('Whimsical', 'STORY_TONE', 'Whimsical', 'Playful and imaginative with unexpected twists and magical realism', 'ALL_AGES', true),
('Epic', 'STORY_TONE', 'Epic', 'Grand scale with high stakes and legendary scope', 'ALL_AGES', true),
('Intimate', 'STORY_TONE', 'Intimate', 'Personal, character-focused with emotional depth', 'ALL_AGES', true);

-- Conflict Types
INSERT INTO prompts (title, prompt_type, prompt_content, reason_to_use, age_target, is_active) VALUES
('Character vs. Self', 'STORY_CONFLICT', 'Character vs. Self', 'Internal struggles with personal demons or difficult decisions', 'ALL_AGES', true),
('Character vs. Character', 'STORY_CONFLICT', 'Character vs. Character', 'Direct opposition between individuals with conflicting goals', 'ALL_AGES', true),
('Character vs. Society', 'STORY_CONFLICT', 'Character vs. Society', 'Protagonist challenges social norms or unjust systems', 'ALL_AGES', true),
('Character vs. Nature', 'STORY_CONFLICT', 'Character vs. Nature', 'Survival against natural disasters or environmental forces', 'ALL_AGES', true),
('Character vs. Technology', 'STORY_CONFLICT', 'Character vs. Technology', 'Struggle against artificial intelligence or technological systems', 'ALL_AGES', true);
```

## Phase 4: API Updates

### 4.1 New Endpoint for Character Roles
```python
@router.get("/api/v1/prompts/character-roles")
async def get_character_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available character role options from prompts table"""
    roles = await crud_prompt.get_by_type(
        db, 
        prompt_type=PromptTypeEnum.CHARACTER_ROLE,
        is_active=True
    )
    return roles
```

### 4.2 Update Character Association Endpoints
Modify existing endpoints to validate `role_in_story` against available prompts.

## Phase 5: Frontend Updates

### 5.1 Character Role Selection
Update character-story association UI:
```javascript
// Load available roles
async function loadCharacterRoles() {
    const response = await fetch('/api/v1/prompts/character-roles');
    const roles = await response.json();
    
    const roleSelect = document.getElementById('character-role-select');
    roles.forEach(role => {
        const option = document.createElement('option');
        option.value = role.title;
        option.textContent = role.title;
        option.setAttribute('title', role.reason_to_use);
        roleSelect.appendChild(option);
    });
}
```

### 5.2 Story Generation Modal Updates
Already covered in STORY_GENERATION_SPEC.md

## Phase 6: Model Updates

### 6.1 Story Model
**File:** `/app/models/story.py`
```python
class Story(Base):
    # ... existing fields ...
    story_genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    story_tone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    primary_conflict_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
```

### 6.2 Schema Updates
**File:** `/app/schemas/story.py`
```python
class StoryBase(BaseModel):
    # ... existing fields ...
    story_genre: Optional[str] = Field(None, max_length=100)
    story_tone: Optional[str] = Field(None, max_length=100)
    primary_conflict_type: Optional[str] = Field(None, max_length=100)
```

## Implementation Order

1. **Day 1: Backend Foundation**
   - Update PromptTypeEnum
   - Create Alembic migration
   - Update Story model and schemas
   - Run migration

2. **Day 2: Data & API**
   - Insert seed data for all prompt types
   - Create API endpoints for fetching options
   - Update existing character association logic

3. **Day 3: Frontend Integration**
   - Update character role selection UI
   - Implement story generation modal
   - Add tooltips showing `reason_to_use`

4. **Day 4: Testing & Polish**
   - Test character role assignment
   - Test story generation with new options
   - Add any missing validations

## Benefits

1. **Consistency**: Standardized roles across all stories
2. **Guidance**: `reason_to_use` helps users understand each role
3. **Flexibility**: Admins can add/modify roles without code changes
4. **Discoverability**: Users can see all available options
5. **Future-Proof**: Same pattern for other dropdowns (themes, settings, etc.)

## Migration Strategy for Existing Data

For existing `role_in_story` values:
1. Analyze current free-text values
2. Map common values to new standardized roles
3. Create migration script to update existing data
4. Keep unmapped values as-is (if allowing custom roles)

## Considerations

1. **Backward Compatibility**: Keep `role_in_story` as string to allow custom values
2. **Validation**: Soft validation - suggest prompts but allow custom text
3. **UI/UX**: Show prompts as suggestions with autocomplete
4. **Performance**: Cache character role prompts in frontend

This approach creates a flexible, maintainable system for managing character roles and story generation options!