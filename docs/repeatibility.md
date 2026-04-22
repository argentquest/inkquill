# Provider Repeatability Analysis

**Date:** 2026-04-21  
**Scope:** All care circle providers (~60 total)  
**Purpose:** Identify providers where the same content can appear on consecutive days for the same patient, and prescribe concrete fixes.

---

## Day-to-Day Comparison Script

Use the Python helper at [validate_care_circle_newsletter_uniqueness.py](/C:/Code/inkandquill/inkquill/scripts/validate_care_circle_newsletter_uniqueness.py) to generate newsletters across multiple days and compare cached provider JSON output for repeats.

### What it does

- Generates Care Circle sessions for consecutive dates using the real session assembly path
- Reads cached provider JSON under `cache/{patient_id}/{YYYY-MM-DD}/`
- Compares normalized provider `data` payloads across days for the same patient
- Ignores layout-only and volatile fields such as:
  - `newsletter_header`
  - `newsletter_footer`
  - `rendered_html`
  - cache metadata
  - footer stats
  - date-stamped local cached image URLs
- Writes a markdown report of any duplicate outputs

### Run it

From the repo root:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_care_circle_newsletter_uniqueness.py --days 3
```

Only for selected patients:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_care_circle_newsletter_uniqueness.py --days 3 --patient-id 17 --patient-id 20
```

With an explicit start date:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_care_circle_newsletter_uniqueness.py --days 3 --start-date 2026-04-21
```

Reuse existing cache instead of forcing regeneration:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_care_circle_newsletter_uniqueness.py --days 3 --reuse-cache
```

Write to a custom report path:

```powershell
.\.venv\Scripts\python.exe .\scripts\validate_care_circle_newsletter_uniqueness.py --days 3 --report artifacts\care_circle_uniqueness_report.md
```

### Output

Default report output:

```text
artifacts/care_circle_uniqueness_report.md
```

Each finding is grouped by patient and reports the provider key plus the dates where the same normalized output appeared.

---

## How the Cache System Works

Each provider runs at most once per patient per day. Results are stored at:

```
cache/{patient_id}/{YYYY-MM-DD}/{provider_key}.json
```

A new cache directory is created each calendar day, so a provider will regenerate its content fresh on a new date — **unless** the content is driven by a small random pool or a deterministic external API. In those cases, the new cache entry can easily contain the same content as the previous day.

**Key insight:** The cache guarantees that a provider won't run twice on the same day for the same patient. It does **not** guarantee that today's output differs from yesterday's or last week's.

---

## Two Provider Classes

| Class | Description | Repeatability scope |
|---|---|---|
| **Common** (`"common": true` in config) | One shared HTML output per day for all patients | Repeats across days at the system level |
| **Patient-specific** | Generated per-patient using patient profile data | Repeats per patient across days |

Common providers are intentional — they reduce LLM cost by sharing output. The risk is not across patients but across calendar days.

---

## Repeatability Risk Scale

| Level | Symbol | Criteria |
|---|---|---|
| Critical | 🔴 | Pool ≤ 10 distinct outputs, OR external API returns the same deterministic daily value |
| High | 🟠 | Pool 11–50, no anti-repeat logic, no patient personalization |
| Medium | 🟡 | Pool 51–100, OR patient-personalized but preference list is small (< 5 items typical) |
| Low | 🟢 | LLM-generated with rich patient context + large/open pool, or large pool > 100 |
| None | ✅ | Output is inherently unique per day (date-anchored, procedural, timestamp-based) |

---

## Providers Already Doing This Well (Reference Implementations)

Before detailing problems, these providers already have sound variability mechanisms:

- **`complete_the_duo`** — Uses `md5(today.isoformat())` as a deterministic seed. Same pairs across all patients on the same day; guaranteed different each day. **Best pattern for common providers.**
- **`gridless_crossword`** — Daily in-memory cache keyed by `(date, difficulty, category)`. Fresh content each calendar day, stable for re-renders within the day.
- **`simple_math`** — Procedurally generated (random numbers + operator). Infinite pool; practically zero repeat risk.
- **`newsletter_header`** — Timestamp-stamped. Inherently unique per session.
- **`this_day_history`** — Wikipedia "on this day" anchored to the calendar date. Unique 365 distinct outputs per year.
- **`weather`** — Real forecast anchored to the date. Inherently unique.
- **`memory_lane_photo`** — LLM generates a Wikimedia search query based on patient era/hometown, then writes a caption. Rich patient context + open-ended query → strong natural variety.
- **`local_history`** — LLM generates a historical fact about the patient's hometown + era. Highly personalized; good variety.

---

## Provider-by-Provider Analysis

