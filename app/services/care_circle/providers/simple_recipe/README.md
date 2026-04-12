# Simple Recipe Provider

## Purpose
Generates a short recipe card tailored to familiar foods and simple preparation steps.

## Runtime Contract
- Provider key: `simple_recipe`
- Registry category: `lifestyle`
- Registry order: `15`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
Uses Care Circle LLM helpers with the dementia-safe system prompt, then falls back to local/static data if generation fails.

- Care Circle LLM helpers used: `generate_image_url_with_usage`, `generate_json_with_usage`, `generate_text_with_usage`
- External sources used: No external API or feed dependency is used at runtime.
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: Yes. Because `common` is true in `config.json`, rendered HTML is cached per day and theme by the base provider.
- Difficulty metadata status: Not currently. `config.json` declares difficulty metadata, but `provider.py` does not read `self.difficulty_config`.

## Inputs Used At Runtime
- Patient preference keys read: `era_of_youth`
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: No provider-specific config keys are read at runtime beyond the merged base config object.

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `ingredients`, `steps`, `title`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Either wire `difficulty_config` into runtime generation or remove the unused difficulty metadata from `config.json` so the docs and implementation do not drift.
- Validate and coerce the generated JSON shape before returning it so templates are protected from malformed or partial model output.
- Normalize patient preference access through a shared helper; the provider layer currently mixes raw `preferences` and nested `preferences.preferences` access patterns.
