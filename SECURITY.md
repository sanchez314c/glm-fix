# Security Policy

## Scope

glmfix reads and writes Claude Code session files (JSONL format) stored in `~/.claude/projects/`. It also creates backup files in the same directory before making any changes.

This tool has direct filesystem access to your Claude Code conversation history. That's worth understanding before you run it.

## What It Touches

- **Reads** all `.jsonl` session files under `~/.claude/projects/*/`
- **Writes** repaired session files back to the same location
- **Creates** timestamped backup copies (`.backup.YYYYMMDD_HHMMSS`) before any modification
- **Restores** the original file automatically if post-repair validation fails

## Security Considerations

### File Path Handling

The tool constructs file paths using `pathlib.Path` rooted at `~/.claude/projects/`. It does not accept arbitrary file paths from user input for read/write operations. Session IDs are matched against filenames that already exist on disk, not used to construct new paths.

### JSONL Parsing

Each line of a session file is parsed with `json.loads()`. Malformed lines are skipped, not executed. The tool never calls `eval()`, `exec()`, or any dynamic code execution on session content.

### No Network Access

glmfix makes zero network calls. Everything is local filesystem operations. No data leaves your machine.

### Backup Safety

Before modifying any file, glmfix renames the original to a timestamped backup using `os.rename()` (atomic on the same filesystem). If the repair fails validation, the backup is restored and the bad output is deleted.

### Session Content Exposure

Running `scan --verbose` prints the first 80 characters of the first user message in each session. If you're sharing terminal output, be aware that this could include sensitive content from your conversations.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

If you find a security issue, please report it privately rather than opening a public issue.

**Contact:** J. Michaels ([@sanchez314c](https://github.com/sanchez314c) on GitHub)

Email or DM on GitHub. I'll respond within a few days. If the issue is confirmed, I'll push a fix and credit you in the changelog (unless you prefer to stay anonymous).
