# Repeatability Fix Tasks

Tasks derived from [repeatibility.md](repeatibility.md). Execute one at a time: implement, test, mark done, move to next.

**Test command (quick smoke-test):**
```powershell
.\.venv\Scripts\python.exe -c "import app.services.care_circle.variety_utils"
```

**Full provider test (requires DB):**
```powershell
.\.venv\Scripts\python.exe scripts\test_care_circle_providers.py
```

---

## Task Status Key
- [ ] pending
- [x] done

---

## Tasks

### Task 1 — Create `variety_utils.py` (shared foundation)
- [ ] **Status:** pending
- **File:** `app/services/care_circle/variety_utils.py` (new)
- **What:** Create two shared helpers used by all subsequent tasks:
  1. `date_seeded_choice(pool, date)` — deterministic per-day selection using `md5(date.isoformat())` seed (same pattern as `complete_the_duo`)
  2. `pick_avoiding_recent(pool, history_path, lookback=14)` — reads/writes a rolling history JSON, excludes items seen in last N days, falls back to full pool if exhausted
- **Test:** `python -c "from app.services.care_circle.variety_utils import date_seeded_choice, pick_avoiding_recent; print('OK')"` and run a self-contained test that simulates 30 days of picks and asserts no two consecutive days repeat within the lookback window.

---

### Task 2 — Fix `daily_quote` API endpoint
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/daily_quote/config.json`
- **What:** Change `api_url` from `https://zenquotes.io/api/today` (returns globally same quote all day) to `https://zenquotes.io/api/random`. This single-line config change makes the provider draw a fresh random quote on each daily generation.
- **Test:** `python -c "import httpx, asyncio; r = asyncio.run(httpx.AsyncClient().get('https://zenquotes.io/api/random')); print(r.json()[0]['q'][:60])"` — run twice and confirm quotes differ.

---

### Task 3 — Apply date-seeding to common static providers
- [ ] **Status:** pending
- **Files (each uses `random.choice()` today):**
  - `morning_stretch/provider.py` — 47 stretches, uses `random.choice(pool)`
  - `gentle_exercise/provider.py` — 30 exercises in config, uses `random.choice(exercises)`
  - `hymn_of_the_day/provider.py` — 40 hymns, uses `random.choice()`
  - `number_sequence/provider.py` — 83 sequences, uses `random.choice()`
  - `old_saying_match/provider.py` — 45 sayings, uses `random.choice()`
  - `word_of_the_day/provider.py` — 80 words, uses `random.choice()`
  - `famous_face/provider.py` — 42 faces, uses `random.choice()`
  - `color_match/provider.py` — 50 color pairs, uses `random.choice()`
  - `finish_phrase/provider.py` — 45 phrases, uses `random.choice()`
  - `word_connect/provider.py` — 15 pairs, uses `random.sample()`
  - `country_spotlight/provider.py` — ~50 countries, uses `random.choice()`
- **What:** Replace each `random.choice(pool)` with `date_seeded_choice(pool, self.get_generation_date())` from `variety_utils`. This guarantees:
  - Same date → same selection (idempotent re-renders)
  - Different date → different selection (no day-over-day clustering)
- **Test:** Instantiate each provider with two different `_for_date` values and assert the selections differ.

---

### Task 4 — Add history exclusion to `brain_booster` topic selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/brain_booster/provider.py`
- **What:** Replace `qt = random.choice(QUESTION_TYPES)` with `pick_avoiding_recent(QUESTION_TYPES, history_path, lookback=len(QUESTION_TYPES))` where `history_path` points to a system-level history file (provider is `common`). Also expand `QUESTION_TYPES` from 4 to 12+ types. Add today's date to the LLM prompt.
- **Test:** Simulate 5 consecutive days of selections and confirm all 4 (or more) types appear before any type repeats.

---

### Task 5 — Add history exclusion to `nostalgia` topic selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/nostalgia/provider.py`
- **What:** Replace `topic = random.choice(NOSTALGIA_TOPICS)` with `pick_avoiding_recent(NOSTALGIA_TOPICS, history_path, lookback=len(NOSTALGIA_TOPICS))`. `nostalgia` is patient-specific so history path is per-patient. Expand `NOSTALGIA_TOPICS` from 6 to 20+ topics. Add today's date to the LLM prompt.
- **Test:** Simulate 20 per-patient picks and assert no topic repeats within the 6 (or more) lookback window.

