# GNews Provider

## Purpose
Fetches current news articles from the GNews API with support for keyword search, top headlines, language/country filtering, and category selection.

## Runtime Contract
- Provider key: `gnews`
- Registry category: `core`
- Patient-safe class flag: `True`
- Common HTML cache: `True`

## How It Works
The provider connects to the GNews REST API (`https://gnews.io/api/v4/`) and supports two modes:

### Search Mode (default)
Keyword-based article search. Useful for city-specific queries (e.g., "Montreal") or topic searches.
- Endpoint: `/api/v4/search`
- Parameters: `q` (query), `lang`, `country`, `category`, `max`

### Top Headlines Mode
Returns top headlines ranked by Google News, optionally filtered by category and country.
- Endpoint: `/api/v4/top-headlines`
- Parameters: `lang`, `country`, `category`, `max`

## Configuration Options

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mode` | string | `"search"` | API mode: `"search"` or `"top-headlines"` |
| `query` | string | `"positive news"` | Search query (search mode only) |
| `lang` | string | `"en"` | Language code (e.g., `en`, `fr`, `es`) |
| `country` | string | `"us"` | Country code (e.g., `us`, `ca`, `gb`) |
| `category` | string | `""` | Topic category (general, world, business, etc.) |
| `max` | int | `5` | Number of articles to return (max 100) |
| `cache_ttl` | int | `600` | Cache TTL in seconds (10 minutes) |

## Supported Categories
`general`, `world`, `nation`, `business`, `technology`, `entertainment`, `sports`, `science`, `health`

## Rate Limits & Plan Constraints
GNews plans limit requests per day and articles per request:
- **Free**: 100 requests/day, 10 articles/request, 12-hour delay
- **Essential**: 1,000 requests/day, 25 articles/request, real-time
- **Business**: 5,000 requests/day, 50 articles/request
- **Enterprise**: 25,000 requests/day, 100 articles/request

The provider includes in-memory caching to reduce duplicate API calls.

## Error Handling
- Returns fallback stories when API key is missing or API call fails
- Deduplicates articles by URL (primary) or title+source hash (fallback)
- Logs warnings on API failures

## Environment Variables
- `GNEWS_API_KEY`: Required for API access (register at https://gnews.io/)

## Output Shape
```json
{
  "articles": [
    {
      "id": "stable_hash_id",
      "title": "Article Title",
      "description": "Short summary",
      "url": "https://...",
      "image_url": "https://...",
      "published_at": "2026-04-19T08:00:00Z",
      "source_name": "Publication Name",
      "source_url": "https://...",
      "provider": "gnews"
    }
  ],
  "source": "GNews"
}
```

## Improvement Opportunities
- Add headline content filtering to suppress distressing stories
- Add per-city bilingual query support (e.g., separate EN/FR requests for Montreal)
- Consider persisting cache to disk for longer TTL across session restarts
