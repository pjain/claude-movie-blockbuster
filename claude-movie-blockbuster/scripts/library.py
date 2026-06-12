#!/usr/bin/env python3
"""
Claude Movie Blockbuster — library management script.

Usage:
  library.py read [--path PATH]
  library.py write --data JSON [--path PATH]
  library.py find --query QUERY [--type TYPE] [--path PATH]
  library.py sync-notes [--path PATH]
  library.py restore-notes [--path PATH]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import date

DEFAULT_PATH = os.path.expanduser("~/.movie-agent/library.json")
NOTES_TITLE = "Claude Movie Blockbuster"
NOTES_SEPARATOR = "--- JSON (do not edit below this line) ---"

EMPTY_LIBRARY = {
    "schema_version": "3.0",
    "profile": {
        "default_region": None,
        "preferred_platforms": [],
        "preferred_genres": [],
        "preferred_languages": [],
        "preferred_countries": [],
        "favorite_titles": [],
        "favorite_people": [],
        "sync_target": None,
        "sync_errors": [],
        "notion_database_id": None,
        "airtable_base_id": None,
        "airtable_table_name": None,
        "updated_at": None,
    },
    "watchlist": [],
    "watched": [],
    "ratings": [],
    "removed": [],
}


# ── JSON helpers ──────────────────────────────────────────────────────────────

def read_library(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        return dict(EMPTY_LIBRARY)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_library(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    dir_ = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def normalize(s):
    return s.lower().strip() if s else ""


def find_title(library, query, media_type=None):
    results = []
    for list_name in ("watchlist", "watched", "ratings", "removed"):
        for record in library.get(list_name, []):
            ids = record.get("ids", {})
            if query in (ids.get("imdb"), ids.get("tmdb")):
                results.append({"list": list_name, "record": record, "score": 2})
                continue
            title_match = normalize(query) in (
                normalize(record.get("title", "")),
                normalize(record.get("original_title", "")),
            )
            type_match = media_type is None or record.get("media_type") == media_type
            if title_match and type_match:
                results.append({"list": list_name, "record": record, "score": 1})
    results.sort(key=lambda x: -x["score"])
    return results


# ── Apple Notes helpers ───────────────────────────────────────────────────────

def _stars_str(record):
    stars = record.get("rating_user", {}).get("stars")
    if stars is None:
        return ""
    full = int(stars)
    half = 1 if (stars - full) >= 0.5 else 0
    return "★" * full + ("½" if half else "")


def _build_note_body(library):
    today = date.today().isoformat()
    lines = [
        f"{NOTES_TITLE} — Movie & TV Library",
        f"Last updated: {today}",
        "",
    ]
    watchlist = library.get("watchlist", [])
    watched = library.get("watched", [])

    lines.append(f"=== WATCHLIST ({len(watchlist)}) ===")
    for r in watchlist:
        platforms = ", ".join(
            p.get("platform", "") for p in r.get("where_to_watch", {}).get("providers", [])
        )
        line = f"• {r.get('title')} ({r.get('media_type', '').capitalize()}, {r.get('year', '?')})"
        if platforms:
            line += f" — {platforms}"
        lines.append(line)

    lines.extend(["", f"=== WATCHED ({len(watched)}) ==="])
    for r in watched:
        stars = _stars_str(r)
        prefix = f"{stars} " if stars else ""
        watched_date = r.get("watched_at", "")
        line = (
            f"{prefix}{r.get('title')} ({r.get('media_type', '').capitalize()}, {r.get('year', '?')})"
        )
        if watched_date:
            line += f" — watched {watched_date}"
        lines.append(line)

    lines.extend([
        "",
        NOTES_SEPARATOR,
        json.dumps(library, indent=2, ensure_ascii=False),
    ])
    return "\n".join(lines)


def _run_applescript(script):
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"osascript error: {result.stderr.strip()}")
    return result.stdout.strip()


def sync_to_notes(library):
    body = _build_note_body(library)
    # Escape backslashes and double quotes for AppleScript string literal.
    body_escaped = body.replace("\\", "\\\\").replace('"', '\\"')
    script = f"""
tell application "Notes"
    if exists note "{NOTES_TITLE}" of default account then
        set body of note "{NOTES_TITLE}" of default account to "{body_escaped}"
    else
        make new note at default account with properties {{name:"{NOTES_TITLE}", body:"{body_escaped}"}}
    end if
end tell
"""
    _run_applescript(script)


def restore_from_notes():
    script = f"""
tell application "Notes"
    if exists note "{NOTES_TITLE}" of default account then
        return body of note "{NOTES_TITLE}" of default account
    else
        return ""
    end if
end tell
"""
    html = _run_applescript(script)
    # Strip HTML tags.
    text = re.sub(r"<[^>]+>", "", html)
    # Decode common HTML entities.
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&#39;", "'")
    # Find JSON block after separator.
    sep_pos = text.find(NOTES_SEPARATOR)
    if sep_pos < 0:
        # Try to find raw JSON if separator missing.
        json_start = text.find("{")
        if json_start < 0:
            raise ValueError(f'No JSON found in Notes note "{NOTES_TITLE}".')
        return json.loads(text[json_start:])
    json_text = text[sep_pos + len(NOTES_SEPARATOR):].strip()
    return json.loads(json_text)


# ── CLI commands ──────────────────────────────────────────────────────────────

def cmd_read(args):
    print(json.dumps(read_library(args.path), indent=2, ensure_ascii=False))


def cmd_write(args):
    data = json.loads(args.data)
    write_library(args.path, data)
    print("ok")


def cmd_find(args):
    lib = read_library(args.path)
    results = find_title(lib, args.query, getattr(args, "type", None))
    print(json.dumps(results, indent=2, ensure_ascii=False))


def cmd_sync_notes(args):
    lib = read_library(args.path)
    sync_to_notes(lib)
    print("ok")


def cmd_restore_notes(args):
    lib = restore_from_notes()
    write_library(args.path, lib)
    print(f"Restored {len(lib.get('watchlist', []))} watchlist and "
          f"{len(lib.get('watched', []))} watched records to {args.path}")


def main():
    parser = argparse.ArgumentParser(description="Claude Movie Blockbuster library manager")
    parser.add_argument("--path", default=DEFAULT_PATH, help="Path to library.json")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("read", help="Print library JSON")

    wp = sub.add_parser("write", help="Atomically write library JSON")
    wp.add_argument("--data", required=True, help="JSON string to write")

    fp = sub.add_parser("find", help="Search library by title or ID")
    fp.add_argument("--query", required=True)
    fp.add_argument("--type", default=None, dest="type")

    sub.add_parser("sync-notes", help="Sync library to Apple Notes")
    sub.add_parser("restore-notes", help="Restore library.json from Apple Notes")

    args = parser.parse_args()
    dispatch = {
        "read": cmd_read,
        "write": cmd_write,
        "find": cmd_find,
        "sync-notes": cmd_sync_notes,
        "restore-notes": cmd_restore_notes,
    }
    fn = dispatch.get(args.cmd)
    if fn is None:
        parser.print_help()
        sys.exit(1)
    fn(args)


if __name__ == "__main__":
    main()
