# Newsletter Footer Provider

## Purpose
Implements the `newsletter_footer` Care Circle provider and renders it through the shared base provider contract.

## Runtime Contract
- Provider key: `newsletter_footer`
- Registry category: `layout`
- Registry order: `99`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `False`

## How It Works Today
Builds the payload from local config, curated in-code data, or deterministic helper logic without calling external services.

- Care Circle LLM helpers used: No Care Circle LLM helper is called.
- External sources used: No external API or feed dependency is used at runtime.
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: No. This provider renders per execution and does not participate in the shared daily HTML cache.
- Difficulty metadata status: No difficulty metadata is declared for this provider.

## Inputs Used At Runtime
- Patient preference keys read: No patient preference keys are read by this provider.
- Direct patient-profile attributes read: No direct patient-profile attributes beyond preference data are read.
- Provider config keys read: `disclaimer`, `elapsed_s`, `generation_date`, `llm_providers`, `model_used`, `total_providers`, `total_tokens`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: No provider-specific themes currently exist; rendering relies on the shared root theme CSS.
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `disclaimer`, `elapsed_s`, `generation_date`, `llm_providers`, `model_used`, `total_providers`, `total_tokens`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Consider treating layout providers as internal assembly components in the family UI so patient-level toggles do not expose non-content modules.
- Add a typed payload contract for footer metrics so generation stats do not silently disappear when upstream assembly changes.
