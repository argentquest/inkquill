# Azure Content Moderator Implementation Plan for AI Storytelling Assistant

## Overview
This plan details the implementation of Azure Content Moderator for detecting and flagging adult content in your AI Storytelling application. Since you're using OpenAI endpoints (not Azure OpenAI), the moderation will wrap around your existing OpenAI calls.

## Phase 1: Azure Setup & Configuration

### 1.1 Azure Content Moderator Service Setup
```
Steps:
1. Log into Azure Portal (portal.azure.com)
2. Create new Content Moderator resource:
   - Click "Create a resource"
   - Search for "Content Moderator"
   - Select subscription and resource group
   - Choose region (same as your other services)
   - Select pricing tier (F0 for free tier, S0 for standard)
   - Create resource

3. Retrieve credentials:
   - Navigate to "Keys and Endpoint"
   - Copy Key 1 or Key 2
   - Copy Endpoint URL
   - Note the region
```

### 1.2 Environment Configuration
```
Add to .env file:
AZURE_CONTENT_MODERATOR_KEY=<your-key>
AZURE_CONTENT_MODERATOR_ENDPOINT=<your-endpoint>
AZURE_CONTENT_MODERATOR_REGION=<region>

# Moderation thresholds
CONTENT_MOD_ADULT_THRESHOLD=0.7
CONTENT_MOD_RACY_THRESHOLD=0.8
CONTENT_MOD_OFFENSIVE_THRESHOLD=0.7
CONTENT_MOD_ENABLED=true
```

### 1.3 Dependencies Installation
```bash
# Add to requirements.txt
azure-cognitiveservices-vision-contentmoderator==1.0.0
azure-cognitiveservices-language-textanalytics==0.2.0
azure-common==1.1.28
```

## Phase 2: Service Layer Implementation

### 2.1 Create Content Moderation Service
```
New file: app/services/content_moderation_service.py

Components:
- ContentModerationService class
- Text moderation methods
- Image moderation methods
- Result caching
- Threshold configuration
- Error handling and fallbacks
```

### 2.2 Moderation Models
```
New file: app/models/content_moderation.py

Database tables:
- moderation_logs
  - id
  - content_type (text/image)
  - content_hash
  - user_id
  - result_json
  - is_flagged
  - reviewed_by
  - review_status
  - created_at
  
- moderation_cache
  - content_hash (primary key)
  - moderation_result
  - expires_at
```

### 2.3 Integration Points

#### 2.3.1 Pre-Generation Moderation (User Input)
```
Locations to modify:
- app/routers/ai_assisted_writing.py
  - WebSocket message handler
  - Before OpenAI API calls
  
- app/routers/ai_scene_writing.py
  - Scene content generation
  - Character descriptions

- app/services/world_building_service.py
  - Character creation
  - Location descriptions
  - Lore items
```

#### 2.3.2 Post-Generation Moderation (AI Output)
```
Locations to modify:
- app/services/ai_story_service.py
  - After OpenAI completion
  - Before returning to user

- app/services/scene_service.py
  - Generated scene content
  - Scene descriptions
```

## Phase 3: API Integration Architecture

### 3.1 Request Flow
```
1. User Input
   ↓
2. Input Validation
   ↓
3. Content Moderation Check
   ├─→ Cache Check
   │    ├─→ Hit: Return cached result
   │    └─→ Miss: Continue
   ↓
4. Azure Content Moderator API
   ├─→ Text Analysis (if applicable)
   └─→ Image Analysis (if applicable)
   ↓
5. Result Processing
   ├─→ Below threshold: Continue
   └─→ Above threshold: Flag/Block
   ↓
6. Cache Result
   ↓
7. Log Moderation Event
   ↓
8. Continue with original flow OR return warning
```

### 3.2 Moderation Service Methods
```python
class ContentModerationService:
    async def moderate_text(content: str) -> ModerationResult
    async def moderate_image(image_url: str) -> ModerationResult
    async def moderate_prompt(prompt: str) -> ModerationResult
    async def moderate_story_content(content: str) -> ModerationResult
    async def batch_moderate_texts(texts: List[str]) -> List[ModerationResult]
```

## Phase 4: User Interface Components

### 4.1 User-Facing Elements
```
1. Content Warning Modal
   - Location: app/templates/partials/_content_warning_modal.html
   - Shows when content is flagged
   - Options: Edit, Cancel, Request Review

2. Content Guidelines Page
   - Location: app/templates/pages/content_guidelines.html
   - Clear explanation of what's not allowed
   - Examples of acceptable vs unacceptable

3. Moderation Status Indicators
   - Visual indicators for moderated content
   - Warning badges on flagged items
```

### 4.2 Admin Interface
```
1. Moderation Dashboard
   - Location: app/templates/pages/admin_moderation.html
   - Queue of flagged content
   - Review interface
   - Statistics and trends

2. Threshold Configuration
   - Dynamic threshold adjustment
   - A/B testing capabilities
   - False positive tracking
```

## Phase 5: Implementation Steps

### 5.1 Backend Implementation Order
```
Week 1:
1. Set up Azure Content Moderator service
2. Create database models and migrations
3. Implement ContentModerationService base class
4. Add caching layer

Week 2:
5. Integrate with AI-assisted writing WebSocket
6. Add pre-generation prompt moderation
7. Implement post-generation content checks
8. Add moderation logging

Week 3:
9. Create admin moderation dashboard
10. Implement review queue
11. Add user notification system
12. Create content guidelines page
```

