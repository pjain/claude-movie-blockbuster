# Claude Movie Blockbuster

A Claude Code–native movie and TV skill: discovery, ratings, streaming availability,
watchlists, and watched history — with optional sync to Apple Notes, Notion, or Airtable.

## Capabilities

- Find movies and TV shows with IMDb, RT ratings, and streaming availability by geography.
- Add titles to a watchlist. Mark watched. Rate with stars or thumbs.
- Get personalized recommendations from watch history and ratings.
- Find titles by director, actor, creator, studio, network, genre, country, language, or franchise.
- TV season and episode tracking.
- Sync to **Apple Notes** (browse your library natively in Notes.app), **Notion**, or **Airtable**.

## Installation (Claude Code)

```bash
mkdir -p ~/.claude/skills
cp -R claude-movie-blockbuster ~/.claude/skills/claude-movie-blockbuster
```

Or clone and symlink (recommended — keeps the skill up-to-date):

```bash
git clone https://github.com/pjain/claude-movie-blockbuster ~/projects/claude-movie-blockbuster
ln -s ~/projects/claude-movie-blockbuster/claude-movie-blockbuster ~/.claude/skills/claude-movie-blockbuster
```

Claude Code loads the skill automatically — no slash command needed. Just ask about movies or TV.

## API keys (optional but recommended)

```bash
export TMDB_API_KEY=your_key        # free at themoviedb.org/settings/api
export OMDB_API_KEY=your_key        # free tier at omdbapi.com/apikey.aspx
export WATCHMODE_API_KEY=your_key   # optional; TMDB providers are the fallback
```

Without keys, Claude falls back to web search.

## Sync options

On first use, Claude asks which sync target you prefer:

| Option | How it works |
|---|---|
| **Apple Notes** (macOS) | Single "Claude Movie Blockbuster" note with a readable summary + JSON block |
| **Notion** | Notion database via Notion MCP (must be connected in Claude Desktop) |
| **Airtable** | Airtable base via Airtable MCP (must be connected in Claude Desktop) |
| **Local only** | `~/.movie-agent/library.json` only |

### Apple Notes — manual sync

```bash
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py sync-notes
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py restore-notes  # restore from Notes
```

## What's different from the original Movie-Agent skill

| Feature | Movie-Agent (Hermes/OpenClaw) | Claude Movie Blockbuster |
|---|---|---|
| Install target | Hermes, OpenClaw | Claude Code / Claude Desktop |
| API patterns | Generic guidance | Exact WebFetch URL patterns |
| JSON writes | Basic | Atomic via `library.py` |
| Apple Notes | Not mentioned | First-class sync via osascript |
| Notion / Airtable | "V2 future" | First-class (if MCP connected) |
| Streaming cache | No rule | 7-day expiry enforced |
| Trigger description | Minimal | Rich — catches all user intents |

## Library location

Default: `~/.movie-agent/library.json`

## License

MIT
