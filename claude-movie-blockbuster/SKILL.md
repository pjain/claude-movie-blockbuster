---
name: claude-movie-blockbuster
description: >
  International movie and TV discovery, ratings, streaming availability, watchlists,
  watch history, and recommendations. Use when the user asks to: find a movie or TV
  show; look up IMDb or Rotten Tomatoes ratings; check where to stream something;
  add a title to their watchlist; mark something as watched; rate something they
  watched; remove a title from any list; get recommendations; find titles by
  director, actor, creator, writer, studio, network, streamer, genre, country,
  language, or franchise; track TV seasons or episodes; or manage their personal
  movie and TV library.
---

# Claude Movie Blockbuster

## Purpose

International movie and TV discovery, ratings, streaming availability, watchlists,
watched history, and recommendations. Uses Claude's native tools — WebFetch, Read,
Write, Bash — and connected MCP servers (Notion, Airtable) plus macOS Apple Notes
via osascript.

Supported: movies, documentaries, shorts, specials, TV shows, miniseries, anime,
reality TV, web series, seasons, episodes, international titles.

## First-run setup

Check whether `~/.movie-agent/library.json` exists.

If it does not:
1. Ask: "What geography should I use by default for streaming availability? (e.g., US, IN, GB)"
2. Store as `profile.default_region` (stable country code).
3. Ask: "Would you like to sync your library to Apple Notes, Notion, or Airtable — or keep it local only?"
   - **Apple Notes** (macOS): Sync to a single "Claude Movie Blockbuster" note you can browse natively.
   - **Notion**: Sync to a Notion database (Notion MCP required).
   - **Airtable**: Sync to an Airtable base (Airtable MCP required).
   - **Local only**: Default JSON at `~/.movie-agent/library.json`.
4. Follow the setup in `references/schemas.md` for the chosen sync target.

Temporary geography: if the user says "I'm in India this week," use `IN` for the current query only unless they explicitly ask to update the default.

## Core entity model

Use **title** for both movies and TV. Every stored record must include `media_type`:
`movie`, `tv`, `season`, `episode`, `special`, `unknown`

TV disambiguation:
- "Add Shogun" → show level (`level: "show"`)
- "I watched Shogun season 1" → season 1 (`level: "season"`)
- "Episode 3 was ok" → episode 3 (confirm show/season if ambiguous)
- If level is ambiguous and affects storage, ask one concise question.

## Data sources

See `references/provider-guide.md` for source priority and international handling.
See `references/api-patterns.md` for exact WebFetch URL patterns.

1. **TMDB** — metadata, stable IDs, cast, crew, watch providers.
2. **OMDb** — IMDb rating + Rotten Tomatoes rating in one call (match by IMDb ID).
3. **Watchmode / TMDB watch providers** — streaming availability by geography.
4. **TVDB, Trakt, or web search** — fallback for international TV or missing fields.

Never fabricate ratings, availability, seasons, or episodes. Use `unknown` when a
source does not return a field.

## Local storage

Default path: `~/.movie-agent/library.json`. Always read before writing.

**Preferred write method (safe atomic write):**
```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py write --data '<json>'
```

**Read method:**
```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py read
```

**Search local library:**
```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py find --query "Shogun" --type tv
```

If the script path is unavailable, use the Read and Write tools directly.

Streaming availability expires after **7 days**. Re-fetch if `where_to_watch.checked_at` is absent or older than 7 days.

De-duplicate by: (1) `ids.imdb`, (2) `ids.tmdb + media_type`, (3) normalized `media_type + title + year`. See `references/schemas.md`.

## Sync targets

After every successful local write, sync to the user's chosen `profile.sync_target`.

### Apple Notes (`"notes"`)

```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py sync-notes
```

Writes a formatted note titled **"Claude Movie Blockbuster"** to the default Notes account.
The note contains a human-readable library summary followed by a JSON block Claude
can parse on demand. See `references/schemas.md` for the note format.

Restore from Notes (e.g., if local JSON is lost):
```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py restore-notes
```

### Notion (`"notion"`)

Use the Notion MCP tools (`notion-create-pages`, `notion-update-page`). Store the
returned `notion_page_id` in each local record. See `references/schemas.md`.

### Airtable (`"airtable"`)

Use Airtable MCP tools. Store `airtable_record_id` in each local record.
See `references/schemas.md`.

**Sync failure handling:** Log failures in `profile.sync_errors` and continue.
Never block a local write on a sync failure.

## Rating system

See `references/rating-guide.md` for the full normalization table.

