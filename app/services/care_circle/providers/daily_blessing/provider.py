import random
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


class DailyBlessingProvider(BaseCareCircleProvider):
    provider_key = "daily_blessing"
    is_safe_for_patient = True

    """
    Provides a simple, warm blessing or prayer each day.
    Gentle and uplifting content for elderly users.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Get a daily blessing.
        
        Returns:
            dict with blessing text
        """
        cfg = self.patient_config
        
        blessings = cfg.get("blessings", [
            "May your day be filled with gentle joy and peaceful moments.",
            "You are a blessing to everyone who knows you.",
            "May the warmth of the sun bring a smile to your heart today.",
            "You are loved more than you know.",
            "Today is a gift. Enjoy every moment.",
            "May your heart be light and your spirit be calm.",
            "You bring so much happiness to those around you.",
            "May peace find you wherever you go today.",
            "Your smile makes the world a better place.",
            "You are stronger than you know and loved more than you realize.",
            "May this day bring you moments of quiet happiness.",
            "You are a treasure to your family and friends.",
            "Today, may you feel the warmth of love all around you.",
            "Every day with you is a blessing to us all.",
            "May your heart be filled with gratitude today.",
            "You make the world a kinder place just by being in it.",
            "May the simple pleasures of today bring you great joy.",
            "You are a shining light to everyone who loves you.",
            "Today, know that you are thought of with warmth and care.",
            "May your day be as wonderful as you are.",
            "May gentle breezes carry comfort to your doorstep today.",
            "You have brought light into so many lives throughout the years.",
            "May your morning coffee taste extra warm and comforting.",
            "The world is better because you are in it.",
            "May you find small beautiful moments throughout your day.",
            "Your kindness has rippled through many lives in wonderful ways.",
            "May today bring you reasons to smile and feel grateful.",
            "You deserve all the happiness that comes your way.",
            "May the songs of birds lift your spirits this fine day.",
            "Your gentle spirit has touched hearts far and wide.",
            "May you feel surrounded by love and warmth today.",
            "Every sunrise is a reminder that you are cared for deeply.",
            "May your footsteps be light and your heart be full.",
            "You have a special gift for making others feel welcome.",
            "May the flowers outside remind you of lifes beauty.",
            "Your presence brings comfort to everyone around you.",
            "May today hold sweet surprises and pleasant moments for you.",
            "You are remembered with fondness and deep appreciation.",
            "May the gentle rain wash away any worries you carry.",
            "Your life has been a beautiful story of love and care.",
            "May you feel the embrace of family and friends today.",
            "The little things in life are meant to bring you joy.",
            "May your day be wrapped in peace and contentment.",
            "You have given so much love to the world around you.",
            "May the stars tonight remind you of infinite possibilities.",
            "Your laughter is a melody that brightens every room.",
            "May you discover something new to be thankful for today.",
            "You are a precious soul who deserves every happiness.",
            "May the quiet moments today fill your heart with calm.",
            "Your wisdom and warmth inspire everyone you meet.",
            "May today be a gentle reminder of how blessed you are.",
            "You have planted seeds of kindness that continue to bloom.",
            "May the sunshine today warm your body and your spirit.",
            "Your gentle words have comforted many through the years.",
            "May you feel a deep sense of peace and belonging today.",
            "You are a wonderful person who brings light to others.",
            "May the beauty of nature lift your heart this fine day.",
            "Your life is a testament to love and enduring grace.",
            "May you be surrounded by all that brings you comfort.",
            "You have a heart of gold that shines brightly for all.",
            "May today bring you moments that make your soul sing.",
            "Your presence in this world is a true gift to us all.",
            "May the evening bring a peaceful close to a lovely day.",
            "You are cherished beyond words by those who know you.",
            "May every hour today bring you a reason to smile.",
            "Your life has been filled with beautiful memories to treasure.",
            "May you feel the gentle hand of care guiding your day.",
            "You are a beacon of warmth and love in this world.",
            "May the simple joys of life find you today and always.",
            "Your kind heart has made the world a better place.",
            "May you rest in the knowledge that you are deeply loved.",
            "You bring a special kind of magic to every gathering.",
            "May the dawn bring new hope and fresh beginnings today.",
            "Your gentle nature is a balm to weary souls everywhere.",
            "May you find comfort in the familiar and joy in the new.",
            "You are a wonderful blessing to all who cross your path.",
            "May the rhythm of the day bring you peace and happiness.",
            "Your loving spirit has created ripples of joy everywhere.",
            "May you feel wrapped in warmth and affection today.",
            "You are a beautiful soul who deserves all lifes blessings.",
            "May the day ahead be filled with gentle surprises and smiles.",
            "Your life is a tapestry woven with threads of love.",
            "May you discover moments of wonder and delight today.",
            "You are held in the highest regard by all who know you.",
            "May the comfort of home surround you with love today.",
            "Your generous heart has enriched so many lives around you.",
            "May you feel the gentle touch of grace in every moment.",
            "You are a treasured gift to this world and everyone in it.",
            "May the day unfold with beauty and peace at every turn.",
            "Your loving presence makes every place feel like home.",
            "May you be blessed with health and happiness today.",
            "You are a shining example of kindness and grace.",
            "May the warmth of friendship surround you always.",
            "Your beautiful spirit lights up the lives of others.",
            "May today bring you everything your heart desires.",
            "You are a wonderful blessing that we are all grateful for.",
        ])
        
        return {
            "blessing": random.choice(blessings)
        }
