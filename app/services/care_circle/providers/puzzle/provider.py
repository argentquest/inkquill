import random
from word_search_generator import WordSearch
import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


def _render_word_search(words: list, grid: list) -> str:
    word_list = ", ".join(words)
    rows_html = ""
    for row in grid:
        cells = "".join(
            '<td class="puzzle-word-search__cell">'
            f'{cell if cell else "&nbsp;"}</td>'
            for cell in row
        )
        rows_html += f"<tr>{cells}</tr>"
    return (
        f'<p class="puzzle-word-search__prompt">'
        f"Find: {word_list}</p>"
        f'<table class="puzzle-grid puzzle-grid--word-search">'
        f"{rows_html}</table>"
    )


def _render_fill_in_the_blank(phrase: str, answer: str) -> str:
    return (
        f'<p class="puzzle-fill-blank__phrase">{phrase}</p>'
        f'<details class="puzzle-answer-reveal">'
        f'<summary class="puzzle-answer-reveal__summary">Show answer</summary>'
        f'<p class="puzzle-answer-reveal__content">'
        f"{answer}</p></details>"
    )


def _render_word_pair(across: str, down: str, clues: dict, grid: list) -> str:
    rows_html = ""
    for r, row in enumerate(grid):
        cells = ""
        for c, ch in enumerate(row):
            if ch:
                cells += (
                    f'<td class="puzzle-word-pair__cell">{ch}</td>'
                )
            else:
                cells += '<td class="puzzle-word-pair__block"></td>'
        rows_html += f"<tr>{cells}</tr>"

    clue_across = clues.get("Across", "")
    clue_down = clues.get("Down", "")
    return (
        f'<table class="puzzle-grid puzzle-grid--word-pair">'
        f"{rows_html}</table>"
        f'<p class="puzzle-word-pair__clue">'
        f"<strong>→ Across:</strong> {clue_across}</p>"
        f'<p class="puzzle-word-pair__clue">'
        f"<strong>↓ Down:</strong> {clue_down}</p>"
        f'<details class="puzzle-answer-reveal">'
        f'<summary class="puzzle-answer-reveal__summary">Show answers</summary>'
        f'<p class="puzzle-answer-reveal__content">'
        f"<strong>Across:</strong> {across} &nbsp; <strong>Down:</strong> {down}</p>"
        f"</details>"
    )


class PuzzleProvider(BaseCareCircleProvider):
    provider_key = "puzzle"
    is_safe_for_patient = True

    """
    Multi-faceted puzzle provider.

    Randomly dispatches to one of three mini-puzzle sub-generators:
    word search, fill-in-the-blank, or word-pair intersect.
    Each result includes a pre-rendered `puzzle_content` HTML field
    so the template can render it without needing complex logic.
    """

    def _get_word_search(self, words: list = None) -> dict:
        cfg = self.patient_config
        if not words:
            words = cfg.get(
                "default_words",
                ["SPRING", "FLOWERS", "SUNSHINE", "GARDEN", "PICNIC"],
            )
        grid_size = cfg.get("grid_size", 10)
        puzzle = WordSearch(",".join(words), level=1, size=grid_size)
        word_strs = [str(w) for w in puzzle.words]
        grid = puzzle.puzzle
        return {
            "type": "word_search",
            "title": "Daily Word Search",
            "instruction": (
                "Find the hidden words. "
                "They only go across (\u2192) or down (\u2193)."
            ),
            "words": word_strs,
            "grid": grid,
            "puzzle_content": _render_word_search(word_strs, grid),
        }

    def _get_fill_in_the_blank(self) -> dict:
        cfg = self.patient_config
        prompts = cfg.get(
            "fill_in_the_blank_prompts",
            [{"phrase": "An apple a day keeps the _____ away.", "answer": "DOCTOR"}],
        )
        selected = random.choice(prompts)
        blanks = "_ " * len(selected["answer"])
        display_phrase = selected["phrase"].replace("_____", blanks.strip())
        return {
            "type": "fill_in_the_blank",
            "title": "Finish the Phrase",
            "instruction": "Can you fill in the missing word?",
            "phrase": display_phrase,
            "answer": selected["answer"],
            "answer_length": len(selected["answer"]),
            "puzzle_content": _render_fill_in_the_blank(
                display_phrase, selected["answer"]
            ),
        }

    def _get_word_pair(self) -> dict:
        cfg = self.patient_config
        pairs = cfg.get(
            "word_pairs",
            [
                {
                    "across": "BUTTER",
                    "down": "BREAD",
                    "clue_across": "Spread it on toast",
                    "clue_down": "Baked from flour",
                }
            ],
        )
        pair = random.choice(pairs)
        across = pair["across"]
        down = pair["down"]

        rows = max(len(down), 1)
        cols = max(len(across), 1)
        grid = [["" for _ in range(cols)] for _ in range(rows)]
        for i, ch in enumerate(across):
            grid[0][i] = ch
        for i, ch in enumerate(down):
            grid[i][0] = ch

        clues = {
            "Across": pair.get("clue_across", ""),
            "Down": pair.get("clue_down", ""),
        }
        return {
            "type": "word_pair",
            "title": "Mini Intersect",
            "instruction": "Use the clues to find the two intersecting words.",
            "grid": grid,
            "across": across,
            "down": down,
            "clues": clues,
            "puzzle_content": _render_word_pair(across, down, clues, grid),
        }

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        puzzle_types = [
            self._get_word_search,
            self._get_fill_in_the_blank,
            self._get_word_pair,
        ]
        prefs = getattr(patient_profile, 'preferences', {}).get("preferences", {})
        custom_words = None
        if prefs.get("favorite_activities"):
            custom_words = [
                act.split()[0].upper()
                for act in prefs["favorite_activities"]
                if act
            ]
            min_words = cfg.get("min_custom_words", 4)
            if len(custom_words) < min_words:
                filler = cfg.get("filler_words", ["JOY", "PEACE", "LOVE"])
                custom_words.extend(filler)
        selected_func = random.choice(puzzle_types)
        if selected_func == self._get_word_search and custom_words:
            return self._get_word_search(custom_words[:6])
        return selected_func()
