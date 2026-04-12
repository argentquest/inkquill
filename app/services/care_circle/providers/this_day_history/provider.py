import httpx
import random
from datetime import date
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from typing import Any, Dict

class ThisDayHistoryProvider(BaseCareCircleProvider):
    provider_key = "this_day_history"
    is_safe_for_patient = True

    """
    Fetches a historical event that occurred on today's calendar date.
    
    Prefers events spanning the 1950s-1970s and utilizes an LLM to rewrite 
    the Wikipedia summary into a softer, memory-care friendly tone.
    """
    
    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Obtain the 'On This Day' historical tidbit.
        
        Calls Wikimedia's feed API asynchronously. If the service fails or 
        times out, a generic fallback message is issued.
        
        Returns:
            dict: Containing the 'year', rewritten 'event' string, 'month', and 'day'.
        """
        cfg = self.patient_config
        today = date.today()
        # Wikimedia On This Day endpoint
        api_url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{today.month:02}/{today.day:02}"
        fallback = cfg.get("fallback", "Many wonderful things have happened on this day!")
        
        headers = {
            "User-Agent": "DailyNewsletter/1.0 (memory-care newsletter; contact@example.com)"
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, headers=headers, follow_redirects=True, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    events = data.get("events", [])
                    
                    # Filter for events in the 1950s-1970s if possible
                    preferred_events = [e for e in events if 1950 <= int(e.get("year", 0)) <= 1975]
                    if not preferred_events:
                        preferred_events = events
                        
                    if preferred_events:
                        event = random.choice(preferred_events)
                        year = event.get("year", "")
                        text = event.get("text", fallback)

                        # Use LLM to rewrite for memory care
                        prompt = f"Rewrite this historical event to be one short, warm sentence for an 88-year-old: '{text} (Year: {year})'. Focus on the positive or neutral aspects only. Avoid any mention of conflict, tragedy, or distressing events."
                        try:
                            llm_response = await generate_text_with_usage(prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=128)
                            self.log_llm_response(llm_response, prompt=prompt, system_prompt=DEMENTIA_SYSTEM_PROMPT)
                            if llm_response.content:
                                return {"year": year, "event": llm_response.content, "month": today.strftime("%B"), "day": today.day}
                        except:
                            pass
                            
                        return {"year": year, "event": text, "month": today.strftime("%B"), "day": today.day}
            return {"year": "", "event": fallback, "month": today.strftime("%B"), "day": today.day}
        except Exception as e:
            app_logger.info(f"Error in ThisDayHistoryProvider: {e}")
            return {"year": "", "event": fallback, "month": today.strftime("%B"), "day": today.day}
