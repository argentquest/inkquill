from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicLittleNemoProvider(WikimediaComicProvider):
    provider_key = "comic_little_nemo"
    comic_name = "Little Nemo in Slumberland"
    comic_author = "Winsor McCay"
    comic_license = "Public Domain"
    comic_attribution = "Winsor McCay, Little Nemo in Slumberland — Public Domain / Wikimedia Commons"
    wikimedia_category = "Little_Nemo_in_Slumberland"
    is_safe_for_patient = True