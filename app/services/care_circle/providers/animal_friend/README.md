# Animal Friend Provider

## Purpose
Implements the `animal_friend` Care Circle provider and renders it through the shared base provider contract.

## Runtime Contract
- Provider key: `animal_friend`
- Registry category: `memory`
- Registry order: `33`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
Fetches remote content directly and falls back to config or embedded static content when the remote call fails.

- Care Circle LLM helpers used: No Care Circle LLM helper is called.
- External sources used: `Dog CEO API`
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: Yes. Because `common` is true in `config.json`, rendered HTML is cached per day and theme by the base provider.
- Difficulty metadata status: Not currently. `config.json` declares difficulty metadata, but `provider.py` does not read `self.difficulty_config`.

## Inputs Used At Runtime
- Patient preference keys read: No patient preference keys are read by this provider.
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: `warm_facts`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `animal`, `fact`, `image_url`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Clarify or rename the remote source path if the provider intentionally uses dog imagery for a generic animal card; right now the implementation reads more like a dog provider.
- Add an image reachability fallback so a dead remote image URL does not leave the card visually empty.
- Either wire `difficulty_config` into runtime generation or remove the unused difficulty metadata from `config.json` so the docs and implementation do not drift.
