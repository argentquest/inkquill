# World News Provider

## Purpose
Top 5 world news headlines with short, plain-language summaries.

## Runtime Contract
- Provider key: `world_news`
- Registry category: `core`
- Registry order: `27`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
Combines remote source data with Care Circle LLM helpers before returning the final payload.

- Care Circle LLM helpers used: `generate_image_url_with_usage`, `generate_json_with_usage`, `generate_text_with_usage`
- External sources used: `RSS feed`
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: Yes. Because `common` is true in `config.json`, rendered HTML is cached per day and theme by the base provider.
- Difficulty metadata status: No difficulty metadata is declared for this provider.

## Inputs Used At Runtime
- Patient preference keys read: No patient preference keys are read by this provider.
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: `fallback_stories`, `item_count`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `stories`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Add headline deduping and content filtering before LLM summarization so syndicated or distressing stories can be suppressed more predictably.
- Cache or persist the fetched feed for the day to reduce repeated RSS and LLM calls during repeated patient session assembly.
- Validate and coerce the generated JSON shape before returning it so templates are protected from malformed or partial model output.
