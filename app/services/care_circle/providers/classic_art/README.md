# Classic Art Provider

## Purpose
Displays a beautiful public-domain painting from the Metropolitan Museum of Art, complete with the title, artist name, date, medium, and a short warm description. Every image is CC0 — free to use with no attribution required.

## Runtime Contract
- Provider key: `classic_art`
- Registry category: `memory`
- Registry order: `41`
- Globally enabled in root catalog: `True`
- Patient visible in root catalog: `True`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works Today
1. Picks a random search term from a curated list (e.g. "landscape", "flowers", "portrait").
2. Queries the Met Open Access search endpoint for public-domain artworks that have images.
3. Picks a random object ID from the first 200 results.
4. Fetches the full object record to get the image URL, title, artist, date, and medium.
5. Builds a short readable description from the metadata fields.

Falls back to a pre-defined list of eight well-known classic artworks when the API is unavailable.

- Care Circle LLM helpers used: None.
- External sources used: Metropolitan Museum of Art Open Access API (`collectionapi.metmuseum.org`)
- Internal helper generators: None.
- Daily common-cache behavior: Yes. `common: true` in `config.json` caches the rendered HTML per day and theme.

## Inputs Used At Runtime
- Patient preference keys read: None.
- Direct patient-profile attributes read: None.
- Provider config keys read: `search_terms` (optional override), `fallback_artworks` (optional override).

## Render Assets
- Templates present: `default`
- Provider-specific themes present: `master_online`, `master_print`

## Output Shape
Payload fields returned by the provider:

| Field | Type | Description |
|-------|------|-------------|
| `title` | str | Artwork title |
| `artist` | str | Artist display name |
| `date` | str | Date or date range |
| `medium` | str | Medium (e.g. "Oil on canvas") |
| `image_url` | str | Direct image URL (CC0) |
| `met_url` | str | Link to the Met's collection page |
| `description` | str | Short warm description built from metadata |
| `search_term` | str | The search term used for this fetch |

## API Reference
- Human browsing: https://www.metmuseum.org/art/collection
- API documentation: https://metmuseum.github.io
- License: CC0 — No rights reserved
