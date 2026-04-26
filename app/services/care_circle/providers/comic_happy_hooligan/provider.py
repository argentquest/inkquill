from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicHappyHooliganProvider(WikimediaComicProvider):
    provider_key = "comic_happy_hooligan"
    comic_name = "Happy Hooligan"
    comic_author = "Frederick Burr Opper"
    comic_license = "Public Domain"
    comic_attribution = "Frederick Burr Opper, Happy Hooligan — Public Domain / Wikimedia Commons"
    wikimedia_category = "Happy_Hooligan"
    is_safe_for_patient = True