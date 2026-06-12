# Schemas

## Local data file

Default path: `~/.movie-agent/library.json`

```json
{
  "schema_version": "3.0",
  "profile": {
    "default_region": null,
    "preferred_platforms": [],
    "preferred_genres": [],
    "preferred_languages": [],
    "preferred_countries": [],
    "favorite_titles": [],
    "favorite_people": [],
    "sync_target": null,
    "sync_errors": [],
    "notion_database_id": null,
    "airtable_base_id": null,
    "airtable_table_name": null,
    "updated_at": null
  },
  "watchlist": [],
  "watched": [],
  "ratings": [],
  "removed": []
}
```

`sync_target` values: `null`, `"notes"`, `"notion"`, `"airtable"`.

## Title record

```json
{
  "title": "Shogun",
  "original_title": "Shogun",
  "media_type": "tv",
  "year": 2024,
  "status": "watchlist",
  "level": "show",
  "season_number": null,
  "episode_number": null,
  "ids": {
    "tmdb": "126308",
    "imdb": "tt2788316",
    "tvdb": null
  },
  "ratings_external": {
    "imdb": "8.6",
    "rotten_tomatoes": "99%"
  },
  "rating_user": {
    "raw": "Fantastic",
    "scale": "inferred_stars_5",
    "stars": 4.0,
    "thumbs": "up",
    "sentiment": "positive",
    "confidence": "high",
    "rated_at": "2026-06-11"
  },
  "genres": ["Drama", "War & Politics"],
  "countries": ["US", "JP"],
  "original_language": "en",
  "spoken_languages": ["en", "ja"],
  "directors": [],
  "creators": ["Rachel Kondo", "Justin Marks"],
  "cast": ["Hiroyuki Sanada", "Cosmo Jarvis", "Anna Sawai"],
  "networks": ["FX"],
  "production_companies": ["FX Productions"],
  "runtime_minutes": null,
  "episode_runtime_minutes": [59],
  "number_of_seasons": 1,
  "number_of_episodes": 10,
  "first_air_date": "2024-02-27",
  "last_air_date": "2024-04-23",
  "where_to_watch": {
    "region": "US",
    "checked_at": "2026-06-11",
    "providers": [
      { "platform": "Hulu", "access_type": "subscription", "deep_link": null }
    ]
  },
  "notion_page_id": null,
  "airtable_record_id": null,
  "added_at": "2026-06-11",
  "watched_at": null,
  "notes": "",
  "updated_at": "2026-06-11"
}
```

## Media type / level values

| media_type | level | Notes |
|---|---|---|
| `movie` | `title` | Feature films, shorts, documentaries, specials |
| `tv` | `show` | Full TV show (default for "add Shogun") |
| `season` | `season` | Requires `season_number` |
| `episode` | `episode` | Requires `season_number` + `episode_number` |
| `special` | `title` | One-off specials |
| `unknown` | `title` | Fallback |

## Status values

`watchlist` | `watched` | `rated` | `removed` (tombstone)

## De-duplication order

1. `ids.imdb`
2. `ids.tmdb` + `media_type`
3. `ids.tvdb` (TV only)
4. Normalized `media_type + title/original_title + year`
5. For seasons/episodes: include `season_number` and `episode_number`
6. If type or year missing and multiple matches exist → ambiguous, ask

## Apple Notes sync

`library.py sync-notes` writes a single note titled **"Claude Movie Blockbuster"** to
the default Notes account using osascript.

Note format (what gets written):
```
Claude Movie Blockbuster — Movie & TV Library
Last updated: 2026-06-11

=== WATCHLIST (2) ===
• Shogun (TV, 2024) — FX / Hulu
• Dune: Part Two (Movie, 2024) — Max

=== WATCHED (1) ===
★★★★★ Parasite (Movie, 2019) — watched 2026-05-20

--- JSON (do not edit below this line) ---
{ ... full library JSON ... }
```

To restore the library from Notes (e.g., after losing `library.json`):
```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py restore-notes
```
The script parses the JSON block below the separator line.

## Notion sync schema

Create a Notion database, then set `profile.notion_database_id` to its ID.

| Property | Type | Notes |
|---|---|---|
| Title | Title | Movie/show name |
| Year | Number | Release/first-air year |
| Media Type | Select | movie, tv, season, episode |
| Status | Select | watchlist, watched, rated |
| IMDb Rating | Text | e.g. "8.6" |
| RT Rating | Text | e.g. "99%" |
| User Stars | Number | 0.5–5.0 |
| User Thumbs | Select | up, down, neutral |
| Genres | Multi-select | |
| Where to Watch | Text | Comma-separated platforms |
| Region | Text | e.g. "US" |
| Added At | Date | |
| Watched At | Date | |
| Notes | Text | |
| TMDB ID | Text | For dedup |
| IMDb ID | Text | For dedup |

After creating a page, store the returned page ID in `notion_page_id`.
Use `notion-update-page` with that ID for subsequent updates.

## Airtable sync schema

Set `profile.airtable_base_id` and `profile.airtable_table_name`. Fields mirror
the Notion schema above. After creating a record, store its ID in `airtable_record_id`.

## User rating schema

```json
{
  "raw": "I loved it",
  "scale": "inferred_stars_5",
  "stars": 5.0,
  "thumbs": "up",
  "sentiment": "positive",
  "confidence": "high",
  "rated_at": "2026-06-11"
}
```

`scale`: `stars_5` | `thumbs` | `inferred_stars_5` | `unknown`
`thumbs`: `up` | `down` | `neutral` | `unknown`
`sentiment`: `positive` | `mixed` | `negative` | `neutral` | `unknown`

## Output templates

### Find title
```
| Title | Type | Year | IMDb | RT | Where to watch in {REGION} | Notes |
|---|---|---:|---:|---:|---|---|
| Shogun | TV | 2024 | 8.6 | 99% | Hulu (sub) | Checked today |
```

### Recommendation
```
1. **Pachinko (TV, 2022)** — Epic multigenerational drama; shares Shogun's
   historical scope and Japanese setting. Apple TV+ (US). IMDb: 8.4.
```
