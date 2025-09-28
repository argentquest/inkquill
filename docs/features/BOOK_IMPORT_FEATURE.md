# Book/Novel Import Feature Specification

## Overview
Enhanced document import system that intelligently detects chapter boundaries in books and novels, automatically creating organized story structures with shared world elements.

## Purpose
Transform the import process for long-form content (novels, books) from a simple text dump into an intelligent parsing system that automatically creates properly structured stories while maintaining world consistency.

## Core Requirements

### 1. Document Types Supported
- Complete novels or books
- Collections of short stories or chapters
- Mixed-format documents with varying chapter styles

### 2. Chapter Detection Strategy
**Hybrid Approach:**
1. **Pattern-Based Detection (Primary)**
   - Common patterns: "Chapter X", "Part X", numbered sections
   - Regex matching for standard formats
   - Line break and separator detection ("***", "---")
   
2. **AI-Assisted Detection (Fallback)**
   - Activated when no clear patterns found
   - LLM analysis for unusual formatting
   - Semantic understanding of content breaks

### 3. Story Creation Rules
- **One story per detected chapter**
- Each chapter becomes an independent story
- Stories maintain original chapter titles (if available)
- No automatic scene detection within chapters
- Preserve chapter order in story listing

### 4. World Element Extraction
- **Global scanning** of entire document
- Create **shared pool** of world elements:
  - Characters (names, descriptions, relationships)
  - Locations (places, settings, landmarks)
  - Lore items (objects, concepts, history)
- All generated stories reference the same world elements
- Automatic cross-referencing across stories

### 5. User Experience Flow

#### Import Process
1. User selects "Import Book/Novel with Chapter Detection" option
2. Document upload and processing begins
3. System automatically:
   - Detects chapter boundaries
   - Creates stories for each chapter
   - Extracts world elements
   - Links everything together
4. Display summary statistics
5. User reviews and adjusts if needed

#### Post-Import Summary
Display concise statistics:
- "Created X stories from X detected chapters"
- "Found X characters and X locations"
- "Successfully imported X words"
- Quick overview of what was imported

### 6. Integration Approach
- **Separate feature** from existing simple import
- New menu option: "Import Book/Novel"
- Existing import remains unchanged
- Users choose based on their content type

## Technical Implementation

### Backend Components

#### 1. Chapter Detection Service
```python
class ChapterDetector:
    def detect_chapters(document_text):
        # Primary: Pattern-based detection
        chapters = detect_by_patterns(document_text)
        
        # Fallback: AI-assisted detection
        if not chapters or confidence_low(chapters):
            chapters = detect_by_ai(document_text)
        
        return chapters
```

#### 2. Pattern Library
- Chapter markers: `/^Chapter\s+\d+/`, `/^Part\s+[IVX]+/`
- Numbered sections: `/^\d+\.\s+/`, `/^\[\d+\]/`
- Named chapters: `/^Chapter\s+\d+:\s+.+/`
- Separators: `/^[\*\-\_]{3,}$/`
- Heading detection: Font size, bold text, caps

#### 3. Story Generation Service
- Create story entry for each detected chapter
- Assign chapter title as story title
- Set appropriate metadata (source document, import date)
- Maintain chapter sequence order

#### 4. World Element Extractor
- NER (Named Entity Recognition) for character names
- Location detection algorithms
- Relationship mapping between entities
- Deduplication logic for repeated mentions

### Frontend Components

#### 1. Import Interface
- New button/option: "Import Book/Novel"
- File upload with format validation
- Progress indicator during processing
- Support for: .txt, .docx, .pdf, .epub, .md

#### 2. Results Dashboard
```
┌─────────────────────────────────────┐
│     Import Complete! ✓              │
├─────────────────────────────────────┤
│ Created: 12 stories                 │
│ Detected: 12 chapters               │
│ Characters found: 23                │
│ Locations found: 15                 │
│ Total words: 85,420                 │
├─────────────────────────────────────┤
│ [View Stories] [View World Elements]│
└─────────────────────────────────────┘
```

### Database Schema Additions

