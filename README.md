# Claude Movie Blockbuster

A Claude Code skill for international movie and TV discovery, ratings, streaming
availability, watchlists, and watch history — with optional sync to Apple Notes
(macOS), Notion, or Airtable.

Once installed, just talk to Claude naturally. No slash commands needed.

> "Find Parasite and where I can watch it in the US"  
> "Add Shogun to my watchlist"  
> "I watched The Bear season 3 — it was fantastic"  
> "Recommend Korean thrillers on Netflix"

---

## Requirements

- **Claude Code** (CLI) or **Claude Desktop** — [get it here](https://claude.ai/download)
- **Python 3.8+** — for the local library script (`python3 --version` to check)
- **Git** — for the recommended clone + symlink install

---

## Installation

### macOS / Linux

**Option A — Copy (simple):**
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/pjain/claude-movie-blockbuster /tmp/claude-movie-blockbuster
cp -R /tmp/claude-movie-blockbuster/claude-movie-blockbuster ~/.claude/skills/claude-movie-blockbuster
```

**Option B — Symlink (recommended — gets updates with `git pull`):**
```bash
git clone https://github.com/pjain/claude-movie-blockbuster ~/projects/claude-movie-blockbuster
mkdir -p ~/.claude/skills
ln -s ~/projects/claude-movie-blockbuster/claude-movie-blockbuster ~/.claude/skills/claude-movie-blockbuster
```

### Windows

Open **PowerShell** (run as Administrator for the symlink option):

**Option A — Copy:**
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"
git clone https://github.com/pjain/claude-movie-blockbuster "$env:TEMP\claude-movie-blockbuster"
Copy-Item -Recurse "$env:TEMP\claude-movie-blockbuster\claude-movie-blockbuster" `
  "$env:USERPROFILE\.claude\skills\claude-movie-blockbuster"
```

**Option B — Symlink (recommended):**
```powershell
git clone https://github.com/pjain/claude-movie-blockbuster "$env:USERPROFILE\projects\claude-movie-blockbuster"
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\claude-movie-blockbuster" `
  -Target "$env:USERPROFILE\projects\claude-movie-blockbuster\claude-movie-blockbuster"
```

> **Windows note:** On Windows, use `python` instead of `python3` in any library commands below.

### Verify the install

After installing, confirm the skill files are in place:

**macOS / Linux:**
```bash
ls ~/.claude/skills/claude-movie-blockbuster/
# Expected: SKILL.md  references/  scripts/
```

**Windows (PowerShell):**
```powershell
Get-ChildItem "$env:USERPROFILE\.claude\skills\claude-movie-blockbuster"
# Expected: SKILL.md  references  scripts
```

---

## First use

Start Claude Code in any directory and ask about a movie or TV show:

```
Find The Dark Knight — IMDb rating and where I can watch it in the US
```

On first use, Claude will ask:
1. **Your default geography** for streaming availability (e.g., `US`, `IN`, `GB`, `CA`)
2. **Where to sync your library**: Apple Notes (macOS only), Notion, Airtable, or local only

Your library is then saved to `~/.movie-agent/library.json` (macOS/Linux) or
`%USERPROFILE%\.movie-agent\library.json` (Windows).

---

## API keys (optional but recommended)

Without keys, Claude falls back to web search. With keys, lookups are faster and more accurate.

| Key | Where to get it | Cost |
|---|---|---|
| `TMDB_API_KEY` | [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api) | Free |
| `OMDB_API_KEY` | [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx) | Free tier |
| `WATCHMODE_API_KEY` | [api.watchmode.com](https://api.watchmode.com/) | Free tier (optional) |

**macOS / Linux** — add to your shell profile (`~/.zshrc`, `~/.bashrc`):
```bash
export TMDB_API_KEY=your_key_here
export OMDB_API_KEY=your_key_here
export WATCHMODE_API_KEY=your_key_here   # optional
```

**Windows** — set permanently via PowerShell:
```powershell
[System.Environment]::SetEnvironmentVariable("TMDB_API_KEY", "your_key_here", "User")
[System.Environment]::SetEnvironmentVariable("OMDB_API_KEY", "your_key_here", "User")
```
Restart Claude Code after setting variables.

---

## Sync options

| Option | Platform | How it works |
|---|---|---|
| **Apple Notes** | macOS only | A single "Claude Movie Blockbuster" note — readable list + JSON block |
| **Notion** | All | Syncs to a Notion database (Notion MCP must be connected) |
| **Airtable** | All | Syncs to an Airtable base (Airtable MCP must be connected) |
| **Local only** | All | `library.json` on disk, no external sync |

### Apple Notes (macOS only)

Claude syncs automatically after each library change. To sync or restore manually:

```bash
# Sync to Notes
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py sync-notes

# Restore library.json from Notes (e.g., after losing the local file)
python3 ~/.claude/skills/claude-movie-blockbuster/scripts/library.py restore-notes
```

### Notion and Airtable

Connect the Notion or Airtable MCP in Claude Desktop first, then tell Claude during
first-run setup that you want to sync there. Claude will walk you through creating
the database/base and configuring it.

---

## Library management commands

The bundled `library.py` script lets you inspect and manage your library directly.

**macOS / Linux:**
```bash
SCRIPT=~/.claude/skills/claude-movie-blockbuster/scripts/library.py

python3 $SCRIPT read              # print full library JSON
python3 $SCRIPT find --query "Shogun" --type tv   # search by title or ID
```

**Windows:**
```powershell
$SCRIPT = "$env:USERPROFILE\.claude\skills\claude-movie-blockbuster\scripts\library.py"

python $SCRIPT read
python $SCRIPT find --query "Shogun" --type tv
```

---

## Capabilities

| What you can ask | Examples |
|---|---|
| Find movies / TV | "Find Interstellar", "Look up Succession" |
| Ratings | "What's the IMDb rating for The Bear?" |
| Streaming availability | "Where can I watch Oppenheimer in India?" |
| Add to watchlist | "Add Dune: Part Two to my watchlist" |
| Mark watched | "I watched Parasite last night" |
| Rate titles | "Parasite was fantastic" / "thumbs up for Shogun" |
| Recommendations | "Recommend A24 horror movies I can stream in the US" |
| Find by person/studio | "Movies by Denis Villeneuve", "All Studio Ghibli films" |
| TV tracking | "Mark Shogun season 1 as watched" |
| International titles | "Find Korean thrillers", "Bollywood films on Netflix" |

---

## What's different from the original Movie-Agent skill

| Feature | Movie-Agent (Hermes/OpenClaw) | Claude Movie Blockbuster |
|---|---|---|
| Install target | Hermes, OpenClaw | Claude Code / Claude Desktop (all platforms) |
| API access | Generic guidance | Exact WebFetch URL patterns |
| JSON writes | Basic | Atomic via `library.py` (no corruption on crash) |
| Apple Notes | Not mentioned | First-class sync (macOS) |
| Notion / Airtable | "V2 future" | First-class (Notion/Airtable MCP) |
| Streaming cache | No rule | 7-day expiry enforced |
| TV support | Movies-first | Full TV season/episode tracking |
| Trigger description | Minimal | Rich — catches all natural-language intents |

---

## Troubleshooting

**Skill not activating?**
- Confirm the directory name is exactly `claude-movie-blockbuster` (not `claude-movie-blockbuster-main` from a ZIP download)
- Run `ls ~/.claude/skills/claude-movie-blockbuster/SKILL.md` to verify the file exists

**`python3` not found on Windows?**
- Use `python` instead of `python3`
- Install Python from [python.org](https://www.python.org/downloads/) if needed (add to PATH during install)

**Apple Notes sync fails?**
- Notes.app must be installed and signed in (it is by default on macOS)
- If you see a permissions error, go to System Settings → Privacy & Security → Automation and allow Terminal/Claude Code to control Notes

**Symlink not working on Windows?**
- Run PowerShell as Administrator, or enable Developer Mode in Windows Settings → System → Developer Mode

---

## Library location

| Platform | Default path |
|---|---|
| macOS / Linux | `~/.movie-agent/library.json` |
| Windows | `%USERPROFILE%\.movie-agent\library.json` |

---

## License

MIT
