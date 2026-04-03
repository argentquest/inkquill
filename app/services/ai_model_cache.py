"""Service helpers for ai model cache."""

# /app/services/ai_model_cache.py
import logging
from sqlalchemy.future import select
from app.db.database import async_session_local
from app.models.ai_model_config import AIModelConfiguration, AIModelTypeEnum, AIProviderEnum
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIModelCache:
    """
    A singleton cache to hold AI model configurations loaded from the database at startup.
    This avoids querying the database for every AI call.
    """
    def __init__(self):
        # Stores config objects by their database ID for easy lookup
        self.configurations = {} 
        # Stores only generative models for quick filtering
        self.generation_models = {} 
        # Stores a reference to the default generative model object
        self.default_generation_model = None

    async def load_models_from_db(self):
        logger.info("Loading all active AI model configurations from database into cache...")
        async with async_session_local() as db:
            result = await db.execute(
                select(AIModelConfiguration).filter_by(is_active=True)
            )
            models = result.scalars().all()
        
        for model in models:
            self.configurations[model.id] = model
            if model.model_type == AIModelTypeEnum.GENERATION:
                self.generation_models[model.id] = model
        
        # Identify the default generation model based on the name in settings
        default_name = settings.DEFAULT_GENERATION_MODEL_NAME
        for model in self.generation_models.values():
            if model.model_name == default_name:
                self.default_generation_model = model
                break
        
        if not self.default_generation_model and self.generation_models:
            # Fallback to the first available model if the configured default isn't found
            self.default_generation_model = next(iter(self.generation_models.values()))
            logger.warning(f"Default model '{default_name}' not found. Falling back to '{self.default_generation_model.display_name}'.")
        elif not self.generation_models:
             logger.error("No active generative models found in the database!")

        logger.info(f"AI Model Cache loaded: {len(self.generation_models)} generation models.")
        if self.default_generation_model:
            logger.info(f"Default generation model set to: '{self.default_generation_model.display_name}'")
        
        # Log provider distribution
        provider_counts = {}
        for model in self.configurations.values():
            provider = model.provider.value
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        logger.info(f"Provider distribution: {provider_counts}")

    def get_models_by_provider(self, provider: AIProviderEnum, model_type: AIModelTypeEnum = None) -> dict:
        """
        Get all models for a specific provider, optionally filtered by type.
        
        Args:
            provider: The AI provider to filter by
            model_type: Optional model type filter
            
        Returns:
            Dictionary of model_id -> model_config for the specified provider
        """
        filtered_models = {}
        
        source_dict = self.configurations
        if model_type == AIModelTypeEnum.GENERATION:
            source_dict = self.generation_models
        for model_id, model in source_dict.items():
            if model.provider == provider:
                filtered_models[model_id] = model
        
        return filtered_models

    def get_available_providers(self) -> list:
        """
        Get list of all providers that have active models.
        
        Returns:
            List of AIProviderEnum values
        """
        providers = set()
        for model in self.configurations.values():
            providers.add(model.provider)
        return list(providers)

    def get_default_model_for_provider(self, provider: AIProviderEnum) -> AIModelConfiguration:
        """
        Get the default generation model for a specific provider.
        
        Args:
            provider: The AI provider
            
        Returns:
            The default model configuration for the provider, or None if no models available
        """
        provider_models = self.get_models_by_provider(provider, AIModelTypeEnum.GENERATION)
        
        if not provider_models:
            return None
        
        if self.default_generation_model and self.default_generation_model.provider == provider:
            return self.default_generation_model

        return next(iter(provider_models.values()))

    def is_provider_available(self, provider: AIProviderEnum) -> bool:
        """
        Check if a provider has any active models available.
        
        Args:
            provider: The AI provider to check
            
        Returns:
            True if provider has active models, False otherwise
        """
        return len(self.get_models_by_provider(provider)) > 0

    def get_model_by_id(self, model_id: int) -> AIModelConfiguration:
        """
        Get a model configuration by ID.
        
        Args:
            model_id: The model configuration ID
            
        Returns:
            The model configuration or None if not found
        """
        return self.configurations.get(model_id)

    def get_generation_models_list(self) -> list:
        """
        Get a list of all generation models for UI display.
        
        Returns:
            List of generation model configurations sorted by display name
        """
        models = list(self.generation_models.values())
        return sorted(models, key=lambda m: m.display_name)


# Create a single, shared instance of the cache to be used across the application
model_cache = AIModelCache()
