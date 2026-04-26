from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicPollyAndHerPalsProvider(WikimediaComicProvider):
    provider_key = "comic_polly_and_her_pals"
    comic_name = "Polly and Her Pals"
    comic_author = "Cliff Sterrett"
    comic_license = "Public Domain"
    comic_attribution = "Cliff Sterrett, Polly and Her Pals — Public Domain / Wikimedia Commons"
    wikimedia_category = "Polly_and_Her_Pals"
    is_safe_for_patient = True