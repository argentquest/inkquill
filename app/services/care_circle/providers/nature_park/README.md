# Nature Park Provider

## Purpose
Displays a beautiful public-domain photograph from a randomly selected U.S. National Park, together with the park name, image caption, and photographer credit. All NPS imagery is public domain and free to use.

## Runtime Contract
- Provider key: `nature_park`
- Registry category: `memory`
- Registry order: `42`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
1. Calls the NPS Parks endpoint for up to 500 parks, requesting the `images` field.
2. Filters to parks that have at least one photograph.
3. Picks a random park, then a random image from that park.
4. Returns the image URL, park name, title, caption, and credit.

If `NPS_API_KEY` is not set in the environment, or if the API call fails for any reason, the provider returns one of eight hardcoded fallback images from well-known parks (Yosemite, Grand Canyon, Yellowstone, etc.).

- Care Circle LLM helpers used: None.
- External sources used: NPS Open Data API (`developer.nps.gov`)
- Daily common-cache behavior: Yes. `common: true` in `config.json` caches the rendered HTML per day and theme.

## Setup
Register for a free NPS API key at: https://www.nps.gov/subjects/developer/get-started.htm

Add to your `.env`:
```
NPS_API_KEY=your_key_here
```

The provider works out of the box without a key — it simply uses the fallback images.

## Inputs Used At Runtime
- Patient preference keys read: None.
- Direct patient-profile attributes read: None.
- Provider config keys read: `fallback_images` (optional override for the built-in fallback list).

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`

## Output Shape

| Field | Type | Description |
|-------|------|-------------|
| `image_url` | str | Direct image URL (NPS public domain) |
| `park_name` | str | Full park name (e.g. "Yosemite National Park") |
| `title` | str | Image title from NPS metadata |
| `caption` | str | Image caption or alt text |
| `credit` | str | Photographer / credit line |

## API Reference
- NPS Developer Portal: https://www.nps.gov/subjects/developer/index.htm
- API Documentation: https://www.nps.gov/subjects/developer/api-documentation.htm
- License: Public Domain (U.S. Government Works)
