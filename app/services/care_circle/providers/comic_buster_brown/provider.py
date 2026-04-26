from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicBusterBrownProvider(WikimediaComicProvider):
    provider_key = "comic_buster_brown"
    comic_name = "Buster Brown"
    comic_author = "Richard F. Outcault"
    comic_license = "Public Domain"
    comic_attribution = "Richard F. Outcault, Buster Brown — Public Domain / Wikimedia Commons"
    wikimedia_category = "Buster_Brown"
    is_safe_for_patient = True