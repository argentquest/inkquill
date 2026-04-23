"""
Word of the Day provider for Care Circle patient sessions.
Delivers a vocabulary enrichment card from a large curated pool.
Static provider — no LLM or external calls required.
"""

import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.variety_utils import date_seeded_choice

logger = logging.getLogger(__name__)


WORDS = [
    {"word": "Serene", "part_of_speech": "adjective", "definition": "Calm, peaceful, and untroubled.", "example": "The lake looked serene in the early morning light."},
    {"word": "Jubilant", "part_of_speech": "adjective", "definition": "Feeling or expressing great happiness and triumph.", "example": "The crowd was jubilant when the team won."},
    {"word": "Wanderlust", "part_of_speech": "noun", "definition": "A strong desire to travel and explore the world.", "example": "Her wanderlust led her to visit dozens of countries."},
    {"word": "Cozy", "part_of_speech": "adjective", "definition": "Warm, comfortable, and snug.", "example": "They sat by the cozy fireplace on a cold winter evening."},
    {"word": "Radiant", "part_of_speech": "adjective", "definition": "Sending out light or glowing with happiness.", "example": "She had a radiant smile that lit up the whole room."},
    {"word": "Cherish", "part_of_speech": "verb", "definition": "To hold something dear and protect it lovingly.", "example": "He cherished every photograph from his childhood."},
    {"word": "Dazzle", "part_of_speech": "verb", "definition": "To greatly impress or astonish someone.", "example": "The fireworks display dazzled everyone watching."},
    {"word": "Meander", "part_of_speech": "verb", "definition": "To wander in a leisurely, relaxed way.", "example": "We meandered through the flower garden all afternoon."},
    {"word": "Whimsy", "part_of_speech": "noun", "definition": "Playful or fanciful behaviour; something delightfully quirky.", "example": "The garden was full of whimsy, with funny little statues everywhere."},
    {"word": "Tranquil", "part_of_speech": "adjective", "definition": "Free from disturbance; calm and quiet.", "example": "The tranquil countryside made everyone feel at ease."},
    {"word": "Gleam", "part_of_speech": "verb", "definition": "To shine brightly, especially with a reflected light.", "example": "Her eyes gleamed with delight when she saw the birthday cake."},
    {"word": "Bountiful", "part_of_speech": "adjective", "definition": "Large in quantity; generously plentiful.", "example": "The garden produced a bountiful harvest of tomatoes."},
    {"word": "Lullaby", "part_of_speech": "noun", "definition": "A gentle song sung to help a child fall asleep.", "example": "Her grandmother always sang a soft lullaby at bedtime."},
    {"word": "Frolic", "part_of_speech": "verb", "definition": "To play and move about cheerfully.", "example": "The lambs frolicked in the green meadow."},
    {"word": "Nostalgia", "part_of_speech": "noun", "definition": "A wistful longing for the happy times of the past.", "example": "Looking through old photos filled her with warm nostalgia."},
    {"word": "Vivid", "part_of_speech": "adjective", "definition": "Producing powerful feelings or strong, clear images in the mind.", "example": "He had vivid memories of his grandmother's kitchen."},
    {"word": "Tender", "part_of_speech": "adjective", "definition": "Gentle and caring; showing love and kindness.", "example": "She gave her grandchild a tender hug."},
    {"word": "Twinkle", "part_of_speech": "verb", "definition": "To shine with a flickering or sparkling light.", "example": "Stars twinkled in the clear night sky."},
    {"word": "Mellow", "part_of_speech": "adjective", "definition": "Pleasantly smooth or soft; relaxed and gentle.", "example": "The mellow music in the cafe made everyone feel relaxed."},
    {"word": "Lively", "part_of_speech": "adjective", "definition": "Full of life and energy; active and spirited.", "example": "The town square was lively with music and dancing."},
    {"word": "Kindle", "part_of_speech": "verb", "definition": "To inspire or arouse a feeling or emotion.", "example": "Old songs can kindle warm memories from long ago."},
    {"word": "Splendid", "part_of_speech": "adjective", "definition": "Magnificent and impressively beautiful.", "example": "They watched the splendid sunset from the porch."},
    {"word": "Saunter", "part_of_speech": "verb", "definition": "To walk in a slow, relaxed manner without hurry.", "example": "He sauntered down the lane enjoying the morning air."},
    {"word": "Bloom", "part_of_speech": "verb", "definition": "To produce flowers; to grow and flourish.", "example": "The roses began to bloom in early June."},
    {"word": "Comfort", "part_of_speech": "noun", "definition": "A state of ease and freedom from pain or worry.", "example": "A warm cup of tea is always a great comfort."},
    {"word": "Enchant", "part_of_speech": "verb", "definition": "To fill someone with delight and wonder.", "example": "The children were enchanted by the magician's tricks."},
    {"word": "Hearty", "part_of_speech": "adjective", "definition": "Warm, enthusiastic, and sincere.", "example": "Everyone gave a hearty laugh at the funny story."},
    {"word": "Ponder", "part_of_speech": "verb", "definition": "To think about something carefully for a long time.", "example": "She sat by the window and pondered happy memories."},
    {"word": "Wondrous", "part_of_speech": "adjective", "definition": "Inspiring wonder or admiration; marvellous.", "example": "The spring flowers were simply wondrous to behold."},
    {"word": "Dapper", "part_of_speech": "adjective", "definition": "Neat and trim in appearance; smartly dressed.", "example": "He looked very dapper in his Sunday suit and hat."},
    {"word": "Linger", "part_of_speech": "verb", "definition": "To stay somewhere a little longer than expected, enjoying it.", "example": "They lingered over afternoon tea for nearly two hours."},
    {"word": "Savour", "part_of_speech": "verb", "definition": "To enjoy something slowly and completely.", "example": "She savoured every bite of her favourite apple pie."},
    {"word": "Sprightly", "part_of_speech": "adjective", "definition": "Full of energy and cheerfulness despite one's age.", "example": "The sprightly grandmother danced at the family party."},
    {"word": "Amble", "part_of_speech": "verb", "definition": "To walk at a slow, easy pace.", "example": "They ambled through the park on a sunny afternoon."},
    {"word": "Gentle", "part_of_speech": "adjective", "definition": "Kind, mild, and soft in nature.", "example": "A gentle breeze rustled through the apple trees."},
    {"word": "Brighten", "part_of_speech": "verb", "definition": "To make or become more cheerful or lighter.", "example": "Her laugh always brightened the whole room."},
    {"word": "Nourish", "part_of_speech": "verb", "definition": "To give something what it needs to grow and be healthy.", "example": "Good food and good company nourish both body and soul."},
    {"word": "Timeless", "part_of_speech": "adjective", "definition": "Not affected by the passage of time; always relevant.", "example": "Their love for each other was timeless and beautiful."},
    {"word": "Flutter", "part_of_speech": "verb", "definition": "To move lightly and rapidly; to wave gently.", "example": "Butterflies fluttered from flower to flower in the garden."},
    {"word": "Gracious", "part_of_speech": "adjective", "definition": "Courteous, kind, and pleasant in a dignified way.", "example": "She was a gracious host who made everyone feel welcome."},
    # — second 40 —
    {"word": "Placid", "part_of_speech": "adjective", "definition": "Not easily upset; calm and peaceful.", "example": "The placid lake reflected the colours of the evening sky."},
    {"word": "Jovial", "part_of_speech": "adjective", "definition": "Cheerful and friendly.", "example": "He was a jovial man who always had a kind word for everyone."},
    {"word": "Earnest", "part_of_speech": "adjective", "definition": "Sincere and serious in intention.", "example": "She made an earnest effort to help her neighbour every week."},
    {"word": "Felicity", "part_of_speech": "noun", "definition": "Intense happiness; great good fortune.", "example": "The birth of a grandchild brought her a sense of pure felicity."},
    {"word": "Reverie", "part_of_speech": "noun", "definition": "A state of pleasant daydreaming.", "example": "She sat by the window, lost in a warm reverie of summer days past."},
    {"word": "Steadfast", "part_of_speech": "adjective", "definition": "Resolutely firm and unwavering.", "example": "His steadfast love for his family never faltered over the years."},
    {"word": "Solace", "part_of_speech": "noun", "definition": "Comfort or consolation in a time of sadness.", "example": "A warm cup of tea and a good book always brought her solace."},
    {"word": "Blithe", "part_of_speech": "adjective", "definition": "Happily carefree; joyfully light-hearted.", "example": "The children's blithe laughter filled the garden all afternoon."},
    {"word": "Halcyon", "part_of_speech": "adjective", "definition": "Denoting a period of great happiness and prosperity.", "example": "She often thought back to those halcyon days by the seaside."},
    {"word": "Cordial", "part_of_speech": "adjective", "definition": "Warm and friendly; heartfelt.", "example": "They exchanged cordial greetings and sat down for tea together."},
    {"word": "Pristine", "part_of_speech": "adjective", "definition": "In its original condition; perfectly clean and fresh.", "example": "The garden looked pristine after the morning rain."},
    {"word": "Resplendent", "part_of_speech": "adjective", "definition": "Attractive and impressive through being richly colourful.", "example": "The autumn trees were resplendent in shades of gold and red."},
    {"word": "Genial", "part_of_speech": "adjective", "definition": "Friendly and cheerful.", "example": "The genial baker greeted each customer with a warm smile."},
    {"word": "Verdant", "part_of_speech": "adjective", "definition": "Green with grass or other rich vegetation.", "example": "They walked through a verdant valley on a fine spring morning."},
    {"word": "Pensive", "part_of_speech": "adjective", "definition": "Engaged in, involving, or reflecting deep or serious thought.", "example": "She sat in a pensive mood, smiling at the memories of years gone by."},
    {"word": "Abundance", "part_of_speech": "noun", "definition": "A very large quantity of something; plenty.", "example": "The garden produced an abundance of fruit that summer."},
    {"word": "Serene", "part_of_speech": "adjective", "definition": "Calm, peaceful, and untroubled.", "example": "The early morning countryside looked absolutely serene."},
    {"word": "Gratitude", "part_of_speech": "noun", "definition": "The quality of being thankful.", "example": "She expressed her gratitude with a heartfelt letter to her neighbour."},
    {"word": "Radiance", "part_of_speech": "noun", "definition": "Light or heat as emitted or reflected by something; great happiness.", "example": "There was a warm radiance about her whenever she spoke of her family."},
    {"word": "Nimble", "part_of_speech": "adjective", "definition": "Quick and light in movement; agile.", "example": "Her fingers were still nimble enough to knit the most beautiful patterns."},
    {"word": "Delight", "part_of_speech": "noun", "definition": "Great pleasure; something that gives great pleasure.", "example": "The smell of fresh bread was an absolute delight every morning."},
    {"word": "Dauntless", "part_of_speech": "adjective", "definition": "Showing fearlessness and determination.", "example": "She was a dauntless woman who faced every challenge with a smile."},
    {"word": "Amber", "part_of_speech": "noun", "definition": "A warm golden-yellow colour.", "example": "The afternoon sun turned the fields a beautiful shade of amber."},
    {"word": "Brisk", "part_of_speech": "adjective", "definition": "Active, fast, and full of energy.", "example": "A brisk morning walk always left her feeling wonderful."},
    {"word": "Elate", "part_of_speech": "verb", "definition": "To make someone very happy and proud.", "example": "The news of the new grandchild elated the whole family."},
    {"word": "Tranquility", "part_of_speech": "noun", "definition": "The quality or state of being calm and free from disturbance.", "example": "The tranquility of the countryside never failed to soothe her soul."},
    {"word": "Beaming", "part_of_speech": "adjective", "definition": "Radiating warmth and happiness; smiling broadly.", "example": "She walked into the room beaming with pride and joy."},
    {"word": "Homely", "part_of_speech": "adjective", "definition": "Comfortable and cosy; simple but pleasantly familiar.", "example": "The cottage had a wonderfully homely feel that put everyone at ease."},
    {"word": "Luminous", "part_of_speech": "adjective", "definition": "Full of or shedding light; bright and shining.", "example": "The full moon was luminous over the peaceful garden."},
    {"word": "Robust", "part_of_speech": "adjective", "definition": "Strong and healthy; vigorous.", "example": "Despite his years, he remained robust and full of good humour."},
    {"word": "Idyllic", "part_of_speech": "adjective", "definition": "Like an idyll; extremely happy, peaceful, or picturesque.", "example": "They spent an idyllic afternoon by the river with their grandchildren."},
    {"word": "Zeal", "part_of_speech": "noun", "definition": "Great energy or enthusiasm in pursuit of something.", "example": "She approached her gardening with the same zeal she always had."},
    {"word": "Fond", "part_of_speech": "adjective", "definition": "Having an affection or liking for; cherishing.", "example": "He was fond of a good story and told them brilliantly."},
    {"word": "Serenity", "part_of_speech": "noun", "definition": "The state of being calm, peaceful, and untroubled.", "example": "The sound of the rain brought a wonderful serenity to the room."},
    {"word": "Wholesome", "part_of_speech": "adjective", "definition": "Conducive to health or well-being; good and clean.", "example": "A wholesome meal shared with family is one of life's great pleasures."},
    {"word": "Invigorate", "part_of_speech": "verb", "definition": "To give strength or energy to.", "example": "The fresh morning air always invigorated her for the day ahead."},
    {"word": "Cherished", "part_of_speech": "adjective", "definition": "Held very dear; greatly loved.", "example": "The old photograph was a cherished reminder of happy times together."},
    {"word": "Dew", "part_of_speech": "noun", "definition": "Tiny drops of water that form on surfaces overnight.", "example": "The morning dew sparkled on the roses like tiny diamonds."},
    {"word": "Warmth", "part_of_speech": "noun", "definition": "A quality of friendliness and affection; gentle heat.", "example": "The warmth of the fire and good company made the evening perfect."},
    {"word": "Youthful", "part_of_speech": "adjective", "definition": "Remaining young in spirit; lively and fresh.", "example": "Her youthful spirit meant she was always the first on the dance floor."},
]


class WordOfTheDayProvider(BaseCareCircleProvider):
    provider_key = "word_of_the_day"
    is_safe_for_patient = True

    """
    Delivers a vocabulary enrichment card with a word, its definition, and an example.
    Pure static provider drawn from a curated pool of 40 warm, positive words.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pool = cfg.get("words", WORDS)
        entry = date_seeded_choice(pool, self.get_generation_date())
        return {
            "word": entry["word"],
            "part_of_speech": entry["part_of_speech"],
            "definition": entry["definition"],
            "example": entry["example"],
        }
