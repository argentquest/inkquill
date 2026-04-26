"""Core application helpers for config."""

# /story_app/app/core/config.py
import os
import logging
from datetime import timezone as dt_timezone
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl
from typing import Optional, List, Union, Dict, Any

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """
    Application Settings Model.
    Reads settings from environment variables.
    """
    APP_PROJECT_NAME: str = Field(default="AI Storytelling Assistant", alias="APP_PROJECT_NAME")
    APP_URL: str = Field(default="http://localhost:8000", alias="APP_URL")
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = Field(default="development", alias="APP_ENV")

    # --- Google Analytics Configuration ---
    GOOGLE_ANALYTICS_ID: Optional[str] = Field(default=None, alias="GOOGLE_ANALYTICS_ID")
    GOOGLE_ANALYTICS_CONSENT_MODE: bool = Field(default=True, alias="GOOGLE_ANALYTICS_CONSENT_MODE")
    COOKIE_CONSENT_REQUIRED: bool = Field(default=True, alias="COOKIE_CONSENT_REQUIRED")

    # --- Bot Detection Configuration ---
    BOT_USER_AGENTS: List[str] = Field(default=[
        "facebookexternalhit", "Twitterbot", "LinkedInBot", "DiscordBot",
        "WhatsApp", "TelegramBot", "SkypeUriPreview", "SlackBot",
        "GoogleBot", "BingBot", "YandexBot", "baiduspider"
    ], alias="BOT_USER_AGENTS")
    FILTER_BOT_ANALYTICS: bool = Field(default=True, alias="FILTER_BOT_ANALYTICS")

    POSTGRES_USER: str = Field(default="user_placeholder", alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="password_placeholder", alias="POSTGRES_PASSWORD")
    POSTGRES_SERVER: str = Field(default="localhost", alias="POSTGRES_SERVER")
    POSTGRES_PORT: str = Field(default="5432", alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="ai_story_app_db_placeholder", alias="POSTGRES_DB")

    AUTH_SECRET_KEY: str = Field(default="a_very_secret_key_that_should_be_long_and_random_in_production", alias="AUTH_SECRET_KEY")
    AUTH_ALGORITHM: str = Field(default="HS256", alias="AUTH_ALGORITHM")
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 7, alias="AUTH_ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 30, alias="REFRESH_TOKEN_EXPIRE_MINUTES")
    TIMEZONE: Any = dt_timezone.utc

    # --- Google OAuth Configuration ---
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = Field(default=None, alias="GOOGLE_OAUTH_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET: Optional[str] = Field(default=None, alias="GOOGLE_OAUTH_CLIENT_SECRET")
    SOCIAL_AUTH_REDIRECT_IS_HTTPS: bool = Field(default=False, alias="SOCIAL_AUTH_REDIRECT_IS_HTTPS")
    SOCIAL_AUTH_LOGIN_REDIRECT_URL: str = Field(default="/dashboard", alias="SOCIAL_AUTH_LOGIN_REDIRECT_URL")
    SOCIAL_AUTH_LOGIN_ERROR_URL: str = Field(default="/login", alias="SOCIAL_AUTH_LOGIN_ERROR_URL")
    SOCIAL_AUTH_NEW_USER_REDIRECT_URL: str = Field(default="/welcome", alias="SOCIAL_AUTH_NEW_USER_REDIRECT_URL")
    OAUTH_ENABLED: bool = Field(default=False, alias="OAUTH_ENABLED")
    GOOGLE_OAUTH_ENABLED: bool = Field(default=False, alias="GOOGLE_OAUTH_ENABLED")

    # --- OpenRouter Configuration (primary LLM provider) ---
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    OPENROUTER_SITE_URL: Optional[str] = Field(default=None, alias="OPENROUTER_SITE_URL")
    OPENROUTER_APP_NAME: Optional[str] = Field(default=None, alias="OPENROUTER_APP_NAME")
    # Default model - any OpenRouter-compatible model identifier
    OPENROUTER_DEFAULT_MODEL: str = Field(default="openai/gpt-4o-mini", alias="OPENROUTER_DEFAULT_MODEL")
    OPENROUTER_PREMIUM_MODEL: str = Field(default="openai/gpt-4o", alias="OPENROUTER_PREMIUM_MODEL")
    
    # --- Care Circle Specific Provider Configuration ---
    CARE_CIRCLE_TEXT_PROVIDER: str = Field(default="AUTO", alias="CARE_CIRCLE_TEXT_PROVIDER")
    CARE_CIRCLE_IMAGE_PROVIDER: str = Field(default="AUTO", alias="CARE_CIRCLE_IMAGE_PROVIDER")
    CARE_CIRCLE_DEFAULT_TEXT_MODEL: str = Field(default="openai/gpt-4o-mini", alias="CARE_CIRCLE_DEFAULT_TEXT_MODEL")
    CARE_CIRCLE_DEFAULT_IMAGE_MODEL: str = Field(default="gpt-image-1", alias="CARE_CIRCLE_DEFAULT_IMAGE_MODEL")
    CARE_CIRCLE_DEFAULT_INPUT_PRICE_USD_PM: float = Field(default=0.60, alias="CARE_CIRCLE_DEFAULT_INPUT_PRICE_USD_PM")
    CARE_CIRCLE_DEFAULT_OUTPUT_PRICE_USD_PM: float = Field(default=0.60, alias="CARE_CIRCLE_DEFAULT_OUTPUT_PRICE_USD_PM")
    AZURE_FOUNDRY_API_KEY: Optional[str] = Field(default=None, alias="AZURE_FOUNDRY_API_KEY")
    AZURE_FOUNDRY_ENDPOINT: Optional[str] = Field(default=None, alias="AZURE_FOUNDRY_ENDPOINT")
    AZURE_FOUNDRY_TEXT_ENDPOINT: Optional[str] = Field(default=None, alias="AZURE_FOUNDRY_TEXT_ENDPOINT")
    AZURE_FOUNDRY_IMAGE_ENDPOINT: Optional[str] = Field(default=None, alias="AZURE_FOUNDRY_IMAGE_ENDPOINT")
    AZURE_FOUNDRY_API_VERSION: str = Field(default="2024-10-21", alias="AZURE_FOUNDRY_API_VERSION")
    AZURE_FOUNDRY_TEXT_DEPLOYMENT: Optional[str] = Field(default=None, alias="AZURE_FOUNDRY_TEXT_DEPLOYMENT")
    AZURE_FOUNDRY_IMAGE_DEPLOYMENT: Optional[str] = Field(default=None, alias="AZURE_FOUNDRY_IMAGE_DEPLOYMENT")

    # --- Third-party Data APIs (Care Circle providers) ---
    NPS_API_KEY: Optional[str] = Field(default=None, alias="NPS_API_KEY")
    GNEWS_API_KEY: Optional[str] = Field(default=None, alias="GNEWS_API_KEY")

    # --- LM Studio (local) Configuration ---
    LMSTUDIO_BASE_URL: str = Field(default="http://localhost:1234/v1", alias="LMSTUDIO_BASE_URL")
    LMSTUDIO_MODEL: str = Field(default="local-model", alias="LMSTUDIO_MODEL")
    LMSTUDIO_ENABLED: bool = Field(default=False, alias="LMSTUDIO_ENABLED")

    # --- Standard OpenAI API Configuration (optional fallback) ---
    OPENAI_API_KEY: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_IMAGE_MODEL: str = Field(default="gpt-image-1", alias="OPENAI_IMAGE_MODEL")

    # --- Active LLM Provider Selection ---
    # Options: OPENROUTER, OPENAI
    ACTIVE_LLM_PROVIDER: str = Field(default="OPENROUTER", alias="ACTIVE_LLM_PROVIDER")
    DEFAULT_GENERATION_MODEL_NAME: str = Field(default="openai/gpt-4o-mini", alias="DEFAULT_GENERATION_MODEL_NAME")
    AI_ORCHESTRATION_BACKEND: str = Field(default="LANGGRAPH", alias="AI_ORCHESTRATION_BACKEND")

    # --- Scheduler Server Configuration ---
    SCHEDULER_HOST: str = Field(default="127.0.0.1", alias="SCHEDULER_HOST")
    SCHEDULER_PORT: int = Field(default=8001, alias="SCHEDULER_PORT")
    SCHEDULER_ENABLED: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    SCHEDULER_MISFIRE_GRACE_TIME: int = Field(default=300, alias="SCHEDULER_MISFIRE_GRACE_TIME")

    # --- Local File Storage Configuration ---
    LOCAL_STORAGE_BASE_PATH: str = Field(default="./data/uploads", alias="LOCAL_STORAGE_BASE_PATH")
    LOCAL_STORAGE_DOCUMENTS_PATH: str = Field(default="documents", alias="LOCAL_STORAGE_DOCUMENTS_PATH")
    LOCAL_STORAGE_PUBLISHED_STORIES_PATH: str = Field(default="published", alias="LOCAL_STORAGE_PUBLISHED_STORIES_PATH")
    LOCAL_STORAGE_GENERATED_IMAGES_PATH: str = Field(default="generated_images", alias="LOCAL_STORAGE_GENERATED_IMAGES_PATH")
    LOCAL_STORAGE_BLOG_MEDIA_PATH: str = Field(default="blog_media", alias="LOCAL_STORAGE_BLOG_MEDIA_PATH")

    # --- Image Generation Provider Settings ---
    ACTIVE_IMAGE_PROVIDER: str = Field(default="DALLE3", alias="ACTIVE_IMAGE_PROVIDER")
    DEFAULT_IMAGE_SIZE: str = Field(default="1024x1024", alias="DEFAULT_IMAGE_SIZE")

    # RunPod Configuration (optional)
    RUNPOD_API_KEY: Optional[str] = Field(default=None, alias="RUNPOD_API_KEY")
    RUNPOD_ENDPOINT_ID: Optional[str] = Field(default=None, alias="RUNPOD_ENDPOINT_ID")
    RUNPOD_MODEL_TYPE: str = Field(default="flux-dev", alias="RUNPOD_MODEL_TYPE")
    RUNPOD_CHECKPOINT_NAME: str = Field(default="flux1-dev.safetensors", alias="RUNPOD_CHECKPOINT_NAME")

    DEFAULT_CHUNK_SIZE_TOKENS: int = Field(default=1000, alias="DEFAULT_CHUNK_SIZE_TOKENS", gt=0)
    DEFAULT_CHUNK_OVERLAP_TOKENS: int = Field(default=100, alias="DEFAULT_CHUNK_OVERLAP_TOKENS", ge=0)

    BACKEND_CORS_ORIGINS: List[str] = Field(default=["*"], alias="BACKEND_CORS_ORIGINS")

    SCENE_EXTRACTION_MAX_TOKENS: int = Field(default=4000, alias="SCENE_EXTRACTION_MAX_TOKENS", gt=0)
    SCENE_EXTRACTION_TEMPERATURE: float = Field(default=0.2, alias="SCENE_EXTRACTION_TEMPERATURE", ge=0.0, le=2.0)
    MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT: int = Field(default=25, alias="MAX_ELEMENTS_PER_TYPE_FROM_BOOK_IMPORT", gt=0, le=50)

    # Story Generation Settings
    @property
    def STORY_GENERATION_MAX_TOKENS(self) -> int:
        return self.AI_MAX_TOKEN_SETTINGS.get("story_generation", 6000)

    @property
    def STORY_GENERATION_TEMPERATURE(self) -> float:
        return self.AI_TEMPERATURE_SETTINGS.get("story_generation", 0.6)

    AI_TEMPERATURE_SETTINGS: Dict[str, float] = {
        "act_review": 0.4, "act_narrative": 0.7, "act_metadata": 0.3,
        "scene_narrative": 0.7, "scene_metadata": 0.3, "scene_extraction": 0.2,
        "world_generation": 0.5, "world_elements_extraction": 0.3,
        "story_generation": 0.6, "test": 0.7
    }

    AI_MAX_TOKEN_SETTINGS: Dict[str, int] = {
        "act_review": 3500, "act_narrative": 3000, "act_metadata": 1500,
        "scene_narrative": 2500, "scene_metadata": 1000, "scene_extraction": 4000,
        "world_generation": 3500, "world_elements_extraction": 8000,
        "story_generation": 6000, "test": 800
    }

    AI_TOP_P_SETTINGS: Dict[str, float] = {
        "act_review": 0.9, "act_narrative": 0.8, "act_metadata": 0.7,
        "scene_narrative": 0.8, "scene_metadata": 0.7, "scene_extraction": 0.7,
        "world_generation": 0.9, "world_elements_extraction": 0.8,
        "story_generation": 0.9, "test": 0.8
    }
    DEFAULT_TOKENIZER: str = Field(default="cl100k_base", alias="DEFAULT_TOKENIZER")
    DEFAULT_MODEL_FOR_CHUNKING: str = Field(default="gpt-3.5-turbo", alias="DEFAULT_MODEL_FOR_CHUNKING")

    # --- Twilio SMS Configuration ---
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, alias="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, alias="TWILIO_AUTH_TOKEN")
    TWILIO_FROM_NUMBER: Optional[str] = Field(default=None, alias="TWILIO_FROM_NUMBER")
    SMS_TEST_MODE: bool = Field(default=True, alias="SMS_TEST_MODE")
    SMS_TEST_NUMBER: Optional[str] = Field(default=None, alias="SMS_TEST_NUMBER")

    # --- Email Configuration ---
    SMTP_SERVER: Optional[str] = Field(default=None, alias="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, alias="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    FROM_EMAIL: Optional[str] = Field(default=None, alias="FROM_EMAIL")
    FROM_NAME: str = Field(default="AI Storytelling Assistant", alias="FROM_NAME")
    EMAIL_TEST_MODE: bool = Field(default=False, alias="EMAIL_TEST_MODE")
    EMAIL_TEST_ADDRESS: Optional[str] = Field(default=None, alias="EMAIL_TEST_ADDRESS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

def get_database_url(db_settings: Settings) -> str:
    """Return database url."""
    user = db_settings.POSTGRES_USER
    password = db_settings.POSTGRES_PASSWORD
    server = db_settings.POSTGRES_SERVER
    port = db_settings.POSTGRES_PORT
    db_name = db_settings.POSTGRES_DB

    if not all([user, password, server, port, db_name]) or \
       any(val.endswith("_placeholder") for val in [user, password, db_name]):
        logger.warning("Database configuration appears incomplete or uses placeholders. Application may not connect to DB.")
        return f"postgresql+asyncpg://postgres:password@localhost:5432/ai_story_app_db_dev_default"

    return f"postgresql+asyncpg://{user}:{password}@{server}:{port}/{db_name}"

SQLALCHEMY_DATABASE_URI = get_database_url(settings)

def log_application_settings():
    """Logs the loaded application settings. Call this *after* logging is configured."""
    logger.info("--- Application Settings Loaded ---")
    logger.info(f"Project Name: {settings.APP_PROJECT_NAME}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Active LLM Provider: {settings.ACTIVE_LLM_PROVIDER}")
    logger.info(f"Google Analytics: {'Enabled' if settings.GOOGLE_ANALYTICS_ID else 'Disabled'}")

    masked_db_uri = SQLALCHEMY_DATABASE_URI
    if settings.POSTGRES_PASSWORD and not settings.POSTGRES_PASSWORD.endswith("_placeholder"):
        masked_db_uri = masked_db_uri.replace(settings.POSTGRES_PASSWORD, "********")
    logger.info(f"Database URI (password masked): {masked_db_uri}")

    logger.info(f"OpenRouter Configured: {bool(settings.OPENROUTER_API_KEY)}")
    logger.info(f"OpenRouter Default Model: {settings.OPENROUTER_DEFAULT_MODEL}")
    logger.info(f"Local Storage Path: {settings.LOCAL_STORAGE_BASE_PATH}")
    logger.info("--- Model Settings ---")
    logger.info(f"Default Chunk Size: {settings.DEFAULT_CHUNK_SIZE_TOKENS} tokens")
    logger.info(f"Default Generation Model (Fallback): {settings.DEFAULT_GENERATION_MODEL_NAME}")
    logger.info("--- Configuration Details Logged ---")

