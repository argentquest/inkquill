import httpx
import random
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



class SongOfTheDayProvider(BaseCareCircleProvider):
    provider_key = "song_of_the_day"
    is_safe_for_patient = True

    """
    Curates a daily song recommendation.

    Selects a song from the user's favourite singers, attempts to locate
    album art from TheAudioDB, and uses an LLM to write a nostalgic,
    warm fact about the track.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Assemble the 'Song of the Day' payload.

        Returns:
            dict: Containing 'artist', 'song', 'album', 'year',
                  'image' (url), and 'fact' (text blob).
        """
        cfg = self.patient_config
        artists_list = cfg.get("artists", [])

        # Use favorite_singers list; fall back to legacy favorite_singer str
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        singers = prefs.get("favorite_singers") or []
        if not singers and prefs.get("favorite_singer"):
            singers = [prefs["favorite_singer"]]
        favorite = random.choice(singers) if singers else ""
        artist_data = None

        if favorite:
            artist_data = next(
                (a for a in artists_list if a["name"] == favorite), None
            )

        if not artist_data and artists_list:
            artist_data = random.choice(artists_list)

        if artist_data:
            singer = artist_data["name"]
            songs = artist_data.get("songs", [])
            song_title = (
                random.choice(songs) if songs else "A wonderful classic"
            )
            era = artist_data.get("era", "1960s")

            image_url = ""
            album_name = ""
            try:
                async with httpx.AsyncClient() as client:
                    search_url = (
                        "https://www.theaudiodb.com/api/v1/json/2/"
                        f"search.php?s={singer}"
                    )
                    resp = await client.get(search_url, timeout=5.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        artists = data.get("artists", [])
                        if artists:
                            image_url = artists[0].get(
                                "strArtistThumb", ""
                            )
            except Exception:
                pass

            try:
                fact_prompt = (
                    f"Write a 1-sentence, warm memory about the song "
                    f"'{song_title}' by {singer}. "
                    f"Make it feel nostalgic and comforting. "
                    f"Avoid any memories of loss, hardship, or distressing events."
                )
                llm_response = await generate_text_with_usage(
                    fact_prompt, system=DEMENTIA_SYSTEM_PROMPT, max_tokens=64
                )
                self.log_llm_response(
                    llm_response,
                    prompt=fact_prompt,
                    system_prompt=DEMENTIA_SYSTEM_PROMPT,
                )
                fact = llm_response.content
                if not fact or len(fact) < 10:
                    fact = (
                        f"'{song_title}' by {singer} is a beautiful song "
                        f"from the {era}."
                    )
            except Exception:
                fact = (
                    f"'{song_title}' by {singer} is a beautiful song "
                    f"from the {era}."
                )

            return {
                "artist": singer,
                "song": song_title,
                "album": album_name,
                "year": era,
                "image": image_url,
                "fact": fact,
            }

        fallback_singer = favorite or "Frank Sinatra"
        return {
            "artist": fallback_singer,
            "song": "A wonderful classic",
            "album": "",
            "year": "1960s",
            "image": "",
            "fact": (
                f"A beautiful song to remind you of the golden days "
                f"of {fallback_singer}."
            ),
        }
