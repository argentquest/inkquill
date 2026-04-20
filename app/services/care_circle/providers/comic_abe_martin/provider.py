from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicAbeMartinProvider(WikimediaComicProvider):
    provider_key = "comic_abe_martin"
    comic_name = "Abe Martin"
    comic_author = "Kin Hubbard"
    comic_license = "Public Domain"
    comic_attribution = "Kin Hubbard, Abe Martin — Public Domain / Wikimedia Commons"
    wikimedia_category = "Abe_Martin_(comic_strip)"
    is_safe_for_patient = True
