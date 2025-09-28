# /ai_rag_story_app/app/utils/bot_detection.py

import re
import logging
from typing import Optional
from fastapi import Request
from app.core.config import settings

logger = logging.getLogger(__name__)

def is_bot_request(request: Request) -> bool:
    """
    Detect if the request is from a bot/crawler based on User-Agent header.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        True if request appears to be from a bot, False otherwise
    """
    user_agent = request.headers.get("user-agent", "").lower()
    
    if not user_agent:
        # No user agent is suspicious, but not necessarily a bot
        return False
    
    # Check against known bot user agents
    for bot_pattern in settings.BOT_USER_AGENTS:
        if bot_pattern.lower() in user_agent:
            logger.debug(f"Bot detected: {bot_pattern} in user agent: {user_agent[:100]}")
            return True
    
    # Additional bot detection patterns
    bot_patterns = [
        r"bot[/\s]",
        r"crawler",
        r"spider",
        r"scraper",
        r"preview",
        r"embed",
        r"unfurl",
        r"externalhit",
        r"validator",
        r"monitoring",
        r"uptime",
        r"check",
    ]
    
    for pattern in bot_patterns:
        if re.search(pattern, user_agent, re.IGNORECASE):
            logger.debug(f"Bot pattern '{pattern}' matched in user agent: {user_agent[:100]}")
            return True
    
    return False

def get_bot_info(request: Request) -> Optional[dict]:
    """
    Get detailed information about the bot if detected.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        Dictionary with bot information or None if not a bot
    """
    if not is_bot_request(request):
        return None
    
    user_agent = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", "")
    
    # Identify specific bot type
    bot_type = "unknown"
    bot_name = "Unknown Bot"
    
    user_agent_lower = user_agent.lower()
    
    if "facebookexternalhit" in user_agent_lower:
        bot_type = "facebook"
        bot_name = "Facebook Link Preview"
    elif "twitterbot" in user_agent_lower:
        bot_type = "twitter"
        bot_name = "Twitter Card Validator"
    elif "linkedinbot" in user_agent_lower:
        bot_type = "linkedin"
        bot_name = "LinkedIn Preview"
    elif "discordbot" in user_agent_lower:
        bot_type = "discord"
        bot_name = "Discord Embed"
    elif "whatsapp" in user_agent_lower:
        bot_type = "whatsapp"
        bot_name = "WhatsApp Preview"
    elif "slackbot" in user_agent_lower:
        bot_type = "slack"
        bot_name = "Slack Link Unfurling"
    elif "googlebot" in user_agent_lower:
        bot_type = "google"
        bot_name = "Google Search Bot"
    elif "bingbot" in user_agent_lower:
        bot_type = "bing"
        bot_name = "Bing Search Bot"
    elif any(pattern in user_agent_lower for pattern in ["bot", "crawler", "spider"]):
        bot_type = "crawler"
        bot_name = "Web Crawler"
    
    return {
        "is_bot": True,
        "bot_type": bot_type,
        "bot_name": bot_name,
        "user_agent": user_agent,
        "referrer": referrer,
        "ip": request.client.host if request.client else None
    }

def should_track_analytics(request: Request) -> bool:
    """
    Determine if this request should be tracked in analytics.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        True if should track, False if should filter out
    """
    if not settings.FILTER_BOT_ANALYTICS:
        return True
    
    return not is_bot_request(request)

def log_bot_activity(request: Request, endpoint: str = None) -> None:
    """
    Log bot activity for monitoring purposes.
    
    Args:
        request: FastAPI Request object
        endpoint: Optional endpoint name for context
    """
    bot_info = get_bot_info(request)
    
    if bot_info:
        logger.info(
            f"Bot activity detected: {bot_info['bot_name']} "
            f"({bot_info['bot_type']}) accessed {endpoint or request.url.path} "
            f"from {bot_info['ip']} - User-Agent: {bot_info['user_agent'][:100]}"
        )