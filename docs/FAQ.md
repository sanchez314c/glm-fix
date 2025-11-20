# Frequently Asked Questions

## Why does this error happen?

**Q: What causes the "Invalid `signature` in `thinking` block" error?**

Anthropic's Opus model validates cryptographic signatures on every `thinking` block in a conversation's history. When you use Claude Code sub-agents powered by non-Opus models (GLM-5, Sonnet, Haiku, etc.), those models produce `thinking` blocks with an empty `signature` field. The session works fine while you're still on that model. The moment you switch back to Opus, the API checks the entire message history and rejects it.

The error looks like:
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error",
"message":"messages.11.content.0: Invalid `signature` in `thinking` block"}}
```

---

## Is it safe to run glmfix on my sessions?

**Q: Could glmfix damage my session files?**

The tool creates a timestamped backup of every file before touching it:
```
<uuid>.jsonl.backup.20260215_183401
```

After writing the repaired file, it re-scans it to confirm zero unsigned blocks remain. If the validation check fails (which would indicate a bug in the repair logic), the tool deletes the bad output and restores the original from backup automatically. You can't end up with a damaged file without also having the original sitting in a backup next to it.

**Q: Should I run `--dry-run` first?**

For `fix-all`, yes — it's a good habit. Dry run runs the full repair pipeline but skips the write step, so you can see exactly how many blocks would be removed from each session before committing.

---

## What actually gets removed?

**Q: What does glmfix delete from my sessions?**

Only thinking blocks where `signature` is empty or missing. Specifically:
- `{"type": "thinking", "thinking": "...", "signature": ""}` — removed
- `{"type": "thinking", "thinking": "..."}` (no signature key) — removed
- `{"type": "thinking", "thinking": "...", "signature": "ErUBCkYI..."}` — kept

All other content is preserved: user messages, text blocks, tool_use blocks, tool_result blocks, and thinking blocks that have valid signatures.

If an assistant message line becomes completely empty after stripping thinking blocks, that line is removed too. An empty message serves no purpose in conversation continuity.

**Q: Will removing thinking blocks break the conversation?**

No. Thinking blocks contain internal model reasoning that was used to generate a response, but the response itself is stored separately in text blocks. The conversation history that matters for continuity — what the user said, what the assistant replied — remains intact.

---

## Session discovery

**Q: Where does glmfix look for session files?**

It globs `~/.claude/projects/*/*.jsonl`. If your Claude Code stores sessions somewhere else, the tool won't find them. The path is hardcoded at the top of `glmfix.py`:

```python
CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
```

**Q: Can I use glmfix on a specific file path instead of scanning by session ID?**

Not directly. The `fix` command takes a session UUID (or partial UUID), not an arbitrary file path. You can work around this by finding the session ID from the filename and passing it to `glmfix.py fix <id>`.

---

## Partial UUID matching

**Q: How many characters of a session ID do I need to provide?**

Enough to uniquely identify one session. The first 8 characters is usually sufficient. If you provide a partial ID that matches multiple sessions, glmfix will tell you and ask for more characters:

```
Multiple sessions match 'b85':
  b85fc237-332b-446a-942e-4cbadea72c2b
  b85a1109-...

Provide more characters to narrow the match.
```

---

## The slash command

**Q: The `/glmfix` command says it can't find `glmfix.py`. What do I do?**

The `commands/glmfix.md` file has a hardcoded path to `glmfix.py`. Open the file and update this line to match where you actually cloned the repo:

```
The repair engine lives at: ~/Desktop/Projects/00_github-INPROCESS/glmfix/glmfix.py
```

**Q: Does `/glmfix` work offline?**

Yes. glmfix makes zero network calls. The slash command runs locally via Bash.

---

## Backups

**Q: Where do backups go?**

Alongside the original session file. If your session is:
```
~/.claude/projects/-home-user-tasks/b85fc237-...c2b.jsonl
```

The backup is:
```
~/.claude/projects/-home-user-tasks/b85fc237-...c2b.jsonl.backup.20260215_183401
```

**Q: Can I delete old backups?**

Yes. Once you've verified the repaired session works (by resuming it in Claude Code), the backup is no longer needed. The `.gitignore` excludes `*.backup.*` from version control.

---

## Errors

**Q: glmfix says "No session files found." but I have Claude Code sessions.**

Check that `~/.claude/projects/` exists and contains subdirectories with `.jsonl` files:

```bash
ls ~/.claude/projects/
ls ~/.claude/projects/*/*.jsonl
```

If the directory doesn't exist, Claude Code hasn't been used yet on this machine or uses a non-standard installation path.
