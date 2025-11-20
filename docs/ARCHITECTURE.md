# Architecture

## The Problem

Claude Code stores conversation history as JSONL files in `~/.claude/projects/`. Each line is a JSON object representing a message in the conversation. Assistant messages contain a `content` array, and some of those content blocks have `"type": "thinking"` with a `signature` field.

When sub-agents powered by non-Opus models (GLM-5, Sonnet, etc.) generate thinking blocks, those blocks lack valid cryptographic signatures. The session works fine under that model. But when you switch to Opus, the API validates every thinking block signature in the full conversation history and rejects the session with a 400 error.

The session is stuck. You can't resume it. glmfix fixes it.

## Data Flow

```
~/.claude/projects/
  <encoded-project-path>/
    <uuid>.jsonl          <-- one file per session
```

Each `.jsonl` line looks like:

```json
{"message": {"role": "assistant", "content": [{"type": "thinking", "thinking": "...", "signature": ""}, {"type": "text", "text": "..."}]}}
```

The `signature` field is the key. If it's empty or missing, that thinking block is unsigned and will cause the 400 error.

## The 8-Step Repair Process

### Step 1: Discovery

`find_session_files()` globs for all `*.jsonl` files under `~/.claude/projects/*/`. Results are sorted by modification time (newest first).

### Step 2: Parse

For each session file, `analyze_session()` reads every line and parses it with `json.loads()`. Malformed lines are skipped.

### Step 3: Detect

For each parsed message, the tool walks the `content` array looking for blocks with `"type": "thinking"`. It checks the `signature` field. Empty string or missing = unsigned = bad. Non-empty = signed = good.

### Step 4: Report

`cmd_scan()` collects all sessions with bad blocks and prints a summary. Each corrupted session shows: short ID, bad block count, message count, and project name. Verbose mode adds file path, size, good block count, first user message, and modification time.

### Step 5: Backup

Before modifying anything, `fix_session()` renames the original file to `<filename>.backup.YYYYMMDD_HHMMSS` using `os.rename()`. This is atomic on the same filesystem, so there's no window where the file is partially written.

### Step 6: Strip

The tool iterates every line again. For each thinking block with an empty or missing signature, it removes that block from the content array. If an assistant message ends up with an empty content array after stripping, the entire line is removed.

### Step 7: Write

The cleaned lines are written to the original filepath. Each line is re-serialized with `json.dumps()` plus a newline.

### Step 8: Validate

The repaired file is re-analyzed with `analyze_session()`. If any unsigned thinking blocks remain (which would mean the repair logic has a bug), the tool deletes the bad output, renames the backup back to the original path, and reports failure.

## Key Functions

| Function | Purpose |
|----------|---------|
| `find_session_files()` | Glob all JSONL session files, sorted by mtime |
| `analyze_session(filepath)` | Parse one file, count signed vs unsigned thinking blocks |
| `fix_session(filepath, dry_run)` | Backup, strip bad blocks, write, validate |
| `find_session_by_id(partial)` | Match a partial UUID against all session filenames |
| `cmd_scan(verbose)` | CLI: scan and report |
| `cmd_fix(session_id)` | CLI: fix one session |
| `cmd_fix_all(dry_run)` | CLI: fix all corrupted sessions |

## What Gets Removed, What Stays

**Removed:** Thinking blocks where `signature` is empty string `""` or missing entirely. Also, any assistant message line that becomes empty after stripping.

**Preserved:** Thinking blocks with a non-empty `signature`. All user messages. All text blocks. All tool_use and tool_result blocks. The overall structure of the JSONL file.

## Project Name Decoding

Claude Code encodes project paths in directory names by replacing `/` with `-`. So `/home/user/my-project` becomes `-home-user-my-project`. The `analyze_session()` function reverses this to show a human-readable project name in scan output.
