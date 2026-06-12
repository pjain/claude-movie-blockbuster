# API Patterns

Use WebFetch with these patterns. Replace `{KEY}` with the environment variable value.
Check availability with `Bash: echo $TMDB_API_KEY` before using. If empty, fall back
to WebSearch or an official provider page and disclose the limitation.

## TMDB (metadata, IDs, cast, watch providers)

Base URL: `https://api.themoviedb.org/3`
Auth: `?api_key={TMDB_API_KEY}` appended to every request.

### Multi-search (type unknown)
```
GET /search/multi?api_key={KEY}&query={encoded_title}&page=1
```
Key fields: `results[].id`, `results[].media_type` (movie|tv), `results[].title`
or `results[].name`, `results[].release_date` or `results[].first_air_date`.

### Movie details
```
GET /movie/{tmdb_id}?api_key={KEY}&append_to_response=credits,external_ids,release_dates,watch/providers,recommendations,similar
```
Key fields: `id`, `imdb_id`, `title`, `release_date`, `runtime`, `genres`,
`production_companies`, `credits.crew` (filter `job=Director`), `credits.cast` (top 5),
`"watch/providers".results.{REGION}` (flatrate/rent/buy/free/ads).

### TV show details
```
GET /tv/{tmdb_id}?api_key={KEY}&append_to_response=credits,external_ids,content_ratings,watch/providers,recommendations,similar
```
Key fields: `id`, `name`, `first_air_date`, `status`, `number_of_seasons`,
`number_of_episodes`, `networks`, `created_by`, `origin_country`, `original_language`,
`"watch/providers".results.{REGION}`.

### TV season details (when episode-level tracking requested)
```
GET /tv/{tmdb_id}/season/{season_number}?api_key={KEY}
```
Key fields: `season_number`, `episode_count`, `episodes[].episode_number`,
`episodes[].name`, `episodes[].air_date`.

### Person credits (find by director/actor/creator)
```
GET /search/person?api_key={KEY}&query={name}        # get person_id
GET /person/{person_id}/combined_credits?api_key={KEY}
```

### Discover by company or network
```
GET /discover/movie?api_key={KEY}&with_companies={id}&sort_by=popularity.desc
GET /discover/tv?api_key={KEY}&with_networks={id}&sort_by=popularity.desc
```

### TMDB watch providers (from movie/TV details)

Structure: `"watch/providers".results.{REGION_CODE}`:
- `flatrate` → subscription
- `rent` → rental
- `buy` → purchase
- `free` or `ads` → free with ads

Region codes: `US`, `IN`, `GB`, `CA`, `JP`, `KR`, `FR`, `AU`, `DE`.

## OMDb (IMDb + Rotten Tomatoes ratings)

Base URL: `https://www.omdbapi.com/`

### By IMDb ID (preferred — avoids wrong-match risk)
```
GET /?apikey={OMDB_API_KEY}&i={imdb_id}&tomatoes=true
```
Key fields: `imdbRating`, `Ratings` array (filter `Source=Rotten Tomatoes` → `Value`).

### By title (fallback — verify year and type)
```
GET /?apikey={OMDB_API_KEY}&t={encoded_title}&y={year}&type=movie|series&tomatoes=true
```

## Watchmode (streaming availability)

Base URL: `https://api.watchmode.com/v1`

```
GET /search/?apiKey={WATCHMODE_API_KEY}&search_field=name&search_value={encoded_title}
GET /title/{watchmode_id}/sources/?apiKey={WATCHMODE_API_KEY}&regions={REGION_CODE}
```
Key fields: `name`, `type` (sub/rent/buy/free-ads/tve), `region`, `web_url`.

## Availability caching rule

Store `where_to_watch.checked_at` (ISO date) with every availability result.
Re-fetch if `checked_at` is absent or more than **7 days** old.

## Recommended environment variable names

```
TMDB_API_KEY
OMDB_API_KEY
WATCHMODE_API_KEY
```

Check with: `Bash: echo $TMDB_API_KEY`