### `activity_suggestion`
- **Type:** Patient-specific
- **Selection:** `random.choice(activities)` from patient `favorite_activities` list; LLM writes 2-sentence invitation
- **Pool size:** Depends on patient profile — typically 3–8 activities
- **Patient data:** `favorite_activities`, `mobility_level`, `favourite_foods`, `pets`, `preferred_pronoun`
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (small preference list; same activity will recur within days)
- **Fix:** Before `random.choice()`, filter out the last 7 days' activity selections from a per-patient history file. LLM prompt already varies the wording even for the same activity.

---

### `ai_trivia`
- **Type:** Common (or patient-specific depending on config)
- **Selection:** `random.choice()` from 6 hardcoded categories; LLM generates era-specific fact + music suggestion
- **Pool size:** 6 categories
- **Patient data:** `era_of_youth`, `favorite_singers`
- **Anti-repeat:** None
- **Risk:** 🟠 High (6 categories means statistical repeat within 3–4 days)
- **Fix:** Apply recent-history exclusion to category selection (exclude last 5 days' categories). Expand category list to at least 15–20. Include today's date in the LLM prompt so even the same category produces different content.

---

### `animal_friend`
- **Type:** Common
- **Selection:** `random.choice()` from 6 hardcoded dog facts; API call to dog.ceo for image
- **Pool size:** 6 facts (image varies via API)
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (6 facts — expected repeat within 3–4 days)
- **Fix:** Expand the hardcoded `_DOG_FACTS` list to 40+ entries. Apply recent-history exclusion against a system-level history file to avoid repeating a fact seen in the last 30 days.

---

### `bingo`
- **Type:** Common
- **Selection:** `random.sample(word_bank, 24)` — 24 words drawn from config word bank
- **Pool size:** Depends on word bank size in config; statistically the same popular words appear frequently
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (sampling without replacement within one card; but same card composition likely repeats across days with small banks)
- **Fix:** Increase word bank size. Use date-seeded `random.seed(date_str)` so the card is deterministic per day (same as `complete_the_duo` pattern) and guaranteed to change each day.

---

### `brain_booster`
- **Type:** Common
- **Selection:** `random.choice()` from 4 hardcoded question types; LLM generates exercises
- **Pool size:** 4 types
- **Patient data:** `era_of_youth`
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (4 question types — repeat within 2–3 days)
- **Fix:** Expand question types to 12+. Apply recent-history exclusion to type selection (exclude last 7 days). Add today's date to the LLM prompt to ensure even the same type produces different specific questions.

---

### `cat_fact`
- **Type:** Common
- **Selection:** Fetches from catfact.ninja API (random fact), random query param on image URL
- **Pool size:** External API — unknown size but finite
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (API pool is limited; same fact can reappear)
- **Fix:** Cache the facts received over time in a system-level history file. On fetch, if the returned fact was seen in the last 60 days, re-fetch (up to 3 retries). Add a large local fallback pool of 60+ cat facts.

---

### `classic_art`
- **Type:** Common
- **Selection:** Met Museum Open Access API query; falls back to a hardcoded artwork list
- **Pool size:** API has thousands of works; fallback list is small
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟢 Low for API path (large pool); 🟠 High when fallback triggers
- **Fix:** Log artwork IDs received from the API in a system-level history file. Exclude artworks seen in the last 90 days from API result selection. Expand the fallback list to 50+ artworks.

---

### `color_match`
- **Type:** Common
- **Selection:** `random.choice()` from 50-item config list
- **Pool size:** 50 color pairs
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟠 High (50 items; statistically ~50% chance of repeat within 8–9 days with pure random)
- **Fix:** Apply date-seeded randomness (`random.seed(date_str)`) so the selection cycles deterministically through all 50 pairs without clustering. Or apply recent-history exclusion for last 45 days.

---

### `comic_abe_martin` / `comic_brownies` / `comic_dino_cartoons` / `comic_mr_skygack` / `comic_wuffle`
- **Type:** Common (all use `WikimediaComicProvider` base)
- **Selection:** Fetches from Wikimedia Commons category; selects a strip
- **Pool size:** Varies per comic; categories can be large
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (pool size unknown; repeat depends on category depth)
- **Fix:** Track seen strip filenames in a system-level history file per comic provider. Exclude strips seen in the last 60 days. If pool exhausted, reset history.

---

### `complete_the_duo`
- **Type:** Common
- **Selection:** `md5(today.isoformat())` seed → deterministic 4 pairs per day from full pool
- **Pool size:** Full pool (size not specified but large)
- **Patient data:** None
- **Anti-repeat:** ✅ Yes — different pairs guaranteed each day by date seed
- **Risk:** ✅ None
- **Note:** This is the reference implementation for common providers. No changes needed.

---

### `country_spotlight`
- **Type:** Common
- **Selection:** `random.choice()` from external JSON file (~50 countries) or 3-item hardcoded fallback
- **Pool size:** ~50 from file; 3 from fallback
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟠 High (50 from file — expect repeat within ~25 days; 🔴 Critical on 3-item fallback)
- **Fix:** Apply date-seeded randomness for the file path. Ensure the external JSON has 100+ entries. Fix the 3-item fallback to at least 30 entries. Track recent selections with recent-history exclusion.

---

### `daily_affirmation`
- **Type:** Common
- **Selection:** Fetches from affirmations.dev API; static fallback
- **Pool size:** API pool unknown; single static fallback
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (single fallback; API may serve the same popular affirmations repeatedly)
- **Fix:** Build a local pool of 100+ affirmations as the primary source, shuffled daily with date-seeded randomness. Use the API as a supplement to rotate new ones in. Remove single-item fallback.

---

### `daily_blessing`
- **Type:** Common
- **Selection:** `random.choice()` from 90 hardcoded blessings
- **Pool size:** 90
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟢 Low (90 items; statistically takes ~45+ days to see a likely repeat)
- **Fix:** Still worthwhile to add date-seeded randomness or recent-history exclusion (last 60 days). With 90 items this is low priority.

---

### `daily_quote`
- **Type:** Common
- **Selection:** Fetches from `zenquotes.io/api/today` — returns the **same quote to all callers globally for the entire day**
- **Pool size:** 1 per day (deterministic for all users)
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🔴 Critical — same quote every hour of the day; quote pool repeats within weeks
- **Fix:** Switch to `zenquotes.io/api/random` (returns a random quote on each call). Apply recent-history exclusion to avoid repeating quotes seen in the last 90 days. Expand the fallback pool to 200+ quotes.

---

### `dog_photo`
- **Type:** Common
- **Selection:** Fetches from dog.ceo API (`/api/breeds/image/random`)
- **Pool size:** Thousands of photos via API
- **Patient data:** None
- **Anti-repeat:** None (but API is genuinely random)
- **Risk:** 🟢 Low (API is large and random)
- **Fix:** No urgent action needed. Optionally track the last 30 image URLs and exclude them on retry.

---

### `family_greeting`
- **Type:** Patient-specific
- **Selection:** `random.choice(family_members)`; LLM writes a 2-sentence message "from" that person
- **Pool size:** Depends on family size — typically 2–6 members
- **Patient data:** `family_members`, `life_roles`, `pets`, `favourite_foods`, `hometown`
- **Anti-repeat:** None
- **Risk:** 🟡 Medium to 🔴 Critical (small families will see the same family member repeatedly)
- **Fix:** Apply recent-history exclusion — track which family member was featured each day and cycle through all members before repeating. This ensures every family member gets featured before any repeats.

---

### `famous_face`
- **Type:** Common
- **Selection:** `random.choice()` from 42 hardcoded famous people
- **Pool size:** 42
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟠 High (42 items — expect repeat within ~21 days)
- **Fix:** Expand the pool to 120+ famous people. Apply date-seeded randomness so faces cycle without random clustering.

---

### `finish_phrase`
- **Type:** Patient-specific
- **Selection:** Random choice from 45 phrases; era-weighted based on `era_of_youth`
- **Pool size:** 45
- **Patient data:** `era_of_youth` (for weighting)
- **Anti-repeat:** None
- **Risk:** 🟠 High (era weighting concentrates selections into a smaller effective pool)
- **Fix:** Apply recent-history exclusion (last 30 days). Era weighting is fine but should work from the non-recently-used subset.

---

### `gentle_exercise`
- **Type:** Common
- **Selection:** Random choice from config list; default config has 1 item
- **Pool size:** 1 in default config
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (1-item default means same exercise every single day)
- **Fix:** Expand the config to 40+ exercises. Apply date-seeded selection so exercises cycle day by day.

---

### `gratitude`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from 5 hardcoded gratitude modes; LLM generates thought
- **Pool size:** 5 modes
- **Patient data:** `display_name`
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (5 modes — repeat expected within 3 days)
- **Fix:** Expand to 15+ modes. Apply recent-history exclusion. Include today's date in LLM prompt so even the same mode produces fresh content.

---

### `gridless_crossword`
- **Type:** Common
- **Selection:** LLM-generated; in-memory daily cache keyed by `(date, difficulty, category)`
- **Pool size:** Open-ended (LLM-generated)
- **Patient data:** None (only difficulty)
- **Anti-repeat:** ✅ Yes — daily cache ensures fresh puzzle each calendar day
- **Risk:** ✅ None
- **Note:** Good implementation. No changes needed.

---

### `hobby_spotlight`
- **Type:** Patient-specific
- **Selection:** `random.choice(hobbies)` from patient profile; LLM writes spotlight content
- **Pool size:** Depends on patient's hobby list — typically 2–5
- **Patient data:** `hobbies`, `life_roles`, `hometown`, `era_of_youth`, `nationality_or_background`
- **Anti-repeat:** None
- **Risk:** 🟡 Medium to 🔴 Critical (small hobby lists cycle very fast)
- **Fix:** Apply recent-history exclusion on hobby selection. With 2 hobbies, the cycle will always alternate (which is the best possible with a small pool — at least it's not back-to-back). Include today's date in the LLM prompt.

---

### `hymn_of_the_day`
- **Type:** Common
- **Selection:** `random.choice()` from 40 hardcoded hymns
- **Pool size:** 40
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟠 High (40 hymns — expect repeat within ~20 days)
- **Fix:** Expand the pool to 100+ hymns. Apply date-seeded randomness or recent-history exclusion (last 60 days).

---

### `joke`
- **Type:** Common
- **Selection:** Fetches from JokeAPI v2 (safe mode, random on each call)
- **Pool size:** External API — large pool
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟢 Low (API is genuinely random and large)
- **Fix:** Optionally track the last 30 joke IDs and pass `blacklistFlags` or `idRange` to JokeAPI to exclude recently seen jokes.

---

### `letter_to_family`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from 10 letter themes; LLM generates letter; falls back to 5 static letters
- **Pool size:** 10 themes (LLM); 5 static fallbacks
- **Patient data:** `display_name`
- **Anti-repeat:** None
- **Risk:** 🟠 High for themes (10); 🔴 Critical for fallback (5)
- **Fix:** Expand themes to 30+. Expand fallback to 30+ static letters. Apply recent-history exclusion on theme selection. Include patient name and today's date in the LLM prompt (already uses name; add date).

---

### `local_history`
- **Type:** Patient-specific
- **Selection:** LLM-generated with patient hometown, era, nationality, life_roles
- **Pool size:** Open-ended
- **Patient data:** `hometown`, `era_of_youth`, `nationality_or_background`, `life_roles`
- **Anti-repeat:** None formally, but LLM output is naturally varied
- **Risk:** 🟢 Low (rich patient context + open-ended generation)
- **Fix:** Include today's date in LLM prompt so the model knows not to repeat content. Track last 14 generated facts in a history file and include them as "facts already covered" in the prompt.

---

### `memory_lane_photo`
- **Type:** Patient-specific
- **Selection:** LLM generates a Wikimedia search query using patient era/hometown; fetches photo; LLM writes caption
- **Pool size:** Open-ended (Wikimedia is vast)
- **Patient data:** `era_of_youth`, `hometown`, `nationality_or_background`, `hobbies`
- **Anti-repeat:** None formally, but query + caption combination is highly variable
- **Risk:** 🟢 Low
- **Fix:** Include today's date in LLM prompt. Track recent Wikimedia filenames in a per-patient history file and avoid repeating the same image.

---

### `mindful_moment`
- **Type:** Common
- **Selection:** LLM generates from 5 exercise type templates; falls back to 6 static exercises
- **Pool size:** 5 LLM types; 6 static fallbacks
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium for LLM path; 🔴 Critical for fallback (6 items)
- **Fix:** Expand exercise type list to 20+. Expand fallback to 40+ entries. Apply recent-history exclusion on type selection. Add today's date to LLM prompt.

---

### `missing_vowels`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from difficulty-filtered personalized pool (family names + favorite_activities + 15 defaults)
- **Pool size:** 15 defaults + patient-specific words (varies)
- **Patient data:** Family member names, `favorite_activities`
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (pool grows with patient data; but small for patients with few activities)
- **Fix:** Apply recent-history exclusion so the same word isn't puzzled twice in a 14-day window. Expand the default pool to 60+ words.

---

### `morning_stretch`
- **Type:** Common
- **Selection:** `random.choice()` from 47 built-in stretches
- **Pool size:** 47
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟠 High (47 stretches — expect repeat within ~24 days)
- **Fix:** Apply date-seeded selection to cycle through stretches without clustering. Or apply recent-history exclusion (last 40 days).

---

### `nature_park`
- **Type:** Common
- **Selection:** NPS Open Data API call returning up to 500 parks; random selection. Falls back to 8 hardcoded images
- **Pool size:** 500 via API; 8 in fallback
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟢 Low for API path; 🔴 Critical for 8-item fallback
- **Fix:** Expand fallback to 40+ parks. Track recently shown parks in a system-level history file (90-day window).

---

### `nature_scene`
- **Type:** Common
- **Selection:** LLM generates scene theme at `temperature=1.0`; then generates description and image
- **Pool size:** Open-ended (LLM with maximum temperature)
- **Patient data:** None
- **Anti-repeat:** None formally, but temperature=1.0 maximizes variation
- **Risk:** 🟢 Low
- **Fix:** No critical action needed. Optionally include today's date and season in the LLM prompt to anchor variety. Track recent scene themes and include them as "already shown recently" context in the prompt.

---

### `newsletter_footer`
- **Type:** Common
- **Selection:** Static content (contact info, unsubscribe links)
- **Pool size:** 1 (static)
- **Patient data:** None
- **Anti-repeat:** ✅ N/A — footer is intentionally static
- **Risk:** ✅ None (by design)

---

### `newsletter_header`
- **Type:** Patient-specific
- **Selection:** Direct data pull — patient name, family name, current timestamp
- **Pool size:** 1 per session
- **Patient data:** `display_name`, `family_name`
- **Anti-repeat:** ✅ Yes — timestamp makes it unique per generation
- **Risk:** ✅ None

---

### `nostalgia`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from 6 hardcoded nostalgia topics; LLM writes warm memory
- **Pool size:** 6 topics
- **Patient data:** `era_of_youth`, `nationality_or_background`, `hometown`, `life_roles`, `favourite_foods`, `favourite_tv_shows`
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (6 topics — repeat within 3–4 days guaranteed by probability)
- **Fix:** Expand topics to 30+. Apply recent-history exclusion (exclude last 14 days' topics). Include today's date in LLM prompt. Even with the same topic, date injection makes the LLM write different specific memories.

---

### `number_sequence`
- **Type:** Common
- **Selection:** `random.choice()` from 83 built-in sequences
- **Pool size:** 83
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (83 items — statistically low repeat risk daily, but with pure random ~37% chance of repeat within 60 days)
- **Fix:** Apply date-seeded selection or recent-history exclusion (last 60 days). Low priority given pool size.

---

### `odd_one_out`
- **Type:** Patient-specific
- **Selection:** Random selection of 2 categories from 50; 3 items from main category + 1 odd item; family members can be injected
- **Pool size:** 50 categories; `C(50,2) = 1225` distinct category pairs
- **Patient data:** `family_members` (optional injection)
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (large combinatorial pool; but random clustering can cause visible repeats)
- **Fix:** Apply date-seeded selection to cycle through category pairs systematically. Low urgency due to large pool.

---

### `old_saying_match`
- **Type:** Common
- **Selection:** `random.choice()` from 45 built-in sayings
- **Pool size:** 45
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟠 High (45 items — expect repeat within ~22 days)
- **Fix:** Expand sayings pool to 120+. Apply date-seeded selection or recent-history exclusion (last 40 days).

---

### `pen_pal_letter`
- **Type:** Patient-specific
- **Selection:** `random.choice(friend_names)` from config; LLM writes letter. Falls back to 5 static letters
- **Pool size:** Depends on config friend names (may be 1–3); 5 static fallbacks
- **Patient data:** `display_name`, `era_of_youth`, `favorite_activities`, `hometown`, `life_roles`, `pets`, `favourite_foods`, `favourite_tv_shows`
- **Anti-repeat:** None
- **Risk:** 🟡 Medium for LLM path (rich patient context); 🔴 Critical for fallback (5 items + small friend pool)
- **Fix:** Expand friend names list to 10+. Apply recent-history exclusion on friend selection (so each friend appears in rotation before repeating). Include today's date in LLM prompt. Expand fallback to 30+ letters.

---

### `personal_affirmation`
- **Type:** Patient-specific
- **Selection:** LLM-generated with patient context; single static fallback
- **Pool size:** Open-ended (LLM); 1 static fallback
- **Patient data:** `display_name`, `favorite_activities`, `life_roles`, `preferred_pronoun`, `pets`
- **Anti-repeat:** None formally
- **Risk:** 🟢 Low for LLM path; 🔴 Critical for 1-item fallback
- **Fix:** Include today's date in LLM prompt. Expand fallback to 30+ affirmations. Track recent affirmation themes in a per-patient history file and include them as "recently used themes" in the LLM prompt.

---

### `puzzle`
- **Type:** Patient-specific
- **Selection:** Random from 20 fill-in-blank prompts + 10 word-pair clues in config
- **Pool size:** 20 prompts, 10 word pairs
- **Patient data:** `favorite_activities` (for custom words)
- **Anti-repeat:** None
- **Risk:** 🟠 High (small config pool; same puzzles recur quickly)
- **Fix:** Substantially expand the config pools. Apply recent-history exclusion. For word-search variant, use patient's full activity list to generate words that vary day to day.

---

### `riddle`
- **Type:** Common
- **Selection:** LLM generated from 5 style templates; falls back to 1 static riddle
- **Pool size:** 5 LLM styles; 1 static fallback
- **Patient data:** None (only difficulty)
- **Anti-repeat:** None
- **Risk:** 🟠 High for LLM path (5 styles); 🔴 Critical for 1-item fallback
- **Fix:** Expand style templates to 20+. Apply recent-history exclusion on style selection. Expand fallback to 40+ riddles. Include today's date in LLM prompt.

---

### `seasonal_poem`
- **Type:** Common
- **Selection:** LLM generates with seasonal context; falls back to 2 static poems per season (8 total)
- **Pool size:** Open-ended (LLM); 2 static fallbacks per season
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium for LLM path; 🔴 Critical for fallback (2 per season)
- **Fix:** Expand fallback to 20+ poems per season (80 total). Include today's date in LLM prompt so each day's poem is anchored to a specific date. Track recently generated poem themes in a history file.

---

### `sensory`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from 5 hardcoded senses; LLM writes activity suggestion
- **Pool size:** 5 senses
- **Patient data:** `favorite_singers`, `favourite_foods`, `pets`, `hometown`, `mobility_level`
- **Anti-repeat:** None
- **Risk:** 🔴 Critical (5 senses — repeat within 3 days)
- **Fix:** Expand sense categories to 20+ (e.g., touch sub-types, smell sub-types, taste contexts). Apply recent-history exclusion. Include today's date in LLM prompt.

---

### `simple_math`
- **Type:** Common
- **Selection:** Procedurally generated (random numbers + operator based on difficulty)
- **Pool size:** Infinite
- **Patient data:** None (only difficulty)
- **Anti-repeat:** ✅ Effectively none — same problem can appear but probability is very low
- **Risk:** ✅ None (procedural)

---

### `simple_recipe`
- **Type:** Patient-specific
- **Selection:** LLM generates from 5 recipe category templates; single static fallback
- **Pool size:** 5 LLM categories; 1 static fallback
- **Patient data:** `era_of_youth`
- **Anti-repeat:** None
- **Risk:** 🟠 High for LLM (5 categories); 🔴 Critical for 1-item fallback
- **Fix:** Expand recipe categories to 30+. Apply recent-history exclusion on category selection. Include today's date in LLM prompt. Expand fallback to 30+ recipes.

---

### `song_of_the_day`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from `favorite_singers` list; fetches album art from TheAudioDB API
- **Pool size:** Depends on patient's singer list — typically 2–5
- **Patient data:** `favorite_singers` (or `favorite_singer`)
- **Anti-repeat:** None
- **Risk:** 🟡 Medium to 🔴 Critical (small singer list → same artist repeats frequently)
- **Fix:** Apply recent-history exclusion on singer selection (cycle through all singers before repeating). If only 1 singer configured, include the singer's songs or albums in the selection to add intra-artist variety.

---

### `spot_the_difference`
- **Type:** Common
- **Selection:** LLM generates word list; left/right columns shuffled independently; falls back to config sets
- **Pool size:** Open-ended (LLM); variable fallback
- **Patient data:** None
- **Anti-repeat:** None formally, but LLM generates different words each time
- **Risk:** 🟢 Low for LLM path
- **Fix:** Include today's date in LLM prompt. Ensure fallback has 30+ distinct sets.

---

### `this_day_history`
- **Type:** Common
- **Selection:** Wikipedia "On This Day" fetched for the calendar date (month/day)
- **Pool size:** 365 distinct outputs per year; same day next year will have same Wikipedia content
- **Patient data:** None
- **Anti-repeat:** ✅ Unique per calendar day within a year
- **Risk:** ✅ None (within a year); 🟡 Medium (year-over-year same date)
- **Fix:** Low priority. LLM rewrites the text, so even the same underlying events get phrased differently year-over-year.

---

### `weather`
- **Type:** Patient-specific
- **Selection:** Real weather forecast for patient's location and date
- **Pool size:** Inherently unique per date/location
- **Patient data:** `city_for_weather` (or lat/lon)
- **Anti-repeat:** ✅ Inherently unique
- **Risk:** ✅ None

---

### `wikimedia_gallery`
- **Type:** Common
- **Selection:** Fetches 500 category members from Wikimedia Commons; selects 12 candidates, filters for English-friendly content
- **Pool size:** ~500 per category
- **Patient data:** `preferred_language`
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (500 is large but random sampling can cluster)
- **Fix:** Track shown image filenames in a system-level history file (90-day window). Exclude recently shown images from the 12-candidate selection.

---

### `word_connect`
- **Type:** Common
- **Selection:** `random.sample(4 pairs from 15)` in config; left/right independently shuffled
- **Pool size:** `C(15,4) = 1365` distinct pair combinations
- **Patient data:** None
- **Anti-repeat:** None, but combinatorial space is reasonable
- **Risk:** 🟠 High (15 source pairs is small; same pairs will cluster with pure random)
- **Fix:** Expand the config to 50+ word pairs. Apply date-seeded selection so pairs cycle without clustering.

---

### `word_of_the_day`
- **Type:** Common
- **Selection:** `random.choice()` from 80 built-in words
- **Pool size:** 80
- **Patient data:** None
- **Anti-repeat:** None
- **Risk:** 🟡 Medium (80 words; statistically ~40% chance of repeat within 60 days with pure random)
- **Fix:** Apply date-seeded selection to cycle through all 80 words before repeating. Expand pool to 200+.

---

### `word_scramble`
- **Type:** Patient-specific
- **Selection:** `random.choice()` from difficulty-filtered pool; patient's family names added if within length constraints
- **Pool size:** ~19 default + family names
- **Patient data:** Family member names
- **Anti-repeat:** None
- **Risk:** 🟠 High (19 base words is very small)
- **Fix:** Expand the base word pool to 100+. Apply recent-history exclusion (last 14 days). Family names are a nice touch — keep them.

---

### `world_news`
- **Type:** Common
- **Selection:** RSS feed fetch; content changes as news cycle changes
- **Pool size:** Effectively unlimited (live news)
- **Patient data:** None
- **Anti-repeat:** ✅ News changes continuously
- **Risk:** ✅ None (by nature of live news feed)

---

## Cross-Cutting Patterns

### Pattern A — Unguarded `random.choice()` on small pools
The most widespread issue. `random.choice()` has no memory, so with a pool of N items, the expected wait before a repeat is roughly `N/2` days.

**Affected providers (pool ≤ 10):** `animal_friend` (6), `brain_booster` (4), `gentle_exercise` (1), `gratitude` (5), `sensory` (5), `nostalgia` (6), `daily_affirmation` (1 fallback), `daily_quote` (deterministic), `riddle` (1 fallback), `simple_recipe` (1 fallback)

**Recommended fix — `pick_avoiding_recent()` utility:**  
Create `app/services/care_circle/variety_utils.py` with a shared helper:

```python
# History stored at: cache/_history/{key}.json (common) or cache/{patient_id}/history/{key}.json (patient-specific)
def pick_avoiding_recent(pool: list, history_path: Path, lookback: int = 14) -> Any:
    history = load_history(history_path)  # list of recent selections
    recent = set(history[-lookback:])
    candidates = [x for x in pool if x not in recent]
    if not candidates:
        candidates = pool  # reset if all options exhausted
    choice = random.choice(candidates)
    save_history(history_path, history + [choice])
    return choice
```

### Pattern B — External API returning a deterministic "today" value
**Affected:** `daily_quote` (`zenquotes.io/api/today`), `daily_affirmation` (affirmations.dev daily endpoint)

**Fix per provider:**
- `daily_quote`: Change API call from `/api/today` to `/api/random`. The random endpoint still returns one quote but draws from the full pool randomly each call.
- `daily_affirmation`: Confirm whether affirmations.dev has a random endpoint; if not, replace with a large local pool (100+) with date-seeded selection.

### Pattern C — LLM topic selection from a small fixed list
The LLM produces varied *wording* even for the same topic, but the **topic itself** repeats frequently, which a patient will notice.

**Affected:** `nostalgia` (6 topics), `sensory` (5 senses), `gratitude` (5 modes), `brain_booster` (4 types), `ai_trivia` (6 categories), `mindful_moment` (5 types), `riddle` (5 styles), `simple_recipe` (5 categories), `letter_to_family` (10 themes)

**Fix:**
1. Expand each topic list to 20+ entries.
2. Apply `pick_avoiding_recent()` to topic selection.
3. Inject today's date into the LLM prompt: `"Today is {date}. Write something fresh and not repetitive."` — this nudges the model to vary content even on the same topic.

### Pattern D — Critically small fallback pools
When LLM calls fail, providers fall back to static lists. Many of these lists are dangerously small.

| Provider | Fallback size | Target |
|---|---|---|
| `gentle_exercise` | 1 | 40+ |
| `simple_recipe` | 1 | 30+ |
| `daily_affirmation` | 1 | 100+ |
| `riddle` | 1 | 40+ |
| `personal_affirmation` | 1 | 30+ |
| `seasonal_poem` | 2 per season | 20+ per season |
| `mindful_moment` | 6 | 40+ |
| `letter_to_family` | 5 | 30+ |
| `pen_pal_letter` | 5 | 30+ |

**Fix:** Expand these config lists. These are pure content additions with no code changes needed beyond the config JSON.

### Pattern E — Common providers: no system-level history
Common providers are shared across all patients on the same day — which is intentional. But there is no mechanism to prevent the same common content from appearing in consecutive daily newsletters.

**Best fix for common providers:** Use the `complete_the_duo` pattern — seed `random` with `hashlib.md5(today.isoformat().encode()).hexdigest()` and convert it to an integer seed. This gives:
- **Deterministic** output per day (stable for re-renders)
- **Guaranteed different** output each calendar day
- **No history file needed**

This should be adopted by: `bingo`, `color_match`, `country_spotlight`, `famous_face`, `finish_phrase`, `hymn_of_the_day`, `morning_stretch`, `number_sequence`, `old_saying_match`, `word_of_the_day`

### Pattern F — LLM prompts without date anchoring
Several LLM-based providers don't include today's date in their prompt. Including the date helps the model naturally vary content (referencing seasonal events, phrasing naturally for the time of year, avoiding repetition).

**Fix:** Update `DEMENTIA_SYSTEM_PROMPT` in `llm_helpers.py` to include:
```
Today's date is {date}. Ensure your response is fresh and has not been used recently.
```
Or inject date in each provider's user-facing prompt where finer control is needed.

---

## Prioritized Fix Roadmap

### Priority 1 — Critical (fix immediately)
These providers can show the same output every single day:

| Provider | Issue | Fix |
|---|---|---|
| `daily_quote` | API always returns the same quote today | Switch to `/api/random` endpoint |
| `gentle_exercise` | 1-item default config | Expand to 40+ exercises |
| `brain_booster` | 4 LLM topics, no exclusion | Expand to 12+, add history exclusion |
| `gratitude` | 5 LLM modes, no exclusion | Expand to 15+, add history exclusion |
| `sensory` | 5 LLM senses, no exclusion | Expand to 20+, add history exclusion |
| `nostalgia` | 6 LLM topics, no exclusion | Expand to 30+, add history exclusion |
| `animal_friend` | 6 dog facts, no exclusion | Expand to 40+, add history exclusion |
| `daily_affirmation` | 1 static fallback | Expand fallback to 100+ |
| `riddle` | 1 static fallback | Expand fallback to 40+ |
| `simple_recipe` | 1 static fallback | Expand fallback to 30+ |
| `personal_affirmation` | 1 static fallback | Expand fallback to 30+ |

### Priority 2 — High (address within next sprint)
| Provider | Issue | Fix |
|---|---|---|
| `ai_trivia` | 6 categories | Expand + history exclusion |
| `color_match` | 50 items, no cycling | Date-seeded random |
| `country_spotlight` | 50 items + 3-item fallback | Expand + date-seeded |
| `famous_face` | 42 items | Expand to 120+, date-seeded |
| `finish_phrase` | 45 items, era-weighted | History exclusion |
| `hymn_of_the_day` | 40 items | Expand to 100+, date-seeded |
| `morning_stretch` | 47 items | Date-seeded cycling |
| `old_saying_match` | 45 items | Expand to 120+, date-seeded |
| `puzzle` | Small config pool | Expand config |
| `riddle` (LLM path) | 5 LLM styles | Expand + history exclusion |
| `simple_recipe` (LLM path) | 5 LLM categories | Expand + history exclusion |
| `word_connect` | 15 pairs | Expand to 50+, date-seeded |
| `word_scramble` | 19 words base | Expand to 100+ |
| `family_greeting` | Per-family cycling | Cycle family members in order |
| `song_of_the_day` | Per-singer cycling | Cycle singers in order |
| `letter_to_family` | 10 themes, 5 fallbacks | Expand both |

### Priority 3 — Medium (polish)
| Provider | Issue | Fix |
|---|---|---|
| `bingo` | No date-seeded cycling | Date-seeded selection |
| `classic_art` | Small fallback | Expand fallback + history on API results |
| `daily_blessing` | 90 items, no cycling | Date-seeded or history exclusion |
| `hobby_spotlight` | Small patient hobby list | History exclusion + date in prompt |
| `hymn_of_the_day` | 40 items | Expand |
| `missing_vowels` | 15 base words | Expand + history exclusion |
| `number_sequence` | 83 items | Date-seeded cycling |
| `pen_pal_letter` | Small friend pool | Expand + history exclusion |
| `seasonal_poem` | 2 fallbacks per season | Expand to 20+ per season |
| `wikimedia_gallery` | No repeat tracking | Track shown filenames |
| `word_of_the_day` | 80 items | Date-seeded + expand |

### Priority 4 — Low / Already Good
`complete_the_duo`, `gridless_crossword`, `local_history`, `memory_lane_photo`, `nature_scene`, `newsletter_footer`, `newsletter_header`, `simple_math`, `this_day_history`, `weather`, `world_news`, `dog_photo`, `joke`, `spot_the_difference`, `nature_park` (API path), `comic_*` (if category is large)

---

## Recommended Shared Infrastructure

### 1. `pick_avoiding_recent()` utility
New file: `app/services/care_circle/variety_utils.py`

Provides a single function used by any provider that selects from a pool:
- Reads a rolling history JSON from `cache/_history/{key}.json` (common) or `cache/{patient_id}/history/{key}.json` (patient-specific)
- Excludes items seen in the last N days (configurable, default 14)
- Falls back to full pool if all items are in history (pool exhausted)
- Saves the chosen item back to history

### 2. Date-seeded `random` for common providers
For common providers where you want deterministic-per-day behaviour (stable under re-renders), use the `complete_the_duo` pattern:
```python
import hashlib, random
seed = int(hashlib.md5(target_date.isoformat().encode()).hexdigest(), 16) % (2**32)
rng = random.Random(seed)
choice = rng.choice(pool)
```
This is the recommended replacement for bare `random.choice()` in all common providers.

### 3. Date injection into LLM prompts
Update `DEMENTIA_SYSTEM_PROMPT` in `llm_helpers.py` (or each provider's prompt) to include the current date. This anchors LLM output to the day and naturally encourages fresh content.

### 4. Fallback pool expansion
Expand all fallback pools with fewer than 30 entries. This is a pure content task (JSON/Python list additions) that requires no architectural change.

### 5. `daily_quote` API endpoint fix
One-line fix in `daily_quote/provider.py`: change `zenquotes.io/api/today` to `zenquotes.io/api/random`.
