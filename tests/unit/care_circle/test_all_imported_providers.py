import pytest
from app.services.care_circle.provider_base import BaseCareCircleProvider

def test_activity_suggestion_structure():
    from app.services.care_circle.providers.activity_suggestion.provider import ActivitySuggestionProvider
    provider = ActivitySuggestionProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_ai_trivia_structure():
    from app.services.care_circle.providers.ai_trivia.provider import AiTriviaProvider
    provider = AiTriviaProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_animal_friend_structure():
    from app.services.care_circle.providers.animal_friend.provider import AnimalFriendProvider
    provider = AnimalFriendProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_bingo_structure():
    from app.services.care_circle.providers.bingo.provider import BingoProvider
    provider = BingoProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_brain_booster_structure():
    from app.services.care_circle.providers.brain_booster.provider import BrainBoosterProvider
    provider = BrainBoosterProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_cat_fact_structure():
    from app.services.care_circle.providers.cat_fact.provider import CatFactProvider
    provider = CatFactProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_color_match_structure():
    from app.services.care_circle.providers.color_match.provider import ColorMatchProvider
    provider = ColorMatchProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_complete_the_duo_structure():
    from app.services.care_circle.providers.complete_the_duo.provider import CompleteTheDuoProvider
    provider = CompleteTheDuoProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_crossword_structure():
    from app.services.care_circle.providers.crossword.provider import CrosswordProvider
    provider = CrosswordProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_daily_affirmation_structure():
    from app.services.care_circle.providers.daily_affirmation.provider import DailyAffirmationProvider
    provider = DailyAffirmationProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_daily_blessing_structure():
    from app.services.care_circle.providers.daily_blessing.provider import DailyBlessingProvider
    provider = DailyBlessingProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_dog_photo_structure():
    from app.services.care_circle.providers.dog_photo.provider import DogPhotoProvider
    provider = DogPhotoProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_family_greeting_structure():
    from app.services.care_circle.providers.family_greeting.provider import FamilyGreetingProvider
    provider = FamilyGreetingProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_finish_phrase_structure():
    from app.services.care_circle.providers.finish_phrase.provider import FinishPhraseProvider
    provider = FinishPhraseProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_gentle_exercise_structure():
    from app.services.care_circle.providers.gentle_exercise.provider import GentleExerciseProvider
    provider = GentleExerciseProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_gratitude_structure():
    from app.services.care_circle.providers.gratitude.provider import GratitudeProvider
    provider = GratitudeProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_gridless_crossword_structure():
    from app.services.care_circle.providers.gridless_crossword.provider import GridlessCrosswordProvider
    provider = GridlessCrosswordProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_hobby_spotlight_structure():
    from app.services.care_circle.providers.hobby_spotlight.provider import HobbySpotlightProvider
    provider = HobbySpotlightProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_joke_structure():
    from app.services.care_circle.providers.joke.provider import JokeProvider
    provider = JokeProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_local_history_structure():
    from app.services.care_circle.providers.local_history.provider import LocalHistoryProvider
    provider = LocalHistoryProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_memory_lane_photo_structure():
    from app.services.care_circle.providers.memory_lane_photo.provider import MemoryLanePhotoProvider
    provider = MemoryLanePhotoProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_missing_vowels_structure():
    from app.services.care_circle.providers.missing_vowels.provider import MissingVowelsProvider
    provider = MissingVowelsProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_nature_scene_structure():
    from app.services.care_circle.providers.nature_scene.provider import NatureSceneProvider
    provider = NatureSceneProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_nostalgia_structure():
    from app.services.care_circle.providers.nostalgia.provider import NostalgiaProvider
    provider = NostalgiaProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_odd_one_out_structure():
    from app.services.care_circle.providers.odd_one_out.provider import OddOneOutProvider
    provider = OddOneOutProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_pen_pal_letter_structure():
    from app.services.care_circle.providers.pen_pal_letter.provider import PenPalLetterProvider
    provider = PenPalLetterProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_personal_affirmation_structure():
    from app.services.care_circle.providers.personal_affirmation.provider import PersonalAffirmationProvider
    provider = PersonalAffirmationProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_puzzle_structure():
    from app.services.care_circle.providers.puzzle.provider import PuzzleProvider
    provider = PuzzleProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_riddle_structure():
    from app.services.care_circle.providers.riddle.provider import RiddleProvider
    provider = RiddleProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_sensory_structure():
    from app.services.care_circle.providers.sensory.provider import SensoryProvider
    provider = SensoryProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_simple_math_structure():
    from app.services.care_circle.providers.simple_math.provider import SimpleMathProvider
    provider = SimpleMathProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_simple_recipe_structure():
    from app.services.care_circle.providers.simple_recipe.provider import SimpleRecipeProvider
    provider = SimpleRecipeProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_song_of_the_day_structure():
    from app.services.care_circle.providers.song_of_the_day.provider import SongOfTheDayProvider
    provider = SongOfTheDayProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_spot_the_difference_structure():
    from app.services.care_circle.providers.spot_the_difference.provider import SpotTheDifferenceProvider
    provider = SpotTheDifferenceProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_this_day_history_structure():
    from app.services.care_circle.providers.this_day_history.provider import ThisDayHistoryProvider
    provider = ThisDayHistoryProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_word_connect_structure():
    from app.services.care_circle.providers.word_connect.provider import WordConnectProvider
    provider = WordConnectProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_word_scramble_structure():
    from app.services.care_circle.providers.word_scramble.provider import WordScrambleProvider
    provider = WordScrambleProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

def test_world_news_structure():
    from app.services.care_circle.providers.world_news.provider import WorldNewsProvider
    provider = WorldNewsProvider()
    assert isinstance(provider, BaseCareCircleProvider)
    assert hasattr(provider, '_generate_payload')
    assert provider.is_safe_for_patient is True  # Patient-safe by contract