### 5.2 Configuration Management
```
New config values in app/core/config.py:
- CONTENT_MODERATION_ENABLED
- AZURE_CONTENT_MODERATOR_KEY
- AZURE_CONTENT_MODERATOR_ENDPOINT
- Threshold configurations
- Cache TTL settings
- Batch size limits
```

## Phase 6: Testing Strategy

### 6.1 Unit Tests
```
test_content_moderation_service.py:
- Test moderation API calls
- Test threshold logic
- Test caching behavior
- Test error handling
```

### 6.2 Integration Tests
```
- End-to-end moderation flow
- WebSocket integration
- Database logging
- Cache invalidation
```

### 6.3 Test Scenarios
```
1. Explicit content in prompts
2. Borderline content (near threshold)
3. False positives (medical, educational)
4. Mixed content (some OK, some not)
5. Performance under load
6. API failure scenarios
```

## Phase 7: Monitoring & Maintenance

### 7.1 Metrics to Track
```
- Moderation API response times
- False positive rate
- True positive rate
- User appeals/disputes
- Cost per moderation
- Cache hit rate
```

### 7.2 Logging Strategy
```
- All moderation decisions
- API errors and timeouts
- Threshold breaches
- User override requests
- Admin review actions
```

### 7.3 Cost Management
```
- Implement request batching
- Cache results for 24 hours
- Rate limit per user
- Monitor monthly usage
- Set up billing alerts
```

## Phase 8: Gradual Rollout Plan

### 8.1 Rollout Stages
```
Stage 1 (Shadow Mode):
- Log moderation results only
- No user impact
- Collect baseline metrics

Stage 2 (Warning Mode):
- Show warnings for flagged content
- Allow users to proceed
- Track user responses

Stage 3 (Enforcement Mode):
- Block highly inappropriate content
- Require review for borderline
- Full admin tools active

Stage 4 (Optimization):
- Tune thresholds based on data
- Implement ML improvements
- Add custom models
```

### 8.2 Feature Flags
```
FLAGS = {
    'moderation_enabled': False,
    'moderation_enforcement': False,
    'moderation_logging': True,
    'moderation_user_override': True,
    'moderation_admin_bypass': True
}
```

## Phase 9: Error Handling & Fallbacks

### 9.1 Failure Scenarios
```
1. Azure API timeout
   → Fallback: Allow with logging
   
2. Invalid API response
   → Fallback: Basic keyword filtering
   
3. Rate limit exceeded
   → Fallback: Queue for batch processing
   
4. Service unavailable
   → Fallback: Temporary bypass with alerting
```

### 9.2 Circuit Breaker Pattern
```
- Implement circuit breaker for Azure API
- Open circuit after 5 consecutive failures
- Half-open after 30 seconds
- Close after successful call
```

## Phase 10: Compliance & Documentation

### 10.1 Privacy Considerations
```
- Document what content is sent to Azure
- Update privacy policy
- Implement data retention policies
- Allow users to request moderation logs
```

### 10.2 User Documentation
```
1. Update Terms of Service
2. Create Content Guidelines
3. Add FAQ section
4. Provide appeal process documentation
```

## Estimated Timeline

```
Week 1: Azure setup, base service implementation
Week 2: Core integration with existing flows
Week 3: UI components and admin tools
Week 4: Testing and shadow mode deployment
Week 5: Gradual rollout and monitoring
Week 6: Full deployment and optimization
```

## Risk Mitigation

1. **Performance Impact**: Use async calls, implement caching
2. **User Experience**: Clear messaging, fast fallbacks
3. **False Positives**: Manual review queue, whitelisting
4. **Cost Overruns**: Monitoring, alerts, rate limiting
5. **Privacy Concerns**: Clear documentation, data minimization

## Cost Estimation

### Azure Content Moderator Pricing (as of 2024)
```
Text Moderation:
- 0-1M transactions: $1 per 1,000 transactions
- 1M-5M transactions: $0.75 per 1,000 transactions
- 5M+ transactions: $0.60 per 1,000 transactions

Image Moderation:
- 0-1M transactions: $1 per 1,000 transactions
- 1M-5M transactions: $0.75 per 1,000 transactions
- 5M+ transactions: $0.60 per 1,000 transactions

Estimated Monthly Cost (10K daily users, 5 requests each):
- 50K requests/day = 1.5M requests/month
- Cost: ~$1,125/month (can be reduced with caching)
```

## Quick Start Checklist

- [ ] Create Azure Content Moderator resource
- [ ] Add API keys to .env file
- [ ] Install Python dependencies
- [ ] Create database migrations
- [ ] Implement ContentModerationService
- [ ] Add moderation to one endpoint (test)
- [ ] Create basic admin interface
- [ ] Deploy in shadow mode
- [ ] Monitor false positive rate
- [ ] Gradually enable enforcement

## Support Resources

- [Azure Content Moderator Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/content-moderator/)
- [Python SDK Reference](https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-contentmoderator/)
- [Best Practices Guide](https://docs.microsoft.com/en-us/azure/cognitive-services/content-moderator/best-practices)
- [API Reference](https://westus.dev.cognitive.microsoft.com/docs/services/57cf753a3f9b070c105bd2c1/operations/57cf753a3f9b070868a1f66c)

This implementation plan provides a comprehensive approach to adding content moderation while maintaining system performance and user experience.