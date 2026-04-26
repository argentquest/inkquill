"""
ASCII art comic provider - generates simple text-based comics without external URLs.
"""
from app.services.care_circle.comic_base_provider import BaseComicStripProvider
from datetime import date
from typing import Any
import random


class ComicAsciiProvider(BaseComicStripProvider):
    provider_key = "comic_ascii"
    comic_name = "ASCII Art Comics"
    comic_author = "Generated"
    comic_license = "Creative Commons"
    comic_attribution = "ASCII Art Comics - Generated for entertainment"
    is_safe_for_patient = True

    # ASCII art comics
    _sample_strips = [
        {
            "ascii_art": """
            ╔══════════════════════════════╗
            ║         SMILE CORNER         ║
            ╠══════════════════════════════╣
            ║    ┌──────────────┐         ║
            ║    │   (^_^)      │         ║
            ║    │   /    \\     │         ║
            ║    └──────────────┘         ║
            ║                              ║
            ║  Keep smiling! It's a       ║
            ║  beautiful day!             ║
            ╚══════════════════════════════╝
            """,
            "caption": "Smile Corner - A reminder to stay positive!",
            "html_content": """
            <div class="ascii-comic">
            <pre style="font-family: monospace; background: #f8f9fa; padding:学校教育">
            ╔══════════════════════════════╗
            ║         SMILE CORNER         ║
            ╠══════════════════════════════╣
            ║    ┌──────────────┐         ║
            ║    │   (^_^)      │         ║
            ║    │   /    \\     │         ║
            ║    └──────────────┘         ║
            ║                              ║
            ║  Keep smiling! It's a       ║
            ║  beautiful day!             ║
            ╚══════════════════════════════╝
            </pre>
            </div>
            """
        },
        {
            "ascii_art": """
            ╔══════════════════════════════╗
            ║         CAT CAFE              ║
            ╠══════════════════════════════╣
            ║  /\\___/\\                     ║
            ║ ( o   o )                    ║
            ║  >  ^  <                     ║
            ║   ────                       ║
            ║                              ║
            ║  "Purr-fect relaxation!"    ║
            ╚══════════════════════════════╝
            """,
            "caption": "Cat Cafe - A moment of feline fun!",
            "html_content": """
            <div class="ascii-comic">
            <pre style="font-family: monospace; background: #f8f9fa; padding: 10px;">
            ╔══════════════════════════════╗
            ║         CAT CAFE              ║
            ╠══════════════════════════════╣
            ║  /\\___/\\                     ║
            ║ ( o   o )                    ║
            ║  >  ^  <                     ║
            ║   ────                       ║
            ║                              ║
            ║  "Purr-fect relaxation!"    ║
            ╚══════════════════════════════╝
            </pre>
            </div>
            """
        },
        {
            "ascii_art": """
            ╔══════════════════════════════╗
            ║         GARDEN TIME           ║
            ╠══════════════════════════════╣
            ║     @@@                      ║
            ║    @   @                     ║
            ║   @     @                    ║
            ║  @       @                   ║
            ║   \\     /                    ║
            ║    \\___/                     ║
            ║                              ║
            ║  Growing joy every day!      ║
            ╚══════════════════════════════╝
            """,
            "caption": "Garden Time - Watch your happiness grow!",
            "html_content": """
            <div class="ascii-comic">
            <pre style="font-family: monospace; background: #f8f9fa; padding: 10px;">
            ╔══════════════════════════════╗
            ║         GARDEN TIME           ║
            ╠══════════════════════════════╣
            ║     @@@                      ║
            ║    @   @                     ║
            ║   @     @                    ║
            ║  @       @                   ║
            ║   \\     /                    ║
            ║    \\___/                     ║
            ║                              ║
            ║  Growing joy every day!      ║
            ╚══════════════════════════════╝
            </pre>
            </div>
            """
        },
    ]

    async def _fetch_strip(self, for_date: date, patient_id: int = 0) -> dict[str, Any]:
        """Return an ASCII art comic. Uses deterministic selection per patient/day."""
        seed = for_date.toordinal() * 100 + patient_id % 100
        rng = random.Random(seed)
        strip = rng.choice(self._sample_strips)
        
        # Return with empty image_url since we're using HTML content
        return {
            "image_url": "",  # No external image URL
            "caption": strip["caption"],
            "attribution": self.comic_attribution,
            "source_url": "",  # No external source
            "ascii_art": strip["ascii_art"],
            "html_content": strip["html_content"]
        }