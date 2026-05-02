# OpenRouter Integration Technical Plan

## 📋 Overview

This document outlines the technical implementation plan for integrating OpenRouter API support into the Context storytelling application. The integration will enable access to 150+ AI models through OpenRouter while maintaining compatibility with existing Azure OpenAI functionality.

## 🎯 Project Objectives

- **Primary Goal**: Add OpenRouter as a second AI provider alongside Azure OpenAI
- **Secondary Goals**: 
  - Expand model selection for users
  - Reduce dependency on single provider
  - Enable cost optimization through provider comparison
  - Access to latest models faster than Azure deployment cycles

## 📊 Current State Analysis

### ✅ **Existing Foundation (Already Implemented)**
- `AIProviderEnum.OPENROUTER` exists in database schema
- Provider-agnostic `AIModelConfiguration` table structure
- Cost tracking system with provider-specific fields
- Model abstraction layer in place
- Modular service architecture

### 🔄 **Areas Requiring Changes**
- Client instantiation logic (hardcoded to Azure)
- Semantic Kernel configuration (Azure-only)
- Model naming conventions (Azure deployment vs OpenRouter format)
- Authentication mechanisms
- Error handling and retry logic

## 🏗️ Implementation Phases

### **Phase 1: Core Infrastructure (Week 1)**
**Goal**: Basic OpenRouter connectivity and configuration

#### 1.1 Configuration Updates
- **File**: `app/core/config.py`
- **Changes**:
  ```python
  # OpenRouter Configuration
  OPENROUTER_API_KEY: str = ""
  OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
  OPENROUTER_SITE_URL: str = ""  # For referrer tracking
  OPENROUTER_APP_NAME: str = ""  # For analytics
  ```

#### 1.2 Client Factory Implementation
- **New File**: `app/services/ai_client_factory.py`
- **Purpose**: Provider-aware client instantiation
- **Responsibilities**:
  - Create Azure OpenAI clients
  - Create OpenRouter clients with proper headers
  - Handle authentication for both providers
  - Manage base URL routing

#### 1.3 Database Migration
- **File**: New Alembic migration
- **Changes**:
  - Add sample OpenRouter model configurations
  - Update existing models with proper provider assignments
  - Add OpenRouter-specific model metadata

### **Phase 2: Service Layer Integration (Week 2)**
**Goal**: Update core services to support both providers

#### 2.1 World Chat Service Updates
- **File**: `app/services/world_chat_service.py`
- **Changes**:
  - Replace direct Azure client with factory-generated client
  - Add provider-specific error handling
  - Update model name resolution logic
  - Maintain backward compatibility

#### 2.2 Cost Tracking Enhancements
- **File**: `app/services/cost_tracker_service.py`
- **Changes**:
  - Handle OpenRouter's credit-based pricing
  - Map OpenRouter costs to token-based system
  - Add provider-specific logging
  - Update cost calculation formulas

#### 2.3 Model Cache Updates
- **File**: `app/services/ai_model_cache.py`
- **Changes**:
  - Support mixed-provider model lists
  - Add provider filtering capabilities
  - Update default model selection logic

### **Phase 3: AI Generation Features (Week 3)**
**Goal**: Enable OpenRouter for world imports and advanced features

#### 3.1 Semantic Kernel Integration
- **File**: `app/services/semantic_kernel_setup.py`
- **Changes**:
  - Multi-provider service registration
  - Dynamic kernel configuration based on model provider
  - Provider-specific execution settings

#### 3.2 World Import Updates
- **File**: `app/processing/importer_jobs.py`
- **Changes**:
  - Support OpenRouter models for JSON generation
  - Provider-aware model selection
  - Enhanced error handling for both providers

#### 3.3 Scene/Act Writing Integration
- **Files**: 
  - `app/routers/ai_assisted_writing.py`
  - `app/routers/ai_scene_writing.py`
- **Changes**:
  - Provider-aware AI generation
  - Streaming support for OpenRouter
  - Cost tracking for real-time writing

### **Phase 4: Advanced Features (Week 4)**
**Goal**: Production-ready features and optimizations

#### 4.1 Error Handling & Resilience
- **New File**: `app/services/provider_resilience.py`
- **Features**:
  - Provider-specific retry logic
  - Automatic failover between providers
  - Rate limit handling
  - Health checks

#### 4.2 Model Management
- **New File**: `app/services/model_availability.py`
- **Features**:
  - Real-time model availability checking
  - Automatic price updates from OpenRouter API
  - Model recommendation engine

#### 4.3 Monitoring & Analytics
- **File**: `app/services/cost_tracker_service.py`
- **Enhancements**:
  - Provider performance metrics
  - Cost comparison analytics
  - Usage pattern analysis

## 🗂️ File Structure Changes

```
app/
├── core/
│   └── config.py                          # ✏️ Add OpenRouter config
├── services/
│   ├── ai_client_factory.py              # 🆕 Provider-aware client factory
│   ├── provider_resilience.py            # 🆕 Error handling & failover
│   ├── model_availability.py             # 🆕 Model management
│   ├── world_chat_service.py             # ✏️ Multi-provider support
│   ├── cost_tracker_service.py           # ✏️ Enhanced cost tracking
│   ├── ai_model_cache.py                 # ✏️ Provider filtering
│   └── semantic_kernel_setup.py          # ✏️ Multi-provider SK setup
├── processing/
│   └── importer_jobs.py                  # ✏️ Provider-aware imports
├── routers/
│   ├── ai_assisted_writing.py           # ✏️ Multi-provider writing
│   └── ai_scene_writing.py              # ✏️ Multi-provider scenes
└── models/
    └── ai_model_config.py               # ✏️ Validation updates
```

