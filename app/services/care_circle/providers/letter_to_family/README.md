# Letter to Family Provider

## Purpose
Generates a warm family-facing letter intended to spark connection and conversation.

## Runtime Contract
- Provider key: `letter_to_family`
- Registry category: `wellbeing`
- Registry order: `49`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `False`

## How It Works Today
Uses Care Circle LLM helpers with the dementia-safe system prompt, then falls back to local/static data if generation fails.

- Care Circle LLM helpers used: `generate_json_with_usage`
- External sources used: No external API or feed dependency is used at runtime.
- Internal helper generators: No dedicated helper generators; the provider returns directly from `_generate_payload`/`get_content`.
- Daily common-cache behavior: No. This provider renders per execution and does not participate in the shared daily HTML cache.
- Difficulty metadata status: No difficulty metadata is declared for this provider.

## Inputs Used At Runtime
- Patient preference keys read: No patient preference keys are read by this provider.
- Direct patient-profile attributes read: `display_name`
- Provider config keys read: `letters`

## Render Assets
- Templates present: `default`
- Provider-specific themes present: No provider-specific themes currently exist; rendering relies on the shared root theme CSS.
- Root theme support: The base provider can also prepend shared CSS from `app/services/care_circle/providers/themes/`.

## Output Shape
- Observed payload fields returned by the provider: `letter`, `suggested_prompt`, `title`
- Rendering path: `BaseCareCircleProvider.execute()` wraps the payload, renders `templates/default.html` when no `rendered_html` is provided, and returns `success`, `provider_key`, and `data`.

## Review Notes
- This README was regenerated from the live provider implementation, root provider catalog config, and the shared base-provider contract.
- Session assembly loads this provider through `app.services.care_circle.session_assembler.get_provider_class()` and mounts it only when the catalog entry is enabled, patient-visible, and the provider class is marked patient-safe.
- The React family admin and template tooling surface this provider through the Care Circle provider registry and template studio endpoints.

## Improvement Opportunities
- Add response-shape validation and content-length limits so generated letters stay usable for templates and downstream delivery.
- Consider capturing family context or patient preferences in the prompt so the generated letter is less generic.
- Validate and coerce the generated JSON shape before returning it so templates are protected from malformed or partial model output.
