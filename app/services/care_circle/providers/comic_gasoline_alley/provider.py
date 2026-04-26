from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicGasolineAlleyProvider(WikimediaComicProvider):
    provider_key = "comic_gasoline_alley"
    comic_name = "Gasoline Alley"
    comic_author = "Frank King"
    comic_license = "Public Domain"
    comic_attribution = "Frank King, Gasoline Alley — Public Domain / Wikimedia Commons"
    wikimedia_category = "Gasoline_Alley"
    is_safe_for_patient = True