## 🔧 Technical Implementation Details

### Authentication Strategy
```python
# Azure OpenAI
client = openai.AsyncAzureOpenAI(
    api_key=settings.AZURE_OPENAI_API_KEY,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
)

# OpenRouter
client = openai.AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url=settings.OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }
)
```

### Model Name Mapping
```python
def resolve_model_name(config: AIModelConfiguration) -> str:
    if config.provider == AIProviderEnum.AZURE:
        return config.model_name  # Azure deployment name
    elif config.provider == AIProviderEnum.OPENROUTER:
        return config.model_name  # Full OpenRouter model path (e.g., "openai/gpt-4o")
```

### Cost Calculation
```python
def calculate_openrouter_cost(usage_data: dict, model_config: AIModelConfiguration) -> float:
    # OpenRouter provides cost directly, but we need to map to our token system
    total_cost = usage_data.get('cost_usd', 0.0)
    
    # Convert to our per-million-token pricing for consistency
    input_tokens = usage_data.get('prompt_tokens', 0)
    output_tokens = usage_data.get('completion_tokens', 0)
    
    return total_cost
```

## 📊 Database Schema Changes

### New Model Configurations
```sql
-- Example OpenRouter model configurations
INSERT INTO ai_model_configurations (
    display_name, model_name, provider, model_type, is_active,
    max_tokens, temperature, is_json_mode,
    user_price_input_usd_pm, user_price_output_usd_pm
) VALUES 
('Claude 3.5 Sonnet (OpenRouter)', 'anthropic/claude-3.5-sonnet', 'OPENROUTER', 'GENERATION', true,
 4000, 0.7, true, 3.00, 15.00),
('DeepSeek R1 (OpenRouter)', 'deepseek/deepseek-r1', 'OPENROUTER', 'GENERATION', true,
 8000, 0.7, true, 0.55, 2.19),
('GPT-4o (OpenRouter)', 'openai/gpt-4o', 'OPENROUTER', 'GENERATION', true,
 4000, 0.7, true, 2.50, 10.00);
```

## 🧪 Testing Strategy

### Unit Tests
- Provider factory functionality
- Model name resolution
- Cost calculation accuracy
- Error handling scenarios

### Integration Tests
- End-to-end chat with OpenRouter
- World import with OpenRouter models
- Cost tracking accuracy
- Provider failover scenarios

### Load Tests
- Concurrent requests to both providers
- Rate limit handling
- Performance comparison

## 🚨 Risk Assessment & Mitigation

### **High Risk Items**
1. **OpenRouter API Changes**: Monitor for breaking changes
   - **Mitigation**: Version pinning, comprehensive error handling
2. **Cost Calculation Errors**: Wrong billing could be expensive
   - **Mitigation**: Extensive testing, cost limits, monitoring

### **Medium Risk Items**
1. **Model Availability**: OpenRouter models may go offline
   - **Mitigation**: Health checks, automatic fallbacks
2. **Rate Limiting**: Different limits than Azure
   - **Mitigation**: Provider-specific retry logic

### **Low Risk Items**
1. **Performance Differences**: Latency variations between providers
   - **Mitigation**: Monitoring, user choice

## 📅 Timeline

| Phase | Duration | Deliverables | Dependencies |
|-------|----------|--------------|--------------|
| Phase 1 | Week 1 | Core config, client factory, DB migration | OpenRouter account setup |
| Phase 2 | Week 2 | Service layer updates, cost tracking | Phase 1 complete |
| Phase 3 | Week 3 | AI features integration | Phase 2 complete |
| Phase 4 | Week 4 | Advanced features, monitoring | Phase 3 complete |

## 🎯 Success Criteria

### **Functional Requirements**
- [ ] Users can select OpenRouter models in UI
- [ ] Chat functionality works with OpenRouter
- [ ] World import works with OpenRouter models
- [ ] Cost tracking is accurate for both providers
- [ ] Error handling gracefully manages provider issues

### **Non-Functional Requirements**
- [ ] No performance degradation for Azure users
- [ ] 99.9% backward compatibility
- [ ] Response times within 10% of current performance
- [ ] Comprehensive logging for debugging

### **Business Requirements**
- [ ] Cost transparency for both providers
- [ ] Easy model switching for users
- [ ] Provider health monitoring
- [ ] Usage analytics per provider

## 📈 Success Metrics

### **Technical Metrics**
- API response times (target: <2s for chat, <30s for imports)
- Error rates (target: <1% for each provider)
- Cost calculation accuracy (target: 100%)

### **Business Metrics**
- User adoption of OpenRouter models
- Cost savings achieved
- Model diversity usage patterns
- User satisfaction with model selection

## 🔧 Implementation Notes

### **Configuration Management**
- Use environment variables for all API keys
- Support different configurations per environment
- Implement configuration validation

### **Monitoring Requirements**
- Provider-specific performance metrics
- Cost tracking per provider
- Error rate monitoring
- Model availability tracking

### **Security Considerations**
- Secure API key storage
- Request logging without exposing keys
- Rate limit protection
- Input validation for all providers

---

## 📞 Support & Maintenance

### **Documentation Updates Needed**
- User guide for model selection
- Admin guide for adding new models
- Troubleshooting guide for provider issues
- Cost comparison guide

### **Operational Procedures**
- Provider health monitoring
- Cost alert thresholds
- Incident response procedures
- Model availability checking

---

*This plan provides a comprehensive roadmap for integrating OpenRouter while maintaining system stability and user experience. Each phase builds upon the previous one, ensuring a robust and scalable implementation.*