Store raw + normalized:
- `rating.raw`: original user phrase
- `rating.scale`: `stars_5`, `thumbs`, or `inferred_stars_5`
- `rating.stars`: 0.5–5.0
- `rating.thumbs`: `up`, `down`, or `neutral`
- `rating.sentiment`: `positive`, `mixed`, `negative`, `neutral`

Quick reference:
- "I loved it" → 5.0 stars, positive
- "Fantastic" → 4.0 stars, positive
- "Good" → 3.5 stars, positive/mixed
- "Ok" / "Okay" → 3.0 stars, mixed
- "thumbs up" → thumbs `up` (use 4.0 stars only if stars are required)
- "thumbs down" → thumbs `down` (use 2.0 stars only if required)

## Task workflows

### Find title

1. Resolve movie vs. TV (TMDB multi-search when ambiguous).
2. Prefer IMDb/TMDB ID when user provides one.
3. Retrieve: metadata, IMDb rating, RT rating, streaming by geography.
4. For TV: include status, season count, original network, latest/next season.
5. Refresh `where_to_watch` if older than 7 days.
6. Return a table. Offer to add to watchlist as natural next step.

Output columns: Title | Type | Year | IMDb | RT | Where to watch in {REGION} | Notes

### Add to watchlist

1. Resolve title and media type.
2. If already in `watched`, ask whether to also add to watchlist or skip.
3. If already in `watchlist`, update metadata and `updated_at`; no duplicate.
4. Store show-level for TV by default.
5. Write locally, then sync.
6. Confirm with title, year, and media type.

### Mark watched

1. Resolve against `watchlist`, `watched`, and fresh lookup.
2. Determine level: movie, show, season, or episode.
3. Add/update in `watched` with `status: "watched"` and `watched_at` (today).
4. Move from `watchlist` unless user asks to keep it.
5. Capture optional rating, notes, rewatch flag, watched platform.
6. Write locally, then sync.

Examples:
- "I watched Parasite and loved it" → watched + 5.0 stars
- "Finished Shogun season 1, fantastic" → season 1 watched + 4.0 stars
- "Episode 3 was ok" → episode 3 watched + 3.0 stars (confirm show/season first)

### Rate title

1. Resolve title and media type.
2. Normalize rating using the rating system.
3. Update `watched` record if present; else update `watchlist`; else create minimal `watched` if wording implies viewing.
4. Write locally, then sync.

### Remove

1. Search all lists: `watchlist`, `watched`, `ratings`, `removed`.
2. One match → remove from all active lists. Multiple matches → ask first.
3. Confirm exactly what was removed. Write locally, then sync.

### Recommend

1. Load watched history, user ratings, watchlist, preferences, default geography.
2. Highly rated watched titles = positive signals. Thumbs-down / low stars = negative signals.
3. Candidates from TMDB similar/recommendations, genre/person/company/network overlaps.
4. Support filters: type, genre, country, language, actor, director, creator, network,
   streamer, production house, franchise, decade, geography.
5. Exclude watched unless rewatch requested. De-prioritize watchlist unless "what should I watch next."
6. Annotate streaming availability in selected geography.
7. Return 5–10 recommendations with one-sentence rationale each.
8. When history is sparse, say so and ask for favorite genres or titles.

### Find by person, company, network, country, language, genre, or franchise

Examples: "Shows by Phoebe Waller-Bridge", "Korean thrillers on Netflix US",
"All Studio Ghibli films", "HBO miniseries I haven't watched".

1. Identify entity type: director, actor, creator, writer, genre, company, network,
   streamer, country, language, or franchise.
2. Use TMDB structured endpoints (person credits, company/keyword discover, network discover).
3. Sort by user's intent (default: relevance/popularity).
4. Annotate watched/watchlist/rating status from local storage.
5. Filter by geography-specific availability when requested.

## Reference files (load on demand — not all upfront)

- `references/schemas.md` — JSON schema, title record shape, Notion/Airtable/Notes schemas
- `references/provider-guide.md` — source priority, international TV, fallback rules
- `references/api-patterns.md` — exact WebFetch URL patterns for TMDB, OMDb, Watchmode
- `references/rating-guide.md` — rating normalization table and ambiguity rules

## Safety

- Do not scrape sites that prohibit automated access when a structured API exists.
- Do not fabricate ratings, availability, seasons, episodes, or providers.
- 7-day streaming availability cache max.
- Keep API keys out of `library.json` and out of chat.
- Confirm ambiguous destructive operations before removing records.
- Do not sync watch history to third-party services without explicit user authorization.
