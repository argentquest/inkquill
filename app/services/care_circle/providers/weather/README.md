# Weather Provider

## Purpose
Today's weather forecast for your area with friendly suggestions.

## Runtime Contract
- Provider key: `weather`
- Registry category: `core`
- Registry order: `1`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `False`

## How It Works Today
Fetches remote content directly and falls back to config or embedded static content when the remote call fails.

- Care Circle LLM helpers used: No Care Circle LLM helper is called.
- External sources used: `wttr.in weather API`
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: No. This provider renders per execution and does not participate in the shared daily HTML cache.
- Difficulty metadata status: Not currently. `config.json` declares difficulty metadata, but `provider.py` does not read `self.difficulty_config`.

## Inputs Used At Runtime
- Patient preference keys read: `city_for_weather`
- Direct patient-profile attributes read: `display_name`
- Provider config keys read: `default_city`, `fallback`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `city`, `condition`, `subheading`, `temperature`, `text`, `type`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Add response normalization for missing temperature or condition fields and consider a short cache window to reduce dependency on repeated external calls.
- Normalize the temperature string encoding so rendered output does not carry mojibake in Fahrenheit labels.
- Either wire `difficulty_config` into runtime generation or remove the unused difficulty metadata from `config.json` so the docs and implementation do not drift.
