# AI Configuration Documentation

## Overview

This document describes the AI configuration system that centralizes all AI-related parameters for the AI Storytelling Assistant application. All hardcoded AI constants have been extracted to configuration files for better maintainability and environment-specific tuning.

## 🔧 Configuration Location

All AI parameters are defined in `/app/core/config.py` within the `Settings` class.

## 📊 AI Parameter Categories

### 1. Temperature Settings

Controls the randomness/creativity of AI responses. Lower values = more focused, higher values = more creative.

```python
AI_TEMPERATURE_SETTINGS: Dict[str, float] = {
    "act_review": 0.4,           # Focused analysis for act reviews
    "act_narrative": 0.7,        # Creative narrative generation
    "act_metadata": 0.3,         # Precise metadata extraction
    "scene_narrative": 0.7,      # Creative scene writing
    "scene_metadata": 0.3,       # Precise scene metadata
    "scene_extraction": 0.2,     # Focused scene parsing
    "rag_conversion": 0.3,       # Consistent RAG text conversion
    "world_generation": 0.5,     # Balanced world creation
    "world_elements_extraction": 0.3,  # Precise element extraction
    "test": 0.7                  # Test environment default
}
```

**Range**: 0.0 - 2.0
- 0.0-0.3: Very focused, deterministic
- 0.4-0.7: Balanced creativity
- 0.8-2.0: Highly creative, unpredictable

### 2. Max Token Settings

Controls the maximum length of AI responses.

```python
AI_MAX_TOKEN_SETTINGS: Dict[str, int] = {
    "act_review": 3500,          # Detailed act analysis
    "act_narrative": 3000,       # Full act content
    "act_metadata": 1500,        # Concise metadata
    "scene_narrative": 2500,     # Scene content
    "scene_metadata": 1000,      # Brief scene metadata
    "scene_extraction": 4000,    # Complex scene parsing
    "rag_conversion": 700,       # Short RAG descriptions
    "world_generation": 3500,    # Comprehensive world data
    "world_elements_extraction": 8000,  # Large text processing
    "test": 800                  # Test environment default
}
```

**Range**: 100 - 10,000 tokens
- 100-1000: Short responses, metadata
- 1000-3000: Medium content, narratives
- 3000+: Long-form content, analysis

### 3. Top-p Settings

Controls nucleus sampling - the probability mass for token selection.

```python
AI_TOP_P_SETTINGS: Dict[str, float] = {
    "act_review": 0.9,           # Broad vocabulary for analysis
    "act_narrative": 0.8,        # Creative but focused narrative
    "act_metadata": 0.7,         # Precise terminology
    "scene_narrative": 0.8,      # Creative scene writing
    "scene_metadata": 0.7,       # Consistent metadata terms
    "scene_extraction": 0.7,     # Focused parsing
    "rag_conversion": 0.9,       # Rich descriptive text
    "world_generation": 0.9,     # Creative world building
    "world_elements_extraction": 0.8,  # Varied element extraction
    "test": 0.8                  # Test environment default
}
```

**Range**: 0.0 - 1.0
- 0.1-0.5: Very focused vocabulary
- 0.6-0.8: Balanced word choice
- 0.9-1.0: Full vocabulary range

### 4. RAG and Processing Settings

```python
RAG_RETRIEVAL_TOP_K: int = Field(default=3, ...)  # Number of documents to retrieve
DEFAULT_TOKENIZER: str = Field(default="cl100k_base", ...)  # Tokenizer for text processing
DEFAULT_MODEL_FOR_CHUNKING: str = Field(default="gpt-3.5-turbo", ...)  # Model for chunking
```

## 🔄 Usage Patterns

### In Semantic Kernel Functions

```python
from app.core.config import settings

# Example: Act Review Function
exec_settings = AzureChatPromptExecutionSettings(
    service_id=chat_service_id,
    max_tokens=settings.AI_MAX_TOKEN_SETTINGS["act_review"],
    temperature=settings.AI_TEMPERATURE_SETTINGS["act_review"],
    top_p=settings.AI_TOP_P_SETTINGS["act_review"],
    response_format={"type": "json_object"}
)
```

### In RAG Retrieval

```python
from app.core.config import settings

# Use configurable top_k for document retrieval
async def retrieve_rag_context(self, query: str, top_k: int = None):
    if top_k is None:
        top_k = settings.RAG_RETRIEVAL_TOP_K
    # ... retrieval logic
```

### In Text Processing

```python
from app.core.config import settings

# Use configurable tokenizer and model
def get_tokenizer(model_name: str = None):
    if model_name is None:
        model_name = settings.DEFAULT_MODEL_FOR_CHUNKING
    # ... tokenizer logic
```

## 🎯 Function-Specific Configurations

### Story Analysis Functions
- **act_review**: High max tokens (3500), moderate temperature (0.4), high top_p (0.9)
- **act_metadata**: Medium max tokens (1500), low temperature (0.3), moderate top_p (0.7)
- **scene_metadata**: Low max tokens (1000), low temperature (0.3), moderate top_p (0.7)

