# Puzzle Provider

## Purpose
Fun word search and fill-in-the-blank puzzles to enjoy.

## Runtime Contract
- Provider key: `puzzle`
- Registry category: `games`
- Registry order: `4`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
Builds the payload from local config, curated in-code data, or deterministic helper logic without calling external services.

- Care Circle LLM helpers used: No Care Circle LLM helper is called.
- External sources used: No external API or feed dependency is used at runtime.
- Internal helper generators: `_get_fill_in_the_blank`, `_get_word_pair`, `_get_word_search`
- Daily common-cache behavior: Yes. Because `common` is true in `config.json`, rendered HTML is cached per day and theme by the base provider.
- Difficulty metadata status: Not currently. `config.json` declares difficulty metadata, but `provider.py` does not read `self.difficulty_config`.

## Inputs Used At Runtime
- Patient preference keys read: `favorite_activities`
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: `filler_words`, `grid_size`, `min_custom_words`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `across`, `answer`, `answer_length`, `clues`, `down`, `grid`, `instruction`, `phrase`, `puzzle_content`, `title`, `type`, `words`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Add deterministic seeding so the same patient and date can reproduce the same puzzle when a session is regenerated.
- Split the three puzzle modes into smaller tested helpers with explicit payload schemas to make template changes safer.
- Either wire `difficulty_config` into runtime generation or remove the unused difficulty metadata from `config.json` so the docs and implementation do not drift.
