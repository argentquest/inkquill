from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicMrSkygackProvider(WikimediaComicProvider):
    provider_key = "comic_mr_skygack"
    comic_name = "Mr. Skygack, from Mars"
    comic_author = "A.D. Condo"
    comic_license = "Public Domain"
    comic_attribution = "A.D. Condo, Mr. Skygack from Mars (1907) — Public Domain / Wikimedia Commons"
    wikimedia_category = "Mr._Skygack,_from_Mars"
    is_safe_for_patient = True