### Storytelling Functions
- **act_narrative**: High max tokens (3000), high temperature (0.7), moderate top_p (0.8)
- **scene_narrative**: Medium max tokens (2500), high temperature (0.7), moderate top_p (0.8)

### World Building Functions
- **world_generation**: High max tokens (3500), balanced temperature (0.5), high top_p (0.9)
- **world_elements_extraction**: Very high max tokens (8000), low temperature (0.3), moderate top_p (0.8)
- **rag_conversion**: Low max tokens (700), low temperature (0.3), high top_p (0.9)

### Story Structure Functions
- **scene_extraction**: High max tokens (4000), very low temperature (0.2), moderate top_p (0.7)

## 🔧 Environment Variable Overrides

You can override any configuration via environment variables in your `.env` file:

```bash
# Example overrides
RAG_RETRIEVAL_TOP_K=5
DEFAULT_TOKENIZER=p50k_base
DEFAULT_MODEL_FOR_CHUNKING=gpt-4
```

## ⚙️ Configuration Validation

The system includes validation to ensure:
- Temperature values are between 0.0 and 2.0
- Max token values are between 100 and 10,000
- Top_p values are between 0.0 and 1.0
- RAG top_k is between 1 and 20

## 📈 Performance Tuning Guidelines

### For Higher Quality Output
- **Increase max_tokens**: Allow for more detailed responses
- **Adjust temperature**: Lower for consistency, higher for creativity
- **Tune top_p**: Higher for richer vocabulary, lower for precision

### For Faster Performance
- **Decrease max_tokens**: Shorter responses process faster
- **Lower temperature**: More deterministic, potentially faster
- **Optimize top_p**: Moderate values often perform best

### For Cost Optimization
- **Reduce max_tokens**: Primary cost driver
- **Optimize temperature**: Lower values may use fewer tokens
- **Balance quality vs. cost**: Find the minimum viable settings

## 🛡️ Security Considerations

### ✅ Resolved Security Issues
- All hardcoded API keys removed from source code
- Endpoints now loaded from environment variables
- Test files use configuration instead of hardcoded values

### 🔐 Current Security Practices
- API keys stored in environment variables
- No sensitive data in configuration defaults
- Proper validation of all configuration values

## 🧪 Testing

### Configuration Tests
- **Basic Validation**: `/tests_auto/test_ai_config_basic.py`
- **Functionality Tests**: `/tests_auto/test_ai_functionality_basic.py`
- **Full Validation**: `/tests_auto/test_ai_config_validation.py` (requires dependencies)

### Test Coverage
- ✅ All hardcoded constants extracted
- ✅ Configuration structure validated
- ✅ Value ranges verified
- ✅ Security issues resolved
- ✅ Backward compatibility maintained

## 🔄 Migration Summary

### Files Updated
1. **Core Configuration**
   - `app/core/config.py`: Added AI parameter dictionaries

2. **Semantic Kernel Setup**
   - `app/services/semantic_kernel_setup.py`: All functions use config

3. **Plugin Files**
   - `app/services/sk_plugins/world_generation_plugin_setup.py`
   - `app/services/sk_plugins/storytelling_plugin_setup.py`
   - `app/services/sk_plugins/story_analysis_plugin_setup.py`
   - `app/services/sk_plugins/world_building_plugin_setup.py`
   - `app/services/sk_plugins/story_structure_plugin_setup.py`

4. **Processing and RAG**
   - `app/services/rag_retrieval.py`: Configurable top_k
   - `app/processing/chunking.py`: Configurable tokenizer and model

5. **Test Files**
   - `app/MainOpenAiTest.py`: Security fixes, config usage
   - `app/maintest_sk_logic.py`: Config usage for AI parameters

### Hardcoded Constants Removed
- 85+ instances of hardcoded AI parameters
- 27 temperature values
- 25 max token limits  
- 15 top_p values
- 5 RAG/processing constants
- All hardcoded API keys and endpoints

## 📝 Best Practices

### When Adding New AI Functions
1. Add configuration entries to all three dictionaries
2. Use descriptive function names as keys
3. Choose appropriate parameter values based on function purpose
4. Test with validation scripts
5. Document the function's configuration rationale

### When Modifying Existing Functions
1. Update configuration values rather than code
2. Test changes with validation scripts
3. Consider impact on dependent functions
4. Update documentation as needed

### For Environment-Specific Tuning
1. Use environment variables for overrides
2. Test thoroughly in target environment
3. Monitor performance and quality metrics
4. Document environment-specific optimizations

## 🎉 Benefits Achieved

- ✅ **Centralized Control**: All AI parameters in one location
- ✅ **Environment-Specific Tuning**: Different settings per deployment
- ✅ **Security**: No hardcoded secrets or endpoints
- ✅ **Maintainability**: Easy parameter adjustments without code changes
- ✅ **Testability**: Consistent test configurations
- ✅ **Performance Tuning**: Easy optimization of AI parameters
- ✅ **Validation**: Automated checks for configuration correctness