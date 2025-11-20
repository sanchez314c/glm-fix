# Troubleshooting

## The Error That Brought You Here

```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error",
"message":"messages.N.content.0: Invalid `signature` in `thinking` block"}}
```

This means a session in your conversation history contains an unsigned thinking block. Run:

```bash
python3 glmfix.py scan
```

Then fix the corrupted session with:

```bash
python3 glmfix.py fix <partial-session-id>
```

---

## Common Issues

### "No session files found."

**Cause:** `~/.claude/projects/` doesn't exist or is empty.

**Check:**
```bash
ls ~/.claude/projects/
```

If the directory doesn't exist, Claude Code hasn't created any sessions on this machine yet. If it exists but is empty, you haven't had any conversations that generated session files.

If Claude Code is installed somewhere non-standard, edit the path constants at the top of `glmfix.py`:

```python
CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
```

---

### "No session found matching: <id>"

**Cause:** The session ID you provided doesn't match any file in `~/.claude/projects/`.

**Fix:**
1. Run `python3 glmfix.py scan` to list all corrupted sessions with their IDs.
2. Copy the first 8 characters of the session ID you want to fix.
3. Run `python3 glmfix.py fix <those-8-chars>`.

---

### "Multiple sessions match '<partial-id>'"

**Cause:** Your partial UUID matches more than one session filename.

**Fix:** Provide more characters. The output shows all matching session IDs — copy enough characters from one to make it unique.

---

### "VALIDATION FAILED — restored backup"

**Cause:** After writing the repaired file, glmfix re-scanned it and still found unsigned thinking blocks. This indicates a bug in the repair logic.

**What happened:** The original file was automatically restored from backup. Your session is unchanged.

**Fix:** Open a GitHub issue with:
- The output of `python3 glmfix.py scan --verbose` for the affected session
- Your Python version (`python3 --version`)
- The session ID (first 8 chars is fine)

---

### Repair says "0 blocks removed" but session is still broken

**Cause:** The session corruption might be a different type than unsigned thinking blocks, or the error message points to a message that glmfix correctly identifies as clean.

**Check:** Run scan with verbose to see the exact block counts:
```bash
python3 glmfix.py scan --verbose
```

If `bad_thinking` is 0 but you're still getting the API error, the problem might be:
- The session is being resumed from a different machine where the corruption happened
- Claude Code has a cached version of the session that glmfix didn't touch
- The 400 error is caused by something other than unsigned thinking blocks (check the full error message for the field path, e.g., `messages.11.content.0`)

---

### "Error reading <filepath>: ..."

**Cause:** The session file is malformed, corrupted at the filesystem level, or permission-restricted.

**Check:**
```bash
python3 -c "
import json
with open('/path/to/session.jsonl') as f:
    for i, line in enumerate(f):
        try:
            json.loads(line.strip())
        except Exception as e:
            print(f'Line {i}: {e}')
"
```

---

### The `/glmfix` slash command can't find `glmfix.py`

**Cause:** The path hardcoded in `commands/glmfix.md` doesn't match where you cloned the repo.

**Fix:** Open `commands/glmfix.md` (and `~/.claude/commands/glmfix.md` if you've already copied it) and update the path on this line:

```
The repair engine lives at: ~/Desktop/Projects/00_github-INPROCESS/glmfix/glmfix.py
```

Change it to the actual location of `glmfix.py` on your machine.

---

### Backup file is taking up too much space

Session JSONL files can be large (multi-megabyte conversations). If you have many backups:

```bash
# See how much space backups are using
du -sh ~/.claude/projects/*/*.backup.* 2>/dev/null | sort -h

# Remove backups older than 7 days (once you've verified sessions work)
find ~/.claude/projects -name "*.backup.*" -mtime +7 -delete
```

---

### Python version error

**Cause:** Running Python older than 3.8.

**Check:**
```bash
python3 --version
```

If you're on Python 3.7 or older, either upgrade Python or use a system that has 3.8+. The minimum version requirement exists because glmfix uses `f-strings` and `pathlib` patterns that aren't available in older versions.

---

## Getting Help

If none of the above resolves your issue:

1. Run `python3 glmfix.py scan --verbose` and capture the full output.
2. Note your Python version and OS.
3. Open an issue at [github.com/sanchez314c/glmfix](https://github.com/sanchez314c/glmfix) using the bug report template.

Include a redacted session ID (first 8 chars only — don't share the full UUID) if relevant.