#### Import Sessions Table
```sql
CREATE TABLE book_import_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    document_name VARCHAR(255),
    total_chapters INTEGER,
    stories_created INTEGER,
    characters_found INTEGER,
    locations_found INTEGER,
    import_date TIMESTAMP,
    import_status VARCHAR(50),
    import_config JSONB
);
```

#### Chapter Mapping Table
```sql
CREATE TABLE chapter_story_mappings (
    id SERIAL PRIMARY KEY,
    import_session_id INTEGER REFERENCES book_import_sessions(id),
    chapter_number INTEGER,
    chapter_title VARCHAR(255),
    story_id INTEGER REFERENCES stories(id),
    original_text TEXT,
    detected_method VARCHAR(50) -- 'pattern' or 'ai'
);
```

## Configuration Options

### Default Settings
```yaml
book_import:
  max_file_size: 10MB
  supported_formats: [txt, docx, pdf, epub, md]
  chapter_detection:
    min_chapter_length: 100  # words
    max_chapter_length: 50000  # words
    confidence_threshold: 0.7
  world_extraction:
    enable_character_detection: true
    enable_location_detection: true
    min_name_occurrences: 2  # minimum times mentioned
  ai_fallback:
    enable: true
    model: "gpt-4"
    max_tokens: 2000
```

## User Benefits

### Time Savings
- Eliminate manual chapter-by-chapter copy/paste
- Automatic story structure creation
- Instant world element catalog

### Organization
- Consistent story structure across imports
- Automatic chapter ordering
- Linked world elements

### Flexibility
- Works with any chapter format
- Handles mixed formatting
- Post-import adjustment capabilities

## Error Handling

### Common Scenarios
1. **No chapters detected**
   - Fall back to creating single story
   - Notify user with option to manually split

2. **Too many chapters detected** (>100)
   - Confirm with user before proceeding
   - Option to merge or select range

3. **File too large**
   - Stream processing for large files
   - Progress updates during import

4. **Corrupted/Unreadable content**
   - Skip problematic sections
   - Report issues in summary

## Success Metrics

### Performance Targets
- Chapter detection accuracy: >90% for standard formats
- Processing speed: <1 second per 10,000 words
- Character/location extraction: >80% accuracy
- User satisfaction: Reduce import time by 75%

### Monitoring
- Track import success rates
- Log detection accuracy
- Monitor processing times
- Collect user feedback

## Future Enhancements

### Phase 2 Features
- Scene detection within chapters
- Dialogue extraction and formatting
- Timeline generation from temporal markers
- Character relationship mapping
- Automatic story arc detection

### Phase 3 Features
- Batch import multiple books
- Series detection and linking
- Automatic world bible generation
- Style analysis and consistency checking
- Translation support for non-English content

## Implementation Timeline

### Week 1-2: Core Development
- Chapter detection algorithm
- Story creation pipeline
- Basic UI implementation

### Week 3: World Extraction
- Character detection
- Location extraction
- Entity linking system

### Week 4: Testing & Polish
- Edge case handling
- Performance optimization
- UI refinements
- User documentation

## Testing Strategy

### Unit Tests
- Chapter detection patterns
- Story creation logic
- World element extraction

### Integration Tests
- Full import pipeline
- Database transactions
- UI interaction flows

### Test Documents
- Standard novel format (clear chapters)
- Mixed format document
- Edge cases (no chapters, many chapters)
- Different languages and encodings

## Documentation Requirements

### User Documentation
- How-to guide for book import
- Supported format specifications
- Troubleshooting common issues
- Best practices for document preparation

### Developer Documentation
- API endpoints
- Detection algorithm details
- Extension points for new patterns
- Configuration options

## Security Considerations

- File size limits to prevent DoS
- Virus scanning for uploaded documents
- Sanitization of extracted content
- Rate limiting for AI fallback calls
- User permission validation

## Conclusion

This enhanced book import feature will significantly improve the user experience for authors and world-builders working with existing long-form content. By automating the tedious process of chapter separation and world element extraction, users can focus on creative work rather than manual data entry.

The hybrid detection approach ensures compatibility with various document formats while maintaining high accuracy. The automatic story creation and shared world element pool provide a solid foundation for further story development and world-building activities.