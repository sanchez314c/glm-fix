# Learnings and Discoveries

Hard-won knowledge from building and testing glmfix. Useful context for anyone extending the tool.

## JSONL Is Not JSON

Claude Code session files are JSONL — each line is an independent JSON object. The entire file is NOT a valid JSON document. Trying to `json.load()` the whole file fails. You must read line-by-line and call `json.loads()` on each stripped line.

## Content Arrays Are Not Always Lists

User message content is sometimes a plain string and sometimes a list of block objects. You can't assume `content` is always iterable. Always check `isinstance(content, list)` before looping. The current code handles both:

```python
content = msg.get("content", "")
if isinstance(content, str):
    result["first_user_msg"] = content[:150]
elif isinstance(content, list):
    for block in content:
        ...
```

## `os.rename()` Is Atomic, `shutil.copy()` Is Not

The backup-before-modify pattern uses `os.rename()` to move the original to a backup path. This is atomic on the same filesystem — there's no window where the original doesn't exist. Using `shutil.copy()` followed by `os.remove()` would create a race condition and also leaves the original potentially intact on failure. `os.rename()` is the right call here.

## The Project Name Encoding Is Not Documented

Claude Code encodes project paths in directory names by replacing `/` with `-`. So `/home/user/my-project` becomes the directory name `-home-user-my-project`. This isn't documented anywhere in Claude Code's official docs — it was discovered by inspecting the actual directory structure. The decode logic in `analyze_session()` is a best-effort heuristic, not a guaranteed round-trip.

## Partial UUID Matching Is Enough

Users don't type full UUIDs. The first 8 hex characters are almost always enough to uniquely identify a session in any real-world Claude Code installation. The `find_session_by_id()` function uses `stem.startswith(partial)` rather than exact match, which lets users type short prefixes naturally.

## Validation Must Re-Parse, Not Re-Use State

After writing the repaired file, the post-repair validation re-reads the file from disk via a fresh call to `analyze_session()`. It does NOT check in-memory state. This matters because the write step (`json.dumps()` + file write) could theoretically introduce a serialization difference. Re-reading from disk catches that.

## Empty Assistant Messages Should Be Dropped

When all thinking blocks are stripped from an assistant message, the `content` array becomes empty. An assistant message with empty content has no value in the conversation history and will likely cause problems if Claude Code re-processes it. The repair logic detects this case and drops the entire line:

```python
if len(new_content) == 0 and msg.get("role") == "assistant":
    removed_lines += 1
    continue
```

## Signed Thinking Blocks Must Be Preserved

The original bug that prompted building this tool: an early version stripped ALL thinking blocks, not just unsigned ones. Signed thinking blocks (with a valid `signature` field) are cryptographically valid and Opus can process them fine. Removing them unnecessarily degrades conversation quality. The fix was simple — only remove blocks where `sig` is falsy.

## Verbose Mode Leaks Session Content

`scan --verbose` prints the first 80 characters of each session's first user message. This is useful for identifying which session is which, but it means terminal output could contain sensitive content from conversations. This was a deliberate tradeoff (usability vs. privacy) but it's worth noting. The SECURITY.md documents this.

## No Test Suite Means Manual Testing Is the Protocol

Without a test suite, every change to `glmfix.py` should be validated by:
1. Running `scan --verbose` against real sessions
2. Running `fix-all --dry-run` to confirm the repair logic doesn't crash
3. Running a real fix on one session and resuming it

The `--dry-run` flag is the safety net. Always use it before committing to `fix-all`.
