# glmfix - AI Assistant Context

## What This Project Does

glmfix repairs Claude Code session files that get corrupted when you use sub-agents powered by non-Opus models (like GLM-5). Those models produce `thinking` blocks without valid cryptographic signatures. When you switch back to Opus, the API rejects the entire session because of the unsigned blocks. glmfix strips only the bad thinking blocks and brings the session back to life.

## Tech Stack

- Python 3.8+ (stdlib only, zero external dependencies)
- Single-file architecture: everything is in `glmfix.py`
- JSONL parsing with the standard `json` module
- File operations via `pathlib` and `os`

## File Structure

```
glmfix.py              # The entire repair engine (scan, fix, fix-all)
commands/glmfix.md     # Claude Code slash command definition for /glmfix
README.md              # User-facing docs
CHANGELOG.md           # Version history
CONTRIBUTING.md        # How to contribute
SECURITY.md            # Security policy
LICENSE                # MIT
.gitignore
.github/
  ISSUE_TEMPLATE/
    bug_report.md
    feature_request.md
  PULL_REQUEST_TEMPLATE.md
docs/
  README.md            # Documentation index
  ARCHITECTURE.md      # How the 8-step repair process works
  INSTALLATION.md      # Setup instructions
  DEVELOPMENT.md       # Dev environment and extending the tool
```

## Key Commands

```bash
# Scan all sessions for corruption
python3 glmfix.py scan
python3 glmfix.py scan --verbose

# Fix a specific session (partial UUID works)
python3 glmfix.py fix b85fc237

# Fix all corrupted sessions
python3 glmfix.py fix-all

# Preview changes without modifying anything
python3 glmfix.py fix-all --dry-run
```

## Key Decisions

- **Stdlib only.** No pip installs, no venvs, no dependency management. This runs anywhere Python 3.8+ exists.
- **Single file.** One script does everything. No package structure, no imports from local modules.
- **Backup before modify.** Every fix creates a timestamped backup via atomic `os.rename()`. If validation fails, the backup is restored automatically.
- **Thinking blocks are disposable.** The tool removes unsigned thinking blocks entirely. These contain internal model reasoning and aren't needed for conversation continuity. Signed blocks are preserved.
- **Partial UUID matching.** Users can pass the first 8 characters of a session ID instead of the full UUID.

## Data Flow

Session files live at `~/.claude/projects/<encoded-project-name>/<uuid>.jsonl`. Each line is a JSON object with a `message` field containing `role` and `content`. Thinking blocks sit inside the `content` array with `"type": "thinking"` and a `signature` field. If `signature` is empty or missing, that block is unsigned and will cause Opus to reject the session.

## Testing

There's no test suite. Validate changes by running against real session files:

```bash
python3 glmfix.py scan --verbose
python3 glmfix.py fix-all --dry-run
```
