"""
Crossword provider.

Generates a daily mini crossword puzzle — one per difficulty level per day.
The puzzle is profile-independent; all profiles at the same difficulty get
the same crossword.  Results are cached in-memory by (date, difficulty).

Pipeline:
  day-of-week -> category
  Template pool -> pick template for today via day-hash
  LLM word generation x2 batches  (fallback: static word bank)
  Node consistency filter
  Slot scanner + intersection mapper
  CSP solver via python-constraint (AC-3 + backtracking, MRV-ordered)
  Generator LLM -> clues
  Validator LLM (Guess Agent) -> rewrite bad clues
  Build grid_data dict for interactive Jinja2 template
  Return dict for Jinja2 template
"""

from __future__ import annotations

import datetime
import hashlib
import random
from dataclasses import dataclass
from typing import Optional

from constraint import Problem, AllDifferentConstraint

import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict


# ── In-memory daily cache ──────────────────────────────────────────────────
_daily_cache: dict[tuple, dict] = {}


# ── Data structures ────────────────────────────────────────────────────────

@dataclass
class Slot:
    id: str
    direction: str   # "ACROSS" or "DOWN"
    row: int
    col: int
    length: int
    number: int = 0  # filled in after numbering sweep


@dataclass
class Intersection:
    slot_a: Slot     # always ACROSS
    slot_b: Slot     # always DOWN
    a_idx: int       # index within ACROSS word
    b_idx: int       # index within DOWN word


# ── Slot scanner ───────────────────────────────────────────────────────────

def _build_slots(template: list[list[int]]) -> list[Slot]:
    """Scan a 0/1 grid; return all ACROSS and DOWN slots of length >= 3."""
    rows = len(template)
    cols = len(template[0])
    slots: list[Slot] = []
    slot_counter = 0

    # ACROSS
    for r in range(rows):
        c = 0
        while c < cols:
            if template[r][c] == 0:
                start = c
                while c < cols and template[r][c] == 0:
                    c += 1
                length = c - start
                if length >= 3:
                    slots.append(Slot(
                        id=f"A{slot_counter}",
                        direction="ACROSS",
                        row=r, col=start, length=length,
                    ))
                    slot_counter += 1
            else:
                c += 1

    # DOWN
    for c in range(cols):
        r = 0
        while r < rows:
            if template[r][c] == 0:
                start = r
                while r < rows and template[r][c] == 0:
                    r += 1
                length = r - start
                if length >= 3:
                    slots.append(Slot(
                        id=f"D{slot_counter}",
                        direction="DOWN",
                        row=start, col=c, length=length,
                    ))
                    slot_counter += 1
            else:
                r += 1

    return slots


# ── Intersection mapper ────────────────────────────────────────────────────

def _find_intersections(slots: list[Slot]) -> list[Intersection]:
    """Find every (ACROSS, DOWN) slot pair that shares a cell."""
    across = [s for s in slots if s.direction == "ACROSS"]
    down = [s for s in slots if s.direction == "DOWN"]
    intersections: list[Intersection] = []

    for a in across:
        for d in down:
            if (
                a.col <= d.col < a.col + a.length
                and d.row <= a.row < d.row + d.length
            ):
                intersections.append(Intersection(
                    slot_a=a,
                    slot_b=d,
                    a_idx=d.col - a.col,
                    b_idx=a.row - d.row,
                ))
    return intersections


# ── Node consistency ───────────────────────────────────────────────────────

def _node_consistent_words(
    word_bank: list[str],
    slot_lengths: set[int],
) -> list[str]:
    """Filter words to those that are alpha and match a required slot length."""
    return [
        w.upper() for w in word_bank
        if w.isalpha() and len(w) in slot_lengths
    ]


# ── CSP solver ─────────────────────────────────────────────────────────────

def _solve(
    slots: list[Slot],
    intersections: list[Intersection],
    word_pool: list[str],
    max_retries: int = 3,
) -> Optional[dict[str, str]]:
    """
    Assign one word per slot using python-constraint (AC-3 + backtracking).
    Variables are MRV-ordered: most intersections first, then shortest word.
    Retries up to max_retries times with a shuffled word pool.
    Returns {slot_id: word} or None if no solution found.
    """
    # Build intersection count per slot (for MRV ordering)
    inter_count: dict[str, int] = {s.id: 0 for s in slots}
    for ix in intersections:
        inter_count[ix.slot_a.id] += 1
        inter_count[ix.slot_b.id] += 1

    # MRV: most constrained (most intersections) first, then shortest word
    ordered_slots = sorted(
        slots,
        key=lambda s: (-inter_count[s.id], s.length)
    )

    pool = list(word_pool)
    for _ in range(max_retries):
        random.shuffle(pool)
        problem = Problem()

        for slot in ordered_slots:
            domain = [w for w in pool if len(w) == slot.length]
            if not domain:
                break
            problem.addVariable(slot.id, domain)
        else:
            # AllDifferent: no word used twice
            problem.addConstraint(
                AllDifferentConstraint(), [s.id for s in slots]
            )

            # Intersection constraints (AC-3 propagation)
            for ix in intersections:
                ai, bi = ix.a_idx, ix.b_idx
                problem.addConstraint(
                    lambda wa, wb, ai=ai, bi=bi: wa[ai] == wb[bi],
                    (ix.slot_a.id, ix.slot_b.id),
                )

            solution = problem.getSolution()
            if solution:
                return solution

    return None


