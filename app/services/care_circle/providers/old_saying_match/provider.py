"""
Old Saying Match provider for Care Circle patient sessions.
Presents a familiar old saying and reveals its meaning — a gentle recognition activity.
Static provider — no LLM or external calls required.
"""

import random
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


SAYINGS = [
    {"saying": "Every cloud has a silver lining.", "meaning": "Even bad situations have some good in them."},
    {"saying": "A stitch in time saves nine.", "meaning": "Fixing a problem early prevents it from getting bigger."},
    {"saying": "The early bird catches the worm.", "meaning": "Those who start early have the best chance of success."},
    {"saying": "Don't judge a book by its cover.", "meaning": "Don't form an opinion based only on how something looks."},
    {"saying": "Two heads are better than one.", "meaning": "Working together is better than working alone."},
    {"saying": "Actions speak louder than words.", "meaning": "What you do matters more than what you say."},
    {"saying": "Better late than never.", "meaning": "It's better to do something late than not to do it at all."},
    {"saying": "You can't teach an old dog new tricks.", "meaning": "It's difficult to make older people change their habits."},
    {"saying": "Birds of a feather flock together.", "meaning": "People with similar interests tend to spend time together."},
    {"saying": "A penny saved is a penny earned.", "meaning": "Saving money is just as good as earning money."},
    {"saying": "Too many cooks spoil the broth.", "meaning": "Too many people involved in something can cause problems."},
    {"saying": "Look before you leap.", "meaning": "Think carefully before you act."},
    {"saying": "Rome wasn't built in a day.", "meaning": "Important things take time and effort."},
    {"saying": "The grass is always greener on the other side.", "meaning": "Other people's lives or situations always seem better than your own."},
    {"saying": "Don't put all your eggs in one basket.", "meaning": "Don't risk everything on a single plan or idea."},
    {"saying": "All that glitters is not gold.", "meaning": "Not everything that looks valuable or attractive really is."},
    {"saying": "A rolling stone gathers no moss.", "meaning": "People who keep moving don't get weighed down by responsibilities."},
    {"saying": "When in Rome, do as the Romans do.", "meaning": "Follow the customs of the place you are visiting."},
    {"saying": "The pen is mightier than the sword.", "meaning": "Written words and ideas have more power than violence."},
    {"saying": "Necessity is the mother of invention.", "meaning": "When you really need something, you find a way to create it."},
    {"saying": "You can lead a horse to water, but you can't make it drink.", "meaning": "You can give someone an opportunity, but you can't force them to take it."},
    {"saying": "Don't cry over spilt milk.", "meaning": "There's no point being upset over something that can't be changed."},
    {"saying": "A friend in need is a friend indeed.", "meaning": "A true friend helps you when you are in trouble."},
    {"saying": "Honesty is the best policy.", "meaning": "It is always better to be truthful."},
    {"saying": "Great minds think alike.", "meaning": "Clever people often come to the same conclusion independently."},
    {"saying": "Beggars can't be choosers.", "meaning": "If you need help, you should accept what is offered."},
    {"saying": "Practice makes perfect.", "meaning": "Doing something repeatedly helps you become very good at it."},
    {"saying": "Where there's smoke, there's fire.", "meaning": "If there are signs of a problem, there probably is one."},
    {"saying": "The squeaky wheel gets the grease.", "meaning": "The one who speaks up loudest gets the most attention."},
    {"saying": "It takes two to tango.", "meaning": "Both sides are equally responsible for a problem or situation."},
    {"saying": "You reap what you sow.", "meaning": "What you do comes back to you — good deeds bring good rewards."},
    {"saying": "Every dog has its day.", "meaning": "Everyone will have a moment of success or good fortune at some point."},
    {"saying": "Strike while the iron is hot.", "meaning": "Take advantage of a good opportunity while you can."},
    {"saying": "Don't bite the hand that feeds you.", "meaning": "Don't hurt the people who are helping or providing for you."},
    {"saying": "A fool and his money are soon parted.", "meaning": "People who are foolish with money tend to lose it quickly."},
    {"saying": "There's no place like home.", "meaning": "Home is the most comfortable and beloved place of all."},
    {"saying": "Good things come to those who wait.", "meaning": "Patience is rewarded in the end."},
    {"saying": "An apple a day keeps the doctor away.", "meaning": "Eating well keeps you healthy."},
    {"saying": "Laughter is the best medicine.", "meaning": "Humour and happiness help you feel better and stay healthy."},
    {"saying": "Time heals all wounds.", "meaning": "With time, even the deepest emotional pain will fade."},
    {"saying": "The proof of the pudding is in the eating.", "meaning": "The real value of something is only shown when it is tried."},
    {"saying": "Many hands make light work.", "meaning": "Tasks become easier when lots of people help."},
    {"saying": "Slow and steady wins the race.", "meaning": "Being consistent and patient leads to success."},
    {"saying": "Don't count your chickens before they hatch.", "meaning": "Don't assume you'll get something before you actually have it."},
    {"saying": "Every little helps.", "meaning": "Even small contributions are valuable."},
    # — second 45 —
    {"saying": "If it ain't broke, don't fix it.", "meaning": "Don't change something that is already working well."},
    {"saying": "You can't have your cake and eat it too.", "meaning": "You can't have two things that are incompatible at the same time."},
    {"saying": "The apple doesn't fall far from the tree.", "meaning": "Children often take after their parents."},
    {"saying": "Every man for himself.", "meaning": "In a difficult situation, each person must look after themselves."},
    {"saying": "Out of sight, out of mind.", "meaning": "When something or someone is not visible, it is easy to forget about them."},
    {"saying": "Absence makes the heart grow fonder.", "meaning": "Being away from someone makes you appreciate them more."},
    {"saying": "All's well that ends well.", "meaning": "A satisfactory outcome makes up for any difficulties along the way."},
    {"saying": "Barking up the wrong tree.", "meaning": "Pursuing a mistaken or misguided course of action."},
    {"saying": "Bite the bullet.", "meaning": "Endure a painful or difficult situation with courage."},
    {"saying": "Break the ice.", "meaning": "Do something to relieve tension or start a conversation."},
    {"saying": "Burning the midnight oil.", "meaning": "Working very late into the night."},
    {"saying": "Can't see the wood for the trees.", "meaning": "Being so focused on details that you miss the bigger picture."},
    {"saying": "Cutting corners.", "meaning": "Doing something the easy way, often sacrificing quality."},
    {"saying": "Don't burn your bridges.", "meaning": "Don't do something that would permanently damage a relationship or opportunity."},
    {"saying": "Easier said than done.", "meaning": "Something sounds straightforward but is actually quite difficult."},
    {"saying": "Fit as a fiddle.", "meaning": "In very good health."},
    {"saying": "Get out of bed on the wrong side.", "meaning": "To wake up in a bad mood."},
    {"saying": "Give someone the cold shoulder.", "meaning": "To deliberately ignore or be unfriendly to someone."},
    {"saying": "Go the extra mile.", "meaning": "Make a special effort; do more than is required."},
    {"saying": "Haste makes waste.", "meaning": "Acting too quickly often leads to mistakes."},
    {"saying": "Hit the nail on the head.", "meaning": "Describe something exactly right."},
    {"saying": "It takes a village to raise a child.", "meaning": "Many people must cooperate to ensure a child develops well."},
    {"saying": "Kill two birds with one stone.", "meaning": "Accomplish two things with a single action."},
    {"saying": "Let sleeping dogs lie.", "meaning": "Don't stir up trouble from the past."},
    {"saying": "Make hay while the sun shines.", "meaning": "Take advantage of favourable conditions while they last."},
    {"saying": "Miss the boat.", "meaning": "To miss an opportunity."},
    {"saying": "No news is good news.", "meaning": "If nothing has been heard, it probably means everything is fine."},
    {"saying": "Once in a blue moon.", "meaning": "Very rarely."},
    {"saying": "On the tip of my tongue.", "meaning": "Knowing something but being unable to recall it immediately."},
    {"saying": "Over the moon.", "meaning": "Extremely happy and delighted."},
    {"saying": "Pull someone's leg.", "meaning": "To joke or tease someone in a friendly way."},
    {"saying": "Put your best foot forward.", "meaning": "Make the best effort you can; present yourself favourably."},
    {"saying": "Raining cats and dogs.", "meaning": "Raining very heavily."},
    {"saying": "Rise and shine.", "meaning": "Wake up and be cheerful and active."},
    {"saying": "Rule of thumb.", "meaning": "A general principle based on experience rather than theory."},
    {"saying": "Sit on the fence.", "meaning": "Avoid taking sides in a dispute."},
    {"saying": "Spill the beans.", "meaning": "Reveal secret information, often accidentally."},
    {"saying": "Take it with a pinch of salt.", "meaning": "Don't believe something entirely; be slightly sceptical."},
    {"saying": "The ball is in your court.", "meaning": "It is now your responsibility to act or decide."},
    {"saying": "The best of both worlds.", "meaning": "Enjoying two different advantages at the same time."},
    {"saying": "Through thick and thin.", "meaning": "Under all circumstances, both good and bad."},
    {"saying": "Tie the knot.", "meaning": "Get married."},
    {"saying": "Under the weather.", "meaning": "Feeling slightly ill."},
    {"saying": "We'll cross that bridge when we come to it.", "meaning": "Deal with a problem when it arises, not before."},
]


class OldSayingMatchProvider(BaseCareCircleProvider):
    provider_key = "old_saying_match"
    is_safe_for_patient = True

    """
    Presents a familiar old saying and its meaning — a gentle recognition and recall activity.
    Pure static provider — 45 classic sayings with meanings in the curated pool.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pool = cfg.get("sayings", SAYINGS)
        entry = random.choice(pool)
        return {
            "saying": entry["saying"],
            "meaning": entry["meaning"],
        }
