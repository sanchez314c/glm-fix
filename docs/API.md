# API Reference

glmfix is a single-file CLI tool with no importable API surface. All public-facing behavior is through the command line. This document covers the internal function signatures for contributors and agents extending the tool.

## CLI Interface

### Entry Point

```
python3 glmfix.py <command> [options]
```

| Command | Arguments | Description |
|---------|-----------|-------------|
| `scan` | `[--verbose\|-v]` | Scan all sessions, report corrupted ones |
| `fix` | `SESSION_ID` | Fix one session by full or partial UUID |
| `fix-all` | `[--dry-run]` | Fix every corrupted session |
| `<uuid>` | (positional) | Shorthand — treats unknown arg as session ID to fix |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success (or no corrupted sessions found) |
| `1` | Failure (repair failed, session not found, ambiguous match) |

---

## Internal Functions

### `find_session_files() -> list[str]`

Globs for all `.jsonl` session files under `~/.claude/projects/*/`. Returns a list of absolute file paths sorted by modification time (newest first).

**Returns:** `list[str]` — absolute paths to JSONL files

---

### `analyze_session(filepath: str) -> dict`

Reads a session JSONL file and counts signed vs unsigned thinking blocks.

**Parameters:**
- `filepath` — absolute path to a `.jsonl` session file

**Returns dict with keys:**

| Key | Type | Description |
|-----|------|-------------|
| `filepath` | `str` | Path to the file |
| `session_id` | `str` | UUID extracted from filename stem |
| `project` | `str` | Human-readable project name (decoded from directory name) |
| `total_lines` | `int` | Total number of lines in the file |
| `total_messages` | `int` | Number of lines with a `message.role` field |
| `good_thinking` | `int` | Count of thinking blocks with a non-empty `signature` |
| `bad_thinking` | `int` | Count of thinking blocks with an empty or missing `signature` |
| `bad_line_numbers` | `list[int]` | 0-indexed line numbers containing unsigned blocks |
| `first_user_msg` | `str` | First user message, truncated to 150 characters |
| `last_modified` | `datetime` | File modification timestamp |
| `file_size` | `int` | File size in bytes |

---

### `fix_session(filepath: str, dry_run: bool = False) -> dict`

Removes unsigned thinking blocks from a session file. Creates a timestamped backup before modifying. Validates the repair and restores the backup if validation fails.

**Parameters:**
- `filepath` — absolute path to a `.jsonl` session file
- `dry_run` — if `True`, runs the full repair pipeline but skips the file write

**Returns dict with keys:**

| Key | Type | Description |
|-----|------|-------------|
| `filepath` | `str` | Path to the file that was processed |
| `backup_path` | `str \| None` | Path to the backup file created, or `None` if no modification was needed |
| `removed_blocks` | `int` | Number of unsigned thinking blocks stripped |
| `removed_lines` | `int` | Number of assistant message lines removed (empty after stripping) |
| `original_lines` | `int` | Line count before repair |
| `final_lines` | `int` | Line count after repair |
| `success` | `bool` | `True` if repair succeeded or file was already clean |
| `dry_run` | `bool` | Whether this was a dry run |

---

### `find_session_by_id(session_id_partial: str) -> list[str]`

Finds session files matching a full or partial UUID.

**Parameters:**
- `session_id_partial` — a full UUID or at least the first few characters of one

**Returns:** `list[str]` — matching absolute file paths (empty if no match, multiple if ambiguous)

---

### `cmd_scan(verbose: bool = False) -> list[dict]`

Prints scan results to stdout. Returns the list of corrupted session analysis dicts.

---

### `cmd_fix(session_id_partial: str) -> bool`

Fixes one session and prints results. Returns `True` on success.

---

### `cmd_fix_all(dry_run: bool = False) -> bool`

Fixes all corrupted sessions and prints per-session results. Returns `True` if all succeeded.

---

## JSONL Data Format

Each line in a session file is a JSON object. The relevant structure:

```json
{
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "thinking",
        "thinking": "internal reasoning text...",
        "signature": "ErUBCkYIARgCIkD..."
      },
      {
        "type": "text",
        "text": "Response text here."
      }
    ]
  }
}
```

A thinking block is considered **unsigned** (corrupted) when `signature` is `""` or the key is absent entirely. A non-empty `signature` string means the block is **signed** (valid).

## Slash Command Interface

The `/glmfix` slash command in `commands/glmfix.md` wraps the CLI. It parses `$ARGUMENTS` and maps them to the CLI modes above. The skill file is not a Python module — it's a Claude Code custom command definition that invokes `glmfix.py` via Bash.
