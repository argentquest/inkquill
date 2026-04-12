"""
Number Sequence provider for Care Circle patient sessions.
Delivers a gentle number pattern puzzle from a curated pool.
Static provider — no LLM or external calls required.
"""

import random
import logging
from typing import Any, Dict

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


SEQUENCES = [
    # Counting / skip-counting
    {"question": "2, 4, 6, 8, ___?", "answer": "10", "hint": "Count by 2s."},
    {"question": "5, 10, 15, 20, ___?", "answer": "25", "hint": "Count by 5s."},
    {"question": "10, 20, 30, 40, ___?", "answer": "50", "hint": "Count by 10s."},
    {"question": "3, 6, 9, 12, ___?", "answer": "15", "hint": "Count by 3s."},
    {"question": "1, 3, 5, 7, ___?", "answer": "9", "hint": "These are odd numbers."},
    {"question": "2, 4, 8, 16, ___?", "answer": "32", "hint": "Each number is doubled."},
    {"question": "100, 90, 80, 70, ___?", "answer": "60", "hint": "Count backwards by 10s."},
    {"question": "50, 45, 40, 35, ___?", "answer": "30", "hint": "Count backwards by 5s."},
    {"question": "1, 2, 4, 7, 11, ___?", "answer": "16", "hint": "Add 1, then 2, then 3, then 4, then 5."},
    {"question": "0, 1, 1, 2, 3, 5, ___?", "answer": "8", "hint": "Add the two numbers before it (Fibonacci!)."},
    # Addition patterns
    {"question": "4, 8, 12, 16, ___?", "answer": "20", "hint": "Count by 4s."},
    {"question": "7, 14, 21, 28, ___?", "answer": "35", "hint": "Count by 7s."},
    {"question": "11, 22, 33, 44, ___?", "answer": "55", "hint": "Count by 11s."},
    {"question": "25, 50, 75, 100, ___?", "answer": "125", "hint": "Count by 25s."},
    {"question": "1, 4, 9, 16, ___?", "answer": "25", "hint": "These are square numbers: 1×1, 2×2, 3×3..."},
    # Subtraction / countdown
    {"question": "20, 17, 14, 11, ___?", "answer": "8", "hint": "Take away 3 each time."},
    {"question": "30, 25, 20, 15, ___?", "answer": "10", "hint": "Take away 5 each time."},
    {"question": "64, 32, 16, 8, ___?", "answer": "4", "hint": "Each number is halved."},
    # Calendar / clock themed
    {"question": "January, February, March, ___?", "answer": "April", "hint": "These are months of the year."},
    {"question": "Monday, Tuesday, Wednesday, ___?", "answer": "Thursday", "hint": "These are days of the week."},
    {"question": "3 o'clock, 6 o'clock, 9 o'clock, ___?", "answer": "12 o'clock", "hint": "Count forward by 3 hours."},
    # Simple multiplication patterns
    {"question": "2, 6, 18, 54, ___?", "answer": "162", "hint": "Multiply by 3 each time."},
    {"question": "1, 2, 4, 8, 16, ___?", "answer": "32", "hint": "Double each time."},
    # Mixed easy
    {"question": "10, 8, 6, 4, ___?", "answer": "2", "hint": "Count backwards by 2s."},
    {"question": "15, 20, 25, 30, ___?", "answer": "35", "hint": "Count by 5s."},
    {"question": "1, 10, 100, 1000, ___?", "answer": "10000", "hint": "Multiply by 10 each time."},
    {"question": "99, 88, 77, 66, ___?", "answer": "55", "hint": "Take away 11 each time."},
    {"question": "2, 3, 5, 8, 13, ___?", "answer": "21", "hint": "Add the two before it together."},
    {"question": "Spring, Summer, Autumn, ___?", "answer": "Winter", "hint": "These are the seasons of the year."},
    {"question": "12, 24, 36, 48, ___?", "answer": "60", "hint": "Count by 12s — like hours on a clock!"},
    # More arithmetic
    {"question": "6, 12, 18, 24, ___?", "answer": "30", "hint": "Count by 6s."},
    {"question": "8, 16, 24, 32, ___?", "answer": "40", "hint": "Count by 8s."},
    {"question": "9, 18, 27, 36, ___?", "answer": "45", "hint": "Count by 9s."},
    {"question": "20, 40, 60, 80, ___?", "answer": "100", "hint": "Count by 20s."},
    {"question": "1, 3, 6, 10, 15, ___?", "answer": "21", "hint": "Add 2, then 3, then 4, then 5, then 6."},
    {"question": "4, 7, 10, 13, ___?", "answer": "16", "hint": "Add 3 each time."},
    {"question": "5, 9, 13, 17, ___?", "answer": "21", "hint": "Add 4 each time."},
    {"question": "2, 5, 10, 17, 26, ___?", "answer": "37", "hint": "Add 3, then 5, then 7, then 9, then 11."},
    {"question": "1, 8, 27, 64, ___?", "answer": "125", "hint": "These are cube numbers: 1×1×1, 2×2×2, 3×3×3..."},
    {"question": "36, 30, 24, 18, ___?", "answer": "12", "hint": "Take away 6 each time."},
    {"question": "40, 32, 24, 16, ___?", "answer": "8", "hint": "Take away 8 each time."},
    {"question": "200, 100, 50, 25, ___?", "answer": "12.5", "hint": "Halved each time."},
    {"question": "1000, 500, 250, 125, ___?", "answer": "62.5", "hint": "Divide by 2 each time."},
    {"question": "3, 9, 27, 81, ___?", "answer": "243", "hint": "Multiply by 3 each time."},
    {"question": "5, 25, 125, 625, ___?", "answer": "3125", "hint": "Multiply by 5 each time."},
    {"question": "4, 16, 64, 256, ___?", "answer": "1024", "hint": "Multiply by 4 each time."},
    # Money / coins
    {"question": "1¢, 5¢, 10¢, 25¢, ___?", "answer": "50¢", "hint": "These are coin values: penny, nickel, dime, quarter, half-dollar!"},
    {"question": "$1, $2, $5, $10, ___?", "answer": "$20", "hint": "These are US bill denominations."},
    {"question": "5¢, 10¢, 15¢, 20¢, ___?", "answer": "25¢", "hint": "Count by 5 cents."},
    {"question": "$0.25, $0.50, $0.75, $1.00, ___?", "answer": "$1.25", "hint": "Count up by 25 cents each time."},
    # Time themed
    {"question": "1 minute, 5 minutes, 10 minutes, 15 minutes, ___?", "answer": "20 minutes", "hint": "Add 5 minutes at a time."},
    {"question": "2:00, 4:00, 6:00, 8:00, ___?", "answer": "10:00", "hint": "Add 2 hours each time."},
    {"question": "1:00, 1:15, 1:30, 1:45, ___?", "answer": "2:00", "hint": "Add 15 minutes each time."},
    {"question": "January, March, May, July, ___?", "answer": "September", "hint": "Every other month of the year."},
    {"question": "Sunday, Tuesday, Thursday, ___?", "answer": "Saturday", "hint": "Every other day of the week."},
    # Shape / letters
    {"question": "A, C, E, G, ___?", "answer": "I", "hint": "Every other letter of the alphabet."},
    {"question": "Z, Y, X, W, ___?", "answer": "V", "hint": "The alphabet going backward."},
    {"question": "A, B, D, G, K, ___?", "answer": "P", "hint": "Add 1, then 2, then 3, then 4, then 5 letters."},
    {"question": "1 side, 2 sides, 3 sides, 4 sides — what comes next for a pentagon?", "answer": "5 sides", "hint": "Count the sides of shapes: line, angle, triangle, square, pentagon."},
    # Real-world themed
    {"question": "1 dozen, 2 dozen, 3 dozen, ___?", "answer": "4 dozen (48 items)", "hint": "A dozen = 12. Count by dozens!"},
    {"question": "Newborn, 1 year, 5 years, 10 years, ___?", "answer": "20 years", "hint": "Common age milestones doubled."},
    {"question": "1st, 2nd, 3rd, 4th, ___?", "answer": "5th", "hint": "Counting positions — ordinal numbers."},
    {"question": "Sunrise, Morning, Noon, Afternoon, ___?", "answer": "Evening", "hint": "The parts of the day in order."},
    {"question": "1 cup, 2 cups, 1 pint, ___?", "answer": "1 quart", "hint": "Measuring liquids: 2 cups = 1 pint, 2 pints = 1 quart."},
    # Greater gaps / patterns
    {"question": "2, 4, 8, 16, 32, ___?", "answer": "64", "hint": "Keep doubling."},
    {"question": "81, 27, 9, 3, ___?", "answer": "1", "hint": "Divide by 3 each time."},
    {"question": "1, 1, 2, 3, 5, 8, 13, ___?", "answer": "21", "hint": "Fibonacci! Add the two numbers before."},
    {"question": "10, 9, 7, 4, ___?", "answer": "0", "hint": "Take away 1, then 2, then 3, then 4."},
    {"question": "1, 4, 9, 16, 25, ___?", "answer": "36", "hint": "Square numbers: 1², 2², 3², 4², 5², 6²"},
    # Simple addition pyramids
    {"question": "2 + 2 = 4; 4 + 4 = 8; 8 + 8 = ___?", "answer": "16", "hint": "Keep doubling the answer."},
    {"question": "3 + 3 = 6; 6 + 6 = 12; 12 + 12 = ___?", "answer": "24", "hint": "Each answer is doubled again."},
    # Mixed word-based
    {"question": "One, Two, Three, Four, ___?", "answer": "Five", "hint": "Simply count!"},
    {"question": "Ten, Twenty, Thirty, Forty, ___?", "answer": "Fifty", "hint": "Count by tens."},
    {"question": "Hundred, Two Hundred, Three Hundred, ___?", "answer": "Four Hundred", "hint": "Count by hundreds."},
    {"question": "First, Second, Third, Fourth, ___?", "answer": "Fifth", "hint": "Ordinal numbers in sequence."},
    {"question": "Once, Twice, Three times, ___?", "answer": "Four times", "hint": "How many times you do something."},
    {"question": "Breakfast, Lunch, ___?", "answer": "Dinner (or Supper)", "hint": "The three meals of the day!"},
    {"question": "Egg, Chick, Hen, ___?", "answer": "Grandmother Hen (or back to Egg)", "hint": "The life cycle of a chicken."},
    # Long sequences
    {"question": "5, 6, 8, 11, 15, ___?", "answer": "20", "hint": "Add 1, then 2, then 3, then 4, then 5."},
    {"question": "100, 95, 85, 70, 50, ___?", "answer": "25", "hint": "Take away 5, then 10, then 15, then 20, then 25."},
    {"question": "2, 3, 5, 7, 11, 13, ___?", "answer": "17", "hint": "These are prime numbers!"},
    {"question": "4, 5, 7, 10, 14, ___?", "answer": "19", "hint": "Add 1, then 2, then 3, then 4, then 5."},
    {"question": "1, 2, 6, 24, 120, ___?", "answer": "720", "hint": "Multiply by 2, then 3, then 4, then 5, then 6 (factorials!)."},
    # Gentle challenge
    {"question": "What is half of 100?", "answer": "50", "hint": "Split 100 into two equal parts."},
    {"question": "What is double 25?", "answer": "50", "hint": "Add 25 + 25."},
    {"question": "What is 10 + 10 + 10?", "answer": "30", "hint": "Count three groups of 10."},
    {"question": "What is 100 ÷ 4?", "answer": "25", "hint": "Split 100 into four equal parts."},
    {"question": "If you have 3 groups of 7, how many do you have in total?", "answer": "21", "hint": "3 × 7 = ?"},
    {"question": "What is 50 + 25 + 25?", "answer": "100", "hint": "A handy one — think of quarters and a dollar!"},
    # Fractions (simple)
    {"question": "1/2, 1/4, 1/8, ___?", "answer": "1/16", "hint": "Each fraction is half the one before."},
    {"question": "1/4, 2/4, 3/4, ___?", "answer": "4/4 (or 1 whole)", "hint": "Count up by quarter pieces."},
    # Shapes and geometry
    {"question": "Triangle has 3 corners; Square has 4; Pentagon has 5; Hexagon has ___?", "answer": "6 corners", "hint": "Count the corners of each shape."},
    # Counting in groups
    {"question": "1 week, 2 weeks, 3 weeks, ___?", "answer": "4 weeks (1 month)", "hint": "Four weeks make roughly one month."},
    {"question": "12 months = 1 year; 24 months = 2 years; 36 months = ___?", "answer": "3 years", "hint": "Count by groups of 12 months."},
    {"question": "365 days = 1 year; 730 days = 2 years; 1095 days = ___?", "answer": "3 years", "hint": "Count groups of 365 days."},
    # Pop culture light
    {"question": "The 12 days of Christmas: Day 1, Day 2, … Day 12 gives how many total gifts?", "answer": "78 gifts", "hint": "Add 1+2+3+4+5+6+7+8+9+10+11+12!"},
    {"question": "There are 7 days in a week. How many days in 4 weeks?", "answer": "28 days", "hint": "7 × 4 = ?"},
    {"question": "A baker's dozen is 13. Two baker's dozens = ___?", "answer": "26", "hint": "13 + 13 = ?"},
    # Seasons and nature
    {"question": "4 seasons in a year; 8 seasons in 2 years; ___?", "answer": "12 seasons in 3 years", "hint": "Multiply 4 by the number of years."},
    {"question": "A day has 24 hours; half a day has ___?", "answer": "12 hours", "hint": "Halve 24."},
    {"question": "An hour has 60 minutes; half an hour has ___?", "answer": "30 minutes", "hint": "Halve 60."},
    {"question": "A minute has 60 seconds; a quarter-minute has ___?", "answer": "15 seconds", "hint": "Divide 60 by 4."},
    # Roman numerals (simplified)
    {"question": "I, II, III, IV, ___?", "answer": "V", "hint": "Roman numerals! I=1, II=2, III=3, IV=4, V=5."},
    {"question": "V, X, L, C, ___?", "answer": "D", "hint": "Roman numerals for 5, 10, 50, 100 — next is 500!"},
    # Playful / trivia
    {"question": "How many sides does a stop sign have?", "answer": "8 (an octagon)", "hint": "Count the sides next time you see one!"},
    {"question": "How many strings does a standard guitar have?", "answer": "6", "hint": "Think of the music you have heard."},
    {"question": "How many players are on a standard basketball team on the court?", "answer": "5", "hint": "Five play at a time for each team."},
    {"question": "How many zeros are in one million?", "answer": "6 zeros", "hint": "1,000,000 — count the zeros."},
    {"question": "How many teeth does a healthy adult have?", "answer": "32", "hint": "Including the four wisdom teeth."},
    {"question": "How many hours are in a full day and night?", "answer": "24 hours", "hint": "Day + night together = one full day."},
    {"question": "If you count to 10 three times, what number do you reach?", "answer": "30", "hint": "10 + 10 + 10 = ?"},
    {"question": "A spider has 8 legs; 3 spiders have ___?", "answer": "24 legs", "hint": "8 × 3 = ?"},
]


class NumberSequenceProvider(BaseCareCircleProvider):
    provider_key = "number_sequence"
    is_safe_for_patient = True

    """
    Presents a gentle number (or pattern) sequence puzzle from a curated pool.
    Pure static provider — 30 puzzles ranging from counting to Fibonacci-style.
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        pool = cfg.get("sequences", SEQUENCES)
        entry = random.choice(pool)
        return {
            "question": entry["question"],
            "answer": entry["answer"],
            "hint": entry.get("hint", ""),
        }
