from app.services.care_circle.comic_base_provider import WikimediaComicProvider


class ComicDinoCartoonsProvider(WikimediaComicProvider):
    provider_key = "comic_dino_cartoons"
    comic_name = "Dinosaur Cartoons"
    comic_author = "Various Artists"
    comic_license = "CC / Public Domain"
    comic_attribution = "Dinosaur cartoon — Wikimedia Commons (see source for individual licence)"
    wikimedia_category = "Dinosaurs_in_art"
    is_safe_for_patient = True
