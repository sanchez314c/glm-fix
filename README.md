# glmfix

Repair Claude Code session files corrupted by cross-model thinking block signatures.

## The Problem

Claude Code stores conversation history as JSONL files in `~/.claude/projects/`. When you use sub-agents powered by different models (like GLM-5 or other non-Opus models), those models produce `thinking` blocks without valid cryptographic signatures. The session keeps working fine under that model, but the moment you switch back to Opus, the API validates every thinking block signature in the conversation history and rejects the whole session:

```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error",
"message":"messages.11.content.0: Invalid `signature` in `thinking` block"}}
```

Your session is now dead. You can't resume it. All that context is stuck.

**glmfix** fixes this. It strips only the unsigned thinking blocks and leaves everything else intact. The thinking content is just internal model reasoning and isn't needed for conversation continuity. Your session comes back to life.

## Features

- **Scan** all sessions across all Claude Code projects for corruption
- **Fix** a specific session by full or partial UUID
- **Fix all** corrupted sessions in one shot
- **Dry run** mode to preview changes without touching anything
- **Automatic backups** with timestamps before any modification
- **Post-repair validation** to make sure the fix actually worked
- **Claude Code slash command** integration via `/glmfix`

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)

## Installation

### As a Claude Code slash command (recommended)

Copy the skill file into your Claude Code commands directory:

```bash
cp commands/glmfix.md ~/.claude/commands/glmfix.md
```

Then use `/glmfix` inside any Claude Code session to scan and fix corrupted sessions.

### Standalone CLI

Just clone the repo. No install step needed.

```bash
git clone https://github.com/sanchez314c/glmfix.git
cd glmfix
```

## Usage

### CLI

```bash
# Scan all sessions for corruption
python3 glmfix.py scan

# Scan with extra detail per file
python3 glmfix.py scan --verbose

# Fix a specific session (partial UUID works)
python3 glmfix.py fix b85fc237

# Fix all corrupted sessions at once
python3 glmfix.py fix-all

# Preview what fix-all would do, without modifying files
python3 glmfix.py fix-all --dry-run
```

### Slash Command

Inside a Claude Code session:

```
/glmfix                    Scan all sessions, report corrupted ones
/glmfix scan               Same as above
/glmfix b85fc237           Fix session matching this partial ID
/glmfix fix-all            Repair all corrupted sessions
```

### Example Output

**Scan:**

```
  CORRUPTED  b85fc237    85 bad blocks   233 msgs  tasks
  CORRUPTED  d3a9f112     3 bad blocks    47 msgs  portfolio

Scanned 42 sessions: 2 corrupted, 40 clean, 88 total unsigned thinking blocks
```

**Fix:**

```
Repairing session b85fc237...
  File: /home/user/.claude/projects/-home-user-tasks/b85fc237-332b-446a-942e-4cbadea72c2b.jsonl
  Bad thinking blocks: 85
  Good thinking blocks: 5
  Total messages: 233

  REPAIR COMPLETE
  Backup: b85fc237-332b-446a-942e-4cbadea72c2b.jsonl.backup.20260215_183401
  Thinking blocks removed: 85
  Empty lines removed: 85
  Lines: 320 -> 235
```

## How It Works

1. Scans all `.jsonl` session files under `~/.claude/projects/`
2. Parses each line as JSON, checks assistant messages for `thinking` blocks
3. Flags any thinking block with an empty or missing `signature` field
4. Before modifying anything, creates a timestamped backup (`.backup.YYYYMMDD_HHMMSS`)
5. Strips the unsigned thinking blocks from content arrays
6. Removes any assistant message lines that become empty after stripping
7. Re-reads the repaired file and validates zero unsigned blocks remain
8. If validation fails, restores the backup automatically

## Project Structure

```
glmfix/
  glmfix.py                # The repair engine (single file, stdlib only)
  commands/
    glmfix.md              # Claude Code slash command skill definition
  docs/
    README.md              # Documentation index
    ARCHITECTURE.md        # 8-step repair process and data flow
    INSTALLATION.md        # Setup as CLI and slash command
    DEVELOPMENT.md         # Dev environment, testing, adding repair strategies
  .github/
    ISSUE_TEMPLATE/
      bug_report.md
      feature_request.md
    PULL_REQUEST_TEMPLATE.md
  README.md
  CHANGELOG.md
  CONTRIBUTING.md
  SECURITY.md
  CLAUDE.md
  AGENTS.md
  LICENSE
  .gitignore
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for dev setup and guidelines.

## License

MIT License. See [LICENSE](LICENSE) for details.
