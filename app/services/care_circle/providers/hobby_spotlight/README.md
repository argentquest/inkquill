# Hobby Spotlight Provider

## Purpose
A warm personal story about one of your favourite hobbies.

## Runtime Contract
- Provider key: `hobby_spotlight`
- Registry category: `lifestyle`
- Registry order: `28`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `False`

## How It Works Today
Uses Care Circle LLM helpers with the dementia-safe system prompt, then falls back to local/static data if generation fails.

- Care Circle LLM helpers used: `generate_image_url_with_usage`, `generate_json_with_usage`, `generate_text_with_usage`
- External sources used: No external API or feed dependency is used at runtime.
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: No. This provider renders per execution and does not participate in the shared daily HTML cache.
- Difficulty metadata status: No difficulty metadata is declared for this provider.

## Inputs Used At Runtime
- Patient preference keys read: `era_of_youth`, `hobbies`, `hometown`, `life_roles`, `nationality_or_background`
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: No provider-specific config keys are read at runtime beyond the merged base config object.

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `hobby`, `story`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Validate and coerce the generated JSON shape before returning it so templates are protected from malformed or partial model output.
- Normalize patient preference access through a shared helper; the provider layer currently mixes raw `preferences` and nested `preferences.preferences` access patterns.
