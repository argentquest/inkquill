# /ai_rag_story_app/app/services/ai_client_factory.py
import logging
from typing import Optional, Union
import openai
from app.core.config import settings
from app.models.ai_model_config import AIProviderEnum, AIModelConfiguration

logger = logging.getLogger(__name__)

class AIClientFactory:
    """Factory for creating provider-specific AI clients."""
    
    @staticmethod
    def create_client(provider: AIProviderEnum) -> Union[openai.AsyncAzureOpenAI, openai.AsyncOpenAI]:
        """
        Create an AI client based on the provider.
        
        Args:
            provider: The AI provider enum
            
        Returns:
            Configured client instance
            
        Raises:
            ValueError: If provider configuration is missing or invalid
        """
        if provider == AIProviderEnum.AZURE:
            return AIClientFactory._create_azure_client()
        elif provider == AIProviderEnum.OPENROUTER:
            return AIClientFactory._create_openrouter_client()
        elif provider == AIProviderEnum.OPENAI:
            return AIClientFactory._create_openai_client()
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    @staticmethod
    def create_client_for_model(model_config: AIModelConfiguration) -> Union[openai.AsyncAzureOpenAI, openai.AsyncOpenAI]:
        """
        Create an AI client for a specific model configuration.
        
        Args:
            model_config: The AI model configuration
            
        Returns:
            Configured client instance
        """
        return AIClientFactory.create_client(model_config.provider)
    
    @staticmethod
    def _create_azure_client() -> openai.AsyncAzureOpenAI:
        """Create Azure OpenAI client."""
        if not settings.AZURE_OPENAI_API_KEY:
            raise ValueError("Azure OpenAI API key is not configured")
        if not settings.AZURE_OPENAI_ENDPOINT:
            raise ValueError("Azure OpenAI endpoint is not configured")
            
        logger.debug("Creating Azure OpenAI client")
        return openai.AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=str(settings.AZURE_OPENAI_ENDPOINT)
        )
    
    @staticmethod
    def _create_openrouter_client() -> openai.AsyncOpenAI:
        """Create OpenRouter client."""
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key is not configured")
            
        logger.debug("Creating OpenRouter client")
        
        # Build default headers for OpenRouter
        default_headers = {}
        if settings.OPENROUTER_SITE_URL:
            default_headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
        if settings.OPENROUTER_APP_NAME:
            default_headers["X-Title"] = settings.OPENROUTER_APP_NAME
            
        return openai.AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            default_headers=default_headers if default_headers else None
        )
    
    @staticmethod
    def _create_openai_client() -> openai.AsyncOpenAI:
        """Create standard OpenAI client."""
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is not configured")
            
        logger.debug("Creating OpenAI client")
        return openai.AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )
    
    @staticmethod
    def resolve_model_name(model_config: AIModelConfiguration) -> str:
        """
        Resolve the model name based on provider.
        
        Args:
            model_config: The AI model configuration
            
        Returns:
            Provider-specific model name
        """
        if model_config.provider == AIProviderEnum.AZURE:
            # Azure uses deployment names
            return model_config.model_name
        elif model_config.provider in [AIProviderEnum.OPENROUTER, AIProviderEnum.OPENAI]:
            # OpenRouter and OpenAI use full model paths
            return model_config.model_name
        else:
            raise ValueError(f"Unsupported provider for model name resolution: {model_config.provider}")
    
    @classmethod
    def validate_provider_configuration(cls, provider: AIProviderEnum) -> bool:
        """
        Validate that a provider is properly configured.
        
        Args:
            provider: The AI provider to validate
            
        Returns:
            True if provider is configured, False otherwise
        """
        try:
            cls.create_client(provider)
            return True
        except ValueError as e:
            logger.warning(f"Provider {provider} is not properly configured: {e}")
            return False