---

### Task 6 — Add history exclusion to `gratitude` mode selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/gratitude/provider.py`
- **What:** Replace `mode = random.choice(GRATITUDE_MODES)` with `pick_avoiding_recent(GRATITUDE_MODES, history_path, lookback=len(GRATITUDE_MODES))`. Gratitude is patient-specific. Expand `GRATITUDE_MODES` from 5 to 15+ modes. Add today's date to the LLM prompt.
- **Test:** Simulate 15 per-patient picks and assert no mode repeats within the lookback window.

---

### Task 7 — Add history exclusion to `sensory` mode selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/sensory/provider.py`
- **What:** Replace `mode = random.choice(SENSORY_MODES)` with `pick_avoiding_recent(SENSORY_MODES, history_path, lookback=len(SENSORY_MODES))`. Expand `SENSORY_MODES` from 5 to 20+ sub-modes (e.g. split "taste" into multiple sub-contexts). Add today's date to the LLM prompt.
- **Test:** Simulate 20 per-patient picks and assert no mode repeats within lookback window.

---

### Task 8 — Add history exclusion to `ai_trivia` category selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/ai_trivia/provider.py`
- **What:** Replace `category = random.choice(TRIVIA_CATEGORIES)` with `pick_avoiding_recent(TRIVIA_CATEGORIES, history_path, lookback=len(TRIVIA_CATEGORIES))`. `ai_trivia` is common; history path is system-level. Expand `TRIVIA_CATEGORIES` from 6 to 18+ categories. Add today's date to the LLM prompt.
- **Test:** Simulate 18 picks and assert all categories appear before any repeats.

---

### Task 9 — Add history exclusion + expand `animal_friend` facts
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/animal_friend/provider.py`
- **What:** Expand `_DOG_FACTS` from 6 to 40+ facts. Replace `random.choice(dog_facts)` with `pick_avoiding_recent(dog_facts, history_path, lookback=30)`. System-level history (provider is common).
- **Test:** Simulate 40 picks and confirm each fact appears once before any fact repeats.

---

### Task 10 — Add history exclusion to `activity_suggestion` selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/activity_suggestion/provider.py`
- **What:** Replace `activity = random.choice(activities)` with `pick_avoiding_recent(activities, history_path, lookback=len(activities))`. Per-patient history path. Also add today's date to LLM prompt.
- **Test:** With a mock patient having 4 activities, simulate 8 picks and confirm all 4 appear before any repeat.

---

### Task 11 — Add history exclusion to `family_greeting` member selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/family_greeting/provider.py`
- **What:** Replace `random.choice(family_members)` with `pick_avoiding_recent(family_members, history_path, lookback=len(family_members))`. Per-patient history. This ensures every family member gets a feature before any repeats.
- **Test:** With a 3-member family, simulate 6 picks and confirm all 3 appear before any repeat.

---

### Task 12 — Add history exclusion to `song_of_the_day` singer selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/song_of_the_day/provider.py`
- **What:** Replace `random.choice(singers)` with `pick_avoiding_recent(singers, history_path, lookback=len(singers))`. Per-patient history.
- **Test:** With a 3-singer list, simulate 6 picks and confirm cycle order.

---

### Task 13 — Add history exclusion to `hobby_spotlight` hobby selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/hobby_spotlight/provider.py`
- **What:** Replace `random.choice(hobbies)` with `pick_avoiding_recent(hobbies, history_path, lookback=len(hobbies))`. Per-patient history. Add today's date to LLM prompt.
- **Test:** With a 3-hobby patient, simulate 6 picks and confirm all hobbies appear before any repeat.

---

### Task 14 — Inject today's date into `DEMENTIA_SYSTEM_PROMPT` at call time
- [ ] **Status:** pending
- **File:** `app/services/care_circle/llm_helpers.py`
- **What:** Add a `get_dementia_system_prompt(for_date=None)` function that appends `f"Today is {for_date.strftime('%A, %B %-d, %Y')}."` to the base prompt. Update `generate_text_with_usage` and `generate_json_with_usage` to accept an optional `for_date` param and pass the enriched prompt as `system`. Update all providers that hard-code `system=DEMENTIA_SYSTEM_PROMPT` to pass `for_date=self.get_generation_date()` instead.
- **Test:** Call `get_dementia_system_prompt(date(2026,4,21))` and confirm the string contains "April 21".

