# Gridless Crossword Provider

## Purpose
Builds a crossword-style clue set where answer initials spell a secret word, using LLM generation with a static fallback.

## Runtime Contract
- Provider key: `gridless_crossword`
- Registry category: `games`
- Registry order: `26`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
Uses Care Circle LLM helpers with the dementia-safe system prompt, then falls back to local/static data if generation fails.

- Care Circle LLM helpers used: `generate_image_url_with_usage`, `generate_json_with_usage`, `generate_text_with_usage`
- External sources used: No external API or feed dependency is used at runtime.
- Internal helper generators: `_get_fallback`
- Daily common-cache behavior: Yes. Because `common` is true in `config.json`, rendered HTML is cached per day and theme by the base provider.
- Difficulty metadata status: Yes. Runtime logic references the shared difficulty helpers.

## Inputs Used At Runtime
- Patient preference keys read: No patient preference keys are read by this provider.
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: `day_categories`, `fallback_words`, `secret_words`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `answers`, `clues`, `instruction`, `secret_word`, `title`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Add payload-schema validation for clues, answers, and secret-word length before rendering.
- Persist daily generated puzzles or seed them deterministically so common-provider caching is backed by stable content generation.
- Validate and coerce the generated JSON shape before returning it so templates are protected from malformed or partial model output.
