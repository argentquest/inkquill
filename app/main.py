# /story_app/app/main.py
"""
Main FastAPI application entry point.
Configures logging, middleware, routers, and application lifecycle.
"""

import os
import logging
from app.core.logging_config import setup_logging

# --- Configure Logging (first priority) ---
LOG_LEVEL_CONSOLE_ENV = os.getenv("LOG_LEVEL_CONSOLE", "DEBUG")
LOG_LEVEL_FILE_ENV = os.getenv("LOG_LEVEL_FILE", "DEBUG")
CLEAR_EXISTING_HANDLERS_ENV = os.getenv("CLEAR_LOG_HANDLERS", "true").lower() == "true"
APP_LOG_DIR_MAIN = os.getenv("APP_LOG_DIR", "./logs")

setup_logging(
    log_level_console_str=LOG_LEVEL_CONSOLE_ENV,
    log_level_file_str=LOG_LEVEL_FILE_ENV,
    clear_existing_handlers=CLEAR_EXISTING_HANDLERS_ENV
)
logger = logging.getLogger("app.main")

logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Files in current directory: {os.listdir('.')}")
logger.info("Starting FastAPI application...")
logger.info("main.py: Logging configured by setup_logging.")
# --- End Logging Configuration ---


# --- FastAPI and third-party imports ---
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import asyncio
import sqlalchemy
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.middleware.sessions import SessionMiddleware


# --- Core components ---
from app.core.config import settings, SQLALCHEMY_DATABASE_URI, log_application_settings
from app.core.middleware import LoggingContextMiddleware, UserActivityMiddleware
from app.core.referral_middleware import ReferralTrackingMiddleware
from app.core.security_middleware import SecurityHeadersMiddleware
from app.db.database import engine
from app.services.ai_orchestration import (
    get_ai_orchestration_backend,
    orchestration_backend_is_semantic_kernel,
)
from app.services import storytelling_runtime

# --- API Router imports ---
from app.routers import (
    auth,
    oauth,  # OAuth router
    users,
    dashboard,  # Dashboard API router
    batch,  # Batch operations router
    story,
    basic_stories,  # Basic stories router
    document_upload,
    ai_assisted_writing,
    ai_scene_writing,
    prompt as prompt_api_router,
    story_wizard_api,
    world as world_api_router,
    character as character_api_router,
    location as location_api_router,
    location_connection as location_connection_api_router,
    lore_item as lore_item_api_router,
    world_importer as world_importer_router,
    world_builder,
    act_ai_review,
    story_class as story_class_api_router,
    image_generation as image_generation_router,
    ai_model_config as ai_model_config_router, # <-- ADD THIS LINE
    brainstorm,
    scene,
    world_chat,
    story_chat,  # Story chat router
    associations,
    forum_category,
    forum_thread,
    forum_post,
    admin_news,
    billing,
    admin_billing,
    admin_cta,  # Admin CTA management
    public_world_chat,
    llm_models,
    published_stories,
    maintenance,
    social_sharing,
    interview,
    welcome_interview,
    ai_text_transform,
    blog,
    blog_categories,
    blog_tags,
    blog_search,
    blog_comments,
    blog_subscriptions,
    blog_media,
    bot_analytics,
    social_preview,
    og_debug,
    blog_engagement,
    blog_ai_writing,
    blog_author_profile,
    blog_analytics,
    blog_integration,
    blog_seo,
    referrals,
    care_circle,
    chatbot
)
from app.routers.act import story_acts_router, acts_router


# --- View Router imports ---
from app.routers import (
    views_general, 
    views_story_act, 
    views_prompt,
    views_document, 
    views_world,
    views_story_class,
    views_world_chat,
    views_forum,
    views_billing,
    views_admin_billing,
    views_public,
    views_llm_models,
    views_published_stories,
    views_admin_maintenance,
    views_story_wizard,
    admin_help_editor,
    views_blog,
    views_referrals
)