# ── Cell numbering ─────────────────────────────────────────────────────────

def _number_slots(
    slots: list[Slot],
) -> dict[tuple[int, int], int]:
    """
    Assign sequential numbers to cells that start an ACROSS or DOWN slot.
    Sweep top-to-bottom, left-to-right.
    Returns {(row, col): number}.
    """
    start_cells: set[tuple[int, int]] = set()
    for s in slots:
        start_cells.add((s.row, s.col))

    sorted_cells = sorted(start_cells)
    cell_numbers: dict[tuple[int, int], int] = {}
    n = 1
    for cell in sorted_cells:
        cell_numbers[cell] = n
        n += 1

    for s in slots:
        s.number = cell_numbers.get((s.row, s.col), 0)

    return cell_numbers


# ── Grid data builder ──────────────────────────────────────────────────────

def _build_grid_data(
    template: list[list[int]],
    cell_numbers: dict[tuple[int, int], int],
    slots: list[Slot],
    solution: dict[str, str],
) -> dict:
    """
    Build a JSON-serialisable dict describing the grid layout.
    Passed to the Jinja2 template for interactive rendering.
    """
    return {
        "rows": len(template),
        "cols": len(template[0]),
        "template": template,
        "cell_numbers": {
            f"{r},{c}": n
            for (r, c), n in cell_numbers.items()
        },
        "slots": [
            {
                "id": s.id,
                "dir": s.direction,
                "row": s.row,
                "col": s.col,
                "length": s.length,
                "num": s.number,
            }
            for s in slots
        ],
        "solution": solution,  # {slot_id: word}
    }


# ── LLM prompts ────────────────────────────────────────────────────────────

def _word_generation_prompt(
    category: str,
    slot_lengths: set[int],
    total: int,
    difficulty: str,
) -> str:
    lengths_str = ", ".join(str(n) for n in sorted(slot_lengths))
    complexity = {
        "easy": "simple and very familiar",
        "medium": "moderately common",
        "hard": "more advanced but still well-known",
    }.get(difficulty, "common")
    return (
        f'Generate {total} single English words related to "{category}".\n'
        f"Words must be {complexity}. "
        f"Each word must be EXACTLY one of these lengths: "
        f"{lengths_str} letters.\n"
        "No spaces, hyphens, or proper nouns. "
        "Suitable for a crossword puzzle.\n"
        'Return ONLY valid JSON: {"words": ["WORD1", "WORD2", ...]}'
    )


def _clue_prompt(words: list[str], category: str) -> str:
    word_list = ", ".join(words)
    return (
        f"Generate one short crossword clue for each of these words: "
        f"{word_list}\n"
        f'The theme is "{category}". '
        "Clues should be warm, simple, and friendly (5-10 words).\n"
        'Return ONLY valid JSON: {"WORD": "clue text", ...}'
    )


def _rewrite_clue_prompt(word: str, bad_clue: str) -> str:
    return (
        f'The clue "{bad_clue}" for the word "{word}" is unclear.\n'
        "Please rewrite it as a simpler, clearer crossword clue "
        "(5-10 words).\n"
        f'Return ONLY valid JSON: {{"{word}": "new clue text"}}'
    )


# ── Provider ───────────────────────────────────────────────────────────────

class CrosswordProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """
    Generates a daily crossword puzzle.
    One puzzle per difficulty level per day (cached in _daily_cache).
    """

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.difficulty_config
        grid_size = cfg["grid_size"]
        difficulty = self.difficulty_level

        # Cache check: same puzzle for all profiles at this difficulty today
        today = datetime.date.today().isoformat()
        cache_key = (today, difficulty)
        if cache_key in _daily_cache:
            return _daily_cache[cache_key]

        # Theme: day of week -> category
        weekday = str(datetime.datetime.now().weekday())
        category = self.config["day_categories"][weekday]

        # Pick template for today via stable day-hash (cycles through pool)
        templates = self.config["grid_templates"][str(grid_size)]
        day_hash = int(hashlib.md5(today.encode()).hexdigest(), 16)
        preferred_idx = day_hash % len(templates)
        # Preferred template first, then others as fallbacks
        template_order = [templates[preferred_idx]] + [
            t for i, t in enumerate(templates) if i != preferred_idx
        ]

        # Build slots from preferred template to find required word lengths
        template = template_order[0]
        slots = _build_slots(template)
        intersections = _find_intersections(slots)
        slot_lengths = {s.length for s in slots}

        # LLM word generation — two batches for a richer pool (~5x slots)
        words: list[str] = []
        batch1_count = len(slots) * 3
        batch2_count = len(slots) * 2

        try:
            raw1, resp1 = await generate_json_with_usage(
                _word_generation_prompt(
                    category, slot_lengths, batch1_count, difficulty
                ),
                system=DEMENTIA_SYSTEM_PROMPT,
            )
            self.log_llm_response(resp1)
            words.extend([
                w.upper() for w in raw1.get("words", [])
                if isinstance(w, str)
                and w.isalpha()
                and len(w) in slot_lengths
            ])
        except Exception:
            pass

        try:
            raw2, resp2 = await generate_json_with_usage(
                _word_generation_prompt(
                    category + " (varied associations)",
                    slot_lengths, batch2_count, difficulty,
                ),
                system=DEMENTIA_SYSTEM_PROMPT,
            )
            self.log_llm_response(resp2)
            words.extend([
                w.upper() for w in raw2.get("words", [])
                if isinstance(w, str)
                and w.isalpha()
                and len(w) in slot_lengths
            ])
        except Exception:
            pass

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique_words: list[str] = []
        for w in words:
            if w not in seen:
                seen.add(w)
                unique_words.append(w)
        words = unique_words

        # Fallback: static word bank filtered by actual slot lengths
        if not words:
            all_bank: list[str] = []
            for cat_words in self.config["word_banks"].values():
                all_bank.extend(cat_words)
            bank = _node_consistent_words(all_bank, slot_lengths)
            words = random.sample(bank, min(len(slots) * 5, len(bank)))

        # CSP solve — try each template in order until one yields a solution
        solution: Optional[dict[str, str]] = None
        final_template = template_order[0]
        final_slots = slots
        final_intersections = intersections

        for tmpl in template_order:
            t_slots = _build_slots(tmpl)
            t_ix = _find_intersections(t_slots)
            t_lengths = {s.length for s in t_slots}
            t_pool = [w for w in words if len(w) in t_lengths]

            sol = _solve(t_slots, t_ix, t_pool)
            if sol:
                solution = sol
                final_template = tmpl
                final_slots = t_slots
                final_intersections = t_ix
                break

        if not solution:
            # Last resort: try full word bank across all categories
            all_bank = []
            for cat_words in self.config["word_banks"].values():
                all_bank.extend(cat_words)
            for tmpl in template_order:
                t_slots = _build_slots(tmpl)
                t_ix = _find_intersections(t_slots)
                t_lengths = {s.length for s in t_slots}
                full_bank = _node_consistent_words(all_bank, t_lengths)
                sol = _solve(t_slots, t_ix, full_bank, max_retries=1)
                if sol:
                    solution = sol
                    final_template = tmpl
                    final_slots = t_slots
                    final_intersections = t_ix
                    break

        if not solution:
            return {
                "error": (
                    "Could not generate crossword today. "
                    "Please try again later."
                )
            }

        # Number cells
        cell_numbers = _number_slots(final_slots)

        # Generator LLM — clues
        placed_words = [solution[s.id] for s in final_slots]
        try:
            clues_json, llm_resp = await generate_json_with_usage(
                _clue_prompt(placed_words, category),
                system=DEMENTIA_SYSTEM_PROMPT,
            )
            self.log_llm_response(llm_resp)
        except Exception:
            clues_json = {w: f"A {category} word" for w in placed_words}

        # Validator — Guess Agent loop (max 2 retries per failing clue)
        for word in placed_words:
            clue = clues_json.get(word, "")
            if not clue:
                continue
            for _ in range(2):
                try:
                    guess, _ = await generate_json_with_usage(
                        f"Clue: '{clue}'. What single word is the answer? "
                        'Return ONLY valid JSON: {"answer": "WORD"}',
                        system=DEMENTIA_SYSTEM_PROMPT,
                    )
                    if guess.get("answer", "").upper() == word:
                        break
                    rewrite, _ = await generate_json_with_usage(
                        _rewrite_clue_prompt(word, clue),
                        system=DEMENTIA_SYSTEM_PROMPT,
                    )
                    clue = rewrite.get(word, clue)
                except Exception:
                    break
            clues_json[word] = clue

        # Build across/down clue lists
        sorted_slots = sorted(final_slots, key=lambda s: s.number)
        across = [
            {
                "num": s.number,
                "clue": clues_json.get(solution[s.id], ""),
                "answer": solution[s.id],
            }
            for s in sorted_slots
            if s.direction == "ACROSS" and s.number > 0
        ]
        down = [
            {
                "num": s.number,
                "clue": clues_json.get(solution[s.id], ""),
                "answer": solution[s.id],
            }
            for s in sorted_slots
            if s.direction == "DOWN" and s.number > 0
        ]

        # Build interactive grid data (replaces Pillow PNG)
        grid_data = _build_grid_data(
            final_template, cell_numbers, final_slots, solution
        )

        result = {
            "title": "Today's Crossword",
            "category": category.replace("_", " ").title(),
            "grid_data": grid_data,
            "across": across,
            "down": down,
        }
        _daily_cache[cache_key] = result
        return result
