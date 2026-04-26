from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicDreamRarebitFiendProvider(WikimediaComicProvider):
    provider_key = "comic_dream_rarebit_fiend"
    comic_name = "Dream of the Rarebit Fiend"
    comic_author = "Winsor McCay"
    comic_license = "Public Domain"
    comic_attribution = "Winsor McCay, Dream of the Rarebit Fiend — Public Domain / Wikimedia Commons"
    wikimedia_category = "Dream_of_the_Rarebit_Fiend"
    is_safe_for_patient = True