from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicBrowniesProvider(WikimediaComicProvider):
    provider_key = "comic_brownies"
    comic_name = "The Brownies"
    comic_author = "Palmer Cox"
    comic_license = "Public Domain"
    comic_attribution = "Palmer Cox, The Brownies — Public Domain / Wikimedia Commons"
    wikimedia_category = "The_Brownies"
    is_safe_for_patient = True
