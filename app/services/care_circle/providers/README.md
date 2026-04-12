# Care Circle Providers

This directory contains the Care Circle provider modules used to assemble a patient's daily session. Each provider is loaded dynamically by `app.services.care_circle.session_assembler`, executed through `BaseCareCircleProvider`, and then rendered into patient-facing HTML with the provider's `templates/default.html` and the shared/root theme CSS.

## Shared Contract
- Provider modules live at `app.services.care_circle.providers.<provider_key>.provider`.
- `session_assembler.get_provider_class()` resolves the provider by naming convention and only mounts classes that inherit from `BaseCareCircleProvider`.
- Session assembly only runs providers whose catalog entries are enabled and patient-visible, and whose classes are marked `is_safe_for_patient = True`.
- Providers may return structured payload dictionaries or free-form content. The base class handles template rendering, fallback wrapping, and optional daily HTML caching for providers with `common = true`.

## What This Review Updated
- Rewrote or created provider-level `README.md` files so they match the live implementation instead of older design assumptions.
- Documented the actual runtime inputs, config keys, payload fields, templates, theme assets, and registry metadata for each provider.
- Added provider-level improvement notes based on the current code and framework wiring.

## Cross-Provider Findings
- Providers reviewed: `51`
- Providers using Care Circle LLM helpers: `22`
- Providers using an external API/feed or remote asset source: `7`
- Providers with provider-specific theme CSS files: `39`
- Providers whose `config.json` declares difficulty metadata that is currently unused in `provider.py`: `28`

### Important Framework Notes
- Most providers that declare `difficulty` in `config.json` do not currently read `self.difficulty_config`; only `gridless_crossword` and `simple_math` appear to use the shared difficulty helpers.
- Provider preference access is not fully normalized across the codebase. Some providers read `patient_profile.preferences` directly while others expect a nested `preferences.preferences` shape.
- The React template-admin helper currently reads and writes provider theme CSS from the `templates/` directory, while the Python base provider loads provider-specific CSS from each provider's `themes/` directory. That mismatch should be corrected before relying on template studio for theme editing.

## Providers With Unused Difficulty Metadata
- `ai_trivia`
- `animal_friend`
- `bingo`
- `brain_booster`
- `cat_fact`
- `color_match`
- `daily_affirmation`
- `daily_blessing`
- `daily_quote`
- `dog_photo`
- `finish_phrase`
- `gentle_exercise`
- `gratitude`
- `joke`
- `memory_lane_photo`
- `missing_vowels`
- `nature_scene`
- `nostalgia`
- `odd_one_out`
- `puzzle`
- `riddle`
- `sensory`
- `simple_recipe`
- `song_of_the_day`
- `this_day_history`
- `weather`
- `word_connect`
- `word_scramble`

## Providers Using External Sources
- `animal_friend`
- `daily_affirmation`
- `daily_quote`
- `dog_photo`
- `nature_scene`
- `weather`
- `world_news`

## Documentation Scope
These READMEs describe the code as it exists today. They do not assume future provider orchestration changes, admin UI improvements, or unpublished template editor behavior.