---

### Task 15 — Add history exclusion to `bingo` word selection
- [ ] **Status:** pending  
- **File:** `app/services/care_circle/providers/bingo/provider.py`
- **What:** Switch from `random.sample(word_bank, 24)` to date-seeded sampling using `date_seeded_choice` logic (seed the `random.Random` with the date hash and call `.sample()`). System-level (provider is common).
- **Test:** Confirm same date → same card, different date → different card.

---

### Task 16 — Expand `word_scramble` base word pool + add history exclusion
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/word_scramble/provider.py`
- **What:** Expand the base word list from 19 to 80+ words. Add `pick_avoiding_recent()` on the selected word (per-patient history, lookback=30).
- **Test:** With the expanded list, simulate 30 picks and confirm no word repeats within the lookback window.

---

### Task 17 — Add history exclusion to `missing_vowels` word selection
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/missing_vowels/provider.py`
- **What:** Expand the default fallback pool from 15 to 60+ words. Add `pick_avoiding_recent()` on selected word (per-patient history, lookback=14).
- **Test:** Simulate 60 picks and confirm no repeat within 14-day window.

---

### Task 18 — Expand `riddle` topic list + LLM styles + fallback pool
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/riddle/provider.py`
- **What:** Expand riddle style templates from 5 to 20+. Apply `pick_avoiding_recent()` on style selection (system-level history). Expand the static fallback pool from 1 to 40+ riddles. Add today's date to LLM prompt.
- **Test:** Simulate 20 picks and confirm all styles appear before any repeats.

---

### Task 19 — Expand `mindful_moment` type list + fallback pool
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/mindful_moment/provider.py`
- **What:** Expand exercise type list from 5 to 20+. Apply `pick_avoiding_recent()` on type selection (system-level history). Expand fallback pool from 6 to 40+. Add today's date to LLM prompt.
- **Test:** Simulate 20 picks and confirm all types appear before any repeats.

---

### Task 20 — Expand `simple_recipe` category list + fallback pool
- [ ] **Status:** pending
- **File:** `app/services/care_circle/providers/simple_recipe/provider.py`
- **What:** Expand recipe categories from 5 to 20+. Apply `pick_avoiding_recent()` on category selection (per-patient history). Expand fallback from 1 to 30+ recipes. Add today's date to LLM prompt.
- **Test:** Simulate 20 picks and confirm all categories appear before any repeats.

---

## Summary Table

| # | Provider(s) | Change | Priority |
|---|---|---|---|
| 1 | `variety_utils.py` (new) | Create shared utility | 🔴 Foundation |
| 2 | `daily_quote` | Switch API to `/random` | 🔴 Critical |
| 3 | 11 common providers | Date-seeded selection | 🔴 Critical |
| 4 | `brain_booster` | History exclusion + expand | 🔴 Critical |
| 5 | `nostalgia` | History exclusion + expand | 🔴 Critical |
| 6 | `gratitude` | History exclusion + expand | 🔴 Critical |
| 7 | `sensory` | History exclusion + expand | 🔴 Critical |
| 8 | `ai_trivia` | History exclusion + expand | 🟠 High |
| 9 | `animal_friend` | History exclusion + expand | 🟠 High |
| 10 | `activity_suggestion` | History exclusion | 🟠 High |
| 11 | `family_greeting` | History exclusion | 🟠 High |
| 12 | `song_of_the_day` | History exclusion | 🟠 High |
| 13 | `hobby_spotlight` | History exclusion | 🟠 High |
| 14 | `llm_helpers.py` | Date injection in system prompt | 🟡 Medium |
| 15 | `bingo` | Date-seeded sampling | 🟡 Medium |
| 16 | `word_scramble` | Expand + history exclusion | 🟡 Medium |
| 17 | `missing_vowels` | Expand + history exclusion | 🟡 Medium |
| 18 | `riddle` | Expand + history exclusion | 🟡 Medium |
| 19 | `mindful_moment` | Expand + history exclusion | 🟡 Medium |
| 20 | `simple_recipe` | Expand + history exclusion | 🟡 Medium |