# --- Call the logging function right after all initial imports are done ---
log_application_settings()

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Handle lifespan."""
    logger.info("Lifespan: Application startup sequence initiated.")
    
    # Load AI model configurations into cache
    from app.services.ai_model_cache import model_cache
    try:
        await model_cache.load_models_from_db()
        logger.info("Lifespan: AI Model Cache loaded from database.")
    except Exception as e_cache:
        logger.critical(f"Lifespan: CRITICAL - Failed to load AI Model Cache from database: {e_cache}", exc_info=True)
    
    orchestration_backend = get_ai_orchestration_backend()
    if orchestration_backend_is_semantic_kernel():
        if storytelling_runtime.kernel and storytelling_runtime.review_act_content_function:
            logger.info("Lifespan: Storytelling runtime and key functions appear to be available.")
        else:
            logger.error("Lifespan: Semantic-kernel backend is enabled, but the storytelling runtime or required functions are unavailable.")
    else:
        logger.info(
            "Lifespan: Skipping semantic-kernel-specific startup checks because AI_ORCHESTRATION_BACKEND='%s'.",
            orchestration_backend,
        )
    
    try:
        async with engine.connect() as connection:
            await connection.execute(sqlalchemy.text("SELECT 1"))
        logger.info("Lifespan: PostgreSQL database connection successful.")
    except Exception as e_db:
        logger.critical(f"Lifespan: CRITICAL - PostgreSQL database connection FAILED: {e_db}", exc_info=True)
    
    logger.info("Lifespan: Application startup sequence complete.")
    try:
        yield
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Lifespan: Shutdown signal received.")
    finally:
        # --- Shutdown logic ---
        logger.info("Lifespan: Application shutdown sequence initiated.")
        if engine:
            try:
                await engine.dispose()
                logger.info("Lifespan: Database engine disposed.")
            except Exception as e:
                logger.warning(f"Lifespan: Error disposing database engine: {e}")
        logger.info("Lifespan: Application shutdown sequence complete.")


app = FastAPI(
    title=settings.APP_PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.APP_ENV.lower() != "production" else None,
    docs_url="/docs" if settings.APP_ENV.lower() != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV.lower() != "production" else None,
    lifespan=lifespan
)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
logger.info("ProxyHeadersMiddleware added to trust X-Forwarded-* headers.")


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o).strip() for o in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page", "X-Per-Page", "X-Pages"]  # For pagination metadata
    )
logger.info(f"CORS configured for origins: {settings.BACKEND_CORS_ORIGINS}")

# Add SessionMiddleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.AUTH_SECRET_KEY,
    session_cookie="session",
    max_age=3600  # 1 hour
)
logger.info("SessionMiddleware added for OAuth support.")

# Add SecurityHeadersMiddleware first (highest priority)
app.add_middleware(SecurityHeadersMiddleware)
logger.info("SecurityHeadersMiddleware added for security protection.")

app.add_middleware(LoggingContextMiddleware)
logger.info("LoggingContextMiddleware added.")

# Add ReferralTrackingMiddleware to detect and track referral parameters
app.add_middleware(ReferralTrackingMiddleware)
logger.info("ReferralTrackingMiddleware added for referral tracking.")

# Add UserActivityMiddleware for comprehensive request logging
app.add_middleware(
    UserActivityMiddleware,
    exclude_paths={
        "/docs", "/redoc", "/openapi.json", "/health", "/static", "/favicon.ico",
        "/api/v1/billing/ai-costs/last",
        "/api/v1/billing/balance",
        "/api/v1/maintenance/status"
    },
    exclude_methods={"OPTIONS"},
    log_request_body=False,  # Set to True if you want to log request bodies
    log_response_body=False,  # Set to True if you want to log response bodies
    max_body_size=1000,
    sensitive_fields={"password", "token", "secret", "api_key", "hashed_password"}
)
logger.info("UserActivityMiddleware added for request logging.")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
logger.info("Static files mounted at /static.")

# Serve locally published HTML stories
import os as _os
_published_dir = _os.path.join(settings.LOCAL_STORAGE_BASE_PATH, settings.LOCAL_STORAGE_PUBLISHED_STORIES_PATH)
_os.makedirs(_published_dir, exist_ok=True)
app.mount("/published/stories", StaticFiles(directory=_published_dir), name="published_stories")
logger.info(f"Published stories served at /published/stories from {_published_dir}")

# --- Setup Jinja2 Template Globals ---
from app.core.template_filters import setup_secure_templates
templates = setup_secure_templates()
logger.info("Secure Jinja2 templates configured with security filters.")
logger.info(f"Jinja2 template globals configured. Google Analytics: {'Enabled' if settings.GOOGLE_ANALYTICS_ID else 'Disabled'}, Consent Mode: {'Enabled' if settings.GOOGLE_ANALYTICS_CONSENT_MODE else 'Disabled'}")

# --- Include API Routers ---
api_v1_prefix = settings.API_V1_STR

# Core API routers
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(oauth.router, prefix=api_v1_prefix)  # OAuth routes
app.include_router(users.router, prefix=api_v1_prefix)
app.include_router(dashboard.router)  # Dashboard API router
app.include_router(batch.router)  # Batch operations router
app.include_router(interview.router)  # Interview router (includes own prefix)
app.include_router(welcome_interview.router)  # Welcome interview router (includes own prefix)

# NEW: Add the AI Model Config router
app.include_router(ai_model_config_router.router, prefix=api_v1_prefix)

# NEW: Add the LLM Models router (public info page)
app.include_router(llm_models.router, prefix=api_v1_prefix)

# NEW: Add the Billing router
app.include_router(billing.router, prefix=api_v1_prefix)

# NEW: Add the Admin Billing router
app.include_router(admin_billing.router, prefix=api_v1_prefix)

# NEW: Add the AI Text Transform router
app.include_router(ai_text_transform.router, prefix=api_v1_prefix)

# Content management routers
app.include_router(prompt_api_router.router, prefix=api_v1_prefix)
app.include_router(world_api_router.router, prefix=api_v1_prefix)
app.include_router(world_importer_router.router, prefix=api_v1_prefix)
app.include_router(world_builder.router, prefix=f"{api_v1_prefix}/world-builder", tags=["World Builder"])
app.include_router(story.router, prefix=api_v1_prefix)
app.include_router(basic_stories.router, prefix=api_v1_prefix)
app.include_router(story_acts_router, prefix=api_v1_prefix)
app.include_router(acts_router, prefix=api_v1_prefix)
app.include_router(act_ai_review.router, prefix=api_v1_prefix)
app.include_router(story_class_api_router.router, prefix=api_v1_prefix)

# Associations management router
app.include_router(associations.router, prefix=api_v1_prefix)

# World element API routers
app.include_router(character_api_router.router_world_characters, prefix=api_v1_prefix)
app.include_router(character_api_router.router_characters, prefix=api_v1_prefix)
app.include_router(character_api_router.router_story_characters, prefix=api_v1_prefix)
app.include_router(location_api_router.router_world_locations, prefix=api_v1_prefix)
app.include_router(location_api_router.router_locations, prefix=api_v1_prefix)
app.include_router(location_api_router.router_story_locations, prefix=api_v1_prefix)
app.include_router(location_connection_api_router.router_world_location_connections, prefix=api_v1_prefix)
app.include_router(location_connection_api_router.router_location_connections, prefix=api_v1_prefix)
app.include_router(lore_item_api_router.router_world_lore_items, prefix=api_v1_prefix)
app.include_router(lore_item_api_router.router_lore_items, prefix=api_v1_prefix)
app.include_router(lore_item_api_router.router_story_lore_items, prefix=api_v1_prefix)

# Scene management API routers
app.include_router(scene.router_act_scenes, prefix=api_v1_prefix)
app.include_router(scene.router_scenes, prefix=api_v1_prefix)

# Document and AI-assisted API routers
app.include_router(document_upload.router, prefix=f"{api_v1_prefix}/documents", tags=["Document Management"])
app.include_router(ai_assisted_writing.router)
app.include_router(blog_ai_writing.router)
app.include_router(ai_scene_writing.router)
app.include_router(image_generation_router.router, prefix=api_v1_prefix)

# World Chat API router
app.include_router(world_chat.router)

# Story Chat API router
app.include_router(story_chat.router, prefix=api_v1_prefix)

# Forum API routers
app.include_router(forum_category.router)
app.include_router(forum_thread.router)
app.include_router(forum_post.router)

# News routers (public and admin)
app.include_router(admin_news.router)  # Public news routes
app.include_router(admin_news.admin_router)  # Admin news routes

# Admin CTA management router
app.include_router(admin_cta.router, prefix=api_v1_prefix)

# Public world chat API router
app.include_router(public_world_chat.router, prefix=api_v1_prefix)

# Published stories API router
app.include_router(published_stories.router, prefix=api_v1_prefix)

# Maintenance management API router
app.include_router(maintenance.router, prefix=api_v1_prefix)

# Social sharing API router
app.include_router(social_sharing.router)

# Admin CTA management router (both API and views)
from app.routers import views_admin_cta
app.include_router(views_admin_cta.router)

# Blog API routers
app.include_router(blog.router)
app.include_router(blog_categories.router)
app.include_router(blog_tags.router)
app.include_router(blog_search.router)
app.include_router(blog_comments.router)
app.include_router(blog_subscriptions.router)
app.include_router(blog_media.router)
app.include_router(blog_engagement.router)
app.include_router(blog_author_profile.router)
app.include_router(blog_analytics.router)
app.include_router(blog_integration.router)
app.include_router(blog_seo.router)

# Referral API router
app.include_router(referrals.router, prefix=api_v1_prefix)
app.include_router(care_circle.router, prefix=api_v1_prefix)

# Bot Analytics API router (for debugging/monitoring)
app.include_router(bot_analytics.router)

# Social Media Preview API router
app.include_router(social_preview.router)

# Open Graph Debug router (for testing social media sharing)
app.include_router(og_debug.router)

logger.info("API routers included.")

# --- Include UI View Routers ---
app.include_router(views_general.router)
app.include_router(views_prompt.router)
app.include_router(views_story_act.router)
app.include_router(views_document.router)
app.include_router(views_story_class.router)
app.include_router(views_world.router) # This now contains all world, char, loc, and lore views
app.include_router(views_world_chat.router)
app.include_router(views_forum.router)
app.include_router(views_billing.router)
app.include_router(views_admin_billing.router)
app.include_router(views_public.router)
app.include_router(views_llm_models.router)
app.include_router(views_published_stories.router)
app.include_router(views_admin_maintenance.router)
app.include_router(views_story_wizard.router)
app.include_router(story_wizard_api.router)
app.include_router(brainstorm.router)
app.include_router(admin_help_editor.router)
app.include_router(views_blog.router)
app.include_router(views_referrals.router)
logger.info("UI view routers included.")

@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots_txt():
    """Serve robots.txt file to control bot behavior"""
    try:
        with open("app/static/robots.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("robots.txt file not found")
        return "User-agent: *\nDisallow: /api/\nAllow: /public/"

@app.get("/", response_class=HTMLResponse, include_in_schema=False, name="root_redirect_to_ui_home")
async def root_redirect_to_ui_home(request: Request):
    """Handle root redirect to ui home."""
    try: 
        ui_home_url = str(request.url_for('ui_home'))
    except Exception as e_url: 
        logger.warning(f"Could not resolve 'ui_home' for root redirect, defaulting to '/ui/'. Error: {e_url}")
        ui_home_url = "/ui/"
    
    # Preserve query parameters for referral tracking
    if request.query_params:
        query_string = str(request.query_params)
        ui_home_url = f"{ui_home_url}?{query_string}"
        logger.info(f"🔍 REDIRECT DEBUG: Redirecting to {ui_home_url} with preserved query params")
    
    return RedirectResponse(url=ui_home_url, status_code=status.HTTP_302_FOUND)

if __name__ == "__main__":
    import uvicorn
    host_env = os.getenv("APP_HOST", "0.0.0.0")
    port_env = int(os.getenv("APP_PORT", "8000"))
    log_level_uvicorn = LOG_LEVEL_CONSOLE_ENV.lower()

    logger.info(f"Running Uvicorn directly from main.py on {host_env}:{port_env} with log level '{log_level_uvicorn}'...")
    uvicorn.run(
        "app.main:app", 
        host=host_env, 
        port=port_env, 
        reload=True,
        log_level=log_level_uvicorn
    )

